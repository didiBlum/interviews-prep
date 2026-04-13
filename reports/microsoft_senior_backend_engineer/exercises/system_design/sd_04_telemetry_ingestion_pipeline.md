# SD 04: Design a Telemetry Ingestion Pipeline (Xbox-scale)

## The Prompt

> "Design a telemetry ingestion pipeline for Xbox that can handle millions of concurrent users sending gameplay events, performance metrics, and crash reports in real-time. The system should support real-time dashboards, alerting, and batch analytics."

**Reported in:** Microsoft Senior interviews — product-specific at scale.
**Sources:** [InterviewQuery](https://www.interviewquery.com/interview-guides/microsoft-software-engineer)

---

## Time Budget (45 minutes)

| Phase | Time | What to Cover |
|-------|------|---------------|
| Clarifying Questions | 3-5 min | Event types, scale, latency, retention |
| High-Level Design | 10 min | Ingestion, processing, storage layers |
| Detailed Design | 15-20 min | Partitioning, processing pipeline, storage tiers |
| Deep Dive | 10-15 min | Backpressure, exactly-once, cost optimization |
| Wrap-up | 2-3 min | Tradeoffs, evolution path |

---

## Clarifying Questions to Ask

1. **Scale:** How many concurrent users? Events per second? (Target: 50M concurrent, ~10M events/sec)
2. **Event types:** What kinds of events? (Gameplay, crashes, performance, purchases, social)
3. **Latency:** Real-time dashboard latency? (Target: < 30 seconds for real-time, hours for batch)
4. **Retention:** How long to keep data? (Hot: 7 days, warm: 90 days, cold: 7 years)
5. **Processing:** What computations? Aggregations? Anomaly detection? Sessionization?
6. **Consumers:** Who reads the data? Dashboards? ML models? Compliance? Game studios?
7. **Reliability:** Can we lose events? (Crash reports: no. Performance metrics: best-effort OK)

---

## Step-by-Step Framework

### 1. Event Schema

```json
{
  "eventId": "uuid",
  "eventType": "gameplay|crash|perf|purchase",
  "userId": "string",
  "deviceId": "string",
  "gameTitle": "string",
  "timestamp": "ISO-8601",
  "payload": { /* type-specific data */ },
  "metadata": {
    "sdkVersion": "string",
    "osVersion": "string",
    "region": "string"
  }
}
```

### 2. High-Level Architecture

```
┌──────────────┐     ┌────────────────┐     ┌─────────────────┐
│  Xbox/PC     │────>│  Ingestion     │────>│  Event Hubs     │
│  Clients     │     │  Gateway       │     │  (Kafka-like)   │
│  (50M+)      │     │  (Regional)    │     │                 │
└──────────────┘     └────────────────┘     └───────┬─────────┘
                                                     │
                                    ┌────────────────┼────────────────┐
                                    │                │                │
                              ┌─────v──────┐  ┌─────v──────┐  ┌─────v──────┐
                              │  Stream    │  │  Stream    │  │  Batch     │
                              │  Processor │  │  Processor │  │  Loader    │
                              │  (Real-    │  │  (Anomaly  │  │  (to Data  │
                              │   time     │  │   Detect)  │  │   Lake)    │
                              │   Agg)     │  │            │  │            │
                              └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
                                    │                │                │
                              ┌─────v──────┐  ┌─────v──────┐  ┌─────v──────┐
                              │  Redis     │  │  Alerting  │  │  Data Lake │
                              │  (Hot      │  │  Service   │  │  (Cold     │
                              │   Store)   │  │            │  │   Store)   │
                              └─────┬──────┘  └────────────┘  └─────┬──────┘
                                    │                                │
                              ┌─────v──────────────────────────────v──────┐
                              │          Dashboard / Analytics            │
                              │          (Azure Data Explorer / Grafana)  │
                              └──────────────────────────────────────────┘
```

### 3. Key Components

#### Ingestion Gateway (Regional)
- HTTP/2 endpoint accepting batched events
- Regional deployment (US West, US East, EU, Asia) — events hit nearest region
- Schema validation, enrichment (add server timestamp, geo info)
- Client SDK batches events (100 events or 10s, whichever comes first)
- Backpressure: HTTP 429 + client-side queue with exponential backoff

#### Event Hubs (Azure)
- **Partitions:** 256+ partitions for parallelism
- **Partition key:** gameTitle (keeps game events together for sessionization)
- **Retention:** 7 days (allows replay for recovery)
- **Throughput:** Each partition handles ~1MB/s ingress → 256 partitions ≈ 256 MB/s
- **Consumer groups:** Separate for real-time processing, anomaly detection, batch loading

#### Stream Processors
- **Real-time aggregation:** 1-minute windows — active users, events/sec, error rates
- **Anomaly detection:** Rolling statistics — alert on crash rate spike, latency anomaly
- **Sessionization:** Group events by (userId, gameTitle, timeWindow) into game sessions
- Built on Azure Stream Analytics or Apache Flink on AKS

#### Storage Tiers
- **Hot (0-7 days):** Redis + Azure Data Explorer — real-time queries, dashboards
- **Warm (7-90 days):** Azure Data Explorer — ad-hoc analytics, incident investigation
- **Cold (90 days - 7 years):** Azure Data Lake (Parquet format) — batch analytics, ML training, compliance

---

## Deep Dive Areas

### Backpressure & Reliability
- **Client-side:** SDK maintains local queue (max 10K events). On connectivity loss, writes to local disk. On reconnect, drains queue.
- **Gateway → Event Hubs:** Async producer with retry. If Event Hubs is saturated, gateway returns 429 to clients.
- **Stream processor lag:** Monitor consumer lag metric. Scale out processors when lag > threshold.
- **Dead letter queue:** Events that fail processing after 3 retries go to DLQ for manual investigation.

### Exactly-Once Processing
- **Event Hubs → Stream processor:** At-least-once delivery. Processors must be idempotent.
- **Idempotency key:** eventId (UUID generated by client SDK)
- **Deduplication window:** 5-minute window in Redis bloom filter. Events older than 5 min assumed unique.
- **Write-ahead log:** Processors checkpoint their offset to Azure Blob Storage every 30s.

### Cost Optimization (Microsoft-specific)
- **Compression:** gzip events at client SDK level (60-80% size reduction)
- **Batching:** Client SDK batches events — reduces HTTP overhead from 1 request/event to 1 request/100 events
- **Tiered storage:** Auto-move from hot (expensive, fast) to cold (cheap, slow) based on age
- **Sampling:** For non-critical performance metrics, sample 10% at client SDK level during peak hours
- **Reserved capacity:** Azure Event Hubs and Data Explorer reserved instances for base load

### Compliance & Privacy
- **GDPR/COPPA:** User deletion requests must propagate through all storage tiers
- **PII scrubbing:** Stream processor strips/hashes PII before writing to Data Lake
- **Data residency:** EU user events stay in EU region (separate Event Hub + storage)
- **Audit trail:** All data access logged

---

## Sample Answer Outline

> "I'd design a three-layer pipeline: regional ingestion gateways → Azure Event Hubs (partitioned by gameTitle) → parallel stream processors for real-time aggregation, anomaly detection, and batch loading to Data Lake. The client SDK batches and compresses events, with local queuing for offline resilience. Storage uses three tiers: Redis for real-time dashboards (7 days), Azure Data Explorer for ad-hoc analytics (90 days), and Data Lake in Parquet for long-term analytics and ML. For Xbox's scale of 50M concurrent users, I'd use 256 Event Hub partitions and auto-scale stream processors based on consumer lag. Cost optimization through client-side batching, compression, and tiered storage keeps costs manageable at this scale."

---

## Common Mistakes

1. **No batching at client** — one HTTP request per event at 10M events/sec is infeasible
2. **Single region** — Xbox is global; latency matters for real-time data
3. **No backpressure** — what happens during game launches (10x traffic)?
4. **Ignoring cost** — at this scale, storage and compute costs are significant
5. **Single storage tier** — using one database for both real-time queries and 7-year retention
6. **No data governance** — GDPR, COPPA for minors, data residency

---

## Connection to Microsoft's Architecture

- **Azure Event Hubs:** Microsoft's managed Kafka-compatible event streaming platform. Used internally for Xbox telemetry, Office 365 diagnostics, and Azure monitoring.
- **Azure Data Explorer (Kusto):** Microsoft's real-time analytics database, built for telemetry workloads. Powers Azure Monitor, Application Insights, and Xbox analytics.
- **Azure Stream Analytics:** Managed stream processing. Integrates natively with Event Hubs and Data Lake.
- **PlayFab:** Microsoft's game backend platform uses a similar telemetry pipeline for game studios.
- **Engineering@Microsoft blog:** References safe deployment practices with telemetry-driven canary analysis — the same pipeline that ingests telemetry data.
