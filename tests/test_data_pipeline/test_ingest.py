from veridian_atlas.data_pipeline.loaders.text_loader import load_text_file

def test_ingest_file(tmp_path):
    p = tmp_path / "doc.txt"
    p.write_text("Hello World")
    content = load_text_file(str(p))
    assert content == "Hello World"
