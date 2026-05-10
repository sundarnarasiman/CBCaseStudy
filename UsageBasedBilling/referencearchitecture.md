# Usage-Based Billing Reference Architecture

## 1. Overview
This reference architecture describes a highly scalable, real-time usage-based billing platform. Unlike traditional flat-fee subscriptions, this system is designed to handle high-volume event streams (e.g., millions of events per second), process them accurately without data loss or duplication, and calculate metered charges dynamically. 

The architecture follows a decoupled, event-driven pattern that separates raw usage ingestion from the rating and invoicing processes, supporting complex pricing structures, rapid iteration, and real-time customer transparency.

## 2. System Diagrams

### 2.1 Architecture Overview Diagram

```mermaid
graph TD
    subgraph "Event Sources"
        A1[Product Telemetry]
        A2[API Gateways]
        A3[IoT / System Logs]
    end

    subgraph "Ingestion Layer"
        B1[Fastify API Handlers]
        B2[Apache Kafka Stream]
    end

    subgraph "Mediation & Metering Layer"
        C1[Stream Processor/Aggregator]
        C2[(Redis - Cache & Deduplication)]
    end

    subgraph "Storage & Data Lakehouse"
        D1[(S3 / MinIO - Raw Events)]
        D2[(ClickHouse - Time-Series Aggregates)]
    end

    subgraph "Rating & Revenue System"
        E1[Rating Engine]
        E2[(Revenue Ledger)]
        E3[Billing API]
    end

    subgraph "Customer Experience & Control"
        F1[Entitlement Gating & Alerts]
        F2[Customer Dashboards]
    end

    subgraph "External Integration"
        G1[Stripe / Chargebee]
        G2[Accounting / CRM]
    end

    %% Data Flow
    A1 --> B1
    A2 --> B1
    A3 --> B2
    B1 --> B2

    B2 --> C1
    C1 <--> C2
    C1 --> D1
    C1 --> D2

    %% Fast Path for Real-Time Alerts
    C2 -.-> F1
    F1 -.->|Stop Services| A2

    %% Billing Flow
    D2 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> G1
    E3 --> G2

    %% Visibility
    D2 --> F2
    E2 --> F2
```

### 2.2 Component Diagram

```mermaid
flowchart TD
    subgraph Client Tier
        C1[Client Applications]
        C2[IoT Devices / Systems]
    end

    subgraph Ingestion Tier
        API[API Gateway / Fastify]
        Queue[Message Broker / Kafka]
    end

    subgraph Processing Tier
        StreamProc[Stream Processor / Flink]
        Cache[(In-Memory Cache / Redis)]
    end

    subgraph Data Tier
        DL[(Raw Data Lake / S3)]
        DW[(Analytics DB / ClickHouse)]
    end

    subgraph Billing & Core Tier
        Rating[Rating Engine]
        Ledger[(Revenue Ledger)]
        BillingSys[Billing & Invoicing API]
    end
    
    subgraph External Systems
        ExtPay[Payment Gateway / Stripe]
        CRM[CRM System]
    end

    C1 -->|Usage Events| API
    C2 -->|Usage Events| API
    API -->|Validate & Publish| Queue
    Queue -->|Consume| StreamProc
    
    StreamProc <-->|Dedupe & Fast Counters| Cache
    StreamProc -->|Archive Raw| DL
    StreamProc -->|Store Aggregates| DW
    
    DW -->|Query Usage| Rating
    Rating -->|Apply Pricing| Ledger
    Ledger -->|Generate Charges| BillingSys
    
    BillingSys -->|Sync & Invoice| ExtPay
    BillingSys -->|Sync Customer| CRM
```

### 2.3 Use Case Diagram

```mermaid
flowchart LR
    %% Actors
    Cust([Customer])
    Dev([Developer / System])
    Admin([Billing Administrator])
    
    %% System Boundary
    subgraph Usage-Based Billing System
        UC1(Send Usage Events)
        UC2(View Usage Dashboards)
        UC3(Manage Pricing Plans)
        UC4(View Invoices)
        UC5(Process Payments)
        UC6(Configure Real-time Alerts)
    end
    
    %% Relationships
    Dev --> UC1
    Cust --> UC2
    Cust --> UC4
    Cust --> UC6
    
    Admin --> UC3
    Admin --> UC4
    
    %% Stripe / External
    Stripe([Payment Provider])
    UC5 --> Stripe
    UC4 -.->|Triggers| UC5
```

