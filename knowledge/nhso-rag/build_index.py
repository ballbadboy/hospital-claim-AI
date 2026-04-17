"""
สปสช RAG — Build Index
ใช้ transcript จาก raw/ + LlamaIndex SimpleFSVectorStore + Ollama embeddings
"""
import os
import json
from pathlib import Path

VAULT = Path(__file__).parent.parent / "nhso-vault"
RAG_DIR = Path(__file__).parent
RAW_DIR = VAULT / "raw"  # note: raw/ gitignored; skip if missing
INDEX_DIR = RAG_DIR / "index_store"


def load_transcript(video_id: str) -> str | None:
    base = RAW_DIR / video_id
    for fname in ["transcript_th.txt", "transcript_en.txt"]:
        p = base / fname
        if p.exists():
            return p.read_text(encoding="utf-8")
    return None


def load_metadata(video_id: str) -> dict:
    p = RAW_DIR / video_id / "metadata.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def build_index():
    from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.llms.ollama import Ollama

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.llm = Ollama(model="gemma4:latest", request_timeout=120.0)
    Settings.chunk_size = 512
    Settings.chunk_overlap = 64

    docs = []
    video_ids = sorted(os.listdir(RAW_DIR))
    print(f"Loading {len(video_ids)} videos...")

    for vid in video_ids:
        transcript = load_transcript(vid)
        if not transcript:
            print(f"  SKIP {vid} — no transcript")
            continue
        meta = load_metadata(vid)
        title = meta.get("title", vid)
        doc = Document(
            text=transcript,
            metadata={
                "video_id": vid,
                "title": title,
                "url": f"https://youtu.be/{vid}",
            },
        )
        docs.append(doc)
        print(f"  OK  {vid} — {title[:60]}")

    # Also index wiki pages (concepts/sources/entities) — richer structured content
    wiki_dir = VAULT
    wiki_count = 0
    for subdir in ["concepts", "sources", "entities"]:
        d = wiki_dir / subdir
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix != ".md":
                continue
            text = f.read_text(encoding="utf-8")
            doc = Document(
                text=text,
                metadata={"type": subdir, "title": f.stem, "url": ""},
            )
            docs.append(doc)
            wiki_count += 1
    print(f"  OK  {wiki_count} wiki pages (concepts/sources/entities)")

    print(f"\nIndexing {len(docs)} documents total (embedding via Ollama)...")
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
    index = VectorStoreIndex.from_documents(
        docs,
        transformations=[splitter],
        show_progress=True,
    )

    index.storage_context.persist(persist_dir=str(INDEX_DIR))
    print(f"\n✅ Index saved to: {INDEX_DIR}")
    print(f"   Documents: {len(docs)}")
    print(f"   Run: python3 query.py")


if __name__ == "__main__":
    build_index()
