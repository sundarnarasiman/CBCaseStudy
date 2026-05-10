import os
import json
import logging
from confluent_kafka import Consumer, KafkaError
import boto3
from clickhouse_driver import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'billing-triggers')
S3_BUCKET = os.getenv('S3_BUCKET', 'invoices-bucket')
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')

# Mock Pricing Catalog
PRICING_CATALOG = {
    'api_call': 0.01,  # 1 cent per API call
    'storage_gb': 0.05 # 5 cents per GB
}

s3_client = boto3.client('s3', region_name='us-east-1')
ch_client = Client(host=CLICKHOUSE_HOST)

class RatingProcessor:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': 'rating-group',
            'auto.offset.reset': 'latest'
        })
        self.consumer.subscribe([KAFKA_TOPIC])

    def fetch_usage(self, customer_id, start_date, end_date):
        """Fetch aggregated usage from ClickHouse"""
        query = '''
            SELECT event_type, sum(total_events) 
            FROM usage_aggregates 
            WHERE customer_id = %(customer_id)s 
              AND usage_date >= %(start_date)s 
              AND usage_date <= %(end_date)s
            GROUP BY event_type
        '''
        try:
            results = ch_client.execute(query, {
                'customer_id': customer_id,
                'start_date': start_date,
                'end_date': end_date
            })
            return results
        except Exception as e:
            logger.error(f"ClickHouse Error: {e}")
            return []

    def calculate_charges(self, usage_data):
        """Apply pricing rules to usage data"""
        line_items = []
        total_amount = 0.0

        for row in usage_data:
            event_type = row[0]
            volume = row[1]
            rate = PRICING_CATALOG.get(event_type, 0.0)
            amount = volume * rate
            total_amount += amount
            
            line_items.append({
                'event_type': event_type,
                'volume': volume,
                'rate': rate,
                'amount': amount
            })

        return line_items, total_amount

    def generate_and_save_invoice(self, customer_id, line_items, total_amount, billing_period):
        """Generate Invoice JSON and save to S3"""
        invoice = {
            'customer_id': customer_id,
            'billing_period': billing_period,
            'line_items': line_items,
            'total_amount': total_amount,
            'status': 'generated'
        }
        
        invoice_key = f"invoices/{customer_id}_{billing_period}.json"
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=invoice_key,
                Body=json.dumps(invoice)
            )
            logger.info(f"Invoice saved to S3: {invoice_key} (Total: ${total_amount})")
            return invoice
        except Exception as e:
            logger.error(f"S3 Error: {e}")
            return None

    def process_trigger(self, trigger_data):
        customer_id = trigger_data.get('customerId')
        start_date = trigger_data.get('startDate')
        end_date = trigger_data.get('endDate')
        billing_period = f"{start_date}_to_{end_date}"

        if not customer_id:
            logger.warning("Trigger missing customerId")
            return

        logger.info(f"Generating invoice for {customer_id} ({billing_period})")
        
        usage_data = self.fetch_usage(customer_id, start_date, end_date)
        line_items, total_amount = self.calculate_charges(usage_data)
        self.generate_and_save_invoice(customer_id, line_items, total_amount, billing_period)

    def run(self):
        logger.info("Starting Rating and Revenue Processor...")
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

                trigger_data = json.loads(msg.value().decode('utf-8'))
                self.process_trigger(trigger_data)
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

if __name__ == "__main__":
    processor = RatingProcessor()
    processor.run()