### 2.4 Domain and Sub-Domain Diagram

```mermaid
graph TD
    subgraph BillingDomain [Usage-Based Billing Domain]
        direction TB
        
        subgraph Ingestion [Event Ingestion & Metering Sub-Domain]
            E1(Event Collection)
            E2(Deduplication)
            E3(Aggregation)
        end
        
        subgraph Rating [Pricing & Rating Sub-Domain]
            R1(Pricing Catalog)
            R2(Rating Engine)
        end
        
        subgraph Billing [Billing & Invoicing Sub-Domain]
            B1(Revenue Ledger)
            B2(Invoice Generation)
            B3(Payment Processing)
        end
        
        subgraph Customer [Customer Experience Sub-Domain]
            C1(Usage Dashboards)
            C2(Entitlements & Gating)
            C3(Real-time Alerts)
        end
        
        Ingestion -->|Aggregated Usage| Rating
        Rating -->|Charges| Billing
        Ingestion -->|Real-time Metrics| Customer
        Billing -->|Invoice Data| Customer
    end
```

## 3. Core Components

### 3.1. Ingestion Layer
*   **Event Ingestion / Instrumentation:** Captures raw usage events (API calls, bytes processed, compute hours) in real-time. Built to handle massive throughput (up to 100k+ events/sec).
*   **Technologies:** Fastify (for high-performance API endpoints), Apache Kafka (for durable, scalable event streaming).

### 3.2. Mediation & Metering Layer
*   **Mediation:** Responsible for collecting, validating, cleansing, and deduplicating events. Ensures idempotent operations by checking unique request IDs so duplicate network retries do not lead to double billing.
*   **Aggregation:** Processes high-volume raw events into billable metrics (e.g., summing GBs or counting API calls).
*   **Technologies:** Redis is utilized as an in-memory fast-path for deduplication, state tracking, and real-time counters.

### 3.3. Storage & Data Lakehouse
*   **Raw Event Storage (Data Lake):** Stores immutable, raw events for auditing and historical back-processing without schema lock-in. 
*   **Analytical Storage (Data Warehouse):** Stores aggregated time-series data optimized for fast querying by the Rating Engine and Customer Dashboards.
*   **Technologies:** Amazon S3 / MinIO (Raw Object Storage), ClickHouse (High-performance Time-Series Database).

### 3.4. Rating & Revenue System
*   **Rating Engine:** Applies complex business rules, tier-based pricing, volume discounts, and hybrid billing logic to the aggregated consumption data.
*   **Revenue Ledger:** A highly available, accurate financial record system that maintains customer balances, manages credits, and supports complex pricing structures.
*   **Billing & Invoicing API:** Acts as the interface to generate formalized charges.

### 3.5. Customer Experience & Control
*   **Entitlement Gating & Alerts:** Uses the fast-path (Redis) to enforce quotas, trigger real-time alerts before a cap is hit, or circuit-break services when funds run out.
*   **Customer Usage Dashboards:** APIs that provide customers with complete transparency over their consumption, spend, and commitment burndowns.

### 3.6. External Integration
*   **Billing Systems:** Finalized charges are pushed to external systems for actual payment collection, invoicing, and compliance.
*   **Technologies:** Stripe, Chargebee.

## 4. Architectural Patterns Used

1.  **Event-Driven Pipeline:** Data flows continuously via Kafka, processing events asynchronously to maintain system responsiveness and near real-time dashboards.
2.  **Decoupled Architecture:** Separates the metering layer from the billing layer. Raw events are completely separated from pricing logic.
3.  **Data Lakehouse Pattern:** Combines the scalability of S3 with the structured analytical power of ClickHouse.
4.  **Idempotency & Resilience:** Guarantees that late-arriving or duplicate events are handled seamlessly without causing revenue leakage or overcharging.
5.  **Product-Centric Billing:** Usage constraints and live costs are tied directly into the product interface for real-time personalization.

## 5. Key Considerations

*   **Performance & Scalability:** Designed to process millions of events gracefully, essential for high-throughput domains like LLMs/AI, IoT, and heavy API usage.
*   **Accuracy:** Robust infrastructure handles delayed events ("late-arriving" events) and ensures the Revenue Ledger is fundamentally accurate for compliance and accounting standard revenue recognition.
*   **Flexibility:** "No schema lock-in" approach allows raw capture, meaning pricing models can pivot easily (e.g., moving from per-seat to per-token pricing) without needing to change how usage is instrumented.

