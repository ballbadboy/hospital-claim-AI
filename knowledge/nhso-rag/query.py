"""
สปสช RAG — Query Interface
"""
import sys
from pathlib import Path

VAULT = Path(__file__).parent.parent / "nhso-vault"
RAG_DIR = Path(__file__).parent
INDEX_DIR = RAG_DIR / "index_store"

SYSTEM_PROMPT = """You are an expert on สปสช (Thailand National Health Security Office) medical billing and reimbursement.
IMPORTANT: Always respond in Thai language only. Never respond in Chinese or English.
Answer only based on the provided context. If unsure, say so in Thai.
Always cite the source video name."""


def load_engine():
    from llama_index.core import Settings, StorageContext, load_index_from_storage
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.llms.ollama import Ollama

    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.llm = Ollama(model="gemma4:latest", request_timeout=300.0)

    storage_context = StorageContext.from_defaults(persist_dir=str(INDEX_DIR))
    index = load_index_from_storage(storage_context)
    return index.as_query_engine(
        similarity_top_k=5,
        system_prompt=SYSTEM_PROMPT,
    )


def main():
    if not INDEX_DIR.exists():
        print("❌ ยังไม่มี index — รัน: python3 build_index.py ก่อน")
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
        # Prepend Thai instruction to force Thai response from qwen
        thai_q = f"[ตอบเป็นภาษาไทยเท่านั้น] {q}"
        response = engine.query(thai_q)
        print(f"คำตอบ:\n{response}\n")

        if hasattr(response, "source_nodes") and response.source_nodes:
            print("แหล่งที่มา:")
            seen = set()
            for node in response.source_nodes:
                vid = node.metadata.get("video_id", "")
                title = node.metadata.get("title", vid)
                url = node.metadata.get("url", "")
                if vid not in seen:
                    print(f"  - {title[:70]}")
                    print(f"    {url}")
                    seen.add(vid)
        print()


if __name__ == "__main__":
    main()
