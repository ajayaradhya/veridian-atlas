# veridian_atlas/api/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class SourceRef(BaseModel):
    chunk_id: str
    section: Optional[str]
    clause: Optional[str]
    preview: str
    deal: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[str] = []               # model returned citations
    citations_model: List[str] = []
    citations_retrieved: List[str] = []     # retrieved context references
    sources: List[SourceRef]
    source_count: int
