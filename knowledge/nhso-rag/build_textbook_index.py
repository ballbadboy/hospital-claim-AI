"""
CVT Textbook Indexer — สร้าง FAISS index จาก PDF textbooks ใน /Documents/CVT/
Index เฉพาะหน้าที่เกี่ยวกับ Cath Lab / Coronary / PCI / Cardiac Surgery
เพื่อให้ MCP server ค้นหาได้
"""
import json
import sys
from pathlib import Path

import faiss
import fitz  # pymupdf
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.faiss import FaissVectorStore

CVT_DIR = Path("/Users/ballbadboy/Documents/CVT")
OUT_DIR = Path(__file__).parent / "textbook_store"
OUT_DIR.mkdir(exist_ok=True)

# ── Keywords ที่ใช้กรองหน้า ──────────────────────────────────────────────────
CATH_KEYWORDS = {
    # Procedures
    "coronary", "catheterization", "angiography", "angioplasty",
    "percutaneous", "pci", "ptca", "stent", "balloon",
    # Anatomy / Disease
    "myocardial infarction", "ischemi", "angina", "occlusion",
    "stenosis", "left main", "lad ", "lcx", "rca ",
    # Devices
    "drug eluting", "bare metal", "iabp", "impella", "ecmo",
    # ICD / DRG related
    "icd-10", "drg", "diagnosis related", "coding",
    # Thai hospital context
    "cath lab", "cardiac", "valve", "cabg", "bypass",
}

# PDFs ที่จะ index (เรียงตาม priority สำหรับ Cath Lab)
TARGET_PDFS = [
    "Manual of Cardiovascular Medicine 4th.pdf",       # ~28MB, practical
    "Johns Hopkins Manual of Cardiot - Yuh, David.pdf", # ~44MB
    "Cardiac Surgery in the Adult, 4th Edition.pdf",   # ~50MB
    "Cardiothoracic Surgery Review.pdf",               # ~120MB, selective
    "32.Cardiov.Therap.A.Compa.to.Braun.Hea.Dise.4e.pdf",  # ~150MB, selective
    # Skip 500MB+ ones unless keyword density is high
]


def page_is_relevant(text: str) -> bool:
    t = text.lower()
    return sum(1 for kw in CATH_KEYWORDS if kw in t) >= 2


def extract_relevant_pages(pdf_path: Path, max_pages: int = 800) -> list[TextNode]:
    """Extract pages relevant to Cath Lab, chunk by page."""
    nodes = []
    doc_name = pdf_path.stem[:60]
    print(f"  Opening {pdf_path.name} ({pdf_path.stat().st_size // 1_000_000}MB)...")

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"  ✗ Cannot open: {e}")
        return []

    total = len(doc)
    kept = 0
    checked = min(total, max_pages)

    for i in range(checked):
        page = doc[i]
        text = page.get_text()
        if len(text.strip()) < 100:  # skip blank/image pages
            continue
        if page_is_relevant(text):
            # Group 3 pages into one node for better context
            if i + 2 < total:
                text += "\n" + doc[i + 1].get_text() + "\n" + doc[i + 2].get_text()
            node = TextNode(
                text=text[:3000],
                metadata={
                    "title": doc_name,
                    "page": i + 1,
                    "total_pages": total,
                    "source": "textbook",
                    "file": pdf_path.name,
                },
            )
            nodes.append(node)
            kept += 1

    doc.close()
    print(f"  ✓ {kept} relevant pages / {checked} checked (total {total})")
    return nodes


def build_index(nodes: list[TextNode]) -> None:
    print(f"\nBuilding FAISS index from {len(nodes)} nodes...")
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.llm = Ollama(model="gemma4:latest")

    faiss_index = faiss.IndexFlatL2(768)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        show_progress=True,
    )
    index.storage_context.persist(persist_dir=str(OUT_DIR))
    print(f"\n✓ Textbook index saved → {OUT_DIR}")


def main():
    all_nodes: list[TextNode] = []

    for pdf_name in TARGET_PDFS:
        pdf_path = CVT_DIR / pdf_name
        if not pdf_path.exists():
            print(f"  ⚠ Not found: {pdf_name}")
            continue
        nodes = extract_relevant_pages(pdf_path)
        all_nodes.extend(nodes)

    if not all_nodes:
        print("❌ ไม่พบหน้าที่เกี่ยวข้อง")
        sys.exit(1)

    build_index(all_nodes)
    print(f"\nTotal nodes indexed: {len(all_nodes)}")


if __name__ == "__main__":
    main()
