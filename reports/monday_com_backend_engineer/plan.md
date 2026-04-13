# Monday.com Backend Engineer — Study Plan

**Total estimated prep time: ~38 hours over 3 weeks**

| Category       | Exercises | Time per exercise | Total     |
| -------------- | --------- | ----------------- | --------- |
| Coding         | 6         | 2h each           | **12h**   |
| System Design  | 4         | 2.5h each         | **10h**   |
| Behavioral     | 5 themes  | 2h each           | **10h**   |
| Company Research|           |                   | **3h**    |
| Mock Interviews |          |                   | **3h**    |
| **Total**      |           |                   | **38h**   |

Daily commitment: ~2h weekdays, ~3h weekends.

---

## Week 1: Coding Focus

The goal this week is to complete all 6 coding exercises. Each session follows this structure:

| Phase           | Duration | What to do                                                        |
| --------------- | -------- | ----------------------------------------------------------------- |
| Solve           | 1h       | Write a working solution from scratch (no hints)                  |
| Review          | 30min    | Compare with optimal approach, note complexity, clean up code     |
| Edge cases      | 30min    | Add tests for empty input, large input, duplicates, concurrency   |

### Day-by-day

| Day         | Activity                                                          | Time  | Exercise File                                        |
| ----------- | ----------------------------------------------------------------- | ----- | ---------------------------------------------------- |
| **Mon (D1)**| Coding #1: Web Crawler / Site Map Graph                          | 2h    | `exercises/coding/01_web_crawler.md`                 |
|             | Build graph from root URL + max_depth using BFS/DFS. Practice LC #1236. | | |
| **Tue (D2)**| Coding #2: Sort table with millions of rows                     | 2h    | `exercises/coding/02_sort_large_table.md`            |
|             | External sort, fractional indexing for moveable rows. Think about what Monday.com actually needs here. | | |
| **Wed (D3)**| Coding #3: Reverse lookup for a hashmap                         | 2h    | `exercises/coding/03_reverse_lookup_hashmap.md`      |
|             | Bidirectional map, handle one-to-many reverse mappings. Practice LC #706. | | |
| **Thu (D4)**| Coding #4: Implement notify(IDs, message)                       | 2h    | `exercises/coding/04_notify_system.md`               |
|             | Resolve teams to users, deduplicate, handle nested teams. Set operations + BFS on org tree. | | |
| **Fri (D5)**| Coding #5: Implement Tic Tac Toe                                | 2h    | `exercises/coding/05_tic_tac_toe.md`                 |
|             | Clean OOP design, win detection, extensible to NxN. Practice LC #348. | | |
| **Sat (D6)**| Coding #6: Generic LeetCode medium + complexity analysis         | 2h    | `exercises/coding/06_generic_leetcode.md`            |
|             | Pick 2-3 medium problems. Practice explaining O(n)/O(n log n) tradeoffs out loud. | | |
| **Sun (D7)**| Behavioral prep #1: Ownership + Why Monday.com                   | 2h    |                                                      |
|             | Write STAR stories for ownership. Sign up for Monday.com free account and use it for 30min. Research their product. | | |

**Week 1 total: ~14h**

---

## Week 2: System Design + Behavioral

### System Design session structure

| Phase            | Duration | What to do                                                      |
| ---------------- | -------- | --------------------------------------------------------------- |
| Attempt          | 1h       | Draw architecture on paper/whiteboard, write out components     |
| Study            | 1h       | Read reference materials, compare with best practices           |
| Verbal practice  | 30min    | Explain your design out loud as if in an interview (record yourself) |

### Day-by-day

| Day          | Activity                                                         | Time  | Exercise File                                        |
| ------------ | ---------------------------------------------------------------- | ----- | ---------------------------------------------------- |
| **Mon (D8)** | System Design #1: Row ordering in a board (E2E)                  | 2.5h  | `exercises/system_design/01_row_ordering.md`         |
|              | Client to server to DB. Fractional indexing, optimistic locking, concurrent users. Study CRDTs. | | |
| **Tue (D9)** | System Design #2: Drag-and-drop with multi-client support        | 2.5h  | `exercises/system_design/02_drag_and_drop.md`        |
|              | Real-time collaboration, WebSockets, conflict resolution. Overlaps with #1 — go deeper on real-time sync. | | |
| **Wed (D10)**| Behavioral prep #2: Failure/mistakes + Conflict resolution       | 2h    |                                                      |
|              | Write 2 STAR stories for failures, 2 for conflicts. Practice telling them in under 2 minutes each. | | |
| **Thu (D11)**| System Design #3: Event-driven system for external apps          | 2.5h  | `exercises/system_design/03_event_driven_apps.md`    |
|              | Kafka/webhooks, retry + DLQ, at-least-once delivery, app registration. Study Monday.com's actual architecture. | | |
| **Fri (D12)**| System Design #4: Scalable task management for enterprise        | 2.5h  | `exercises/system_design/04_task_management.md`      |
|              | Multi-tenant, permissions, search, analytics. Think about mondayDB (Lambda Architecture: Redis speed layer + Cassandra batch layer). | | |
| **Sat (D13)**| Behavioral prep #3: Mentoring + Initiative                       | 2h    |                                                      |
|              | Write STAR stories for mentoring and initiative. Practice all behavioral stories back-to-back. | | |
| **Sun (D14)**| Company deep dive                                                | 3h    |                                                      |
|              | Read Monday.com engineering blog posts: multi-regional architecture, mondayDB, technical interviews guide. Prepare 2-3 product improvement ideas. | | |

