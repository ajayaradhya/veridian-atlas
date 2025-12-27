# veridian_atlas/api/server.py
from fastapi import FastAPI
from veridian_atlas.api.schemas import QueryRequest, QueryResponse, SourceRef
from veridian_atlas.rag.query_service import QueryService

app = FastAPI(
    title="Veridian Atlas RAG API",
    description="Local RAG engine for financial contract Q&A",
    version="0.2.0"
)

service = QueryService()

# ---- UI / System Check ----
@app.get("/health")
def health_check():
    return service.health()

# ---- Full RAG: retrieve + answer ----
@app.post("/ask", response_model=QueryResponse)
def ask_contract(request: QueryRequest):
    result = service.answer(request.query, request.top_k)
    return result

# ---- Retrieval Only (for UI sidebars, previews, highlight) ----
@app.post("/search")
def search_contract(request: QueryRequest):
    contexts = service.engine.retrieve(request.query, top_k=request.top_k)
    return {
        "query": request.query,
        "results": [
            {
                "chunk_id": c["chunk_id"],
                "section": c.get("section_id"),
                "clause": c.get("clause_id"),
                "preview": c.get("text")[:220] + "..." if len(c.get("text","")) > 220 else c.get("text",""),
            } for c in contexts
        ]
    }

# ---- OPTIONAL: For UI Markdown Preview ----
@app.get("/chunk/{chunk_id}")
def get_chunk(chunk_id: str):
    doc = service.engine.get_chunk(chunk_id)
    if not doc:
        return {"error": "Chunk not found", "chunk_id": chunk_id}
    return doc
