# API Gateway

This is the front-facing ingestion layer built with **Python FastAPI** and **Apache Kafka**. It provides a highly performant, type-checked endpoint for clients to submit usage events.

## Prerequisites
- Python 3.8+
- Apache Kafka Broker

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Dependencies: `fastapi uvicorn confluent-kafka pytest httpx`)*

## Running the Server
Ensure `KAFKA_BROKER` and `KAFKA_TOPIC` are configured (or use the defaults).
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Testing
Run unit tests with:
```bash
pytest test_main.py
```

## API Docs
FastAPI automatically generates Swagger documentation. Once the server is running, visit:
`http://localhost:8000/docs`
