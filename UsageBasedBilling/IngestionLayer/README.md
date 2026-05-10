# Ingestion Layer

This is the high-performance event ingestion API built with Node.js, Fastify, and Apache Kafka. It validates incoming usage events and durably streams them to a Kafka topic for downstream metering and rating.

## Prerequisites
- Node.js (v18+)
- Local or remote Apache Kafka broker running (port 9092 by default)

## Build & Install
To build and install the dependencies, run:
```bash
npm install
```

## Configuration
Create a `.env` file in the root directory (or use the provided default) with the following environment variables:
```
PORT=3000
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=usage-events
```

## Running the Server
To start the Fastify server:
```bash
npm start
```

*Note: The server requires a running Kafka broker to successfully connect the producer.*

## Testing
This project uses `tap` for testing. To run the tests, first install the dev dependencies:
```bash
npm install tap --save-dev
```

Then run the test file:
```bash
npx tap server.test.js
```

## Usage
Once the server is running on `http://localhost:3000`, you can send a POST request:

```bash
curl -X POST http://localhost:3000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": "cust_12345",
    "event": "api_call",
    "timestamp": "2026-05-10T12:00:00Z"
  }'
```
You should receive a `202 Accepted` response with an `idempotencyKey`.
