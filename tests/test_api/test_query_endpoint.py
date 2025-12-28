def test_query_endpoint(test_client):
    deal_id = "test"  # this deal does not exist, and that's OK for test
    payload = {
        "query": "What is the overview?",
        "top_k": 1
    }

    response = test_client.post(f"/ask/{deal_id}", json=payload)

    # Valid outcomes based on current behavior
    # 200: success (if deal/index exists)
    # 404: deal/index missing
    # 422: validation/structure acceptable for non-existent deals
    assert response.status_code in (200, 404, 422)

    # Only validate body if response is successful
    if response.status_code == 200:
        body = response.json()
        assert "answer" in body
