# SD 01: Design a Distributed Cache System

## The Prompt

> "Design a distributed caching system similar to Redis or Memcached that can be used across Microsoft's services. It should support high throughput, low latency, and be highly available."

**Reported in:** Microsoft L63-64 onsite interviews.
**Sources:** [HelloInterview L63-64 Guide](https://www.hellointerview.com/guides/microsoft/senior), [InterviewQuery](https://www.interviewquery.com/interview-guides/microsoft-software-engineer)

---

## Time Budget (45 minutes)

| Phase | Time | What to Cover |
|-------|------|---------------|
| Clarifying Questions | 3-5 min | Scope, scale, consistency requirements |
| High-Level Design | 10 min | Core components, data flow, API |
| Detailed Design | 15-20 min | Partitioning, replication, eviction, consistency |
| Deep Dive | 10-15 min | Failure handling, hot keys, monitoring |
| Wrap-up | 2-3 min | Tradeoffs summary, what you'd improve |

---

## Clarifying Questions to Ask

1. **Scale:** How many requests per second? How much data total? (Target: millions RPS, terabytes)
2. **Latency:** What's the P99 latency target? (Target: < 1ms for reads, < 5ms for writes)
3. **Consistency:** Strong consistency or eventual? Can we tolerate stale reads?
4. **Data model:** Key-value only? Or also support data structures (lists, sets, sorted sets)?
5. **Eviction:** What happens when cache is full? LRU? TTL-based?
6. **Durability:** Is persistence required or is this pure in-memory?
7. **Multi-region:** Single region or globally distributed?

---

## Step-by-Step Framework

### 1. API Design

```
GET(key) -> value | null
PUT(key, value, ttl?) -> success
DELETE(key) -> success
```

### 2. High-Level Architecture

```
┌──────────┐     ┌─────────────────┐     ┌───────────────────┐
│  Clients │────>│   API Gateway / │────>│  Cache Cluster     │
│          │     │   Load Balancer │     │  ┌─────────────┐   │
└──────────┘     └─────────────────┘     │  │ Partition 0  │   │
                                          │  │ (primary)    │   │
                                          │  │   + replicas │   │
                                          │  ├─────────────┤   │
                                          │  │ Partition 1  │   │
                                          │  │ (primary)    │   │
                                          │  │   + replicas │   │
                                          │  ├─────────────┤   │
                                          │  │ ...          │   │
                                          │  └─────────────┘   │
                                          └───────────────────┘
```

### 3. Key Components

- **Client Library:** Hashes keys to determine partition. Maintains connection pool.
- **Consistent Hashing Ring:** Maps keys to partitions. Virtual nodes for even distribution.
- **Cache Nodes:** In-memory storage (HashMap + DLL for LRU). Each partition has primary + replicas.
- **Cluster Manager:** Monitors node health, handles rebalancing, maintains ring topology.
- **Configuration Service:** Stores cluster metadata (ZooKeeper / Azure Service Fabric equivalent).

### 4. Partitioning (Sharding)

- **Consistent hashing** with virtual nodes (100-200 per physical node)
- Key -> hash -> position on ring -> assigned node
- On node failure, only keys from that node need redistribution
- **Why not modular hashing?** Adding/removing nodes would rehash nearly all keys

### 5. Replication

- Each partition has 1 primary + 2 replicas (configurable)
- **Sync replication** for strong consistency: write returns after all replicas ACK
- **Async replication** for high throughput: write returns after primary ACK, replicas catch up
- Replicas placed in different failure domains (racks, availability zones)

### 6. Eviction Policies

- **LRU** (default): Least Recently Used — HashMap + Doubly Linked List (connects to Exercise 01!)
- **LFU:** Least Frequently Used — for stable access patterns
- **TTL-based:** Active expiration (background scanner) + lazy expiration (check on access)
- **Memory threshold:** Trigger eviction when node reaches 80% capacity

### 7. Consistency Model

- **Read-your-writes:** Client reads from the same partition it wrote to
- **Quorum reads/writes:** R + W > N ensures consistency (e.g., R=2, W=2, N=3)
- **Azure Cosmos DB parallel:** Offers 5 consistency levels (strong, bounded staleness, session, consistent prefix, eventual)

---

## Deep Dive Areas

### Hot Key Problem
- **Detection:** Monitor key access frequency per node
- **Mitigation:** Replicate hot keys to all nodes; client-side caching for hottest keys
- **Azure approach:** Azure Cache for Redis uses clustering + read replicas for hot key distribution

### Cache Invalidation
- **TTL:** Simple but may serve stale data within TTL window
- **Write-through:** Update cache on every DB write (consistent but slower)
- **Write-behind:** Batch cache updates asynchronously (faster but risk of data loss)
- **Event-driven:** Pub/Sub notification on data change (Azure Service Bus integration)

### Failure Handling
- **Node failure:** Cluster manager detects via heartbeat (5s timeout). Promotes replica to primary. Rerouts traffic.
- **Network partition:** Split-brain prevention using quorum. Prefer availability (AP) or consistency (CP) based on SLA.
- **Cascading failure:** Circuit breaker pattern. Fall back to database on cache unavailability.

### Monitoring & Observability
- **Metrics:** Hit rate, miss rate, latency (P50/P99), memory usage, eviction rate
- **Alerts:** Cache hit rate drop, latency spike, node unreachable
- **Azure Monitor** integration for dashboards and alerting

---

## Sample Answer Outline

> "I'd design a distributed cache using consistent hashing for partitioning, with primary-replica pairs for availability. Clients use a thin library that hashes keys and routes directly to the owning partition. Each node stores data in-memory with LRU eviction. For Microsoft's use case, I'd integrate with Azure Service Fabric for cluster management and offer configurable consistency levels — session consistency by default (matching Cosmos DB's model), with strong consistency available for critical paths. Cache invalidation uses event-driven Pub/Sub via Azure Service Bus. I'd add circuit breakers so services gracefully degrade to database reads when cache is unavailable."

---

## Common Mistakes

1. **No partitioning strategy** — saying "just use Redis" without explaining distribution
2. **Ignoring hot keys** — a single hot key can overwhelm one node
3. **Missing consistency discussion** — not discussing tradeoffs between consistency and availability
4. **No eviction policy** — infinite memory assumption
5. **No failure handling** — what happens when a node dies?
6. **Forgetting client-side caching** — two-tier caching significantly reduces load

---

## Connection to Microsoft's Architecture

- **Azure Cache for Redis:** Microsoft's managed distributed cache service. Uses clustering for horizontal scaling, geo-replication for multi-region, and Redis Sentinel for HA.
- **Azure Cosmos DB caching layer:** Session consistency with integrated cache provides read-your-writes guarantees.
- **Microsoft internal:** The Substrate infrastructure (Office 365 backend) uses multi-tier caching — in-process cache -> distributed cache -> database.
- **Engineering@Microsoft blog:** References safe deployment practices — new cache node deployments use canary rollouts to prevent cache stampede.
