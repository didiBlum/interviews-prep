# System Design Exercise 4: Scalable Task Management System

## The Prompt (As Asked in Interview)

> "Design a scalable task management system for enterprise teams."

This is the broadest of the four exercises -- a classic open-ended system design question. The key is to scope it well, then go deep on the areas that matter for Monday.com: multi-tenant data model, real-time collaboration, flexible schemas, and horizontal scaling.

---

## Time Budget (45 Minutes)

| Phase | Minutes | What to Cover |
|-------|---------|---------------|
| Clarify requirements & scope | 6 | What "task management" means, enterprise scale, features to include/exclude |
| Core data model | 8 | Boards, groups, items, columns -- flexible schema design |
| API design | 5 | CRUD operations, GraphQL, real-time subscriptions |
| Storage architecture | 10 | Multi-tenant storage, mondayDB pattern, indexing |
| Real-time collaboration | 6 | WebSocket, event propagation, consistency |
| Scale & multi-region | 6 | Sharding, caching, CDN, multi-region strategy |
| Enterprise features | 4 | Permissions, audit, compliance |

---

## Clarifying Questions to Ask

1. **Scope of "task management"** -- "Should I design a full work OS like Monday.com (flexible boards, custom columns, automations), or a simpler Trello-like tool with fixed task fields?"
2. **Enterprise scale** -- "How many organizations? How many users per org? Thousands of orgs with 10K+ users each?"
3. **Flexibility** -- "Do tasks have a fixed schema (title, assignee, due date), or can teams define custom columns/fields?"
4. **Views** -- "Do we need multiple views of the same data (table, Kanban, timeline, calendar)?"
5. **Real-time** -- "Is real-time collaboration a requirement? Multiple users editing the same board simultaneously?"
6. **Integrations** -- "Do we need to support external integrations (Slack notifications, email, webhooks)?"
7. **Multi-tenancy** -- "Is this a SaaS product serving many organizations, or a single-tenant deployment?"
8. **Offline support** -- "Do enterprise users need offline access, or is always-online acceptable?"

---

## Step-by-Step Framework

### Step 1: Feature Scope (Agree With Interviewer)

**In scope** (P0):
- Organizations (accounts) with users, teams, roles
- Boards containing groups containing items (tasks)
- Flexible column system (status, person, date, text, number, etc.)
- CRUD operations on all entities
- Real-time updates across clients
- Search across items
- Permissions (board-level, item-level)

**In scope** (P1 -- mention, design if time):
- Automations (when X happens, do Y)
- Views (table, Kanban, timeline)
- File attachments
- Activity log / audit trail

**Out of scope** (mention to show judgment):
- Mobile app specifics
- Billing/subscription management
- App marketplace

### Step 2: Core Data Model

The most important design decision: **flexible schema for items**.

Monday.com's insight: Tasks are not a fixed schema. Different teams need different fields. The column system must be extensible without schema migrations.

**Entity Relationship**:

```
Account (tenant)
  |-- has many Users
  |-- has many Boards
        |-- has many Columns (define the schema)
        |-- has many Groups
              |-- has many Items
                    |-- has many ColumnValues (actual data per column)
```

**Table designs**:

```sql
-- Accounts (tenants)
accounts:
  id: UUID (PK)
  name: STRING
  plan: STRING
  region: STRING  -- for data residency

-- Users
users:
  id: UUID (PK)
  account_id: UUID (FK)
  email: STRING
  name: STRING

-- Boards
boards:
  id: UUID (PK)
  account_id: UUID (FK, partition key for multi-tenancy)
  name: STRING
  board_kind: ENUM (main, shareable, private)
  created_by: UUID (FK -> users)

-- Columns (board schema definition)
columns:
  id: UUID (PK)
  board_id: UUID (FK)
  type: STRING  -- "status", "person", "date", "text", "number", "formula"
  title: STRING
  settings: JSONB  -- type-specific config (e.g., status labels/colors)
  position: STRING  -- lexicographic ordering

-- Groups (sections within a board)
groups:
  id: UUID (PK)
  board_id: UUID (FK)
  title: STRING
  position: STRING
  color: STRING

-- Items (tasks/rows)
items:
  id: UUID (PK)
  board_id: UUID (FK)
  group_id: UUID (FK)
  name: STRING
  position: STRING  -- ordering within group
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
  creator_id: UUID (FK -> users)

-- Column Values (the flexible data -- EAV pattern)
column_values:
  item_id: UUID (FK)
  column_id: UUID (FK)
  value: JSONB  -- polymorphic storage
  PRIMARY KEY (item_id, column_id)
```

