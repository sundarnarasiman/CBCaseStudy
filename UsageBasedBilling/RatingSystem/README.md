# Rating and Revenue System

This Python application acts as the final rating and billing logic layer. It listens to a Kafka topic (`billing-triggers`) for end-of-month or on-demand invoice triggers. When triggered, it queries the **ClickHouse** data warehouse for aggregated usage, applies the correct pricing catalog rules, and generates an invoice JSON, which is then securely stored in **S3**.

## Prerequisites
- Python 3.8+
- Apache Kafka Broker
- AWS Credentials configured for `boto3` (for S3 Invoices)
- ClickHouse Server

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Dependencies: `confluent-kafka boto3 clickhouse-driver pytest`)*

## Running the Processor
Ensure `KAFKA_BROKER`, `S3_BUCKET`, and `CLICKHOUSE_HOST` are properly configured in your environment or use the defaults.

```bash
python rating_processor.py
```

## Testing
Run unit tests with:
```bash
python -m unittest test_rating_processor.py
```
