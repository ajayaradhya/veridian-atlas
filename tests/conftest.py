
import pytest
from veridian_atlas.api.server import create_app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def test_client():
    app = create_app()
    return TestClient(app)

@pytest.fixture
def sample_text():
    return "This is sample content for testing."
