# NHSO Vault RAG — Scripts

Local RAG over the 184 concept pages + 43 YouTube source summaries.

## Prereqs

```bash
ollama pull nomic-embed-text  # 274 MB embedding model
ollama pull gemma4:latest     # 9.6 GB LLM
pip install llama-index faiss-cpu llama-index-vector-stores-faiss llama-index-embeddings-ollama llama-index-llms-ollama
```

## Build index (~40 seconds for 229 pages)

```bash
python3 build_faiss.py
```

## Query

```bash
python3 query_faiss.py
```

## Use via MCP (for Claude Code)

Already wired in `.mcp.json` as `nhso-vault`. Restart Claude Code to activate.

Tools exposed:
- `search_wiki(query)` — semantic search
- `get_wiki_page(title)` — fetch specific page
- `list_concepts()` — list all concept pages
