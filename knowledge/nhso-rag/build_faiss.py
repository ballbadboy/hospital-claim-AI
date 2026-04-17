"""
สปสช RAG — Build Index with FAISS
ใช้ FAISS vector store แทน SimpleVectorStore (หลีก JSON corruption)
"""
import os
import json
from pathlib import Path

VAULT = Path(__file__).parent.parent / "nhso-vault"
RAG_DIR = Path(__file__).parent
RAW_DIR = VAULT / "raw"  # note: raw/ gitignored; skip if missing
INDEX_DIR = RAG_DIR / "faiss_store"


def build_index():
    import faiss
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.core.storage import StorageContext
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.llms.ollama import Ollama
    from llama_index.vector_stores.faiss import FaissVectorStore

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.llm = Ollama(model="gemma4:latest", request_timeout=300.0)
    Settings.chunk_size = 512
    Settings.chunk_overlap = 64

    # nomic-embed-text dimension = 768
    faiss_index = faiss.IndexFlatL2(768)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    docs = []

    # Load wiki pages (concepts + sources + entities) — structured content
    wiki_dir = VAULT
    for subdir in ["concepts", "sources", "entities"]:
        d = wiki_dir / subdir
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix != ".md":
                continue
            text = f.read_text(encoding="utf-8")
            docs.append(Document(
                text=text,
                metadata={"type": subdir, "title": f.stem, "url": ""},
            ))
    print(f"Wiki pages: {len(docs)}")

    # Load transcripts
    t_count = 0
    for vid in sorted(os.listdir(RAW_DIR)):
        for fname in ["transcript_th.txt", "transcript_en.txt"]:
            p = RAW_DIR / vid / fname
            if p.exists():
                meta_p = RAW_DIR / vid / "metadata.json"
                meta = json.loads(meta_p.read_text()) if meta_p.exists() else {}
                title = meta.get("title", vid)
                docs.append(Document(
                    text=p.read_text(encoding="utf-8"),
                    metadata={"type": "transcript", "video_id": vid, "title": title, "url": f"https://youtu.be/{vid}"},
                ))
                t_count += 1
                break
    print(f"Transcripts: {t_count}")
    print(f"\nTotal: {len(docs)} docs — indexing...")

    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True,
    )

    index.storage_context.persist(persist_dir=str(INDEX_DIR))
    print(f"\n✅ FAISS index saved: {INDEX_DIR}")
    print(f"   Run: python3 query_faiss.py")


if __name__ == "__main__":
    build_index()
