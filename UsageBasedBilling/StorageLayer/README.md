# Storage and Data Lakehouse Layer

This Python application acts as the data sink for the billing architecture. It listens to the Kafka topic (`usage-events`) and performs two primary storage tasks:
1. **Raw Event Storage (Data Lake):** Uploads every single raw JSON event to AWS S3 for long-term auditing and replay capabilities.
2. **Aggregated Storage (Data Warehouse):** Stores basic aggregated views in ClickHouse for high-speed querying by the Rating engine and Customer dashboards.

## Prerequisites
- Python 3.8+
- Apache Kafka Broker
- AWS Credentials configured for `boto3` (for S3)
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
python storage_processor.py
```

## Testing
Run unit tests with:
```bash
python -m unittest test_storage_processor.py
```
