import os
import json
import logging
from confluent_kafka import Consumer, Producer, KafkaError
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_IN_TOPIC = os.getenv('KAFKA_IN_TOPIC', 'ingress-events')
KAFKA_OUT_TOPIC = os.getenv('KAFKA_OUT_TOPIC', 'usage-events')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)

class IdempotencyProcessor:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': 'idempotency-group',
            'auto.offset.reset': 'earliest'
        })
        self.producer = Producer({'bootstrap.servers': KAFKA_BROKER})
        self.consumer.subscribe([KAFKA_IN_TOPIC])

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f'Delivery failed: {err}')
        else:
            logger.debug(f'Delivered to {msg.topic()}')

    def process_event(self, event_data):
        idempotency_key = event_data.get('idempotencyKey')
        
        if not idempotency_key:
            logger.warning("Event missing idempotencyKey. Forwarding anyway.")
            return self.forward_event(event_data)

        # SETNX returns 1 if key was set (new), 0 if key exists (duplicate)
        is_new = r.setnx(f"idempotent:{idempotency_key}", "1")
        if is_new:
            r.expire(f"idempotent:{idempotency_key}", 86400 * 7) # Keep 7 days
            return self.forward_event(event_data)
        else:
            logger.info(f"Duplicate event dropped: {idempotency_key}")
            return False

    def forward_event(self, event_data):
        customer_id = event_data.get('customerId', 'unknown')
        self.producer.produce(
            KAFKA_OUT_TOPIC,
            key=customer_id.encode('utf-8'),
            value=json.dumps(event_data).encode('utf-8'),
            callback=self.delivery_report
        )
        self.producer.poll(0)
        return True

    def run(self):
        logger.info("Starting Idempotency Processor...")
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

                data = json.loads(msg.value().decode('utf-8'))
                self.process_event(data)
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()
            self.producer.flush()

if __name__ == "__main__":
    processor = IdempotencyProcessor()
    processor.run()
