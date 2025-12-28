flowchart TB

    %% ----------------- INGESTION -----------------
    A1[Raw Documents (PDF, TXT, Agreements)] -->|Placed in Folder| A2[/src/veridian_atlas/data/deals/<deal>/raw/]
    A2 --> B1[Run Ingestion: run_ingestion.py]
    B1 -->|Extract Text & Metadata| B2[sections.json]
    B2 --> B3[/processed/]

    %% ----------------- CHUNKING -----------------
    B3 --> C1[Run Chunker: run_chunker.py]
    C1 -->|Split into clauses/tables/paragraphs| C2[chunks.jsonl]

    %% ----------------- EMBEDDINGS + INDEX -----------------
    C2 --> D1[Generate Embeddings (Sentence-Transformers)]
    D1 --> D2[Vector Embeddings]
    D2 -->|Persist to index| D3[ChromaDB Collections]

    %% ----------------- QUERY FLOW -----------------
    E1[User Question] -->|UI Request| E2[FastAPI Endpoint: /ask/{deal_id}]
    E2 -->|Select deal collection| D3
    D3 -->|Top-K Vector Search| E3[Retrieved Chunks (Context)]
    E3 -->|Context to LLM| E4[Local/External LLM]
    E4 -->|Grounded Answer with Citations| E5[Final Answer]

    %% ----------------- UI LAYER -----------------
    E5 --> F1[React UI (Vite + Tailwind)]
    F1 --> F2[Citation Panel]
    F1 --> F3[Query History Sidebar]

    F2 -. request specific chunk .-> E2
