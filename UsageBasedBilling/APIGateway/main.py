import os
import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from confluent_kafka import Producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Usage Based Billing - API Gateway")

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'usage-events')

# Configure Kafka Producer
try:
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
except Exception as e:
    logger.error(f"Failed to initialize Kafka producer: {e}")
    producer = None

class UsageEvent(BaseModel):
    customerId: str
    event: str
    timestamp: str
    idempotencyKey: str = None
    metadata: dict = {}

def delivery_report(err, msg):
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

@app.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(event: UsageEvent):
    if not producer:
        raise HTTPException(status_code=500, detail="Kafka producer not configured")
        
    # Autogenerate an idempotency key if not present
    if not event.idempotencyKey:
        import uuid
        event.idempotencyKey = f"auto-{uuid.uuid4()}"

    payload = event.model_dump_json()
    
    try:
        producer.produce(
            KAFKA_TOPIC, 
            key=event.customerId.encode('utf-8'), 
            value=payload.encode('utf-8'), 
            callback=delivery_report
        )
        producer.poll(0) # trigger delivery callbacks
    except Exception as e:
        logger.error(f"Error producing to Kafka: {e}")
        raise HTTPException(status_code=500, detail="Failed to enqueue event")

    return {"status": "accepted", "idempotencyKey": event.idempotencyKey}

@app.on_event("shutdown")
def shutdown_event():
    if producer:
        logger.info("Flushing Kafka Producer...")
        producer.flush()
