# Veridian Atlas
### Structured answers from unstructured worlds.

Veridian Atlas is a **local, enterprise-style Retrieval-Augmented Generation (RAG) engine** that transforms raw documents into structured, queryable knowledge. It brings together **document ingestion, semantic chunking, embeddings, vector search, metadata governance, and LLM reasoning**—designed to mimic how real financial/legal RAG systems operate in Fortune 100 environments.

This is not a chatbot project.  
This is an **architecture**.

It is built so you can learn every layer:
- where truth lives,
- how it moves,
- how retrieval finds it,
- and how generation presents it—**without hallucinating**.

## Why This Exists
Organizations do not ask:
> "Generate an answer."

They ask:
> "Retrieve the correct answer, prove it, and show your source."

Veridian Atlas is a hands-on platform to understand:
- How enterprise RAG avoids hallucinations
- How documents become searchable knowledge
- Why embeddings exist (not optional)
- Why chunking is a design decision, not preprocessing
- How vector DBs are the backbone of truth narrowing
- How metadata acts as the first line of governance
- How prompts become **answer boundaries**, not creativity

---

## Core Capabilities
| Capability | Description |
|------------|-------------|
| Ingestion Pipeline | Extracts text from PDFs, normalizes, versions, structures |
| Chunking Layer | Creates clause-level, semantic units (sections, definitions, tables) |
| Table Intelligence | Row-level structure for numeric precision & retrieval |
| Embedding Engine | Canonical text → vectors for semantic search |
| Vector Store | FAISS/Chroma with metadata filtering & ANN |
| Metadata Governance | deal_id, access_group, versioning, effective_date |
| Retrieval Layer | Top-K with business-rule post-filtering |
| Bounded LLM Reasoning | Answers **only** from retrieved chunks |
| Observability | Query, chunk, and response traceability |

---

## System Architecture
```
Raw PDFs ──► Ingestion ──► Chunking ──► Embeddings ──► Vector Store
                                          │
                                          ▼
                                      Retrieval
                                          │
                                          ▼
                                    Bounded LLM
```

---

## Project Structure
```
veridian-atlas/
├─ data/
├─ ingestion/
├─ embeddings/
├─ vectorstore/
├─ retrieval/
├─ app/
└─ examples/
```

---

## Example Query Flow
**User:**  
`What's the maturity date for Blackbay III?`

**Pipeline:**  
1. Normalize & embed query  
2. Filter by metadata: `deal_id=Blackbay_III`  
3. Vector similarity search (top-K)  
4. Select most relevant clause(s)  
5. LLM answers only from retrieved context  

**Answer:**  
> The Revolving Credit Facility under Blackbay III matures on **December 31, 2026**.  
> *(Source: Section 2.10, Credit Agreement)*

---

## Technology Choices
| Layer | Tool |
|-------|------|
| Text Extraction | pypdf / pdfplumber |
| Embeddings | OpenAI or HF models |
| Vector DB | ChromaDB / FAISS |
| Reasoning | GPT-4o / local LLM |
| Runtime | FastAPI |

---

## Roadmap
- [ ] CLI: `va ingest file.pdf`
- [ ] Hybrid retrieval (BM25 + vectors)
- [ ] Amendment semantic diffing
- [ ] UI dashboard

---

## License
MIT — because ideas should travel.