**Week 2 total: ~17h**

---

## Week 3: Integration + Mock Interviews

| Day          | Activity                                                         | Time  |
| ------------ | ---------------------------------------------------------------- | ----- |
| **Mon (D15)**| Re-solve Coding #1 (Web Crawler) and #4 (Notify) from scratch   | 2h    |
|              | These are the most likely to appear. Time yourself — aim for 30min each. | |
| **Tue (D16)**| Mock interview: Full coding round                                | 1.5h  |
|              | Pick a problem you haven't seen. 45min to solve + 15min complexity discussion + 30min review. | |
| **Wed (D17)**| Mock interview: Full system design round                         | 1.5h  |
|              | Re-do Row Ordering (#1) or Event-Driven (#3) as a timed 45min session. Record and review. | |
| **Thu (D18)**| Behavioral dry run — all stories                                 | 2h    |
|              | Run through every STAR story. Practice with a friend or record yourself. Keep each answer under 2 minutes. | |
| **Fri (D19)**| Weak spots review                                                | 1h    |
|              | Revisit whichever area felt weakest. Re-read Monday.com blog posts. Review your product improvement ideas. | |

**Week 3 total: ~8h**

---

## Key Resources to Read

Read these during the company deep dive (D14) and weak spots review (D19):

| Resource                                                    | Why                                         |
| ----------------------------------------------------------- | ------------------------------------------- |
| [A Guide to Technical Interviews at monday.com](https://engineering.monday.com/a-guide-to-technical-interviews-at-monday-com/) | They tell you exactly what they look for     |
| [monday.com Multi-Regional Architecture](https://engineering.monday.com/monday-coms-multi-regional-architecture-a-deep-dive/) | Understand their infrastructure decisions    |
| [mondayDB Architecture (Medium)](https://medium.com/@liranbrimer/nice-to-meet-you-mondaydb-architecture-6d201b41e660) | Lambda Architecture — comes up in system design |
| [monday.com Infrastructure Management](https://engineering.monday.com/how-we-manage-software-infrastructure-at-monday-com/) | CDKTF, EKS, microservices context            |
| Monday.com free account (use the product)                   | They will ask what you would change          |

---

## Readiness Checklist

Check off each item as you complete it. All boxes should be checked before your interview.

### Coding

- [ ] Web Crawler / Site Map Graph — solved, reviewed, edge cases covered
- [ ] Sort table with millions of rows — solved, can explain fractional indexing
- [ ] Reverse lookup hashmap — solved, handles one-to-many correctly
- [ ] notify(IDs, message) — solved, handles nested teams + deduplication
- [ ] Tic Tac Toe — solved with clean OOP, extensible to NxN
- [ ] Generic LeetCode medium — can solve a new medium in 30min with complexity analysis
- [ ] Can explain time and space complexity for every solution out loud

### System Design

- [ ] Row ordering E2E — can draw full architecture (client, API, DB, concurrency handling)
- [ ] Drag-and-drop multi-client — can explain real-time sync approach (WebSockets, CRDTs or OT)
- [ ] Event-driven external apps — can design webhook/Kafka system with retry + DLQ
- [ ] Scalable task management — can discuss multi-tenant architecture, mondayDB approach
- [ ] Can explain tradeoffs for each design (consistency vs. availability, latency vs. correctness)

### Behavioral

- [ ] 2 ownership stories ready (STAR format, under 2 minutes each)
- [ ] 2 failure/mistake stories ready
- [ ] 2 conflict resolution stories ready
- [ ] 1 mentoring story ready
- [ ] "Why Monday.com?" answer prepared with specific product knowledge
- [ ] 2-3 product improvement ideas for "What would you change about Monday.com?"

### Company Knowledge

- [ ] Used Monday.com product (free account)
- [ ] Read engineering blog — technical interviews guide
- [ ] Read engineering blog — multi-regional architecture
- [ ] Read mondayDB architecture article
- [ ] Know their tech stack: Node.js/TypeScript, Redis, Cassandra, Kafka, AWS/EKS
- [ ] Know their values: ownership, transparency, deploy to production multiple times daily
- [ ] Aware of recent AI/MCP initiatives
