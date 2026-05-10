import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

with patch('confluent_kafka.Consumer'):
    from main import app, USAGE_CACHE

client = TestClient(app)

def test_get_customer_usage_empty():
    response = client.get("/api/usage/unknown_cust")
    assert response.status_code == 200
    assert response.json() == {"customer_id": "unknown_cust", "usage": {}}

def test_get_customer_usage_exists():
    USAGE_CACHE['cust_1'] = {'api_call': 5}
    response = client.get("/api/usage/cust_1")
    assert response.status_code == 200
    assert response.json() == {"customer_id": "cust_1", "usage": {'api_call': 5}}