## 6. Implementation Details: Ingestion Layer

### 6.1 Overview
The **Ingestion Layer** is the entry point for all usage data. It must be highly performant, resilient, and capable of buffering large volumes of events before they are persisted or processed by the downstream metering engine.

### 6.2 Technology Choices
* **Framework:** **Node.js with Fastify**. Fastify is chosen for its extremely low overhead, fast routing, and high throughput capabilities compared to Express or other web frameworks, making it ideal for an ingestion gateway.
* **Message Broker:** **Apache Kafka**. Kafka is used to stream the received events durably. It acts as a massive buffer, decoupling the ingestion gateway from the downstream metering and rating processes.

### 6.3 Flow and Responsibilities
1. **API Endpoint (`POST /events`):** Fastify exposes a lightweight endpoint that accepts usage events (e.g., `{ "customerId": "123", "event": "api_call", "timestamp": "...", "idempotencyKey": "..." }`).
2. **Validation:** Basic schema validation (JSON Schema via Fastify) ensures malformed payloads are rejected immediately.
3. **Kafka Producer:** The Fastify application uses a Kafka client (like `kafkajs`) to publish the validated event to a specific topic (e.g., `usage-events`).
4. **Immediate Acknowledgment:** Once the event is safely handed off to Kafka, Fastify immediately returns a `202 Accepted` response to the client to ensure the client is not blocked.

### 6.4 Sequence Diagram
The sequence below illustrates the fast, non-blocking ingestion path where the gateway validates the event and durably queues it in Kafka before responding to the client.

```mermaid
sequenceDiagram
    participant Client as Application / Client
    participant Fastify as API Gateway (Fastify)
    participant Validator as JSON Schema Validator
    participant Kafka as Message Broker (Kafka)
    participant Consumer as Downstream Metering

    Client->>Fastify: POST /ingest { event payload }
    Fastify->>Validator: Validate Payload
    
    alt Invalid Payload
        Validator-->>Fastify: Validation Error
        Fastify-->>Client: 400 Bad Request
    else Valid Payload
        Validator-->>Fastify: Valid
        Fastify->>Fastify: Generate Idempotency Key (if missing)
        Fastify->>Kafka: Producer.send(topic, message)
        Kafka-->>Fastify: ACK (Message durably stored)
        Fastify-->>Client: 202 Accepted (idempotencyKey)
    end
    
    %% Asynchronous Processing
    Kafka-->>Consumer: Stream event asynchronously
    Consumer->>Consumer: Deduplicate & Meter
```

### 6.5 Implementation Blueprint
A typical Fastify ingestion route integrated with Kafka:

```javascript
// Example Fastify route publishing to Kafka
fastify.post('/ingest', { schema: eventSchema }, async (request, reply) => {
    const eventPayload = request.body;
    
    // Produce event to Kafka topic
    await kafkaProducer.send({
        topic: 'usage-events',
        messages: [
            { key: eventPayload.customerId, value: JSON.stringify(eventPayload) }
        ],
    });
    
    // Acknowledge receipt immediately
    return reply.code(202).send({ status: 'accepted' });
});
```

### 6.6 Class Diagram
```mermaid
classDiagram
    class IngestionServer {
        +start()
        +registerRoutes()
    }
    class EventController {
        +ingestEvent(Request req, Reply reply)
    }
    class SchemaValidator {
        +validate(EventPayload payload)
    }
    class KafkaProducer {
        +connect()
        +send(topic, message)
    }
    class EventPayload {
        +String customerId
        +String event
        +DateTime timestamp
        +String idempotencyKey
        +Object metadata
    }
    
    IngestionServer --> EventController : routes to
    EventController --> SchemaValidator : uses
    EventController --> KafkaProducer : delegates to
    EventController ..> EventPayload : receives
```

### 6.7 Deployment Diagram
```mermaid
flowchart TD
    subgraph K8s Cluster [Kubernetes Cluster]
        subgraph Ingestion Pods
            App1[Fastify Server 1]
            App2[Fastify Server 2]
        end
        ALB[Load Balancer] --> App1
        ALB --> App2
    end
    
    subgraph Kafka Cluster [Managed Kafka (MSK / Confluent)]
        K1[(Broker 1)]
        K2[(Broker 2)]
    end
    
    App1 -->|Produce| K1
    App2 -->|Produce| K2
```

