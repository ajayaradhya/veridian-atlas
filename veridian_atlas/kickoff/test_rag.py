"""
test_rag.py
-----------
Deal-aware RAG validation. Each deal gets questions that match its own documents.
Run:
    python -m veridian_atlas.kickoff.test_rag
"""

from veridian_atlas.rag.rag_engine import answer_query

# ------------------------------------------------------
# TARGETED QUESTIONS PER DEAL (based on your .txt files)
# ------------------------------------------------------

TEST_MATRIX = {
    "Blackbay_III": [
        "What does clause 2.1 in the Payment Terms and Fee Schedule describe?",
        "Retrieve onboarding or setup fee provisions from the Payment Terms document.",
        "What does the agreement specify about late payment obligations?",
        "Fetch clause 2.2 from the Master Service Agreement.",
        "What documentation is required before first draw under Conditions Precedent?"
    ],

    "SilverRock_II": [
        "What collateral is pledged under the Security Package Schedule?",
        "What triggers disbursement control under the Security Package Schedule?",
        "What is defined under clause 2.3 in the Definitions and Glossary?",
        "What happens if the DSCR covenant is breached?",
        "List the collateral components referenced in Schedule section 1."
    ],

    "AxiomCapital_V": [
        "What documentation is required before the first draw under Conditions Precedent?",
        "What do the Legal Opinions clauses require?",
        "What is the maturity date of the Revolving Credit Facility?",
        "What rights are granted under clause 3.4 of the Lease Commitment Agreement?",
        "What is the collateral enforcement process described in section 2?"
    ],
}

# ------------------------------------------------------
# TEST RUNNER
# ------------------------------------------------------

def run_tests():
    print("\n================= RAG SYSTEM TEST =================\n")

    for deal, questions in TEST_MATRIX.items():
        print(f"\n************** DEAL: {deal} **************")

        for q in questions:
            print("\n--------------------------------------------------")
            print(f"QUERY: {q}")
            print("--------------------------------------------------")

            try:
                result = answer_query(query=q, deal_name=deal)
            except Exception as e:
                print(f"[ERROR] Failed to process → {e}")
                continue

            answer = result.get("answer", "").strip()
            citations = result.get("citations", [])
            retrieved = result.get("retrieved_chunks", [])

            print(f"\nANSWER: {answer}")
            print(f"CITATIONS: {citations}")
            print(f"RETRIEVED: {retrieved}")

    print("\n================= TEST COMPLETE =================\n")


# ------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------

if __name__ == "__main__":
    run_tests()
