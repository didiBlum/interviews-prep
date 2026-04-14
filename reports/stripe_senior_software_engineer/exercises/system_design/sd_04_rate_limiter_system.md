# System Design: Rate Limiter (System Level)

**Source:** Stripe system design round (leetcodewizard.io, Exponent, 2025-2026)

## The Prompt

"Design a distributed rate limiting system for Stripe's API. It should handle hundreds of thousands of requests per second, support per-customer limits, and be highly available."

## Time Budget (45 minutes)

| Phase | Time | Focus |
|-------|------|-------|
| Clarify requirements | 5 min | Scale, consistency, limit types |
| High-level design | 10 min | Architecture, algorithm choice |
| Detailed design | 15 min | Storage, synchronization, failure modes |
| Deep dive | 10 min | Consistency trade-offs, multi-region |
| Q&A | 5 min | Trade-offs |

## Clarifying Questions to Ask

1. "Per-customer, per-endpoint, or global rate limits?"
2. "What happens when rate limited? 429 response? Queue the request?"
3. "Hard limit or soft limit (allow brief bursts)?"
4. "Multi-region? Do limits need to be globally enforced?"
5. "What's the total QPS across all customers?"
6. "Do we need real-time rate limit status in customer dashboards?"

## Step-by-Step Framework

### 1. Algorithm Choice

| Algorithm | Pros | Cons | Best For |
|-----------|------|------|----------|
| **Token Bucket** | Allows bursts, simple | Approximate | API rate limiting |
| **Sliding Window Log** | Exact | High memory | Low-volume, precision-needed |
| **Sliding Window Counter** | Low memory, good accuracy | Approximate at boundaries | High-volume |
| **Fixed Window** | Simplest | Boundary burst problem | Simple use cases |

**Recommendation: Token Bucket** — industry standard for API rate limiting, handles bursts naturally.

### 2. Token Bucket Implementation
- Each customer has a bucket with capacity C and refill rate R tokens/second
- Request arrives: if tokens > 0, decrement and allow; else reject (429)
- Lazy refill: on each request, compute tokens_to_add = (now - last_refill) * R

### 3. Storage: Redis

```
Key: rate_limit:{customer_id}:{endpoint}
Value: {tokens: float, last_refill: timestamp}
```

- Atomic operations via Redis Lua script (EVAL)
- TTL on keys: auto-expire inactive customers

```lua
-- Lua script for atomic token bucket
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(data[1]) or capacity
local last_refill = tonumber(data[2]) or now

-- Refill
local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * refill_rate)

-- Check
if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    return 1  -- allowed
else
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    return 0  -- rejected
end
```

### 4. Architecture

```
[Client] → [API Gateway / Load Balancer]
                    ↓
            [Rate Limiter Middleware]
                    ↓
            [Redis Cluster] (shared state)
                    ↓
            [Backend Service] (if allowed)
```

### 5. Limit Configuration

```yaml
default:
  requests_per_second: 100
  burst_capacity: 200

tiers:
  starter:
    requests_per_second: 25
  growth:
    requests_per_second: 100
  enterprise:
    requests_per_second: 1000

per_endpoint:
  /v1/charges:
    requests_per_second: 50
  /v1/customers:
    requests_per_second: 200
```

### 6. Response Headers

```
HTTP/1.1 429 Too Many Requests
Retry-After: 1
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1618884480
```

## Key Components to Draw

```
[Clients] → [API Gateway]
                 ↓
         [Rate Limit Check] ←→ [Redis Cluster]
                 ↓                    ↑
         [Backend Services]    [Config Service]
                               (tier limits, overrides)
```

## Deep Dive Areas

### Multi-Region Consistency
- **Option 1: Global Redis** — single source of truth, but adds cross-region latency
- **Option 2: Regional Redis** — fast but limits are per-region (customer gets 100 RPS * N regions)
- **Option 3: Hybrid** — regional enforcement with periodic global sync
- **Stripe's likely approach:** Regional with slightly relaxed limits (accept some over-counting for lower latency)

### Redis Failure
- **Redis down:** Fail open (allow all requests) or fail closed (block all)?
- **Recommendation:** Fail open with degraded monitoring. Blocking all API requests is worse than brief over-limit.
- **Mitigation:** Redis Cluster with replicas, automatic failover. Local in-memory fallback for short outages.

### Hot Customers
- One customer sending 100K RPS hits a single Redis key repeatedly
- **Solution:** Shard rate limit counters across multiple Redis keys with local aggregation
- Or: local per-worker token bucket with periodic sync to Redis

## Sample Answer Outline

> "I'd design a token bucket rate limiter backed by Redis, integrated as middleware in the API gateway.
>
> Each customer has a token bucket stored in Redis with capacity (burst) and refill rate (sustained RPS). On each request, a Lua script atomically checks and decrements tokens, avoiding race conditions.
>
> Limits are configured per tier (starter/growth/enterprise) and optionally per endpoint. The API gateway reads the customer's tier from an in-memory cache and applies the appropriate limits.
>
> For multi-region, I'd use regional Redis clusters with slightly relaxed limits to avoid cross-region latency. Periodic sync ensures global limits aren't exceeded by more than a small margin.
>
> On Redis failure, the system fails open — allowing requests through with logging. This is safer than blocking all API traffic. Response headers include standard rate limit information for client-side retry logic."

## Common Mistakes

1. **Not using atomic operations** — Race conditions between check and decrement. Always use Lua scripts or MULTI/EXEC.
2. **Ignoring fail-open vs. fail-closed** — Must discuss explicitly. Stripe would fail open.
3. **Fixed window only** — Shows limited knowledge. Discuss token bucket or sliding window.
4. **No per-customer configuration** — Real systems need tiered limits.
5. **Ignoring response headers** — Stripe's actual API returns rate limit headers. Show you know the UX.

## Connection to Stripe's Actual Architecture

- Stripe returns `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers
- Default rate limit: 100 read requests/second, 100 write requests/second (test mode: 25)
- Per-endpoint limits exist (e.g., search endpoints have lower limits)
- 429 responses include `Retry-After` header
- Stripe uses Redis extensively across their infrastructure
- Rate limiting is critical for protecting their payment processing pipeline from abuse
