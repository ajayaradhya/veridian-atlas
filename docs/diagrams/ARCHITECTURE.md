```mermaid
flowchart TB
    %% =========================================================
    %% STYLE PRESETS (GitHub / VS Code Compatible)
    %% =========================================================
    classDef stage fill:#1e1e1e,stroke:#555,stroke-width:1px,color:#f0f0f0,rx:6px,ry:6px;
    classDef io fill:#0f1116,stroke:#666,stroke-width:1px,color:#d4d4d4,rx:6px,ry:6px;
    classDef compute fill:#1a2333,stroke:#4a90e2,stroke-width:1px,color:#e6e6e6,rx:6px,ry:6px;
    classDef storage fill:#1a2b1e,stroke:#4b8b3b,stroke-width:1px,color:#e7ffe5,rx:6px,ry:6px;
    classDef user fill:#222222,stroke:#888,stroke-width:1px,color:#f5f5f5,rx:6px,ry:6px;

    %% =========================================================
    %% 1) INGESTION
    %% =========================================================
    subgraph INGESTION_FLOW [ Ingestion Pipeline ]
        A1["Raw Documents (PDF, TXT, Agreements)"]:::io
        A2["/src/veridian_atlas/data/deals/<deal>/raw/"]:::storage
        B1["run_ingestion.py"]:::compute
        B2["sections.json (normalized text output)"]:::io
        B3["/processed/"]:::storage

        A1 -->|place files| A2
        A2 --> B1
        B1 -->|extract content & structure| B2
        B2 --> B3
    end

    %% =========================================================
    %% 2) CHUNKING STAGE
    %% =========================================================
    subgraph CHUNKING_PIPELINE [ Chunking ]
        C1["run_chunker.py"]:::compute
        C2["chunks.jsonl (semantic units)"]:::io
        B3 --> C1
        C1 -->|split clauses / tables / sections| C2
    end

    %% =========================================================
    %% 3) EMBEDDINGS + VECTOR INDEX
    %% =========================================================
    subgraph EMBEDDINGS_AND_INDEX [ Embeddings + Indexing ]
        D1["Sentence-Transformers (local embeddings)"]:::compute
        D2["Vector embeddings"]:::io
        D3["ChromaDB Collections"]:::storage

        C2 --> D1
        D1 --> D2
        D2 -->|persist| D3
    end

    %% =========================================================
    %% 4) QUERY RESOLUTION FLOW
    %% =========================================================
    subgraph QUERY_PIPELINE [ Query Routing ]
        E1["User Question"]:::user
        E2["FastAPI /ask/{deal_id}"]:::compute
        E3["Top-K Retrieved Chunks"]:::io
        E4["Local or External LLM (bounded answer)"]:::compute
        E5["Final Answer + Citations"]:::user

        E1 --> E2
        E2 -->|select matching deal index| D3
        D3 -->|vector similarity search| E3
        E3 -->|context provided| E4
        E4 -->|answer grounded in evidence| E5
    end

    %% =========================================================
    %% 5) FRONTEND UI LOOP
    %% =========================================================
    subgraph USER_INTERFACE [ React Frontend ]
        F1["React (Vite + Tailwind)"]:::user
        F2["Citation Panel"]:::user
        F3["Query History Sidebar"]:::user

        E5 --> F1
        F1 --> F2
        F1 --> F3
        F2 -. request a chunk .-> E2
    end
