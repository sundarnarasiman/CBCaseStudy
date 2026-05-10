import os
import json
import logging
import smtplib
from email.message import EmailMessage
from confluent_kafka import Consumer, KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'notifications')
SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.getenv('SMTP_PORT', 1025)) # Default to MailHog/Mailpit for local dev

class NotificationProcessor:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BROKER,
            'group.id': 'notification-group',
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([KAFKA_TOPIC])

    def send_email(self, recipient, subject, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = 'billing@graviton.io'
        msg['To'] = recipient

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                # server.login(user, password) if needed
                server.send_message(msg)
            logger.info(f"Email sent to {recipient}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False

    def process_notification(self, notification_data):
        recipient = notification_data.get('email')
        subject = notification_data.get('subject', 'Important Notification')
        body = notification_data.get('body', '')

        if not recipient:
            logger.warning("Notification missing email recipient")
            return

        self.send_email(recipient, subject, body)

    def run(self):
        logger.info("Starting Notification Processor...")
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
                self.process_notification(data)
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

if __name__ == "__main__":
    processor = NotificationProcessor()
    processor.run()
