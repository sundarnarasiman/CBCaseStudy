# Idempotency Layer

This Python service consumes from the `ingress-events` Kafka topic, checks Redis to see if the `idempotencyKey` has been processed recently, and if it is new, forwards it to the `usage-events` topic.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Dependencies: `confluent-kafka redis pytest`)*

## Running
```bash
python idempotency_processor.py
```

## Testing
```bash
python -m unittest test_idempotency_processor.py
```
