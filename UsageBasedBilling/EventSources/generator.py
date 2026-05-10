import os
import time
import json
import uuid
import random
from confluent_kafka import Producer

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'ingress-events')

EVENTS = ['api_call', 'storage_gb', 'compute_hour']
CUSTOMERS = ['cust_001', 'cust_002', 'cust_003']

def generate_event():
    return {
        "customerId": random.choice(CUSTOMERS),
        "event": random.choice(EVENTS),
        "timestamp": "2026-05-10T12:00:00Z",
        "idempotencyKey": str(uuid.uuid4())
    }

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def main():
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    print("Starting mock event generator...")
    try:
        while True:
            event = generate_event()
            producer.produce(
                KAFKA_TOPIC,
                key=event['customerId'].encode('utf-8'),
                value=json.dumps(event).encode('utf-8'),
                callback=delivery_report
            )
            producer.poll(0)
            time.sleep(1) # Emit 1 event per second
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush()

if __name__ == "__main__":
    main()
