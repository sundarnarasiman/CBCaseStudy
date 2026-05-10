import os
import json
import logging
from confluent_kafka import Consumer, KafkaError
import boto3
from clickhouse_driver import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'usage-events')
S3_BUCKET = os.getenv('S3_BUCKET', 'raw-usage-events-bucket')
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')

# Initialize Clients
s3_client = boto3.client('s3', region_name='us-east-1')
ch_client = Client(host=CLICKHOUSE_HOST)

class StorageProcessor:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': 'storage-group',
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([KAFKA_TOPIC])
        
        # Ensure ClickHouse table exists
        ch_client.execute('''
            CREATE TABLE IF NOT EXISTS usage_aggregates (
                customer_id String,
                event_type String,
                usage_date Date,
                total_events UInt64
            ) ENGINE = MergeTree()
            ORDER BY (customer_id, event_type, usage_date)
        ''')

    def save_raw_to_s3(self, event_data):
        """Upload raw event to S3 data lake"""
        try:
            event_id = event_data.get('idempotencyKey', 'unknown')
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=f"raw_events/{event_id}.json",
                Body=json.dumps(event_data)
            )
            logger.info(f"Saved raw event {event_id} to S3")
            return True
        except Exception as e:
            logger.error(f"Failed to save to S3: {e}")
            return False

    def save_aggregate_to_clickhouse(self, event_data):
        """Store basic aggregation in ClickHouse for fast analytics"""
        try:
            customer_id = event_data.get('customerId')
            event_type = event_data.get('event')
            timestamp = event_data.get('timestamp', '2026-01-01')[:10] # Get YYYY-MM-DD
            
            # Simple upsert/insert pattern for aggregated view
            ch_client.execute(
                'INSERT INTO usage_aggregates (customer_id, event_type, usage_date, total_events) VALUES',
                [(customer_id, event_type, timestamp, 1)]
            )
            logger.info(f"Inserted event for {customer_id} into ClickHouse")
            return True
        except Exception as e:
            logger.error(f"Failed to save to ClickHouse: {e}")
            return False

    def process_event(self, event_data):
        if not event_data.get('customerId'):
            return
        
        # 1. Save raw to S3
        self.save_raw_to_s3(event_data)
        
        # 2. Save aggregate to ClickHouse
        self.save_aggregate_to_clickhouse(event_data)

    def run(self):
        logger.info("Starting Storage and Data Lakehouse Processor...")
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(msg.error())
                        break

                event_data = json.loads(msg.value().decode('utf-8'))
                self.process_event(event_data)
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

if __name__ == "__main__":
    processor = StorageProcessor()
    processor.run()
