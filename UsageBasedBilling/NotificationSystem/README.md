# Notification System

This Python application acts as the notification hub. It listens to a Kafka topic (`notifications`) for alert events (e.g., usage threshold reached, invoice generated) and sends emails via SMTP.

## Prerequisites
- Python 3.8+
- Apache Kafka Broker
- SMTP Server (e.g., MailHog for local development on port 1025)

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Dependencies: `confluent-kafka pytest`)*

## Running the Processor
Ensure `KAFKA_BROKER`, `KAFKA_TOPIC`, `SMTP_HOST`, and `SMTP_PORT` are configured in your environment.

```bash
python notifier.py
```

## Testing
Run unit tests with:
```bash
python -m unittest test_notifier.py
```
