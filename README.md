# 🗺️ Veridian Atlas
**Structured answers from unstructured worlds.**

Veridian Atlas is a **hands-on Retrieval-Augmented Generation (RAG) system** designed to teach how real enterprise-grade document intelligence works — from PDF ingestion to chunking, embeddings, vector search, and retrieval-bound LLM answers.

If you want to understand *every moving part* of a RAG pipeline instead of treating it like a black box, this is your map.

---

<p align="center">
  <img src="https://img.shields.io/badge/status-active-brightgreen" />
  <img src="https://img.shields.io/badge/focus-RAG%20Architecture-blue" />
  <img src="https://img.shields.io/badge/embeddings-semantic-orange" />
  <img src="https://img.shields.io/badge/vector_store-FAISS%2FChroma-red" />
</p>

---

## 🚀 What is Veridian Atlas?

A lightweight but realistic replica of an enterprise RAG flow:

```
PDF → Ingestion → Chunking → Embedding → Vector DB → Retrieval → Answer
```

It is built to demonstrate:
- How clauses and tables become **queryable units**
- Why embeddings are required for semantic matching
- How metadata prevents data leakage & hallucinations
- How vector DBs **narrow the blast radius of context**
- Why LLMs should answer from **retrieved truth, not memory**

This is not a chatbot.  
This is retrieval with governance.

---

## ✨ Core Features

- 📄 **Document Ingestion**
  - Extract text from PDFs, normalize, version, store

- 🧩 **Semantic Chunking**
  - Clause, section, table-row, amendment-aware segments

- 🧠 **Text & Table Embeddings**
  - Canonical text form → vector space for semantic similarity

- 🗃 **Vector Store**
  - FAISS or Chroma with metadata filtering & ANN index

- 🔍 **Retrieval Layer**
  - Top‑K similarity + business rule scoring

- 🤖 **Bounded LLM Answers**
  - Model only answers from retrieved context, never guesses

---

## 📐 Architecture Overview

```
                     ┌────────────────────────┐
                     │      Ingestion         │
Raw PDFs ───────────►│  text, metadata, OCR   │
                     └───────────┬────────────┘
                                 │
                                 ▼
                      ┌─────────────────────┐
                      │     Chunking        │
                      │ clauses • tables    │
                      └──────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │    Embeddings      │
                       └─────────┬──────────┘
                                 │
                                 ▼
                ┌─────────────────────────────────┐
                │         Vector Database         │
                │  ANN search + metadata filters  │
                └─────────────────────┬───────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │   Retrieval  │
                              └──────┬───────┘
                                     │
                                     ▼
                             🤖 LLM Answer Engine
```

---

## 🏗 Folder Layout

```
veridian-atlas/
├─ data/              # raw and processed docs
├─ ingestion/         # PDF → text → metadata
├─ embeddings/        # canonical text + vectors
├─ vectorstore/       # FAISS/Chroma integration
├─ retrieval/         # semantic search & filtering
├─ app/               # FastAPI endpoint layer
└─ examples/          # demo notebooks
```

---

## 🔎 Real Query Example

**User asks**
```
What's the maturity date for Blackbay III?
```

**Runtime flow**
1. Normalize query → embed
2. Metadata filter: `deal_id=Blackbay_III`
3. Vector similarity search (top‑K)
4. Retrieve clause from Section 2.10
5. LLM answers only from retrieved context

**Result**
> The Revolving Credit Facility under Blackbay III matures on **December 31, 2026**.  
> *(Source: Section 2.10 – Credit Agreement)*

---

## 🛠 Tech Choices

| Layer | Tool |
|-------|------|
| Text Extraction | `pypdf`, `pdfplumber` |
| Embeddings | OpenAI / HuggingFace |
| Vector DB | **Chroma** (default) or FAISS |
| Runtime API | FastAPI |
| Reasoning Model | GPT‑4o or local LLM |

---

## 🧭 Roadmap

- [ ] CLI: `va ingest file.pdf`
- [ ] Hybrid Search (BM25 + vectors)
- [ ] Amendment tracking & temporal overrides
- [ ] Streamlit/Gradio mini UI
- [ ] Offline/local embedding mode

---

## 📄 License
MIT — use, remix, learn.

---

## 💬 Want to extend this?
Open an issue or start a discussion. The goal is clarity, not complexity.

---

**Veridian Atlas**  
*Structured answers from unstructured worlds.*
