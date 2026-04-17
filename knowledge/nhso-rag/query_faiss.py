"""
สปสช RAG — Query with FAISS
"""
import sys
from pathlib import Path

VAULT = Path(__file__).parent.parent / "nhso-vault"
RAG_DIR = Path(__file__).parent
INDEX_DIR = RAG_DIR / "faiss_store"

SYSTEM_PROMPT = """You are an expert on สปสช (Thailand NHSO) medical billing.
CRITICAL: Always respond in Thai language only. ตอบภาษาไทยเท่านั้น
Use only the provided context. Cite source video/page names."""


def load_engine():
    from llama_index.core import Settings, StorageContext, load_index_from_storage
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.llms.anthropic import Anthropic
    from llama_index.vector_stores.faiss import FaissVectorStore

    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.llm = Anthropic(model="claude-haiku-4-5-20251001", max_tokens=2048)

    vector_store = FaissVectorStore.from_persist_dir(str(INDEX_DIR))
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=str(INDEX_DIR)
    )
    index = load_index_from_storage(storage_context=storage_context)
    return index.as_query_engine(
        similarity_top_k=5,
        system_prompt=SYSTEM_PROMPT,
    )


def main():
    if not INDEX_DIR.exists():
        print("❌ ยังไม่มี index — รัน: python3 build_faiss.py ก่อน")
        sys.exit(1)

    print("🔍 สปสช RAG — พิมพ์คำถาม (exit เพื่อออก)\n")
    engine = load_engine()

    while True:
        try:
            q = input("คำถาม: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q or q.lower() == "exit":
            break

        print("\nกำลังค้นหา...\n")
        response = engine.query(f"[ตอบเป็นภาษาไทยเท่านั้น] {q}")
        print(f"คำตอบ:\n{response}\n")

        if hasattr(response, "source_nodes") and response.source_nodes:
            print("แหล่งที่มา:")
            seen = set()
            for node in response.source_nodes:
                title = node.metadata.get("title", "")
                url = node.metadata.get("url", "")
                key = title or url
                if key and key not in seen:
                    line = f"  - {title[:70]}"
                    if url:
                        line += f"\n    {url}"
                    print(line)
                    seen.add(key)
        print()


if __name__ == "__main__":
    main()
