# 🏗 Veridian Atlas – System Architecture (Mermaid)

```mermaid
flowchart TB
    A1[📂 Raw Documents\nPDF, TXT, Agreements] -->|placed in| A2[📁 /src/veridian_atlas/data/deals/<deal>/raw]
    A2 --> B1[[🛠 Run Ingestion\nrun_ingestion.py]]
    B1 -->|Extracts text + structure| B2[(sections.json)]
    B2 -->|Stored to| B3[📁 processed/]

    B3 --> C1[[📐 Chunking\nrun_chunker.py]]
    C1 -->|Clause/Table/Paragraph Split| C2[(chunks.jsonl)]

    C2 --> D1[[🧠 Embeddings\nsentence-transformers]]
    D1 -->|Vectorize text| D2[(Vectors)]
    D2 -->|Persist| D3[🗄️ ChromaDB\nchroma_db/collections]

    E1[❓ Client Question] -->|UI/HTTP POST| E2[⚙️ FastAPI /ask/{deal}]
    E2 -->|Lookup Collection by Deal| D3
    D3 -->|Top-K Semantic Search| E3[(Retrieved Chunks)]
    E3 -->|Context Provided →| E4[[🤖 Local LLM / GPT / HF Model]]
    E4 -->|Grounded Answer| E5((📌 Final Answer + Citations))

    E5 --> F1[🖥️ React UI (Vite/Tailwind)]
    F1 -->|Displays Answer + Sources| F2[🔍 Citation Panel]
    F1 -->|History Stored| F3[🕒 Sidebar / Interaction Log]

    F2 -. click clause .-> E2
```
