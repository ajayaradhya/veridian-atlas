"""
run_query.py
------------
Deal-aware query runner for the RAG engine.

CLI Usage:
    python -m veridian_atlas.cli.run_query --question "Your question"
    python -m veridian_atlas.cli.run_query --deal Blackbay_III --question "fees?"

Programmatic:
    from veridian_atlas.cli.run_query import run as run_query
    answer = run_query("What are the fee terms?", deal="Blackbay_III")
"""

import click
import argparse
from veridian_atlas.rag_engine.pipeline.rag_engine import answer_query

# ------------------------------------------------------
# PROGRAMMATIC ENTRYPOINT
# ------------------------------------------------------

def run(question: str, deal: str | None = None) -> dict:
    """
    Executes a RAG query and returns a structured response.
    Returns dict: { "answer": str, "citations": [...], "retrieved": [...] }
    """

    if not question or not isinstance(question, str):
        raise ValueError("Query text required: run(question='text', deal='DealName')")

    result = answer_query(query=question, deal_name=deal)

    return {
        "answer": result.get("answer", "").strip(),
        "citations": result.get("citations", []),
        "retrieved": result.get("retrieved_chunks", []),
    }


# ------------------------------------------------------
# CLI MODE
# ------------------------------------------------------

@click.command()
@click.option("--deal", required=False)
@click.argument("question")
def cli(question, deal):
    """
    Test-friendly CLI wrapper. Calls existing run().
    """
    output = run(question, deal)
    click.echo(output.get("answer", ""))


def get_args():
    parser = argparse.ArgumentParser(description="Run a question against the RAG engine.")
    parser.add_argument("--question", type=str, required=True, help="Query text for the model")
    parser.add_argument("--deal", type=str, help="Optional: route query to a specific deal")
    return parser.parse_args()


def main():
    args = get_args()
    output = run(args.question, args.deal)

    print("\n===================================================")
    print("RAG QUERY RESULT")
    print("===================================================\n")
    print(f"QUESTION : {args.question}")
    if args.deal:
        print(f"DEAL     : {args.deal}")

    print("\nANSWER:")
    print(output["answer"])
    print("\nCITATIONS:")
    print(output["citations"])
    print("\nRETRIEVED CHUNKS:")
    print(output["retrieved"])
    print("\n===================================================\n")


if __name__ == "__main__":
    main()
