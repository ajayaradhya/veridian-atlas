# veridian_atlas/api/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class SourceRef(BaseModel):
    chunk_id: str
    section: Optional[str]
    clause: Optional[str]
    preview: str
    deal: Optional[str]

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    query: str
    sources: List[SourceRef]
    source_count: int