**Why JSONB for column values**: Different column types have different data shapes:
- Status: `{"index": 2, "label": "Done"}`
- Person: `{"personsAndTeams": [{"id": 123, "kind": "person"}]}`
- Date: `{"date": "2026-04-01", "time": "09:00:00"}`
- Number: `{"value": 42, "unit": "hours"}`

This is the Entity-Attribute-Value (EAV) pattern with JSONB, which is exactly how Monday.com models their flexible column system.

### Step 3: API Design (GraphQL)

```graphql
type Query {
  boards(accountId: ID!, limit: Int, page: Int): [Board!]!
  board(id: ID!): Board
  items(boardId: ID!, groupId: ID, queryParams: ItemQueryParams): ItemConnection!
}

type Mutation {
  createItem(boardId: ID!, groupId: ID!, name: String!, columnValues: JSON): Item!
  updateColumnValue(itemId: ID!, columnId: ID!, value: JSON!): Item!
  moveItem(itemId: ID!, targetGroupId: ID!, afterItemId: ID, beforeItemId: ID): Item!
  deleteItem(itemId: ID!): ID!
  createBoard(accountId: ID!, name: String!, columns: [ColumnInput!]): Board!
}

type Subscription {
  boardUpdated(boardId: ID!): BoardEvent!
}

type Board {
  id: ID!
  name: String!
  columns: [Column!]!
  groups: [Group!]!
  items(limit: Int, cursor: String): ItemConnection!
}

type Item {
  id: ID!
  name: String!
  group: Group!
  columnValues: [ColumnValue!]!
}
```

**Why GraphQL**: Clients fetch exactly the columns they need. A table view needs all columns; a Kanban view needs only status + assignee. GraphQL avoids over-fetching -- critical for boards with 30+ columns.

### Step 4: Storage Architecture (mondayDB Pattern)

**The Lambda Architecture choice**:

```
                         Writes
                           |
              +------------+------------+
              |                         |
              v                         v
      Redis (Speed Layer)       Kafka (Event Log)
      - Active boards cache       |
      - Sorted sets for ordering  v
      - Session/presence data   Cassandra (Batch Layer)
                                - Durable storage
                                - All historical data
                                - Wide-column: good for EAV
```

**Why this combination**:
- **Redis**: Sub-millisecond reads for active boards. A user opens a board -- load it from Redis. If cache miss, hydrate from Cassandra.
- **Cassandra**: Handles massive write throughput (column value updates across millions of items). Wide-column model is natural for EAV: partition by `(board_id, item_id)`, columns for each column value.
- **Kafka**: Durable event log connecting the two. Also feeds search indexing, analytics, automations.

**Cassandra table design**:

```
CREATE TABLE item_column_values (
  board_id UUID,
  item_id UUID,
  column_id UUID,
  value TEXT,  -- JSON string
  updated_at TIMESTAMP,
  PRIMARY KEY ((board_id), item_id, column_id)
);
-- Partition key: board_id (all items for a board in one partition)
-- Clustering: item_id, column_id (efficient per-item and per-column queries)
```

**Redis structure for an active board**:

```
board:{boardId}:meta         -> Hash {name, settings, ...}
board:{boardId}:columns      -> Hash {col1: settings, col2: settings}
board:{boardId}:group:{gId}:items -> Sorted Set (score=position, member=itemId)
item:{itemId}:values         -> Hash {col1: jsonValue, col2: jsonValue}
```

### Step 5: Real-Time Collaboration

```
Client A (makes change)
  |
  | GraphQL Mutation (HTTP)
  |
  v
Board Service
  |
  | 1. Write to Redis
  | 2. Publish to Kafka topic: board-events
  |    Key: board_id, Value: { type, itemId, changes, actorId }
  |
  v
Kafka -> WebSocket Gateway (consumer group)
  |
  | 3. Look up all WS connections subscribed to this board_id
  | 4. Send event to all subscribers EXCEPT actorId
  |
  v
Clients B, C, D: apply incremental update to local state
```

**Handling stale state**: Each board has a monotonically increasing version. Client tracks `lastSeenVersion`. On reconnect or suspicion of missed events, client requests delta: `GET /boards/{id}/changes?since=version`.

### Step 6: Search

Enterprise users need to search across thousands of items.

**Search architecture**:

```
Kafka (board-events)
  |
  v
Search Indexer (consumer group)
  |
  v
Elasticsearch
  Index per account (multi-tenant isolation)
  Document = Item + all column values denormalized
```

**Query**: `GET /search?q=urgent+deploy&board_ids=123,456&column_filters=status:stuck`

Elasticsearch handles full-text search on item names and text column values, plus structured filtering on status, dates, numbers.

### Step 7: Multi-Tenancy & Enterprise Scale

