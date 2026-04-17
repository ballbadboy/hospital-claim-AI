"""
สปสช RAG — Hybrid retrieval (semantic + keyword) + Ollama generation
- Semantic: FAISS vector search via LlamaIndex
- Keyword: direct grep over wiki pages (handles specific codes like C305)
- Generation: llama3.2:3b via subprocess (avoids pipeline timeouts)
"""
import re
import sys
import subprocess
from pathlib import Path

VAULT = Path(__file__).parent.parent / "nhso-vault"
RAG_DIR = Path(__file__).parent
INDEX_DIR = RAG_DIR / "faiss_store"
WIKI_DIR = VAULT

_retriever = None  # module-level cache


def _get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    from llama_index.core import Settings, StorageContext, load_index_from_storage
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.vector_stores.faiss import FaissVectorStore
    from llama_index.llms.ollama import Ollama

    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.llm = Ollama(model="gemma4:latest")

    vector_store = FaissVectorStore.from_persist_dir(str(INDEX_DIR))
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=str(INDEX_DIR)
    )
    index = load_index_from_storage(storage_context=storage_context)
    _retriever = index.as_retriever(similarity_top_k=8)
    return _retriever


def _semantic_retrieve(query: str, top_k: int = 8) -> list[dict]:
    retriever = _get_retriever()
    retriever._similarity_top_k = top_k
    nodes = retriever.retrieve(query)
    return [{"text": n.text, "score": n.score, "meta": n.metadata, "source": "semantic"} for n in nodes]


def _keyword_retrieve(query: str, max_files: int = 5) -> list[dict]:
    """Search wiki files directly for query terms — handles codes like C305."""
    results = []
    _STOPWORDS = {'FOR', 'AND', 'OR', 'THE', 'IS', 'IN', 'OF', 'TO', 'A', 'AN',
                  'BY', 'AT', 'ON', 'AS', 'BE', 'DO', 'GO', 'UP', 'VS'}

    # Extract keywords: C-codes (C305), acronyms (DMS, DMIS), Thai words ≥3 chars
    c_codes = re.findall(r'\b[A-Z]\d{3,}\b', query.upper())
    acronyms = [w for w in re.findall(r'\b[A-Z]{2,}\b', query.upper()) if w not in _STOPWORDS]
    eng_words = re.findall(r'\b[A-Za-z][a-z]{3,}\b', query)  # Seamless, Claim, etc.
    thai_words = re.findall(r'[\u0e00-\u0e7f]{3,}', query)
    keywords = list(set(c_codes + acronyms + [w.lower() for w in eng_words] + thai_words))

    if not keywords:
        return results

    wiki_pages = []
    for subdir in ["concepts", "entities", "sources"]:
        d = WIKI_DIR / subdir
        if d.exists():
            wiki_pages.extend(d.glob("*.md"))

    scored: list[tuple[float, Path]] = []
    for page in wiki_pages:
        try:
            text = page.read_text(encoding="utf-8")
        except Exception:
            continue
        content_hits = sum(1 for kw in keywords if kw.lower() in text.lower())
        if content_hits == 0:
            continue
        # Bonus: keywords appearing in the filename signal a dedicated concept page
        title_hits = sum(1 for kw in keywords if kw.lower() in page.stem.lower())
        score = content_hits + title_hits * 3  # weight title matches heavily
        scored.append((score, page))

    scored.sort(key=lambda x: -x[0])
    for hits, page in scored[:max_files]:
        text = page.read_text(encoding="utf-8")
        subdir = page.parent.name
        results.append({
            "text": text[:1500],
            "score": 0.0,  # keyword match, no vector score
            "meta": {"title": page.stem, "type": subdir, "url": ""},
            "source": "keyword",
        })

    return results


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Hybrid: semantic + keyword. Keyword results prepended (higher priority)."""
    keyword_chunks = _keyword_retrieve(query, max_files=3)
    semantic_chunks = _semantic_retrieve(query, top_k=top_k)

    # Deduplicate by title — keyword results win over semantic for same page
    seen_titles: set[str] = set()
    merged: list[dict] = []

    for chunk in keyword_chunks + semantic_chunks:
        title = chunk["meta"].get("title", "")
        if title not in seen_titles:
            seen_titles.add(title)
            merged.append(chunk)

    return merged[:top_k + 3]  # return a few extra for richer context


def generate(query: str, context_chunks: list[dict]) -> str:
    context = "\n\n---\n\n".join(
        f"[{c['meta'].get('title', 'unknown')}]\n{c['text'][:1000]}"
        for c in context_chunks
    )
    prompt = (
        "คุณเป็นผู้เชี่ยวชาญด้านการเบิกจ่ายสิทธิ์บัตรทอง สปสช\n"
        "กฎ: ตอบเป็นภาษาไทยเท่านั้น ห้ามใช้ภาษาอื่น\n"
        "กฎ: ใช้เฉพาะข้อมูลในส่วน 'ข้อมูลอ้างอิง' เท่านั้น\n"
        "กฎ: ถ้าไม่มีข้อมูลในส่วนอ้างอิง ให้ตอบว่า 'ไม่มีข้อมูลในระบบ'\n\n"
        f"ข้อมูลอ้างอิง:\n{context}\n\n"
        f"คำถาม: {query}\n\n"
        "คำตอบ (ภาษาไทย):"
    )

    result = subprocess.run(
        ["ollama", "run", "llama3.2:3b", prompt],
        capture_output=True, text=True, timeout=120
    )
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", result.stdout)
    return text.strip()


def main():
    if not INDEX_DIR.exists():
        print("❌ ยังไม่มี index — รัน: python3 build_faiss.py ก่อน")
        sys.exit(1)

    print("🔍 สปสช RAG — พิมพ์คำถาม (exit เพื่อออก)\n")
    print("กำลังโหลด index...")
    _get_retriever()
    print("พร้อมแล้ว\n")

    while True:
        try:
            q = input("คำถาม: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() == "exit":
            break

        print("\nกำลังค้นหา...")
        chunks = retrieve(q, top_k=5)

        print("\nแหล่งที่มา:")
        seen: set[str] = set()
        for c in chunks:
            title = c["meta"].get("title", "")
            url = c["meta"].get("url", "")
            key = title or url
            if key and key not in seen:
                tag = "[keyword]" if c["source"] == "keyword" else f"[{c['score']:.2f}]"
                line = f"  {tag} {title[:70]}"
                if url:
                    line += f" — {url}"
                print(line)
                seen.add(key)

        print("\nกำลังสร้างคำตอบ...")
        answer = generate(q, chunks)
        print(f"\nคำตอบ:\n{answer}\n")


if __name__ == "__main__":
    main()
