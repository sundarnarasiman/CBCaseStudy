import os
import logging
from fastapi import FastAPI
import asyncio
from confluent_kafka import Consumer, KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Usage Based Billing - External Integrations")

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'invoices-generated')

class ExternalIntegrationWorker:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': 'external-integrations-group',
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([KAFKA_TOPIC])

    def sync_to_crm(self, invoice_data):
        # Mock CRM Sync
        logger.info(f"Syncing invoice to CRM for customer: {invoice_data.get('customer_id')}")

    def run_once(self):
        msg = self.consumer.poll(1.0)
        if msg is None:
            return
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                logger.error(msg.error())
            return

        import json
        data = json.loads(msg.value().decode('utf-8'))
        self.sync_to_crm(data)

worker = ExternalIntegrationWorker()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting background Kafka consumer...")
    asyncio.create_task(consume_loop())

async def consume_loop():
    while True:
        worker.run_once()
        await asyncio.sleep(0.1)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
