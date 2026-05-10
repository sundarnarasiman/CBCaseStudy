import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

with patch('confluent_kafka.Consumer'):
    from main import app, worker

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch.object(worker, 'sync_to_crm')
def test_sync_to_crm(mock_sync):
    invoice = {"customer_id": "cust_1"}
    worker.sync_to_crm(invoice)
    mock_sync.assert_called_once_with(invoice)
