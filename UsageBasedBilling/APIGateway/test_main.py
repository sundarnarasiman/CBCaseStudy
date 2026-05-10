import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Patch the producer before importing the app
with patch('confluent_kafka.Producer') as MockProducer:
    mock_producer_instance = MagicMock()
    MockProducer.return_value = mock_producer_instance
    from main import app, producer

client = TestClient(app)

def test_ingest_event_success():
    payload = {
        "customerId": "cust_001",
        "event": "api_call",
        "timestamp": "2026-05-10T12:00:00Z"
    }
    
    response = client.post("/events", json=payload)
    
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert "idempotencyKey" in data
    
    # Check that producer.produce was called
    producer.produce.assert_called_once()

def test_ingest_event_invalid_schema():
    payload = {
        # missing customerId
        "event": "api_call"
    }
    
    response = client.post("/events", json=payload)
    assert response.status_code == 422 # Validation error
