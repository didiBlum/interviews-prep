# System Design Exercise 3: Event-Driven External App Triggers

## The Prompt (As Asked in Interview)

> "How can external apps be triggered by an action on the table? Think about event-driven architecture, failure tolerance."

---

## Time Budget (45 Minutes)

| Phase | Minutes | What to Cover |
|-------|---------|---------------|
| Clarify requirements | 5 | What kinds of actions, what kinds of apps, SLAs |
| High-level event flow | 8 | Action -> Event -> Delivery to external app |
| Event pipeline design | 10 | Kafka topics, consumer groups, webhook dispatch |
| Failure tolerance deep dive | 12 | Retries, dead letter queues, circuit breakers, idempotency |
| Subscription & registration model | 5 | How apps register for events, filtering |
| Scale, security, and monitoring | 5 | Rate limiting, auth, observability |

---

## Clarifying Questions to Ask

1. **Action types** -- "What types of table actions should trigger apps? Item created, updated, deleted, status changed, column value changed, moved between groups? All of them?"
2. **App types** -- "Are these third-party apps from a marketplace, or also first-party integrations (Slack, Gmail)? Both?"
3. **Delivery mechanism** -- "Do we push to apps via webhooks, or do apps poll? Or both?"
4. **Latency SLA** -- "What's the acceptable delay between the action on the table and the app receiving the trigger? Sub-second, seconds, minutes?"
5. **Delivery guarantee** -- "At-least-once or exactly-once? Is it acceptable for an app to receive the same event twice if we ensure no events are lost?"
6. **Volume** -- "How many events per second across the platform? How many subscribed apps per event on average?"
7. **Filtering granularity** -- "Can an app subscribe to specific boards, specific columns, or specific value changes (e.g., 'status changed to Done')?"
8. **App reliability** -- "External apps may be down or slow. What happens? Do we buffer? For how long?"

---

## Step-by-Step Framework

### Step 1: Identify the Components

```
+------------------+     +----------------+     +------------------+
|   Monday.com     |     |   Event        |     |   Webhook        |
|   Core Platform  | --> |   Pipeline     | --> |   Dispatch       |
|   (mutations)    |     |   (Kafka)      |     |   Service        |
+------------------+     +----------------+     +------------------+
                                                        |
                                                        v
                                                 +--------------+
                                                 | External App |
                                                 | Endpoints    |
                                                 +--------------+
```

### Step 2: Event Generation

