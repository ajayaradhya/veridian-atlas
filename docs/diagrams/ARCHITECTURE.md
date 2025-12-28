flowchart TB

    %% ----------------- INGESTION -----------------
    A1[Raw Documents\n(PDF, TXT, Agreements)] -->|Placed In Folder| A2[/src/veridian_atlas/data/deals/<deal>/raw/]
    A2 --> B1[Run Ingestion (run_ingestion.py)]
    B1 -->|Extract Text & Metadata| B2[sections.json]
    B2 --> B3[/processed/]

    %% ----------------- CHUNKING -----------------
    B3 --> C1[Run Chunker (run_chunker.py)]
    C1 -->|Clause/Table/Paragraph Split| C2[chunks.jsonl]

    %% ----------------- EMBEDDINGS + INDEX -----------------
    C2 --> D1[Embeddings (Sentence-Transformers)]
    D1 -->|Vectorize| D2[Vector Embeddings]
    D2 -->|Persist| D3[ChromaDB Collection\n/ data/indexes/chroma_db]

    %% ----------------- QUERY FLOW -----------------
    E1[User Question] -->|UI Request| E2[FastAPI `/ask/{deal_id}`]
    E2 -->|Fetch Collection by Deal| D3
    D3 -->|Top-K Semantic Search| E3[Retrieved Chunks]
    E3 -->|Context| E4[LLM (Local / External)]
    E4 -->|Grounded Answer + Citations| E5[Final Response]

    %% ----------------- UI LAYER -----------------
    E5 --> F1[React UI (Vite + Tailwind)]
    F1 -->|Display Answer & Sources| F2[Citation Panel]
    F1 -->|Store Interactions| F3[Query History Sidebar]

    %% RECURSIVE INSPECTION
    F2 -. request chunk .-> E2
