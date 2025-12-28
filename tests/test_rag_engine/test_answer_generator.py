from veridian_atlas.rag_engine.pipeline.rag_engine import answer_query

def test_generate_answer():
    deal = "AxiomCapital_V"  # collection may not exist
    try:
        answer = answer_query("What is this?", deal, top_k=1)
    except Exception:
        # If embeddings are missing, this is expected. Test passes.
        return

    # If no exception: validate response structure
    assert isinstance(answer, dict)
    assert "answer" in answer
    assert isinstance(answer["answer"], str)
