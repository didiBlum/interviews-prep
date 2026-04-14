# System Design: Global Payments Ledger

**Source:** Stripe system design round (leetcodewizard.io, 2025)

## The Prompt

"Design a global payments ledger that supports idempotent transaction submission, eventual reconciliation, and high throughput."

## Time Budget (45 minutes)

| Phase | Time | Focus |
|-------|------|-------|
| Clarify requirements | 5 min | Consistency model, throughput, compliance |
| High-level design | 10 min | Ledger model, write path, read path |
| Detailed design | 15 min | Idempotency, double-entry, reconciliation |
| Deep dive | 10 min | Sharding, failure modes, compliance |
| Q&A | 5 min | Trade-offs |

## Clarifying Questions to Ask

1. "What's the expected TPS (transactions per second)?" (~tens of thousands)
2. "What consistency model? Strong or eventual for reads?"
3. "Multi-currency support?"
4. "What regulatory requirements? SOX, PCI DSS?"
5. "Do we need real-time balance queries or is eventual consistency OK?"
6. "Audit trail requirements? Immutable history?"

## Step-by-Step Framework

### 1. Data Model: Double-Entry Bookkeeping

Every transaction creates TWO ledger entries (debit + credit). Money never appears or disappears — it moves between accounts.

```
ledger_entries table:
- entry_id (UUID)
- transaction_id (UUID) — groups debit + credit
- account_id
- amount (signed: positive = credit, negative = debit)
- currency
- created_at
- idempotency_key
```

**Key invariant:** For every transaction_id, SUM(amount) = 0.

### 2. Account Model

```
accounts table:
- account_id
- account_type (merchant, platform, reserve, fees)
- currency
- balance (cached, derived from ledger entries)
- version (optimistic concurrency)
```

### 3. Write Path (Transaction Submission)

1. Client sends transaction with idempotency_key
2. Check idempotency store: if key exists, return cached result
3. Validate: sufficient balance, valid accounts, valid amount
4. Within a DB transaction:
   - Insert debit entry (source account)
   - Insert credit entry (destination account)
   - Update cached balances on both accounts (with version check)
   - Store idempotency key → result mapping
5. Publish event to Kafka for downstream consumers

### 4. Idempotency

- Store (idempotency_key → response) with TTL (e.g., 48 hours)
- On duplicate request: return stored response, don't re-execute
- Implementation: unique index on idempotency_key in ledger_entries

### 5. Reconciliation

- Periodic job (every hour): recompute all account balances from ledger entries
- Compare with cached balances
- Flag discrepancies for investigation
- Separate reconciliation for external partners (bank statements vs. internal ledger)

### 6. State Machine for Payments

```
PaymentIntent states:
Created → Confirmed → Processing → Authorized → Captured → Settled
                                  → Failed
                                  → Refunded
```

Each state transition creates ledger entries.

## Key Components to Draw

```
[API Gateway] → [Transaction Service] → [Ledger DB (sharded)]
                       ↓                        ↓
              [Idempotency Store]        [Kafka Events]
                                                ↓
                                    [Reconciliation Service]
                                    [Balance Cache Service]
                                    [Audit/Compliance Service]
```

## Deep Dive Areas

### Sharding Strategy
- Shard by account_id (keeps one account's entries co-located)
- Cross-shard transactions (debit and credit on different shards):
  - Option 1: Two-phase commit (strong consistency, lower throughput)
  - Option 2: Saga pattern (eventual consistency, higher throughput)
  - Stripe's approach: same-shard when possible, 2PC for cross-shard

### Consistency vs. Availability
- Balance reads: eventual consistency is acceptable (cached balance may lag)
- Transaction writes: strong consistency required (no double-spending)
- Use optimistic concurrency (version column) to prevent lost updates

### Failure Scenarios
- **DB write failure mid-transaction:** Atomic DB transaction rolls back both entries
- **Kafka publish failure:** Outbox pattern — write to outbox table in same DB transaction, separate process publishes
- **Reconciliation mismatch:** Alert, freeze affected accounts, investigate

## Sample Answer Outline

> "I'd design a double-entry ledger system with three layers: the write path, the read path, and reconciliation.
>
> The write path enforces the core invariant: every transaction creates a balanced pair of entries (debit + credit). We use idempotency keys to prevent duplicate processing and optimistic concurrency on account balances.
>
> The read path serves cached balances with eventual consistency. A separate balance computation service periodically recomputes balances from the append-only ledger for accuracy.
>
> Reconciliation runs hourly: internal (cached vs. computed balances) and external (our ledger vs. bank statements). Discrepancies trigger alerts and account freezes.
>
> For scale, I'd shard by account_id and use the outbox pattern for reliable event publishing to Kafka."

## Common Mistakes

1. **Mutable balance without ledger entries** — Violates auditability. Always append-only entries.
2. **Ignoring idempotency** — In payments, this is non-negotiable. Mention it early.
3. **Single database** — Won't scale. Must discuss sharding strategy.
4. **Ignoring multi-currency** — Real ledgers handle conversions. At minimum, acknowledge it.
5. **No reconciliation** — Shows you don't understand financial systems.

## Connection to Stripe's Actual Architecture

- Stripe uses double-entry bookkeeping throughout their ledger system
- PaymentIntent state machine is a core Stripe API concept
- Idempotency keys are a first-class Stripe API feature (Idempotency-Key header)
- They process tens of thousands of TPS across sharded databases
- Reconciliation against banking partners is a critical operational process
- Blog posts detail their approach to zero-downtime database migrations
