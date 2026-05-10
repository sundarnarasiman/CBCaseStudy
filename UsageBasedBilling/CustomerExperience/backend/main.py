import os
import json
import logging
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from confluent_kafka import Consumer, KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Usage Based Billing - Customer Experience API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'usage-events')

# In-memory store for demo purposes (usually this would query ClickHouse)
USAGE_CACHE = {}

class UsageConsumer:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': 'customer-exp-group',
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([KAFKA_TOPIC])

    def run_once(self):
        msg = self.consumer.poll(1.0)
        if msg is None:
            return
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                logger.error(msg.error())
            return

        data = json.loads(msg.value().decode('utf-8'))
        cust_id = data.get('customerId')
        event_type = data.get('event')
        
        if cust_id not in USAGE_CACHE:
            USAGE_CACHE[cust_id] = {}
        if event_type not in USAGE_CACHE[cust_id]:
            USAGE_CACHE[cust_id][event_type] = 0
            
        USAGE_CACHE[cust_id][event_type] += 1

worker = UsageConsumer()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting background Kafka consumer...")
    asyncio.create_task(consume_loop())

async def consume_loop():
    while True:
        worker.run_once()
        await asyncio.sleep(0.1)

@app.get("/api/usage/{customer_id}")
def get_customer_usage(customer_id: str):
    data = USAGE_CACHE.get(customer_id)
    if not data:
        return {"customer_id": customer_id, "usage": {}}
    return {"customer_id": customer_id, "usage": data}
