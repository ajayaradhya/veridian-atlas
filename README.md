# Veridian Atlas
**Enterprise RAG for Deal Documents, Agreements & Clause Intelligence**

Veridian Atlas is a full-stack **Retrieval-Augmented Generation (RAG) system** that turns deal documents, credit agreements, fee schedules, and clause libraries into a structured, queryable intelligence layer.

It performs ingestion → chunking → embeddings → vector indexing → evidence retrieval → grounded answers with citations.

This system is designed for environments where correctness and traceability matter more than creativity.

> This is not a chatbot.  
> This is retrieval with governance.

## Why Veridian Atlas
- Retrieval never mixes or leaks across deals
- Answers grounded in retrieved clauses (no hallucination)
- Transparent pipeline, each step inspectable
- Fully local, no external API dependency required

---

## 📸 UI Preview

Veridian Atlas includes a lightweight client dashboard for deal selection, asking questions, inspecting retrieved clauses, and validating citations.

### 🔹 Home Screen / Landing
> Deal selection, onboarding, and first query entry
![Home Screen](docs/screenshots/ui_home.png)

### 🔹 Ask a Question
> Query → retrieve → answer flow (LLM is constrained to retrieved context)
![Query Flow](docs/screenshots/ui_query.png)

### 🔹 Retrieved Chunks & Citations
> Inspection panel showing specific source clauses sent to the LLM
![Citation Panel](docs/screenshots/ui_chunk_panel.png)

### 🔹 Deal Sidebar / History
> Quick access to past queries, sorted by deal & timestamp
![Sidebar](docs/screenshots/ui_sidebar.png)

---

# ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| Runtime | Python 3.11 |
| Vector Store | ChromaDB |
| Embeddings | Sentence-Transformers |
| API Backend | FastAPI |
| UI | React + Vite + Tailwind |
| LLM | Local or external optional |

---

# 📁 Project Structure

```
veridian-atlas/
├─ src/
│  ├─ veridian_atlas/
│  │  ├─ api/
│  │  ├─ cli/
│  │  ├─ core/
│  │  ├─ data/
│  │  ├─ data_pipeline/
│  │  ├─ rag_engine/
│  │  └─ utils/
│  └─ frontend/
└─ requirements.txt
```

---

# 🚀 Backend Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn veridian_atlas.api.server:app --reload --port 8000
```

API: `http://127.0.0.1:8000`

---

# 🖥️ Frontend Setup

```bash
cd src/frontend
npm install
```

Create `.env`:
```
VITE_API_URL=http://127.0.0.1:8000
```

Run:
```bash
npm run dev
```

---

# 🎯 CLI Commands

```bash
python -m veridian_atlas.cli.run_project --reset
python -m veridian_atlas.cli.run_project --deal Blackbay_III
python -m veridian_atlas.cli.run_query --deal SilverRock_II --question "fees?"
```

---

# 🌐 Key Endpoints

| Method | Endpoint |
|--------|-----------|
| GET | /deals |
| POST | /ask/{deal_id} |
| POST | /search/{deal_id} |
| GET | /chunk/{deal_id}/{chunk_id} |

---

# 📄 License
MIT

---
