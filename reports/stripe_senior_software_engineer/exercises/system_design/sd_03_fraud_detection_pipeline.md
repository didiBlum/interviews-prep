# System Design: Fraud Detection Pipeline

**Source:** Stripe system design round (leetcodewizard.io, 2025)

## The Prompt

"Design a streaming fraud detection pipeline that evaluates transaction risk in under 1 second."

## Time Budget (45 minutes)

| Phase | Time | Focus |
|-------|------|-------|
| Clarify requirements | 5 min | Latency SLA, accuracy vs. speed, false positive tolerance |
| High-level design | 10 min | Pipeline stages, data flow |
| Detailed design | 15 min | Feature computation, model serving, rules engine |
| Deep dive | 10 min | Real-time features, model updates, monitoring |
| Q&A | 5 min | Trade-offs |

## Clarifying Questions to Ask

1. "What's the latency budget? P99 < 1 second? < 100ms?"
2. "What actions on fraud detection? Block, flag for review, allow with monitoring?"
3. "What's the acceptable false positive rate?" (blocking legitimate transactions = revenue loss)
4. "Do we need to support custom merchant-defined rules?"
5. "Real-time only, or also batch (post-transaction) analysis?"
6. "How quickly do fraud patterns change? How often do we retrain models?"

## Step-by-Step Framework

### 1. Pipeline Architecture (3 Layers)

```
Transaction → [Rules Engine] → [ML Model] → [Decision Engine] → Allow/Block/Review
                   ↑                ↑
            [Rule Store]    [Feature Store]
```

### 2. Rules Engine (Deterministic, < 10ms)
- Hard rules: block if card is on a blocklist, block known fraud BINs
- Velocity rules: > 5 transactions in 1 minute from same card
- Amount rules: transaction > $10,000 → additional verification
- Custom merchant rules: merchant-defined thresholds
- **Implementation:** In-memory rule evaluation, rules loaded from config store

### 3. Feature Computation (Real-time + Precomputed)

**Real-time features (computed per request):**
- Transaction amount, currency, merchant category code (MCC)
- Time since last transaction from this card
- Number of transactions in last 1min / 5min / 1hr / 24hr
- Geographic distance from last transaction
- Device fingerprint match

**Precomputed features (from feature store):**
- Card's historical fraud rate
- Merchant's chargeback rate
- User's account age and verification status
- Average transaction amount (rolling 30-day)

**Implementation:** Redis for real-time counters, feature store (Redis/DynamoDB) for precomputed.

### 4. ML Model Serving
- Input: feature vector (real-time + precomputed features)
- Output: fraud probability (0.0 to 1.0)
- Model: Gradient boosted trees (fast inference, interpretable)
- Serving: model loaded in-memory per worker, no network call
- Latency budget: < 5ms per inference

### 5. Decision Engine
- Combines rule engine output + ML score
- Thresholds: score > 0.9 → block, 0.5-0.9 → review, < 0.5 → allow
- Override rules take precedence (blocklisted card always blocked)
- Logs decision + features for audit and model retraining

### 6. Feedback Loop
- Manual review outcomes → labeled data for retraining
- Chargeback data (arrives days/weeks later) → ground truth
- Model retraining: daily batch job, A/B tested before full deployment
- Shadow mode: new models score in parallel, compare to production model

## Key Components to Draw

```
[API Gateway] → [Rules Engine] → [Feature Service] → [ML Scorer] → [Decision]
                     ↓                  ↓                  ↓            ↓
              [Rule Config]      [Redis Counters]    [Model Store]  [Decision Log]
                                 [Feature Store]                        ↓
                                                                [Kafka Events]
                                                                       ↓
                                                              [Batch Retraining]
                                                              [Analytics Dashboard]
```

## Deep Dive Areas

### Real-Time Feature Computation
- **Sliding window counters:** Redis INCR with TTL, or Kafka Streams windowed aggregation
- **Challenge:** Computing "transactions in last 5 minutes" across distributed workers
- **Solution:** Centralized Redis per-card counters with atomic MULTI/EXEC
- **Geo-distance:** Cache last known location per card, compute haversine distance

### Model Updates Without Downtime
- Blue/green deployment: load new model, route % of traffic, compare
- Shadow scoring: new model scores alongside old, log both, alert on divergence
- Rollback: instant switch back to previous model version

### Monitoring
- **Accuracy metrics:** precision, recall, F1 on a rolling window
- **Latency metrics:** P50/P99 per pipeline stage
- **Business metrics:** false positive rate (FPR), blocked legitimate transaction rate
- **Drift detection:** alert if feature distributions shift significantly

## Sample Answer Outline

> "I'd design a three-layer pipeline: rules engine, ML scoring, and decision engine, all in the hot path of a transaction request.
>
> The rules engine applies deterministic checks (blocklists, velocity limits, amount thresholds) in under 10ms using in-memory rule evaluation.
>
> The ML layer computes real-time features (velocity counters from Redis, geo-distance) and combines them with precomputed features from a feature store, then runs inference on a gradient boosted model loaded in-memory. Target: < 50ms total.
>
> The decision engine combines the rule output and ML score to decide: allow, block, or flag for review. Every decision is logged with the full feature vector for auditability and retraining.
>
> The feedback loop is critical: chargeback data and manual review outcomes flow back as labeled data for daily model retraining, deployed via blue/green with shadow scoring."

## Common Mistakes

1. **Calling an external ML service** — Network latency kills the < 1s budget. Load model in-memory.
2. **No rules engine** — ML alone isn't enough. Need hard rules for compliance and immediate threats.
3. **Ignoring the feedback loop** — Without retraining, model degrades as fraud patterns evolve.
4. **No monitoring** — Must track both ML metrics AND business metrics (revenue impact of false positives).
5. **Batch-only processing** — Must be real-time for pre-authorization decisions.

## Connection to Stripe's Actual Architecture

- **Stripe Radar:** Their production fraud detection product, available to all merchants
- Radar uses ML trained on billions of transactions across Stripe's network
- Merchants can define custom Radar rules (velocity, amount, metadata matching)
- Stripe's engineering blog discusses real-time feature computation at scale
- They use Kafka (50 clusters) for streaming event processing
- Decision outcomes feed back into model training pipelines
