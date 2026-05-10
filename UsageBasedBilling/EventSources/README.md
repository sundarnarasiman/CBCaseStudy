# Event Sources

This module provides mock event generators that simulate traffic from external IoT devices, product telemetry, and applications. It pushes these events directly into the `ingress-events` Kafka topic.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Dependencies: `confluent-kafka`)*

## Running
```bash
python generator.py
```

## Testing
```bash
python -m unittest test_generator.py
```
