# Adding New Deals to Veridian Atlas

## Extend the System with New Deals

This guide explains how to add new deal documents, run processing, build indexes, and query them through the UI.

---

## 1️⃣ Place Raw Documents
Create a new folder under:

```
src/veridian_atlas/data/deals/
└── YourNewDealName/
    └── raw/
        ├── Agreement_1.txt
        ├── Fee_Schedule.txt
        └── Clauses_Appendix.txt
```

Requirements:
- Folder name = Deal ID
- Only `.txt` supported by default (PDF requires loader extension)
- Content must be text-based (not scanned images unless OCR added)

---

## 2️⃣ Run the Processing Pipeline
From project root:

```bash
# Activate virtual environment
.venv\Scripts\activate     # Windows
source .venv/bin/activate    # Mac/Linux

# Build ingestion → chunks → embeddings → index
python -m veridian_atlas.cli.run_project --deal YourNewDealName --reset
```

This creates:

```
processed/sections.json
processed/chunks.jsonl
```

And updates Chroma index:

```
src/veridian_atlas/data/indexes/chroma_db/
```

---

## 3️⃣ Start Backend & Frontend

### Backend
```bash
uvicorn veridian_atlas.api.server:app --reload --port 8000
```

### Frontend
```bash
cd src/frontend
npm run dev
```

---

## 4️⃣ Query in the UI
Open the dashboard:

```
http://localhost:5173/
```

Steps:
1. Select your new deal
2. Ask a question
3. Review citations & chunks via side panel

Example query:
```
What are the payment obligations?
```

---

## 5️⃣ Troubleshooting Guide

| Issue | Solution |
|-------|-----------|
| Deal not in dropdown | Restart frontend & backend |
| Missing chunks.jsonl | Re-run with `--reset` |
| Old index behavior | Delete `chroma_db` folder, rebuild |
| PDF not processed | Convert PDF → .txt or update loader |

---

## 🔧 CLI Reference
```bash
python -m veridian_atlas.cli.run_project --deal YourDeal --reset
python -m veridian_atlas.cli.run_query --deal YourDeal --question "fees?"
npm run dev
```