**Tenant isolation strategies** (pick based on scale):

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| Shared DB, shared schema | All tenants in same tables, `account_id` filter | Default for most tenants |
| Shared DB, separate schema | Per-tenant schema/keyspace | Mid-size enterprises wanting isolation |
| Dedicated DB | Separate Cassandra cluster | Largest enterprises, data residency requirements |

Monday.com likely uses **shared infrastructure with logical isolation** for most customers, with dedicated options for enterprise.

**Sharding strategy**:
- Cassandra is naturally distributed. Partition key = `board_id` distributes across nodes.
- Redis: shard by `board_id % N` across Redis cluster nodes.
- Kafka: partition board-events topic by `board_id`.

**Multi-region deployment**:

```
Region US-East (primary for US accounts)
  - Full stack: API, Board Service, Redis, Cassandra, Kafka

Region EU-West (primary for EU accounts)
  - Full stack (data residency compliance)

Cross-region:
  - Cassandra: multi-DC replication for disaster recovery
  - Kafka: MirrorMaker for event replication
  - Account affinity: each account is "homed" to a region
  - Global load balancer routes users to their home region
```

### Step 8: Enterprise Features

**Permissions model**:

```
Hierarchy:
  Account Admin > Team Admin > Board Owner > Board Member > Viewer > Guest

Board-level:
  - Owner: full control
  - Member: edit items
  - Viewer: read-only

Column-level:
  - Restricted columns: only certain roles can edit (e.g., budget column)

Item-level:
  - Item creator restrictions (can only edit own items)
```

**Implementation**: Permission checks in the Board Service middleware. Cache user permissions in Redis per session. Invalidate on role change.

**Audit log**:
- Every mutation produces a Kafka event.
- Audit Log Service consumes all events, writes to append-only storage (S3 + Athena for querying).
- Enterprise compliance: 7-year retention, exportable, filterable by user/board/action.

---

## Key Components to Draw

1. **System architecture overview**: Client -> API Gateway -> Board Service -> mondayDB (Redis + Cassandra) + Kafka -> WebSocket Gateway -> Other Clients
2. **Data model ER diagram**: Account -> Board -> (Columns, Groups) -> Items -> ColumnValues
3. **mondayDB Lambda Architecture**: Write path (Redis + Kafka -> Cassandra), Read path (Redis cache -> Cassandra fallback)
4. **Multi-region deployment**: Two regions with full stacks, cross-region replication arrows
5. **Search pipeline**: Kafka -> Search Indexer -> Elasticsearch

---

## Deep Dive Areas (Where Interviewer Probes)

### 1. "Why not use a relational DB like PostgreSQL?"
- **For the core item/column-value data**: EAV in Postgres works but has join penalties at scale. Adding a column to a board with 100K items requires no schema change in our JSONB approach, but querying across arbitrary columns is expensive.
- **Cassandra advantages**: Linear horizontal scaling, high write throughput (every column value update is a write), tunable consistency, natural fit for wide-column EAV.
- **Postgres is still useful**: For account/user metadata, billing, permissions -- structured, relational, low-volume data. Use the right tool for each job.
- Mention: Monday.com's eng blog discusses moving from relational to mondayDB specifically because of the limitations of traditional DBs at their scale.

### 2. "How do you handle a board with 100K items?"
- **Don't load everything**: Cursor-based pagination. Default page size = 50 items.
- **Virtual scrolling**: Client renders only visible rows + buffer.
- **Redis sorted set**: O(log n) for range queries. Getting items 500-550 is efficient.
- **Column value lazy loading**: For a board with 30 columns and 100K items, that's 3M column values. Load column values only for visible items, on demand.
- **Group-level loading**: Load one group at a time. Collapsed groups don't load their items.

### 3. "How do you handle formula columns that depend on other columns?"
- Formula columns (e.g., "Duration = End Date - Start Date") are computed, not stored.
- **Option A**: Compute on read. Board Service evaluates formulas when returning items. Cache results in Redis.
- **Option B**: Compute on write. When a dependency column changes, recompute and store the formula value. Better for sort/filter on formula columns.
- **Dependency tracking**: Maintain a DAG of column dependencies per board. On value change, traverse DAG and recompute affected formulas.
- Monday.com supports formula columns -- this is a real challenge they solve.

### 4. "How do you handle permissions without adding latency?"
- Permission checks on every API call add latency if they hit the DB.
- **Cache user's effective permissions** in Redis: `permissions:{userId}:{boardId} -> {role, columnRestrictions}`.
- TTL: 5 minutes. Invalidate immediately on permission change via Kafka event.
- For item-level restrictions: encode rules in a lightweight policy engine evaluated in-memory (no DB call per item).

