"""
สปสช Knowledge MCP Server
Exposes the wiki knowledge base as MCP tools for Claude to use
during hospital claim AI conversations.

Tools:
  search_wiki(query)        — hybrid retrieval (keyword + semantic)
  get_wiki_page(title)      — fetch a specific wiki page by filename stem
  list_concepts()           — list all concept page titles
"""
import asyncio
import re
import sys
from pathlib import Path

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

VAULT = Path(__file__).parent.parent / "nhso-vault"
RAG_DIR = Path(__file__).parent
WIKI_DIR = VAULT
INDEX_DIR = RAG_DIR / "faiss_store"
TEXTBOOK_INDEX_DIR = RAG_DIR / "textbook_store"

server = Server("spsach-wiki")

# ── retrievers (lazy-loaded once each) ──────────────────────────────────────

_retriever = None
_textbook_retriever = None


def _load_retriever(index_dir: Path, top_k: int = 8):
    from llama_index.core import Settings, StorageContext, load_index_from_storage
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.llms.ollama import Ollama
    from llama_index.vector_stores.faiss import FaissVectorStore

    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.llm = Ollama(model="gemma4:latest")

    vector_store = FaissVectorStore.from_persist_dir(str(index_dir))
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=str(index_dir)
    )
    index = load_index_from_storage(storage_context=storage_context)
    return index.as_retriever(similarity_top_k=top_k)


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = _load_retriever(INDEX_DIR)
    return _retriever


def _get_textbook_retriever():
    global _textbook_retriever
    if _textbook_retriever is None:
        if not TEXTBOOK_INDEX_DIR.exists():
            return None
        _textbook_retriever = _load_retriever(TEXTBOOK_INDEX_DIR, top_k=6)
    return _textbook_retriever


# ── retrieval helpers ────────────────────────────────────────────────────────

_STOPWORDS = {"FOR", "AND", "OR", "THE", "IS", "IN", "OF", "TO", "A", "AN",
              "BY", "AT", "ON", "AS", "BE", "DO", "GO", "UP", "VS"}


def _keyword_retrieve(query: str, max_files: int = 5) -> list[dict]:
    c_codes = re.findall(r"\b[A-Z]\d{3,}\b", query.upper())
    acronyms = [w for w in re.findall(r"\b[A-Z]{2,}\b", query.upper()) if w not in _STOPWORDS]
    eng_words = re.findall(r"\b[A-Za-z][a-z]{3,}\b", query)
    thai_words = re.findall(r"[\u0e00-\u0e7f]{3,}", query)
    keywords = list(set(c_codes + acronyms + [w.lower() for w in eng_words] + thai_words))

    if not keywords:
        return []

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
        title_hits = sum(1 for kw in keywords if kw.lower() in page.stem.lower())
        score = content_hits + title_hits * 3
        scored.append((score, page))

    scored.sort(key=lambda x: -x[0])
    results = []
    for _, page in scored[:max_files]:
        text = page.read_text(encoding="utf-8")
        results.append({
            "text": text[:2000],
            "meta": {"title": page.stem, "type": page.parent.name, "url": ""},
            "source": "keyword",
        })
    return results


def _semantic_retrieve(query: str, top_k: int = 5) -> list[dict]:
    retriever = _get_retriever()
    retriever._similarity_top_k = top_k
    nodes = retriever.retrieve(query)
    return [
        {"text": n.text, "score": n.score, "meta": n.metadata, "source": "semantic"}
        for n in nodes
    ]


def _hybrid_retrieve(query: str, top_k: int = 5) -> list[dict]:
    keyword_chunks = _keyword_retrieve(query, max_files=3)
    semantic_chunks = _semantic_retrieve(query, top_k=top_k)

    seen: set[str] = set()
    merged: list[dict] = []
    for chunk in keyword_chunks + semantic_chunks:
        title = chunk["meta"].get("title", "")
        if title not in seen:
            seen.add(title)
            merged.append(chunk)
    return merged[:top_k + 3]


