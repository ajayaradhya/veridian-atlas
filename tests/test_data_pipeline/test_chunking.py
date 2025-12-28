from veridian_atlas.data_pipeline.processors.chunker import chunk_text

def test_chunk_text(sample_text):
    chunks = chunk_text(sample_text, chunk_size=10)
    assert isinstance(chunks, list)
    assert len(chunks) > 0
