import os
import json
import logging
from confluent_kafka import Consumer, KafkaError
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'usage-events')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Initialize Redis for fast deduplication and counters
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

class MediationProcessor:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': 'mediation-group',
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([KAFKA_TOPIC])

    def deduplicate(self, idempotency_key):
        """
        Check if the event was already processed within the last 24 hours.
        Returns True if duplicate, False if new.
        """
        if not idempotency_key:
            return False
            
        # SETNX returns 1 if key was set (new), 0 if key already exists (duplicate)
        is_new = r.setnx(f"dedupe:{idempotency_key}", "1")
        if is_new:
            # Expire after 24 hours
            r.expire(f"dedupe:{idempotency_key}", 86400)
            return False
        return True

    def update_counter(self, customer_id, event_type):
        """
        Increment the real-time usage counter in Redis
        """
        key = f"meter:{customer_id}:{event_type}"
        new_count = r.incr(key)
        logger.info(f"Updated counter for {customer_id} -> {event_type}: {new_count}")
        return new_count

    def process_event(self, event_data):
        idempotency_key = event_data.get('idempotencyKey')
        customer_id = event_data.get('customerId')
        event_type = event_data.get('event')

        if not customer_id or not event_type:
            logger.error("Invalid event format")
            return

        if self.deduplicate(idempotency_key):
            logger.warning(f"Duplicate event ignored: {idempotency_key}")
            return

        # Fast path update
        self.update_counter(customer_id, event_type)
        
        # Here we would normally batch and flush to ClickHouse / S3

    def run(self):
        logger.info("Starting Mediation Processor...")
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
    processor = MediationProcessor()
    processor.run()
