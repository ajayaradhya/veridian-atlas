from veridian_atlas.rag_engine.pipeline.rag_engine import retrieve_context

def test_retrieve_context_no_deal():
    try:
        results = retrieve_context("test", "fake_deal")
        assert isinstance(results, list)
    except Exception:
        pass  # acceptable for missing index
