# Interview Prep Plan: Stripe Senior Software Engineer

## Overview

- **Total estimated prep time:** ~45–55 hours
- **Recommended timeline:** 3–4 weeks
- **Priority order:** Coding exercises → System Design → Bug Bash practice → Integration practice → Behavioral

## Week-by-Week Plan

### Week 1: Coding Fundamentals (Core Stripe Patterns)


| Day | Activity                                           | Time | Details                                                        |
| --- | -------------------------------------------------- | ---- | -------------------------------------------------------------- |
| 1   | Exercise 01: Rate Limiter                          | 2h   | 1h solve + 0.5h review solution + 0.5h practice edge cases     |
| 1   | Exercise 05: Blur Credit Cards                     | 1.5h | 1h solve + 0.5h review (warm-up: string/regex)                 |
| 2   | Exercise 02: Transaction Ledger                    | 2h   | 1h solve + 0.5h review + 0.5h practice all 3 parts             |
| 2   | Exercise 07: Brace Expansion                       | 1.5h | 1h solve + 0.5h review                                         |
| 3   | Exercise 03: User Deduplication                    | 2.5h | 1.5h solve (3 parts) + 0.5h review + 0.5h union-find deep dive |
| 3   | Exercise 08: Currency Exchange                     | 1.5h | 1h solve + 0.5h review graph approach                          |
| 4   | Exercise 04: Subscription Scheduler                | 2h   | 1h solve + 0.5h review + 0.5h practice follow-ups              |
| 4   | Exercise 06: AccountScheduler                      | 2h   | 1h solve + 0.5h review + 0.5h LRU deep dive                    |
| 5   | Re-solve hardest 2 exercises under time pressure   | 2h   | 45 min each, simulate interview conditions                     |
| 5   | Practice: clean code, naming, edge case commentary | 1h   | Review all solutions for production quality                    |


**Week 1 total: ~18.5h**

### Week 2: System Design Deep Dives


| Day | Activity                                                       | Time | Details                                                        |
| --- | -------------------------------------------------------------- | ---- | -------------------------------------------------------------- |
| 1   | SD 01: Webhook Delivery System                                 | 2.5h | 1h self-attempt + 1h study reference + 0.5h verbal walkthrough |
| 1   | Read Stripe engineering blog (2-3 posts)                       | 1h   | Focus on infrastructure, Kafka, observability                  |
| 2   | SD 02: Global Payments Ledger                                  | 2.5h | 1h self-attempt + 1h study reference + 0.5h verbal walkthrough |
| 2   | Study: Idempotency patterns (idempotency keys, state machines) | 1h   | Core Stripe concept                                            |
| 3   | SD 03: Fraud Detection Pipeline                                | 2.5h | 1h self-attempt + 1h study reference + 0.5h verbal walkthrough |
| 3   | Study: Kafka architecture + streaming patterns                 | 1h   | Stripe uses 50 Kafka clusters                                  |
| 4   | SD 04: Rate Limiter (System Level)                             | 2.5h | 1h self-attempt + 1h study reference + 0.5h verbal walkthrough |
| 4   | Study: Stripe tech stack overview                              | 1h   | Ruby monorepo, AWS, Kubernetes, Prometheus                     |
| 5   | Mock: Pick 1 SD question, do 45-min timed attempt              | 1.5h | 45 min attempt + 45 min self-critique                          |
| 5   | Study: PCI compliance basics for system design                 | 0.5h | Know boundary constraints                                      |


**Week 2 total: ~16h**

### Week 3: Bug Bash + Integration + Behavioral


| Day | Activity                                                           | Time | Details                                                                                       |
| --- | ------------------------------------------------------------------ | ---- | --------------------------------------------------------------------------------------------- |
| 1   | Bug Bash practice: clone Python `requests` library                 | 2h   | Practice navigating unfamiliar codebase, running tests, using debugger                        |
| 1   | Bug Bash practice: clone Flask or Express                          | 1.5h | Fix a known bug from git history; practice stack trace analysis                               |
| 2   | Integration practice: build a Stripe API integration               | 2h   | Use Stripe test mode; create charges, list customers, handle webhooks                         |
| 2   | Integration practice: read unfamiliar API docs under time pressure | 1h   | Pick any REST API you haven't used; build integration in 45 min                               |
| 3   | Behavioral prep: write STAR stories                                | 2h   | Write 6+ stories covering ownership, reliability, communication, failure, conflict, mentoring |
| 3   | Behavioral prep: read behavioral_prep.md                           | 1h   | Map your stories to each Stripe behavioral question                                           |
| 4   | Mock coding interview                                              | 1.5h | Have someone give you a multi-part problem; 45 min + debrief                                  |
| 4   | Mock system design interview                                       | 1.5h | 45 min timed + debrief                                                                        |
| 5   | Company research: use Stripe product                               | 1.5h | Create test account, explore Dashboard, API docs, developer experience                        |
| 5   | Prepare "Why Stripe?" answer                                       | 0.5h | Authentic, specific, tied to your experience                                                  |


**Week 3 total: ~15h**

### Week 4 (Optional): Polish & Confidence


| Day | Activity                                      | Time | Details                                               |
| --- | --------------------------------------------- | ---- | ----------------------------------------------------- |
| 1   | Re-solve 3 coding exercises under strict time | 2h   | Focus on clean code + verbal explanation while coding |
| 2   | Full mock onsite: coding + SD back-to-back    | 3h   | Simulate real interview energy management             |
| 3   | Review all system design references           | 2h   | Verbal walkthrough of each design                     |
| 4   | Final behavioral rehearsal                    | 1h   | Practice STAR stories out loud                        |
| 5   | Rest and review notes                         | 1h   | Light review, no heavy practice                       |


**Week 4 total: ~9h**

## Readiness Checklist

- Can solve all 8 coding exercises within 45-min time limit
- Can articulate system design for each SD question (whiteboard 45 min)
- Can navigate an unfamiliar OSS codebase and find bugs systematically
- Can integrate with a REST API from docs alone within 45 min
- Have 6+ STAR stories covering all behavioral themes
- Can explain Stripe's tech stack and architecture patterns
- Have used the Stripe product and formed opinions about developer experience
- Can answer "Why Stripe?" authentically and specifically
- Practice coding while explaining your thought process out loud
- Understand idempotency, double-entry ledgers, and webhook reliability deeply