### 6.8 Data Model
```mermaid
erDiagram
    USAGE_EVENT {
        string customerId PK
        string idempotencyKey UK "Unique Identifier for Retries"
        string event "Type of event e.g., api_call"
        datetime timestamp "When it occurred"
        json metadata "Additional flexible properties"
    }
```

## 7. Implementation Details: Mediation and Metering Layer

### 7.1 Overview
The **Mediation and Metering Layer** is a Python-based processing engine that consumes raw events from Kafka. It ensures exactly-once semantics by deduplicating events using Redis and maintains high-speed counters for real-time usage tracking before data is eventually persisted into the Data Warehouse.

### 7.2 Sequence Diagram
```mermaid
sequenceDiagram
    participant Kafka as Event Stream (Kafka)
    participant Processor as MediationProcessor
    participant Redis as In-Memory Cache (Redis)
    participant DB as Analytical DB (ClickHouse)

    Kafka->>Processor: Poll events
    loop For each event
        Processor->>Redis: SETNX dedupe:{idempotencyKey} "1"
        alt Key exists (Duplicate)
            Redis-->>Processor: Returns 0
            Processor->>Processor: Ignore event
        else Key does not exist (New)
            Redis-->>Processor: Returns 1
            Processor->>Redis: EXPIRE dedupe:{idempotencyKey} 86400 (24h)
            Processor->>Redis: INCR meter:{customerId}:{eventType}
            Redis-->>Processor: Returns updated count
            Processor->>DB: Batch/Flush event to Storage
        end
    end
```

### 7.3 Class Diagram
```mermaid
classDiagram
    class MediationProcessor {
        -Consumer consumer
        -Redis redisClient
        +__init__()
        +deduplicate(idempotency_key) bool
        +update_counter(customer_id, event_type) int
        +process_event(event_data)
        +run()
    }
    
    class RedisClient {
        +setnx(key, value)
        +expire(key, time)
        +incr(key)
    }
    
    class KafkaConsumer {
        +subscribe(topics)
        +poll(timeout)
    }
    
    MediationProcessor --> RedisClient : uses for fast path
    MediationProcessor --> KafkaConsumer : consumes from
```

### 7.4 Deployment Diagram
```mermaid
flowchart TD
    subgraph K8s Cluster [Kubernetes Cluster]
        subgraph Worker Pods [Mediation Workers]
            W1[Python Processor 1]
            W2[Python Processor 2]
            W3[Python Processor 3]
        end
        
        W1 --> RedisMaster
        W2 --> RedisMaster
        W3 --> RedisMaster
    end
    
    subgraph Kafka Cluster [Managed Kafka]
        K[(Broker Topic: usage-events)]
    end
    
    subgraph Cache Cluster [Managed Redis]
        RedisMaster[(Redis Primary)]
    end
    
    K -->|Poll Events| W1
    K -->|Poll Events| W2
    K -->|Poll Events| W3
```

### 7.5 Data Model
```mermaid
erDiagram
    REDIS_DEDUPE_KEY {
        string key PK "dedupe:{idempotencyKey}"
        string value "1"
        int ttl "86400 seconds"
    }
    
    REDIS_METER_KEY {
        string key PK "meter:{customerId}:{eventType}"
        int count "Accumulated usage"
    }
```

## 8. Implementation Details: Storage and Data Lakehouse

### 8.1 Overview
The **Storage and Data Lakehouse Layer** bridges the gap between raw streaming events and queryable analytical data. It consumes events from Kafka, uploading immutable raw JSON payloads to an **S3 Data Lake** for long-term auditing, while simultaneously upserting structured records into **ClickHouse** for high-speed, aggregative queries by the Rating system.

### 8.2 Sequence Diagram
```mermaid
sequenceDiagram
    participant Kafka as Event Stream (Kafka)
    participant Storage as StorageProcessor
    participant S3 as Data Lake (S3)
    participant CH as Data Warehouse (ClickHouse)

    Kafka->>Storage: Poll event
    Storage->>S3: PutObject(Bucket, Key=raw_events/{id}.json)
    S3-->>Storage: HTTP 200 OK
    Storage->>CH: INSERT INTO usage_aggregates VALUES (...)
    CH-->>Storage: OK
```

