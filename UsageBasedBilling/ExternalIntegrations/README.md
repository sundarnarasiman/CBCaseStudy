# External Integrations

This FastAPI application listens to the `invoices-generated` Kafka topic and syncs data to external CRMs or accounting systems (e.g., Salesforce, NetSuite).

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Dependencies: `fastapi uvicorn confluent-kafka pytest httpx`)*

## Running
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

## Testing
```bash
pytest test_main.py
```