def _chunks_to_text(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        title = c["meta"].get("title", "unknown")
        url = c["meta"].get("url", "")
        src_tag = f"[{title}]" + (f" ({url})" if url else "")
        parts.append(f"{src_tag}\n{c['text'][:1500]}")
    return "\n\n---\n\n".join(parts)


# ── MCP tool handlers ────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_wiki",
            description=(
                "ค้นหาข้อมูลจาก สปสช knowledge base "
                "รองรับรหัส C-code (C305, C172 ฯลฯ), ชื่อระบบ (DMIS, DRG, FVS), "
                "และคำถามภาษาไทยเกี่ยวกับการเบิกจ่ายและ claim"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "คำถามหรือ keyword ที่ต้องการค้นหา",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "จำนวน chunks สูงสุดที่จะคืน (default 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_wiki_page",
            description="ดึงหน้า wiki เต็มๆ โดยระบุชื่อไฟล์ (เช่น 'c305-appeal-process')",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "ชื่อไฟล์ wiki (ไม่ต้องมี .md)",
                    }
                },
                "required": ["title"],
            },
        ),
        types.Tool(
            name="list_concepts",
            description="แสดงรายการ concept pages ทั้งหมดใน wiki (ใช้หา topics ที่มี)",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="search_textbooks",
            description=(
                "ค้นหาในตำราแพทย์ CVT (Cardiovascular & Thoracic Surgery textbooks) "
                "ใช้สำหรับคำถามทางคลินิก เช่น PCI, coronary anatomy, stent, CABG, "
                "cardiac surgery techniques, cardiology medications"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "คำถามทางคลินิกหรือ keyword ภาษาอังกฤษ/ไทย",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "จำนวน chunks สูงสุด (default 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "search_wiki":
        query = arguments["query"]
        top_k = int(arguments.get("top_k", 5))
        chunks = _hybrid_retrieve(query, top_k=top_k)
        if not chunks:
            return [types.TextContent(type="text", text="ไม่พบข้อมูลที่เกี่ยวข้องใน wiki")]

        sources = [c["meta"].get("title", "") for c in chunks]
        content = _chunks_to_text(chunks)
        result = f"พบ {len(chunks)} แหล่งข้อมูล: {', '.join(sources)}\n\n{content}"
        return [types.TextContent(type="text", text=result)]

    if name == "get_wiki_page":
        title = arguments["title"]
        for subdir in ["concepts", "entities", "sources", "queries"]:
            page = WIKI_DIR / subdir / f"{title}.md"
            if page.exists():
                return [types.TextContent(type="text", text=page.read_text(encoding="utf-8"))]
        return [types.TextContent(type="text", text=f"ไม่พบหน้า '{title}' ใน wiki")]

    if name == "list_concepts":
        concepts_dir = WIKI_DIR / "concepts"
        if not concepts_dir.exists():
            return [types.TextContent(type="text", text="ไม่มี concepts directory")]
        titles = sorted(p.stem for p in concepts_dir.glob("*.md"))
        return [types.TextContent(type="text", text="\n".join(titles))]

    if name == "search_textbooks":
        retriever = _get_textbook_retriever()
        if retriever is None:
            return [types.TextContent(
                type="text",
                text="Textbook index ยังไม่พร้อม — รัน build_textbook_index.py ก่อน"
            )]
        query = arguments["query"]
        top_k = int(arguments.get("top_k", 5))
        retriever._similarity_top_k = top_k
        nodes = retriever.retrieve(query)
        if not nodes:
            return [types.TextContent(type="text", text="ไม่พบข้อมูลในตำราแพทย์")]
        parts = []
        for n in nodes:
            title = n.metadata.get("title", "unknown")
            page = n.metadata.get("page", "?")
            file = n.metadata.get("file", "")
            parts.append(f"[{title} p.{page}] ({file})\n{n.text[:1500]}")
        result = f"พบ {len(nodes)} sections จากตำราแพทย์:\n\n" + "\n\n---\n\n".join(parts)
        return [types.TextContent(type="text", text=result)]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── entry point ──────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