### 8.3 Class Diagram
```mermaid
classDiagram
    class StorageProcessor {
        -Consumer consumer
        -S3Client s3_client
        -ClickHouseClient ch_client
        +__init__()
        +save_raw_to_s3(event_data) bool
        +save_aggregate_to_clickhouse(event_data) bool
        +process_event(event_data)
        +run()
    }
    
    StorageProcessor --> S3Client : Uploads raw JSON
    StorageProcessor --> ClickHouseClient : Inserts aggregations
```

### 8.4 Deployment Diagram
```mermaid
flowchart TD
    subgraph Storage Tier (K8s)
        S1[Python Storage Sink 1]
        S2[Python Storage Sink 2]
    end
    
    subgraph Kafka Cluster [Managed Kafka]
        K[(Broker Topic: usage-events)]
    end
    
    subgraph AWS Cloud
        S3[(Amazon S3 / Data Lake)]
    end
    
    subgraph Analytics Tier
        CH[(ClickHouse Cluster)]
    end
    
    K -->|Poll Events| S1
    K -->|Poll Events| S2
    
    S1 -->|PutObject| S3
    S2 -->|PutObject| S3
    
    S1 -->|Insert Batch| CH
    S2 -->|Insert Batch| CH
```

### 8.5 Data Model
```mermaid
erDiagram
    S3_RAW_OBJECT {
        string key PK "raw_events/{idempotencyKey}.json"
        json body "Full raw event payload"
    }
    
    CLICKHOUSE_AGGREGATES {
        string customer_id PK
        string event_type PK
        date usage_date PK
        uint64 total_events "Accumulated event count per day"
    }
```

## 9. Implementation Details: Rating and Revenue System

### 9.1 Overview
The **Rating and Revenue System** operates asynchronously, responding to billing triggers (e.g., end-of-month processes) published to Kafka. It reaches out to **ClickHouse** to retrieve aggregated usage data, calculates charges against a pricing catalog, and outputs finalized invoice documents to an **S3 Bucket**.

### 9.2 Sequence Diagram
```mermaid
sequenceDiagram
    participant Kafka as Trigger Stream (Kafka)
    participant Rating as RatingProcessor
    participant CH as Data Warehouse (ClickHouse)
    participant S3 as Invoice Bucket (S3)

    Kafka->>Rating: Poll billing-trigger event
    Rating->>CH: SELECT sum(events) FROM aggregates WHERE customerId = X
    CH-->>Rating: Return usage data
    Rating->>Rating: Apply pricing catalog & rules
    Rating->>Rating: Generate Invoice JSON
    Rating->>S3: PutObject(Bucket, Key=invoices/{customer}_{period}.json)
    S3-->>Rating: HTTP 200 OK
```

### 9.3 Class Diagram
```mermaid
classDiagram
    class RatingProcessor {
        -Consumer consumer
        -ClickHouseClient ch_client
        -S3Client s3_client
        +__init__()
        +fetch_usage(customer_id, start_date, end_date) List
        +calculate_charges(usage_data) Tuple
        +generate_and_save_invoice(customer_id, line_items, total) dict
        +process_trigger(trigger_data)
        +run()
    }
    
    RatingProcessor --> ClickHouseClient : Fetches aggregates
    RatingProcessor --> S3Client : Saves finalized invoice
```

### 9.4 Deployment Diagram
```mermaid
flowchart TD
    subgraph Rating Tier (K8s / CronJob)
        R1[Rating Processor 1]
    end
    
    subgraph Kafka Cluster [Managed Kafka]
        K[(Topic: billing-triggers)]
    end
    
    subgraph Analytics Tier
        CH[(ClickHouse Cluster)]
    end
    
    subgraph AWS Cloud
        S3[(Amazon S3 / Invoices)]
    end
    
    K -->|Trigger Signal| R1
    R1 -->|Query Data| CH
    R1 -->|Write Invoice| S3
```

### 9.5 Data Model
```mermaid
erDiagram
    S3_INVOICE_DOCUMENT {
        string key PK "invoices/{customerId}_{period}.json"
        string customer_id
        string billing_period
        json line_items "Array of charges per event type"
        float total_amount
        string status "e.g., generated"
    }
```
