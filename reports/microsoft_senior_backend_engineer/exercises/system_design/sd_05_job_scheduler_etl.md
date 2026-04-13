# SD 05: Design a Cloud Job Scheduler / ETL Pipeline

## The Prompt

> "Design a cloud-based job scheduler that supports one-time and recurring jobs, handles dependencies between jobs (DAGs), and can process ETL pipelines at scale."

**Reported in:** Microsoft Senior L63 onsite.
**Sources:** [Roundz Substack - L63 Hyderabad](https://roundz.substack.com/p/microsoft-senior-software-engineer-63), [Prachub - Feb 2026](https://prachub.com/companies/microsoft/positions/software-engineer)

---

## Time Budget (45 minutes)

| Phase | Time | What to Cover |
|-------|------|---------------|
| Clarifying Questions | 3-5 min | Job types, scale, reliability, SLAs |
| High-Level Design | 10 min | Core components, job lifecycle, storage |
| Detailed Design | 15-20 min | DAG execution, failure handling, scaling |
| Deep Dive | 10-15 min | Exactly-once, priority, monitoring |
| Wrap-up | 2-3 min | Tradeoffs |

---

## Clarifying Questions to Ask

1. **Job types:** One-time, recurring (cron), event-triggered? All three?
2. **Scale:** How many jobs per day? How many concurrent jobs? (Target: millions/day, 100K concurrent)
3. **Dependencies:** DAG support? How deep can the dependency chain be?
4. **SLAs:** Maximum acceptable scheduling delay? (Target: < 1 second for on-time scheduling)
5. **Failure handling:** Retry policies? Dead letter queue? Manual intervention?
6. **Job duration:** Seconds to hours? Or long-running (days)?
7. **Multi-tenant:** Shared scheduler across teams/orgs, or dedicated?

---

## Step-by-Step Framework

### 1. API Design

```
// Job management
CreateJob(name, schedule, config, dependencies[]) -> jobId
UpdateJob(jobId, schedule, config) -> success
DeleteJob(jobId) -> success
GetJobStatus(jobId) -> {status, lastRun, nextRun, history}

// Execution
TriggerJob(jobId) -> executionId
CancelExecution(executionId) -> success
GetExecutionLogs(executionId) -> [LogEntry]
```

### 2. High-Level Architecture

```
┌───────────┐     ┌──────────────┐     ┌─────────────────┐
│  API      │────>│  Scheduler   │────>│  Job Queue      │
│  Service  │     │  Service     │     │  (Service Bus)  │
└───────────┘     └──────┬───────┘     └───────┬─────────┘
                         │                      │
                  ┌──────v───────┐       ┌──────v─────────┐
                  │  Job Store   │       │  Worker Pool   │
                  │  (Cosmos DB) │       │  (AKS)         │
                  └──────────────┘       └───────┬────────┘
                                                  │
                                          ┌───────v────────┐
                                          │  Result Store  │
                                          │  + Audit Log   │
                                          └────────────────┘
```

### 3. Key Components

#### Scheduler Service
- **Cron evaluator:** Parses cron expressions, determines next fire time
- **Timer wheel:** Efficient data structure for managing millions of scheduled events
- Runs leader-elected (single active scheduler for consistency) with hot standby
- Every second: scan for due jobs, enqueue to Job Queue

#### Job Queue (Azure Service Bus)
- Priority queues: critical, high, normal, low
- Message lock: 5-minute visibility timeout during processing
- Dead letter queue: after N retries, move to DLQ
- Partitioned by tenant/namespace for isolation

#### Worker Pool (AKS)
- Stateless workers pull jobs from queue
- Auto-scale based on queue depth (KEDA — Kubernetes Event-Driven Autoscaler)
- Each worker: dequeue → execute → report result → ACK message
- Resource isolation: jobs run in containers with CPU/memory limits

#### Job Store (Cosmos DB)
- **Partition key:** tenantId
- Stores: job definition, schedule, dependency graph, execution history
- Schema:
```json
{
  "jobId": "job-123",
  "tenantId": "team-abc",
  "name": "daily-user-export",
  "schedule": "0 2 * * *",
  "config": { "source": "users_db", "dest": "data_lake", "format": "parquet" },
  "dependencies": ["job-100", "job-101"],
  "status": "active",
  "lastExecution": { "id": "exec-456", "status": "success", "duration": 120 },
  "retryPolicy": { "maxRetries": 3, "backoff": "exponential" }
}
```

### 4. DAG Execution Engine

```
When job J is triggered:
  1. Resolve dependency graph (BFS from J)
  2. Find all root nodes (no unmet dependencies)
  3. Enqueue root nodes to Job Queue
  4. On job completion:
     a. Update execution status in Job Store
     b. Check all downstream jobs
     c. For each downstream: if ALL dependencies complete → enqueue
  5. If any job fails: mark downstream as BLOCKED, notify
```

- **Cycle detection:** Validate DAG on job creation (topological sort — connects to Exercise 07!)
- **Parallel execution:** Independent branches of the DAG run concurrently
- **Partial retry:** Retry only failed branch, not entire DAG

### 5. Failure Handling

- **Job failure:** Retry with exponential backoff (1s, 2s, 4s, 8s...). Max 3 retries default.
- **Worker crash:** Message lock expires after 5 min → message becomes visible again → another worker picks up.
- **Scheduler failure:** Leader election via Cosmos DB lease. Standby promotes within seconds.
- **Poison messages:** After max retries, move to DLQ. Alert operations team.
- **Idempotency:** Each execution has unique executionId. Workers must be idempotent.

---

## Deep Dive Areas

### Exactly-Once Execution
- **Challenge:** Worker crashes after completing job but before ACK-ing message
- **Solution:** Worker writes completion record to Job Store with executionId. On re-delivery, check if executionId already completed → skip.
- **Two-phase:** (1) Start execution record, (2) execute, (3) complete execution record, (4) ACK message

### Priority & Fairness
- Multiple priority queues (critical > high > normal > low)
- Workers poll highest-priority queue first
- Tenant fairness: rate limit jobs per tenant to prevent noisy neighbor
- Reserved capacity: critical jobs have dedicated worker pool

### ETL-Specific Patterns
- **Incremental loads:** Track watermark (last processed timestamp) per source
- **Schema evolution:** Handle new columns, type changes gracefully
- **Data validation:** Post-load row count verification, checksum validation
- **Partitioned writes:** Write output data partitioned by date/tenant for efficient queries

### Monitoring & Observability
- **Metrics:** Job success/failure rate, queue depth, execution latency, worker utilization
- **Alerts:** Job SLA breach, failure rate spike, queue depth > threshold
- **Execution timeline:** Visual DAG showing completed/running/blocked/failed nodes
- **Azure Monitor** integration with custom dashboards

---

## Sample Answer Outline

> "I'd build a scheduler service with leader election that evaluates cron schedules every second and enqueues due jobs to Azure Service Bus priority queues. Stateless workers on AKS pull jobs, execute in containers, and report results. DAG dependencies are resolved using topological ordering — independent branches run in parallel, downstream jobs trigger when all parents complete. Job state lives in Cosmos DB partitioned by tenant. For reliability: message locks handle worker crashes, idempotent execution prevents duplicates, and exponential backoff handles transient failures. Auto-scaling via KEDA keeps worker pool right-sized to queue depth."

---

## Common Mistakes

1. **No DAG support** — simple queue-based scheduler can't handle job dependencies
2. **Single scheduler, no HA** — scheduler crash means no jobs run
3. **No idempotency** — network failures cause duplicate executions
4. **No priority** — critical ETL jobs stuck behind low-priority batch jobs
5. **No tenant isolation** — one team's runaway job starves others
6. **No monitoring** — jobs silently failing with no alerting

---

## Connection to Microsoft's Architecture

- **Azure Data Factory:** Microsoft's managed ETL/ELT service. Uses a similar pipeline + activity model with dependency graphs.
- **Azure Logic Apps:** Low-code workflow engine with triggers and actions — related scheduler pattern.
- **Azure Functions with Durable Functions:** Serverless orchestration supporting fan-out/fan-in, chaining, and human interaction patterns.
- **Azure Batch:** Manages large-scale parallel and HPC workloads — the worker pool concept at extreme scale.
- **Engineering@Microsoft blog:** "Managed DevOps Pools — The Origin Story" describes how Microsoft schedules and manages compute resources for build/release pipelines.
