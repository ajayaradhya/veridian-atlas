# veridian_atlas/api/schemas.py
from pydantic import BaseModel
from typing import List, Optional


# ---------------------------------------------------------
# Returned per chunk (side panel or source preview in UI)
# ---------------------------------------------------------
class SourceRef(BaseModel):
    chunk_id: str
    section: Optional[str]
    clause: Optional[str]
    preview: str
    deal: str  # always include for cross-deal UI context


# ---------------------------------------------------------
# REQUEST BODY
# ---------------------------------------------------------
class QueryRequest(BaseModel):
    deal_id: str  # deal to target
    query: str
    top_k: int = 3  # default retrieval depth


# ---------------------------------------------------------
# RESPONSE: FULL RAG
# ---------------------------------------------------------
class QueryResponse(BaseModel):
    deal_id: str  # REQUIRED (fix for validation)
    query: str
    answer: str
    citations: List[str] = []  # LLM citation ids
    source_count: int
    sources: List[SourceRef]  # source chunk preview list


# ---------------------------------------------------------
# RESPONSE: RETRIEVAL-ONLY (for /search/{deal_id})
# ---------------------------------------------------------
class SearchResult(BaseModel):
    chunk_id: str
    section: Optional[str]
    clause: Optional[str]
    preview: str


class SearchResponse(BaseModel):
    deal_id: str
    query: str
    count: int
    results: List[SearchResult]


# ---------------------------------------------------------
# DEAL & DOCUMENT METADATA (for sidebars / dropdowns)
# ---------------------------------------------------------
class DealInfo(BaseModel):
    deal_id: str
    has_embeddings: bool
    raw_documents: List[str]
    processed_documents: List[str]


class DealList(BaseModel):
    deals: List[str]
