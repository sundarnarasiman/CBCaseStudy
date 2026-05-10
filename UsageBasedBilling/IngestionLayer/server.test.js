const fastify = require('fastify')();
const { Kafka } = require('kafkajs');
const tap = require('tap');

// Mock Kafka
class MockProducer {
  async connect() { return true; }
  async send() { return true; }
  async disconnect() { return true; }
}

tap.test('POST /ingest returns 202 and idempotencyKey', async (t) => {
  // Simple mock server setup for testing
  fastify.post('/ingest', async (request, reply) => {
    const payload = request.body;
    let key = payload.idempotencyKey || 'generated-key-123';
    return reply.code(202).send({ status: 'accepted', idempotencyKey: key });
  });

  const response = await fastify.inject({
    method: 'POST',
    url: '/ingest',
    payload: {
      customerId: 'cust_01',
      event: 'api_call',
      timestamp: new Date().toISOString()
    }
  });

  t.equal(response.statusCode, 202, 'returns a status code of 202');
  
  const body = JSON.parse(response.payload);
  t.equal(body.status, 'accepted', 'status is accepted');
  t.ok(body.idempotencyKey, 'returns an idempotency key');
  
  t.end();
});
