# System Design: Webhook Delivery System

**Source:** Most frequently cited Stripe system design question (Prepfully, Glassdoor, 2024-2026)

## The Prompt

"Design a system that delivers webhooks to customers reliably. The system should handle millions of events per day, guarantee at-least-once delivery, and provide visibility into delivery status."

## Time Budget (45 minutes)

| Phase | Time | Focus |
|-------|------|-------|
| Clarify requirements | 5 min | Scale, SLAs, ordering guarantees |
| High-level design | 10 min | Components, data flow, API |
| Detailed design | 15 min | Retry logic, failure handling, storage |
| Deep dive | 10 min | Scale, monitoring, edge cases |
| Q&A | 5 min | Trade-offs, alternatives |

## Clarifying Questions to Ask

1. "What's the expected event volume?" (Stripe: ~billions/day)
2. "What delivery guarantee? At-least-once, at-most-once, exactly-once?"
3. "Do events need to be delivered in order?"
4. "What's the SLA for delivery latency? (e.g., 99% within 5 seconds)"
5. "How should we handle endpoints that are down for hours/days?"
6. "Do customers need to see delivery status/logs?"

## Step-by-Step Framework

### 1. Event Ingestion
- Internal services publish events to a message queue (Kafka)
- Events are persisted to a durable store before acknowledgment
- Each event has: event_id (UUID), type, payload, timestamp, customer_id

### 2. Event Processing Pipeline
- Consumer workers read from Kafka partitions
- Partition by customer_id for ordering within a customer
- Lookup customer's webhook URL and signing secret
- Sign payload with HMAC-SHA256

### 3. Delivery Attempt
- HTTP POST to customer's URL with signed payload
- Timeout: 30 seconds
- Success: 2xx response → mark delivered
- Failure: non-2xx or timeout → schedule retry

### 4. Retry Strategy
- Exponential backoff: 1min, 5min, 30min, 2hr, 8hr, 24hr
- Max retries: 5-7 attempts over ~3 days
- After max retries: mark as "failed", notify customer
- Dead-letter queue for permanently failed events

### 5. Idempotency
- Include event_id in headers so customers can deduplicate
- Customers should implement idempotent handlers
- Our system may deliver the same event twice (at-least-once)

### 6. Monitoring & Visibility
- Customer dashboard showing delivery status per event
- Webhook logs: request/response headers, body, timing
- Alerting: if a customer's endpoint has been failing for >1 hour
- Disable endpoints after extended failures (re-enable via API)

## Key Components to Draw

```
[Internal Services] → [Kafka Topics] → [Delivery Workers]
                                              ↓
                                    [Customer Endpoints]
                                              ↓
                              [Retry Queue] ← [Failure Handler]
                                              ↓
                                    [Dead Letter Queue]

[Event Store DB] ← logs all attempts
[Dashboard API] → reads from Event Store
```

## Deep Dive Areas

### Ordering
- **Within a customer:** Partition by customer_id in Kafka → guaranteed order
- **Across customers:** No ordering guarantee (nor needed)
- **Problem:** Retries can cause out-of-order delivery
- **Solution:** Include sequence numbers; let customers reorder if needed

### Scaling
- Kafka partitions: scale horizontally by adding partitions + consumers
- Delivery workers: stateless, scale independently
- Database: shard event store by customer_id
- Rate limiting: per-customer concurrency limit (e.g., 5 concurrent deliveries)

### Failure Scenarios
- **Customer endpoint down:** Retry with backoff, alert after threshold
- **Kafka broker down:** Replication factor 3, automatic failover
- **Delivery worker crash:** Kafka redelivers uncommitted messages
- **Database down:** Buffer in Kafka, drain when DB recovers

## Sample Answer Outline

> "I'd design a pipeline with three main stages: ingestion, delivery, and recovery.
>
> For ingestion, internal services publish events to Kafka, partitioned by customer_id. This gives us durability and ordering.
>
> For delivery, a pool of stateless workers consumes from Kafka, signs the payload with the customer's secret, and POSTs to their URL. On success, we commit the offset and log the delivery. On failure, we push to a retry topic with exponential backoff metadata.
>
> For recovery, a separate retry consumer processes failed deliveries with increasing delays. After max retries, events go to a dead-letter queue and we notify the customer.
>
> Key design decisions: at-least-once delivery (simplest for customers to handle), HMAC signing for security, per-customer partitioning for ordering, and a dashboard API backed by the event store for visibility."

## Common Mistakes

1. **Not discussing idempotency** — At-least-once means duplicates happen. Must provide event_id for dedup.
2. **Fixed retry intervals** — Shows lack of distributed systems experience. Always exponential backoff + jitter.
3. **Ignoring ordering** — Acknowledge the problem even if you choose not to solve it.
4. **No monitoring** — Stripe is operationally mature. Always include dashboards, alerts, and logs.
5. **Synchronous processing** — Don't block the event producer on delivery. Always async via queue.

## Connection to Stripe's Actual Architecture

- Stripe sends webhooks for 200+ event types (payment_intent.succeeded, charge.refunded, etc.)
- Uses Kafka with 50 clusters, 700 TB daily publish throughput
- Events include a `livemode` flag to distinguish test/prod
- Signature uses `Stripe-Signature` header with HMAC-SHA256
- Retry schedule: 1hr, 2hr, 4hr, 8hr... up to 3 days
- Dashboard shows real-time webhook delivery logs with request/response
