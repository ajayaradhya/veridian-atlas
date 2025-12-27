# veridian_atlas/api/server.py
from fastapi import FastAPI
from veridian_atlas.api.schemas import QueryRequest, QueryResponse, SourceRef
from veridian_atlas.rag.query_service import QueryService

app = FastAPI(
    title="Veridian Atlas RAG API",
    description="Local RAG engine for financial contract Q&A",
    version="0.3.2"
)

service = QueryService()


# ---------------------------------------------------------
# ROOT ROUTE (prevents hanging on "/")
# ---------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Veridian Atlas RAG API is running.",
        "endpoints": ["/health", "/ask", "/search", "/docs"]
    }


# ---------------------------------------------------------
# SYSTEM HEALTH
# ---------------------------------------------------------
@app.get("/health")
def health_check():
    return service.health()


# ---------------------------------------------------------
# FULL RAG ANSWER (retrieve + LLM)
# ---------------------------------------------------------
@app.post("/ask", response_model=QueryResponse)
def ask_contract(request: QueryRequest):
    return service.answer(request.query, request.top_k)


# ---------------------------------------------------------
# RETRIEVAL ONLY (for UI previews, sidebars)
# ---------------------------------------------------------
@app.post("/search")
def search_contract(request: QueryRequest):
    from veridian_atlas.rag.rag_engine import retrieve_context
    contexts = retrieve_context(request.query, top_k=request.top_k)

    return {
        "query": request.query,
        "count": len(contexts),
        "results": [
            {
                "chunk_id": c["chunk_id"],
                "section": c.get("section"),
                "clause": c.get("clause"),
                "preview": c["content"][:240] + "..." if len(c["content"]) > 240 else c["content"]
            }
            for c in contexts
        ]
    }


# ---------------------------------------------------------
# CHUNK LOOKUP (safe version)
# ---------------------------------------------------------
@app.get("/chunk/{chunk_id}")
def get_chunk(chunk_id: str):
    from veridian_atlas.rag.rag_engine import get_chroma_collection
    collection = get_chroma_collection()
    result = collection.get(where={"chunk_id": chunk_id})

    if not result:
        return {"error": "Chunk not found", "chunk_id": chunk_id}

    return result