**Where events are born**: Every mutation in the Board Service already publishes to Kafka (this is Monday.com's existing pattern). The key insight is that **app triggers tap into the same event stream** -- no new event generation needed.

```
Board Service (handles user action)
  |
  | 1. User changes status column to "Done"
  | 2. Board Service writes to mondayDB
  | 3. Board Service publishes to Kafka topic: "board-events"
  |
  v
Kafka Topic: board-events
  Partition key: board_id (ensures ordering per board)
  Event schema:
  {
    eventId: "uuid-v4",
    type: "column_value_changed",
    boardId: 12345,
    itemId: 67890,
    columnId: "status",
    previousValue: { label: "In Progress" },
    newValue: { label: "Done" },
    userId: 111,
    accountId: 222,
    timestamp: "2026-03-26T10:00:00Z"
  }
```

### Step 3: Subscription Registry

Apps register what events they care about. This is the **Trigger Registration** model:

```
Table: app_event_subscriptions
  subscription_id: UUID (PK)
  app_id: UUID
  account_id: UUID        -- which customer installed this app
  board_id: UUID           -- optional: null means all boards
  event_type: STRING       -- e.g., "column_value_changed"
  filter: JSONB            -- e.g., { "columnId": "status", "newValue.label": "Done" }
  webhook_url: STRING      -- where to deliver
  secret: STRING           -- for HMAC signing
  created_at: TIMESTAMP
  is_active: BOOLEAN
```

**How apps register**: Via Monday.com's App Framework SDK during installation. The app manifest declares triggers:

```json
{
  "triggers": [
    {
      "type": "column_value_changed",
      "config": {
        "columnTypes": ["status"],
        "boardScope": "subscribed"
      },
      "webhookUrl": "https://myapp.example.com/hooks/monday"
    }
  ]
}
```

### Step 4: Event Processing Pipeline

```
Kafka Topic: board-events
  |
  v
Trigger Matcher Service (consumer group: "trigger-matcher")
  |
  | 1. Consume event
  | 2. Look up subscriptions matching:
  |    - account_id + board_id + event_type
  |    - Apply filter predicates (column, value, etc.)
  | 3. For each matching subscription, produce to:
  |
  v
Kafka Topic: webhook-dispatch
  Partition key: app_id (ensures ordering per app)
  {
    dispatchId: "uuid",
    subscriptionId: "sub-uuid",
    appId: "app-uuid",
    webhookUrl: "https://...",
    secret: "hmac-secret",
    payload: { ...original event... },
    attemptNumber: 1,
    createdAt: "2026-03-26T10:00:00Z"
  }

  |
  v
Webhook Dispatch Service (consumer group: "webhook-dispatcher")
  |
  | 1. Consume dispatch message
  | 2. Sign payload with HMAC-SHA256 using app's secret
  | 3. POST to webhook_url with timeout (5 seconds)
  | 4. If 2xx: done, mark delivered
  | 5. If non-2xx or timeout: retry logic (see failure tolerance)
```

### Step 5: Failure Tolerance (This Is the Heart of the Question)

The interviewer specifically asked about failure tolerance. Spend significant time here.

**Layer 1: Kafka provides durability and replayability**
- Events are persisted in Kafka with configurable retention (e.g., 7 days).
- If the Trigger Matcher crashes, it restarts and resumes from its last committed offset.
- If the Webhook Dispatcher crashes, same -- no events lost.

**Layer 2: Exponential backoff retry**

```
Retry schedule:
  Attempt 1: immediate
  Attempt 2: 30 seconds
  Attempt 3: 2 minutes
  Attempt 4: 10 minutes
  Attempt 5: 1 hour
  Attempt 6: 6 hours
  Attempt 7: 24 hours (final)

Implementation:
  - On failure, publish retry message to a "webhook-retry" topic
    with a delivery_after timestamp.
  - A Retry Scheduler service (or SQS delay queues) holds the message
    until delivery_after, then re-publishes to webhook-dispatch.
  - Use SQS delay queues or a Redis sorted set as a time-based scheduler.
```

**Layer 3: Dead Letter Queue (DLQ)**
- After all retry attempts exhausted, move to DLQ topic: `webhook-dlq`
- Alert the app developer via Monday.com's developer dashboard
- Allow manual replay from DLQ once the app is fixed
- DLQ retention: 30 days

**Layer 4: Circuit breaker per app endpoint**

```
State machine per (app_id, webhook_url):

  CLOSED (normal)
    -> If 5 consecutive failures: transition to OPEN

  OPEN (blocked)
    -> All webhook dispatches queued, not sent
    -> After 5 minutes: transition to HALF_OPEN

  HALF_OPEN (probing)
    -> Send 1 test webhook
    -> If success: transition to CLOSED, flush queued events
    -> If failure: transition back to OPEN

Stored in Redis:
  circuit:{appId}:{urlHash} -> { state, failCount, lastAttempt }
```

**Why circuit breaker matters**: A failing app endpoint shouldn't consume dispatch capacity. Without it, one broken app blocks the entire dispatch pipeline.

**Layer 5: Idempotency**
- Every event has a unique `eventId`.
- Include `eventId` in the webhook payload.
- Apps SHOULD deduplicate by `eventId` (documented in Monday.com's API docs).
- On the platform side: track delivered `dispatchId` in Redis (TTL 24h) to avoid re-dispatching on consumer restarts.

**Layer 6: Ordering guarantee**
- Kafka partitioning by `board_id` ensures per-board event ordering.
- Webhook dispatch topic partitioned by `app_id` ensures per-app ordering.
- If strict ordering matters: dispatch sequentially per app. If not: parallel dispatch with sequence numbers so the app can reorder.

### Step 6: Security

- **HMAC signature**: Every webhook POST includes `X-Monday-Signature: HMAC-SHA256(payload, app_secret)`. App verifies to ensure authenticity.
- **URL validation**: On subscription registration, verify the webhook URL is reachable and returns a challenge response (like Slack's URL verification).
- **Mutual TLS**: Optional for enterprise apps.
- **Payload filtering**: Never send data the app doesn't have permission to see. Check app OAuth scopes against event payload fields.
- **Rate limiting**: Per-app webhook delivery rate (e.g., 100/second) to prevent abuse and protect app endpoints.

---

## Key Components to Draw

1. **End-to-end event flow**: User action -> Board Service -> Kafka (board-events) -> Trigger Matcher -> Kafka (webhook-dispatch) -> Webhook Dispatcher -> External App
2. **Retry & DLQ flow**: Dispatcher failure -> Retry topic (with delay) -> re-dispatch -> after N failures -> DLQ
3. **Circuit breaker state machine**: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
4. **Subscription registry data model**: Apps, subscriptions, filters
5. **Fan-out diagram**: One board event matches 5 app subscriptions, producing 5 webhook dispatch messages

---

## Deep Dive Areas (Where Interviewer Probes)

### 1. "What if an app's webhook takes 30 seconds to respond?"
- Set a hard timeout (5 seconds). Treat timeout as failure, trigger retry.
- Why 5 seconds: dispatch threads/connections are a finite resource. One slow app shouldn't consume them.
- Use async HTTP client (non-blocking I/O in Node.js) so one slow call doesn't block others.
- Consider: offer async webhook pattern where app responds 200 immediately and processes in background. Monday.com's webhook docs actually recommend this.

### 2. "How do you prevent one noisy board from overwhelming apps?"
- **Rate limiting at the event level**: If a board generates 1000 events/second (bulk import), batch/aggregate them.
- **Batched webhook delivery**: Instead of 1000 individual webhooks, bundle events into batches of 50, delivered every 1 second.
- **Backpressure from Kafka**: If the dispatcher can't keep up, Kafka naturally applies backpressure (consumer lag grows, but events are durable).

### 3. "How does this scale to millions of subscriptions?"
- Trigger Matcher maintains an **in-memory index** of subscriptions, refreshed periodically from the DB.
- Index structure: `Map<accountId, Map<boardId, Map<eventType, List<Subscription>>>>` -- O(1) lookup.
- For accounts with wildcard board subscriptions (all boards), maintain a separate index.
- Shard Trigger Matcher by account_id or board_id ranges for horizontal scaling.

### 4. "What about event schema evolution?"
- Webhook payloads must be versioned. Include `"apiVersion": "2026-03"` in every payload.
- Apps declare which API version they target. Platform transforms events to match the app's expected schema.
- Never remove fields in a minor version. Only add.
- Breaking changes require a new major API version with migration period.

### 5. "How do you monitor this system?"
- **Metrics**: events_produced/s, events_matched/s, webhooks_dispatched/s, webhook_success_rate, webhook_latency_p99, retry_rate, dlq_size, circuit_breaker_trips
- **Per-app dashboard**: Each app developer sees their webhook success rate, average latency, recent failures.
- **Alerting**: Alert Monday.com ops if global dispatch failure rate > 5%. Alert app developers if their failure rate > 20%.
- **Distributed tracing**: Each event carries a traceId from origination through dispatch, enabling end-to-end debugging.

---

## Sample Answer Outline (Strong Skeleton)

> "I'd build this as a three-stage pipeline: event generation, trigger matching, and webhook dispatch, all connected via Kafka.
>
> **Event generation** is already part of Monday.com's architecture -- every board mutation publishes an event to Kafka. We tap into this existing stream.
>
> **Trigger matching**: A consumer reads board events, looks up which app subscriptions match (by account, board, event type, and filter predicates), and produces a webhook dispatch message for each match. Subscriptions are cached in memory for fast lookup.
>
> **Webhook dispatch**: A separate consumer group handles HTTP delivery to app endpoints. Each dispatch is signed with HMAC for security.
>
> **Failure tolerance is the critical part**. Five layers:
> 1. Kafka durability -- events survive consumer crashes.
> 2. Exponential backoff retries -- 7 attempts over 24 hours using a delay queue.
> 3. Dead letter queue -- after all retries, events go to DLQ for manual replay.
> 4. Circuit breaker per app -- if an endpoint fails consecutively, stop sending and probe periodically. This protects the dispatch pipeline from one bad app.
> 5. Idempotency keys -- every event has a unique ID so apps can deduplicate.
>
> **Separation into two Kafka topics** (board-events and webhook-dispatch) is important because it decouples the rate of user actions from the rate of webhook delivery, and allows independent scaling of matchers and dispatchers.
>
> For security: HMAC signatures on every webhook, URL verification on registration, OAuth scope filtering on payloads, and per-app rate limits."

---

## Common Mistakes

| Mistake | Why It's Bad | What to Do Instead |
|---------|-------------|-------------------|
| Calling webhooks synchronously from the mutation path | Blocks user's action on external app latency | Fully async via Kafka -- user action returns immediately |
| No retry strategy | One transient failure = permanently lost event | Exponential backoff with 7 attempts over 24 hours |
| Retrying without a circuit breaker | A dead app endpoint wastes resources forever | Circuit breaker stops retries, probes periodically |
| No idempotency mechanism | App processes the same event multiple times | Include unique eventId, document deduplication for app developers |
| Single Kafka topic for everything | Can't scale matcher and dispatcher independently | Separate topics: board-events -> trigger matching -> webhook-dispatch |
| Ignoring webhook security | Man-in-the-middle, spoofing attacks | HMAC signatures, URL verification, TLS |
| Not considering event ordering | App receives "deleted" before "created" | Partition by board_id for ordering; include sequence numbers |
| Designing without thinking about noisy neighbors | One hyperactive board overwhelms all apps | Batching, rate limiting, per-board backpressure |

---

## Connection to Monday.com's Actual Architecture

- **Monday.com Apps Framework**: Monday.com has a real app marketplace with 200+ integrations. They support trigger-based automations where board actions invoke app logic. This question directly models that system.
- **Webhooks in Monday.com API**: Their public API documentation describes webhooks that fire on board events (item created, column changed, etc.) -- exactly what this exercise designs.
- **Kafka backbone**: Monday.com's engineering uses Kafka as the central event bus. Board events flowing through Kafka is their actual architecture.
- **Automations & Integrations**: Monday.com's "Automations" feature (when X happens, do Y) is built on this same event-driven pattern. Some automations trigger internal actions; others trigger external apps.
- **Failure handling**: Monday.com's developer docs mention webhook retry policies and the importance of responding quickly (< 5 seconds). This aligns with the circuit breaker and timeout design.
- **SQS/SNS usage**: Monday.com reportedly uses AWS SQS for delayed/retry queues and SNS for fan-out -- alternatives to using Kafka for the retry mechanism. Mentioning both shows breadth.
- **mondayDB pattern**: The event originates from the same write path that updates mondayDB (Redis + Cassandra). The Kafka publish is part of that write path, ensuring events are generated reliably.
- **Multi-region considerations**: Events generated in one region may need to trigger apps hosted in another. Cross-region Kafka replication (MirrorMaker) or region-local dispatch with global subscription registry.
- **Scale reference**: Monday.com has 225K+ customers, many with automations. The system must handle millions of events/day with sub-minute delivery latency for the vast majority.