### 5. "How do you ensure data consistency between Redis and Cassandra?"
- **Write**: Write to Redis first (for speed), then publish to Kafka, Kafka consumer writes to Cassandra.
- **Risk**: If Kafka consumer fails after Redis write, data is in Redis but not Cassandra.
- **Mitigation**: Redis data has TTL. On cache expiry, data is re-read from Cassandra. If Cassandra is behind, there's a brief inconsistency.
- **Reconciliation**: Periodic background job compares Redis and Cassandra for active boards, fixes divergence.
- **Alternative**: Write to Cassandra first (source of truth), then update Redis. Higher latency for the user but stronger consistency.
- Monday.com's mondayDB likely uses Redis as a write-through or write-ahead cache with Kafka as the replication log.

---

## Sample Answer Outline (Strong Skeleton)

> "I'll design a multi-tenant task management platform with flexible schemas, real-time collaboration, and enterprise-grade scale.
>
> **Data model**: The core abstraction is Board -> Groups -> Items, with a flexible column system. Columns define the schema (status, person, date, custom fields). Column values are stored as JSONB per item per column -- the EAV pattern. This lets teams customize their boards without schema migrations.
>
> **Storage -- mondayDB Lambda Architecture**: Active boards are served from Redis for sub-millisecond reads. Redis holds sorted sets for item ordering and hashes for column values. All writes go through Kafka to Cassandra for durable storage. Cassandra's wide-column model is natural for EAV: partition by board_id, cluster by item_id and column_id.
>
> **API**: GraphQL so clients fetch exactly the columns they need. Mutations for CRUD operations, subscriptions for real-time updates.
>
> **Real-time collaboration**: Every mutation publishes to Kafka. WebSocket Gateway servers consume board events and fan out to subscribed clients. Optimistic updates on the client side for responsiveness.
>
> **Search**: Kafka feeds a Search Indexer that maintains Elasticsearch indices per account. Full-text search on item names plus structured filtering on column values.
>
> **Multi-tenancy**: Shared infrastructure with logical isolation by account_id. Enterprise customers can get dedicated resources. Data residency handled by account-level region affinity.
>
> **Scale**: Cassandra and Kafka scale horizontally. Redis cluster sharded by board_id. Boards with 100K+ items use cursor-based pagination and virtual scrolling. Multi-region deployment with account affinity to a primary region."

---

## Common Mistakes

| Mistake | Why It's Bad | What to Do Instead |
|---------|-------------|-------------------|
| Fixed task schema (title, assignee, due date, done) | Misses the entire point -- enterprise teams need custom fields | Design a flexible column system from the start |
| Single relational DB for everything | Won't scale to millions of boards with millions of items | Use purpose-built stores: Cassandra for data, Redis for speed, Elasticsearch for search |
| No multi-tenancy design | This is a SaaS platform, not a single-team tool | Tenant isolation from day one: account_id in every query, data residency, permission boundaries |
| Ignoring real-time | Enterprise collaboration is real-time now | WebSocket architecture is a must |
| Flat item list without groups | Misses core UX of task management boards | Groups/sections are essential for organizing work |
| Over-designing the UI/frontend | This is a backend interview | Mention React + optimistic updates briefly, spend time on backend architecture |
| Not discussing the read/write tradeoff | Storage choice depends heavily on read vs. write patterns | Be explicit: high write volume (every cell edit is a write), high read volume (every board view) |
| Skipping permissions | Enterprise = strict access control | At minimum describe role-based board permissions |

---

## Connection to Monday.com's Actual Architecture

- **This IS Monday.com**: The question is essentially "design Monday.com." Lean into this. Reference their actual concepts: boards, groups, items, columns, column values.
- **mondayDB**: Monday.com's eng blog describes their Lambda Architecture (Redis speed layer + Cassandra batch layer) explicitly. This is the storage answer they want to hear.
- **Flexible column system**: Monday.com's public API exposes column types (status, person, date, text, number, formula, mirror, etc.). Your data model should mirror this.
- **GraphQL API**: Monday.com's API is entirely GraphQL. Designing the API as GraphQL shows alignment.
- **Kafka event backbone**: Monday.com uses Kafka for event propagation to WebSockets, search indexing, automations, integrations, and analytics.
- **Multi-region**: Monday.com serves enterprise customers globally with data residency requirements (EU, US, AU). Multi-region is not theoretical -- it's a real constraint.
- **Scale numbers**: 225K+ paying customers, millions of boards, billions of column values. Design for this magnitude.
- **Node.js/TypeScript backend**: Mention this when discussing the Board Service implementation.
- **Eng blog references**: Monday.com has published about their journey from monolith to microservices, their custom DB layer, and their approach to scaling real-time collaboration. Referencing this shows genuine interest.
- **Work OS concept**: Monday.com positions itself as a "Work OS" -- not just task management. The flexible schema is what enables this. Your design should explain why rigid schemas fail and flexible ones enable the "OS" concept.
