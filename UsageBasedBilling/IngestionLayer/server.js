require('dotenv').config();
const fastify = require('fastify')({ logger: true });
const { Kafka } = require('kafkajs');

// Initialize Kafka client
const kafka = new Kafka({
  clientId: 'ingestion-gateway',
  brokers: [process.env.KAFKA_BROKER || 'localhost:9092']
});

const producer = kafka.producer();
const KAFKA_TOPIC = process.env.KAFKA_TOPIC || 'usage-events';

// JSON Schema for validating incoming events
const eventSchema = {
  body: {
    type: 'object',
    required: ['customerId', 'event', 'timestamp'],
    properties: {
      customerId: { type: 'string' },
      event: { type: 'string' },
      timestamp: { type: 'string', format: 'date-time' },
      idempotencyKey: { type: 'string' },
      metadata: { type: 'object' }
    }
  }
};

// Ingestion route
fastify.post('/ingest', { schema: eventSchema }, async (request, reply) => {
  const eventPayload = request.body;
  
  // Assign a generated idempotency key if one is not provided
  if (!eventPayload.idempotencyKey) {
    eventPayload.idempotencyKey = `${eventPayload.customerId}-${eventPayload.timestamp}-${Math.random().toString(36).substring(7)}`;
  }

  try {
    // Produce event to Kafka topic
    await producer.send({
      topic: KAFKA_TOPIC,
      messages: [
        { 
          key: eventPayload.customerId, 
          value: JSON.stringify(eventPayload) 
        }
      ],
    });
    
    request.log.info(`Event pushed to Kafka for customer: ${eventPayload.customerId}`);
    
    // Acknowledge receipt immediately
    return reply.code(202).send({ 
      status: 'accepted',
      idempotencyKey: eventPayload.idempotencyKey 
    });
    
  } catch (error) {
    request.log.error(error, 'Failed to publish event to Kafka');
    return reply.code(500).send({ status: 'error', message: 'Internal Server Error' });
  }
});

// Start the server
const start = async () => {
  try {
    await producer.connect();
    fastify.log.info('Kafka producer connected successfully');
    
    const port = process.env.PORT || 3000;
    await fastify.listen({ port, host: '0.0.0.0' });
    fastify.log.info(`Server listening on port ${port}`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
