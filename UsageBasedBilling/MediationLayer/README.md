# Mediation and Metering Layer

This layer is written in Python. It consumes usage events streamed from the Ingestion Layer via Apache Kafka, deduplicates them using Redis (fast-path), and maintains real-time usage counters. 

## Prerequisites
- Python 3.8+
- Apache Kafka Broker (localhost:9092)
- Redis Server (localhost:6379)

## Build & Install

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install confluent-kafka redis pytest
```
*(Or use `pip install -r requirements.txt` if available)*

## Configuration

The processor looks for the following environment variables (defaults are provided):
- `KAFKA_BROKER` (default: localhost:9092)
- `KAFKA_TOPIC` (default: usage-events)
- `REDIS_HOST` (default: localhost)
- `REDIS_PORT` (default: 6379)

## Running the Processor

Ensure Kafka and Redis are running, then execute:
```bash
python processor.py
```

## Testing

To run the unit tests (which mock Kafka and Redis):
```bash
python -m unittest test_processor.py
```
Or use pytest:
```bash
pytest test_processor.py
```
