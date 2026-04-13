# SD 02: Design Microsoft Teams Chat Service

## The Prompt

> "Design a scalable chat service similar to Microsoft Teams. It should support 1:1 and group messaging with message ordering, delivery guarantees, and real-time notifications for millions of concurrent users."

**Reported in:** Microsoft Senior interviews — product-specific system design.
**Sources:** [InterviewQuery](https://www.interviewquery.com/interview-guides/microsoft-software-engineer), [Educative](https://www.educative.io/blog/microsoft-system-design-interview), [DesignGurus](https://www.designgurus.io/blog/microsoft-system-design-interview-questions)

---

## Time Budget (45 minutes)

| Phase | Time | What to Cover |
|-------|------|---------------|
| Clarifying Questions | 3-5 min | Scale, features, consistency requirements |
| High-Level Design | 10 min | Core services, data flow, storage |
| Detailed Design | 15-20 min | Message ordering, delivery, presence, notifications |
| Deep Dive | 10-15 min | Offline sync, compliance, scaling |
| Wrap-up | 2-3 min | Tradeoffs, what you'd build first |

---

## Clarifying Questions to Ask

1. **Scale:** How many concurrent users? (Target: 300M+ monthly active, ~50M concurrent)
2. **Features:** 1:1 chat, group chat, channels? File sharing? Reactions? Threads?
3. **Message ordering:** Strict per-conversation ordering? Or best-effort?
4. **Delivery guarantees:** At-least-once? Exactly-once? Read receipts?
5. **Offline support:** Can users receive messages when offline? How long to retain?
6. **Compliance:** Message retention policies? eDiscovery? Audit logging? (Microsoft-specific!)
7. **Multi-device:** Users on phone + desktop simultaneously?

---

## Step-by-Step Framework

### 1. API Design

```
SendMessage(conversationId, senderId, content, messageType) -> messageId
GetMessages(conversationId, cursor, limit) -> [Message]
MarkAsRead(conversationId, userId, messageId) -> success
GetConversations(userId) -> [Conversation]
```

### 2. High-Level Architecture

```
┌──────────┐    WebSocket     ┌──────────────┐     ┌─────────────┐
│  Client   │<──────────────>│  Gateway      │────>│  Chat        │
│  (Teams)  │                │  Service      │     │  Service     │
└──────────┘                 └──────────────┘     └──────┬──────┘
                                                          │
                              ┌────────────────┐         │
                              │  Notification   │<────────┤
                              │  Service        │         │
                              └────────────────┘         │
                                                          │
                    ┌──────────────┐  ┌──────────────┐   │
                    │  Presence    │  │  Message      │<──┘
                    │  Service     │  │  Store        │
                    └──────────────┘  │  (Cosmos DB)  │
                                       └──────────────┘
                                              │
                                       ┌──────────────┐
                                       │  Message Bus  │
                                       │  (Event Hubs) │
                                       └──────────────┘
```

### 3. Key Components

#### Gateway Service
- Manages WebSocket connections (long-lived)
- Routes messages to Chat Service
- Handles connection lifecycle (connect, heartbeat, reconnect)
- Sticky sessions via consistent hashing on userId

#### Chat Service
- Business logic: validate, persist, fan-out
- Generates monotonically increasing messageId per conversation (for ordering)
- Publishes message events to Event Hubs

#### Message Store (Azure Cosmos DB)
- **Partition key:** conversationId (all messages in a conversation on same partition)
- **Sort key:** messageId (timestamp-based, e.g., Snowflake ID)
- **Why Cosmos DB?** Global distribution, tunable consistency, low-latency reads
- **Consistency:** Session consistency (user always sees their own writes)

#### Notification Service
- Consumes from Event Hubs
- Determines delivery channel: WebSocket (online), Push notification (mobile), Email (offline)
- Fan-out: for group chat with 100 members, generates 100 notification events
- Deduplication using messageId + recipientId

#### Presence Service
- Tracks online/offline/away/busy status
- Heartbeat-based: client sends heartbeat every 30s; absent for 2 min = offline
- Stored in Redis (ephemeral, high-read pattern)
- Used to decide: deliver via WebSocket or push notification?

---

## Deep Dive Areas

### Message Ordering
- **Per-conversation ordering:** Each message gets a server-assigned sequence number within the conversation
- **Snowflake IDs:** timestamp (41 bits) + partition ID (10 bits) + sequence (12 bits)
- **Why not client timestamps?** Clock skew across devices. Server timestamp is authoritative.
- **Eventual consistency window:** Messages may briefly appear out of order during network partition; client reorders by sequence number on receipt

### Delivery Guarantees
- **At-least-once:** Message published to Event Hubs (durable). Notification service retries on failure.
- **Idempotency:** Client deduplicates using messageId. Server deduplicates using (conversationId, senderId, clientMessageId)
- **Read receipts:** Separate event type. Aggregated (don't send individual receipt per member for large groups).

### Offline Sync
- When user comes online, query Message Store for messages since lastSyncTimestamp
- Use cursor-based pagination (not offset-based) for consistency
- **Catch-up queue:** For short offline periods (< 24h), messages buffered in per-user queue

### Compliance & Auditing (Microsoft-specific!)
- **Message retention:** Configurable per organization (7 days to 10 years)
- **eDiscovery:** All messages indexed in Azure Cognitive Search for legal hold queries
- **Audit logging:** Every message action (send, edit, delete) logged to immutable audit store
- **DLP (Data Loss Prevention):** Real-time content scanning for sensitive data (SSN, credit cards)
- **EU data residency:** Messages from EU users stored in EU Cosmos DB region

### Scaling
- **Hot conversations:** Very active group chats → partition by conversationId handles this
- **Celebrity problem:** User with 10,000 group memberships → fan-out on read, not write
- **Connection scaling:** Each Gateway server handles ~100K WebSocket connections
- **50M concurrent users → 500 Gateway servers**

---

## Sample Answer Outline

> "I'd build a microservices architecture with four core services: Gateway (WebSocket management), Chat Service (business logic), Notification Service (multi-channel delivery), and Presence Service (online status). Messages are stored in Azure Cosmos DB partitioned by conversationId with session consistency for read-your-writes. Message ordering uses server-assigned Snowflake IDs. Fan-out for group messages goes through Azure Event Hubs for durability and backpressure. For Microsoft specifically, I'd add a compliance layer with DLP scanning, eDiscovery indexing, and configurable retention policies — this is critical for enterprise customers. The system scales horizontally: each service is stateless and can be auto-scaled on AKS."

---

## Common Mistakes

1. **Single monolithic service** — chat needs separation of concerns for independent scaling
2. **Client-side timestamps for ordering** — clock skew breaks ordering
3. **No offline handling** — users switching networks/devices is the norm
4. **Fan-out on write for huge groups** — doesn't scale for 10K-member channels
5. **Ignoring compliance** — Microsoft interviews specifically probe this
6. **No presence service** — wasting push notifications on online users

---

## Connection to Microsoft's Architecture

- **Microsoft Teams actual architecture:** Uses Azure Service Fabric for microservices, Cosmos DB for storage, Azure Event Hubs for messaging, Azure Notification Hubs for push.
- **Substrate:** The shared infrastructure layer for Office 365 services, handling identity, storage, and search across Teams, Outlook, and OneDrive.
- **Compliance:** Microsoft 365 compliance center provides eDiscovery, DLP, and information governance — a key differentiator from competitors.
- **Engineering@Microsoft blog:** "The Interaction Changes Everything" (Dec 2025) discusses treating AI agents as collaborators in Teams.
