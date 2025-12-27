# veridian_atlas/api/server.py
from fastapi import FastAPI
from veridian_atlas.api.schemas import QueryRequest, QueryResponse, SourceRef
from veridian_atlas.rag.query_service import QueryService

app = FastAPI(
    title="Veridian Atlas RAG API",
    description="Local RAG engine for financial contract Q&A",
    version="0.3.0"
)

service = QueryService()

# ---- System / UI Health Check ----
@app.get("/health")
def health_check():
    return service.health()

# ---- FULL RAG PIPELINE ----
@app.post("/ask", response_model=QueryResponse)
def ask_contract(request: QueryRequest):
    result = service.answer(request.query, request.top_k)

    # Normalize UI output from updated rag_engine results
    return {
        "query": result.get("query"),
        "answer": result.get("answer"),
        "citations": result.get("citations", []),
        "citations_model": result.get("citations_model", []),
        "citations_retrieved": result.get("citations_retrieved", []),
        "source_count": len(result.get("sources", [])),
        "sources": [
            {
                "chunk_id": s["chunk_id"],
                "section": s.get("section"),
                "clause": s.get("clause"),
                "preview": s["content"][:300] + "..." if len(s["content"]) > 300 else s["content"],
                "deal": s.get("deal")  # optional if present in metadata
            }
            for s in result.get("sources", [])
        ],
    }

# ---- RETRIEVAL ONLY (for UI sidebar / highlighting) ----
@app.post("/search")
def search_contract(request: QueryRequest):
    contexts = service.engine.retrieve(request.query, top_k=request.top_k)
    return {
        "query": request.query,
        "count": len(contexts),
        "results": [
            {
                "chunk_id": c["chunk_id"],
                "section": c.get("section"),
                "clause": c.get("clause"),
                "preview": c["content"][:240] + "..." if len(c["content"]) > 240 else c["content"],
            }
            for c in contexts
        ]
    }

# ---- Return a Specific Chunk (for markdown preview / inspector) ----
@app.get("/chunk/{chunk_id}")
def get_chunk(chunk_id: str):
    doc = service.engine.get_chunk(chunk_id)
    if not doc:
        return {"error": "Chunk not found", "chunk_id": chunk_id}

    return {
        "chunk_id": doc["chunk_id"],
        "section": doc.get("section"),
        "clause": doc.get("clause"),
        "content": doc.get("content")
    }
