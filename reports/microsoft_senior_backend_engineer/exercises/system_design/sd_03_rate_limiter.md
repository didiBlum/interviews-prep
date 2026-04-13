# SD 03: Design a Distributed Rate Limiter

## The Prompt

> "Design a distributed rate limiting service that can be used across Microsoft's API Gateway to protect backend services. It should handle millions of requests per second with minimal latency impact."

**Reported in:** Microsoft L63-64 onsite interviews.
**Sources:** [HelloInterview L63-64 Guide](https://www.hellointerview.com/guides/microsoft/senior), [CodingInterview.com](https://www.codinginterview.com/guide/microsoft-interview-questions/), [GeeksforGeeks](https://www.geeksforgeeks.org/system-design/microsoft-system-design-interview-questions/)

---

## Time Budget (45 minutes)

| Phase | Time | What to Cover |
|-------|------|---------------|
| Clarifying Questions | 3-5 min | Scope, granularity, consistency |
| High-Level Design | 10 min | Core components, algorithms, data flow |
| Detailed Design | 15-20 min | Algorithm deep dive, distributed coordination |
| Deep Dive | 10-15 min | Edge cases, monitoring, failure modes |
| Wrap-up | 2-3 min | Tradeoffs summary |

---

## Clarifying Questions to Ask

1. **Granularity:** Rate limit per user? Per API key? Per IP? Per endpoint?
2. **Scale:** How many unique keys? How many requests per second? (Target: 10M+ RPS across cluster)
3. **Accuracy:** Is approximate rate limiting acceptable? (Slight over/under-counting OK?)
4. **Latency budget:** How much latency can the rate limiter add? (Target: < 1ms P99)
5. **Rules:** Fixed window? Sliding window? Token bucket? Configurable per API?
6. **Response:** What happens when rate limited? HTTP 429 with Retry-After header?
7. **Multi-region:** Do rate limits apply globally or per region?

---

## Step-by-Step Framework

### 1. API Design

```
// Internal API called by API Gateway on every request
CheckRateLimit(key, rule) -> { allowed: boolean, remaining: int, retryAfter: seconds }

// Management API for configuring rules
CreateRule(name, limit, window, granularity) -> ruleId
UpdateRule(ruleId, limit, window) -> success
```

### 2. Rate Limiting Algorithms

#### Token Bucket (Recommended)
- Bucket holds `maxTokens` tokens, refills at `refillRate` tokens/sec
- Each request consumes 1 token; rejected if bucket empty
- **Pros:** Allows bursts up to bucket size, smooth long-term rate
- **Cons:** Requires per-key state

#### Sliding Window Log
- Store timestamp of each request in a sorted set
- Count requests in [now - window, now]; reject if >= limit
- **Pros:** Most accurate
- **Cons:** Memory-heavy (stores every timestamp)

#### Sliding Window Counter (Best tradeoff)
- Combine current window count + weighted previous window count
- `count = currentWindowCount + previousWindowCount * overlapRatio`
- **Pros:** Low memory, good accuracy
- **Cons:** Approximate

### 3. High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌──────────────────┐
│  Client   │────>│  API Gateway │────>│  Rate Limiter    │
│           │     │              │     │  Service         │
└──────────┘     └──────┬───────┘     └────────┬─────────┘
                        │                       │
                        │ if allowed            │ counters
                        v                       v
                 ┌──────────────┐     ┌──────────────────┐
                 │  Backend     │     │  Redis Cluster   │
                 │  Services    │     │  (per-region)    │
                 └──────────────┘     └──────────────────┘
                                              │
                                       ┌──────────────┐
                                       │  Rules Store  │
                                       │  (Cosmos DB)  │
                                       └──────────────┘
```

### 4. Detailed Design

#### Storage: Redis
- Key: `ratelimit:{userId}:{endpoint}:{windowId}`
- Value: counter (integer)
- TTL: window size + buffer (auto-cleanup)
- **Why Redis?** In-memory, atomic INCR, built-in TTL, sub-millisecond latency

#### Token Bucket Implementation in Redis
```
-- Lua script (atomic execution on Redis)
local key = KEYS[1]
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1]) or max_tokens
local last_refill = tonumber(bucket[2]) or now

-- Refill tokens
local elapsed = now - last_refill
local new_tokens = math.min(max_tokens, tokens + elapsed * refill_rate)

-- Try to consume
if new_tokens >= 1 then
    redis.call('HMSET', key, 'tokens', new_tokens - 1, 'last_refill', now)
    redis.call('EXPIRE', key, max_tokens / refill_rate * 2)
    return {1, math.floor(new_tokens - 1)}  -- allowed, remaining
else
    return {0, 0}  -- denied
end
```

#### Rules Configuration
- Stored in Cosmos DB, cached locally with 60s TTL
- Example rules:
  - Free tier: 100 requests/min per user
  - Standard: 1000 requests/min per user
  - Premium: 10000 requests/min per user
  - Global: 1M requests/min per endpoint (DDoS protection)

---

## Deep Dive Areas

### Distributed Coordination
- **Local-first:** Each API Gateway node maintains local counters
- **Sync periodically:** Every 100ms, sync local counts to Redis
- **Tradeoff:** Slightly over-counts (allows ~N * local_buffer extra requests where N = number of nodes)
- **For strict limits:** Use Redis directly on every request (adds ~1ms latency)

### Race Conditions
- **Redis Lua scripts** are atomic — no race conditions within a single Redis node
- **Multi-node Redis cluster:** Key is hashed to a single node — no cross-node races for the same key
- **Client retry storms:** Use exponential backoff with jitter in Retry-After header

### Multi-Region Rate Limiting
- **Per-region:** Simpler, each region has its own Redis cluster and independent limits
- **Global:** Need cross-region counter synchronization
  - Option A: Dedicated global Redis with higher latency (~50ms cross-region)
  - Option B: Eventual consistency — sync counts every second, tolerate slight over-limit

### Failure Handling
- **Redis down:** Fail open (allow requests) or fail closed (reject)? Typically fail open with degraded local rate limiting.
- **API Gateway restart:** Local counters lost; Redis state is source of truth
- **Clock skew:** Use Redis server time (not client time) for window calculations

---

## Sample Answer Outline

> "I'd implement a distributed rate limiter using Token Bucket algorithm stored in a Redis cluster. Each API Gateway node calls Redis with a Lua script for atomic token consumption — this adds < 1ms latency. Rules are stored in Cosmos DB and cached locally. For Microsoft's Azure API Gateway scale, I'd use per-region Redis clusters with local-first counting and periodic sync for most use cases, reserving global coordination for critical quotas. The system returns HTTP 429 with Retry-After headers. For compliance and observability, all rate limit events are logged to Azure Monitor."

---

## Common Mistakes

1. **Single Redis node** — won't handle millions of RPS; need Redis Cluster
2. **Non-atomic operations** — check-then-increment without Lua script creates race conditions
3. **No failure mode discussion** — what happens when Redis is down?
4. **Fixed window only** — creates burst-at-window-boundary problem
5. **No per-endpoint granularity** — different APIs need different limits
6. **Ignoring multi-region** — Microsoft is global; rate limits span regions

---

## Connection to Microsoft's Architecture

- **Azure API Management:** Microsoft's managed API Gateway includes built-in rate limiting with configurable policies per product/user/subscription.
- **Azure Redis Cache:** Managed Redis service used for rate limiting counters.
- **Azure Front Door:** Global load balancer with built-in WAF and rate limiting for DDoS protection.
- **Throttling patterns:** Microsoft's Azure Architecture Center documents retry patterns with exponential backoff — a key pattern for handling rate-limited responses.
