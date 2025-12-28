# veridian_atlas/api/server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from veridian_atlas.api.schemas import QueryRequest, QueryResponse, SearchResponse
from veridian_atlas.rag_engine.pipeline.rag_engine import (
    retrieve_context,
    answer_query,
    get_chroma_collection,
)
from veridian_atlas.rag_engine.services.query_service import QueryService

app = FastAPI(
    title="Veridian Atlas RAG API",
    description="Local multi-deal RAG engine for financial contracts.",
    version="0.6.0",
)

# ---------------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = QueryService()


# ---------------------------------------------------------
# ROOT + HEALTH
# ---------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Veridian Atlas RAG API is active.",
        "routes": [
            "/health",
            "/deals",
            "/deals/{deal_id}",
            "/deals/{deal_id}/docs",
            "/ask/{deal_id}",
            "/search/{deal_id}",
            "/chunk/{deal_id}/{chunk_id}",
        ],
    }


@app.get("/health")
def health_check():
    return service.health()


# Serve the built UI
app.mount("/static", StaticFiles(directory="src/veridian_atlas/static"), name="static")


@app.get("/ui")
def serve_ui():
    return FileResponse("src/veridian_atlas/static/index.html")


# ---------------------------------------------------------
# LIST ALL DEALS
# ---------------------------------------------------------
@app.get("/deals")
def list_deals():
    base = Path("veridian_atlas/data/deals")
    if not base.exists():
        return {"deals": []}
    deals = [d.name for d in base.iterdir() if d.is_dir()]
    return {"deals": deals}


# ---------------------------------------------------------
# DEAL METADATA (status of processed files)
# ---------------------------------------------------------
@app.get("/deals/{deal_id}")
def deal_metadata(deal_id: str):
    base = Path(f"veridian_atlas/data/deals/{deal_id}")
    if not base.exists():
        raise HTTPException(status_code=404, detail="Deal not found")

    processed = base / "processed" / "chunks.jsonl"
    embeddings_dir = Path("veridian_atlas/data/indexes/chroma_db")

    return {
        "deal_id": deal_id,
        "paths": {
            "raw_dir": str(base / "raw"),
            "processed_chunks_file": str(processed),
            "raw_exists": (base / "raw").exists(),
            "chunks_exists": processed.exists(),
            "embeddings_exists": embeddings_dir.exists(),
        },
    }


# ---------------------------------------------------------
# DOCUMENT VIEW (raw + processed)
# ---------------------------------------------------------
@app.get("/deals/{deal_id}/docs")
def deal_documents(deal_id: str):
    base = Path(f"veridian_atlas/data/deals/{deal_id}")
    if not base.exists():
        raise HTTPException(status_code=404, detail="Deal not found")

    return {
        "deal_id": deal_id,
        "documents": {
            "raw": [d.name for d in (base / "raw").glob("*")],
            "processed": [p.name for p in (base / "processed").glob("*")],
        },
    }


# ---------------------------------------------------------
# ASK (LLM + RETRIEVAL)
# ---------------------------------------------------------
@app.post("/ask/{deal_id}", response_model=QueryResponse)
def ask_for_deal(deal_id: str, request: QueryRequest):
    try:
        result = answer_query(request.query, deal_id, request.top_k)
    except Exception:
        raise HTTPException(
            status_code=404, detail="Deal not found or missing embeddings. Run indexing first."
        )

    # format results for Pydantic
    formatted_sources = []
    for src in result.get("sources", []):
        formatted_sources.append(
            {
                "chunk_id": src["chunk_id"],
                "section": src.get("section"),
                "clause": src.get("clause"),
                "preview": (
                    src["content"][:300] + "..." if len(src["content"]) > 300 else src["content"]
                ),
                "deal": deal_id,
            }
        )

    return {
        "deal_id": deal_id,  # REQUIRED FIELD
        "query": result.get("query"),
        "answer": result.get("answer"),
        "citations": result.get("citations", []),
        "source_count": len(formatted_sources),
        "sources": formatted_sources,
    }


# ---------------------------------------------------------
# SEARCH (RETRIEVAL ONLY)
# ---------------------------------------------------------
@app.post("/search/{deal_id}", response_model=SearchResponse)
def search_for_deal(deal_id: str, request: QueryRequest):
    try:
        contexts = retrieve_context(request.query, deal_id, request.top_k)
    except Exception:
        raise HTTPException(status_code=404, detail="Deal not found or index missing")

    return {
        "deal_id": deal_id,
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
        ],
    }


# ---------------------------------------------------------
# CHUNK LOOKUP (UI Side Panel)
# ---------------------------------------------------------
@app.get("/chunk/{deal_id}/{chunk_id}")
def get_chunk(deal_id: str, chunk_id: str):
    try:
        col = get_chroma_collection(deal_id)
        result = col.get(where={"chunk_id": chunk_id})
    except Exception:
        raise HTTPException(status_code=404, detail="Deal not found or embeddings missing")

    if not result or not result.get("documents"):
        raise HTTPException(status_code=404, detail="Chunk not found")

    return result


# ---------------------------------------------------------
# APP FACTORY (USED FOR TESTS)
# ---------------------------------------------------------
def create_app():
    """
    Application factory for tests and modular execution.
    Returns the configured FastAPI app instance.
    """
    return app
