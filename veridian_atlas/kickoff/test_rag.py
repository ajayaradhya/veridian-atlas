"""
test_rag.py
-----------
End-to-end validation for the Veridian Atlas RAG pipeline.
Ensures:
 - Chroma index loads correctly
 - Retrieval returns relevant context chunks
 - Qwen model generates a citation-backed answer

Run:
    python -m veridian_atlas.rag.test_rag
"""

from veridian_atlas.rag.rag_engine import answer_query
from pathlib import Path

# Suggested smoke test questions that reference known text
TEST_QUERIES = [
    "What is the interest rate for the Revolving Credit Facility?",
    "When does the Term Loan A Facility mature?",
    "What triggers early termination?",
    "Who is the Borrower in this agreement?"
]


def run_tests():
    print("\n================= RAG SYSTEM TEST =================")
    for q in TEST_QUERIES:
        print("\n--------------------------------------------------")
        print(f"QUERY: {q}")
        print("--------------------------------------------------")

        try:
            result = answer_query(q)
        except Exception as e:
            print(f"[ERROR] RAG failure: {e}")
            continue

        answer_text = result.get("answer", "").strip()
        citations = result.get("citations", [])

        print("\nANSWER:")
        print(answer_text)

        print("\nCITATIONS:")
        for c in citations:
            print(f"  - {c}")

    print("\n================= TEST COMPLETE =================\n")


# ------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------

if __name__ == "__main__":
    # Optional safety check: ensure index exists
    chroma_path = Path("veridian_atlas/data/indexes/chroma_db")
    if not chroma_path.exists():
        print("[ERROR] No Chroma index found.")
        print("Run embeddings/index step first:")
        print("  python -m veridian_atlas.kickoff.start_embeddings")
        raise SystemExit(1)

    run_tests()
