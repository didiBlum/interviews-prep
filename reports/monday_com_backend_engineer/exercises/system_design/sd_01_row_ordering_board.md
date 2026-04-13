# System Design Exercise 1: Row Ordering in a Board

## The Prompt (As Asked in Interview)

> "Design the ordering of rows inside a board, end-to-end from client to server and DB. How to implement order and movement of items, handle simultaneous changes."

---

## Time Budget (45 Minutes)

| Phase | Minutes | What to Cover |
|-------|---------|---------------|
| Clarify requirements | 5 | Scale, consistency model, collaboration needs |
| High-level design | 8 | Client -> API -> Service -> DB flow, draw the diagram |
| Ordering data model | 10 | How order is represented and stored (this is the core) |
| Concurrent edits & conflict resolution | 10 | Simultaneous reorder handling, optimistic locking |
| Monday.com-specific storage | 7 | mondayDB (Redis + Cassandra), why Lambda Architecture fits |
| Scale & edge cases | 5 | Boards with 10K+ rows, bulk moves, undo |

---

## Clarifying Questions to Ask

1. **Board size range** -- "What's the typical number of rows per board? Tens, thousands, hundreds of thousands?" (Monday.com boards can have up to 10K+ items; subitems add more.)
2. **Grouping** -- "Are rows organized into groups/sections within a board, or is it a flat list?" (Monday.com has groups -- this changes the ordering scope.)
3. **Multi-user concurrency** -- "How many users might be editing the same board simultaneously? Is real-time collaboration a hard requirement?"
4. **Ordering granularity** -- "Is order per-view or per-board? Can different users see different orderings?" (Monday.com supports custom views with sorts/filters.)
5. **Move types** -- "Do we need to support single-row moves, multi-select bulk moves, and cross-group moves?"
6. **Consistency model** -- "Is eventual consistency acceptable, or do all users need to see the exact same order at the same moment?"
7. **Undo/redo** -- "Do we need to support undoing a reorder?"
8. **Sort vs. manual order** -- "When a board has a sort applied, does manual ordering still need to persist underneath?"

---

## Step-by-Step Framework

### Step 1: Define the Ordering Model (This Is the Core Decision)

Three main approaches -- discuss tradeoffs of each:

**Option A: Integer position column**
- Each row has `position: INTEGER` (e.g., 1, 2, 3, ...).
- Moving row from position 5 to position 2 requires updating positions 2, 3, 4, 5.
- Problem: O(n) writes on every move. Catastrophic at scale.
- Verdict: Too expensive. Reject but mention why.

**Option B: Fractional / float ordering**
- Each row has `position: FLOAT` (e.g., 1.0, 2.0, 3.0).
- Moving between positions 2.0 and 3.0 gives new position 2.5.
- Problem: Precision exhaustion after many moves (2.5, 2.25, 2.125...). Requires periodic rebalancing.
- Verdict: Simple, works well with periodic normalization. Good starting point.

**Option C: String-based lexicographic ordering (RECOMMENDED)**
- Each row has `position: STRING` using a lexicographic scheme (e.g., "a", "b", "c" or a library like `fractional-indexing`).
- Moving between "b" and "c" produces "bV" (midpoint in character space).
- Advantages: No precision loss for a very long time, single-row write per move, natural sort in DB.
- Used by: Figma, Linear, Notion -- and likely Monday.com given their scale.
- Verdict: Best approach. Recommend this.

### Step 2: Data Model

```
Board
  id: UUID
  account_id: UUID

Group (section within a board)
  id: UUID
  board_id: UUID
  position: STRING  // lexicographic order among groups

Item (row)
  id: UUID
  board_id: UUID
  group_id: UUID
  position: STRING  // lexicographic order within the group
  updated_at: TIMESTAMP
  version: INTEGER  // for optimistic concurrency
```

### Step 3: End-to-End Flow

```
Client (React)
  |
  | 1. User drags row -- optimistic UI update immediately
  |
  v
API Gateway (GraphQL -- Monday.com uses GraphQL)
  |
  | 2. Mutation: moveItem(itemId, targetGroupId, afterItemId, beforeItemId)
  |
  v
Board Service (Node.js/TypeScript)
  |
  | 3. Calculate new position string between afterItem.position and beforeItem.position
  | 4. Optimistic lock: check item.version matches expected
  | 5. Write new position + increment version
  |
  v
mondayDB
  |-- Redis (speed layer): immediate read consistency for active boards
  |-- Cassandra (batch layer): durable storage, eventually consistent
  |
  | 6. Publish event to Kafka: "item.position_changed"
  |
  v
Kafka -> WebSocket Service
  |
  | 7. Push update to all other clients viewing this board
  |
  v
Other Clients: apply remote position update
```

### Step 4: Handling Simultaneous Changes

**Scenario**: User A moves item X to position between B and C. User B simultaneously moves item Y to the same gap.

**Resolution with lexicographic ordering**:
- User A calculates midpoint("b", "c") = "bV"
- User B calculates midpoint("b", "c") = "bV"
- Conflict: two items with same position string.

**Solution -- Server-side arbitration**:
1. Each move request includes `expectedVersion` of the item.
2. Server uses optimistic locking (compare-and-set in Redis).
3. First request succeeds. Second request finds version mismatch.
4. Second request re-reads current positions, recalculates midpoint (now between "b" and "bV" or "bV" and "c"), and retries.
5. Client receives the canonical position via WebSocket and corrects if needed.

**Alternative -- CRDT-based approach** (mention for bonus points):
- Use a list CRDT (e.g., RGA or Logoot) where each position is a unique identifier.
- Concurrent insertions at the same position are deterministically resolved by user ID tiebreaker.
- More complex but eliminates all conflicts. Mention that Monday.com's WorkForms and collaborative editing may use CRDTs.

### Step 5: Storage in mondayDB

**Redis (Speed Layer)**:
- Sorted Set per board-group: `board:{boardId}:group:{groupId}:items`
- Score = lexicographic position (or numeric hash of position string)
- `ZRANGEBYSCORE` for paginated retrieval of ordered items
- TTL-based eviction for inactive boards

**Cassandra (Batch Layer)**:
- Partition key: `(board_id, group_id)`
- Clustering column: `position` (allows range queries in order)
- `SELECT * FROM items WHERE board_id = ? AND group_id = ? ORDER BY position ASC`
- Handles boards that fall out of Redis cache

**Write path**:
1. Write to Redis first (immediate consistency for active users)
2. Publish to Kafka
3. Kafka consumer writes to Cassandra (durable, async)

**Read path**:
1. Check Redis -- if cache hit, return sorted items
2. Cache miss -- read from Cassandra, populate Redis, return

---

## Key Components to Draw

1. **Client-Server flow diagram**: React -> GraphQL API -> Board Service -> mondayDB (Redis + Cassandra) -> Kafka -> WebSocket -> Other Clients
2. **Data model**: Board -> Groups -> Items with position strings
3. **Lexicographic ordering illustration**: Show "a", "n", "z" and inserting between "n" and "z" produces "t", then between "n" and "t" produces "q"
4. **Concurrent move sequence diagram**: Two users moving items simultaneously, showing version check, rejection, retry
5. **mondayDB read/write paths**: Lambda Architecture diagram with speed and batch layers

---

## Deep Dive Areas (Where Interviewer Probes)

### 1. "What happens when position strings get very long?"
- After thousands of moves to the same gap, strings grow. Solution: **periodic rebalancing** -- a background job reads all items in a group, assigns fresh evenly-spaced position strings, writes them in a batch.
- Trigger: when any position string exceeds a threshold length (e.g., 50 chars).
- Must be done atomically (or with a lock) to avoid conflicts during rebalancing.

### 2. "How does this work across regions?"
- Monday.com runs multi-region. If two users in different regions reorder simultaneously:
  - Each region's Redis has local state.
  - Kafka replicates events cross-region.
  - Conflict resolution: last-writer-wins with vector clocks, or route all writes for a board to a single "owner" region.
  - Better: use a single-leader model per board (board affinity to a region) to avoid cross-region conflicts.

### 3. "What about boards with 50K items?"
- Don't load all positions into memory. Use cursor-based pagination.
- Redis sorted set handles this efficiently with `ZRANGEBYSCORE ... LIMIT offset count`.
- Client uses virtual scrolling -- only requests visible range + buffer.

### 4. "How does sorting interact with manual ordering?"
- Manual `position` is always stored.
- When a user applies a sort (e.g., by due date), the UI ignores `position` and sorts client-side or server-side by the sort column.
- When sort is removed, manual `position` order is restored.
- Important: sorting is a **view-level** concern, not a data mutation.

### 5. "How do you handle undo?"
- Before executing a move, store `{itemId, previousGroupId, previousPosition}` in an undo stack (client-side or in a short-lived Redis key per user session).
- Undo = move the item back to its previous position (same flow as a normal move).

---

## Sample Answer Outline (Strong Skeleton)

> "I'd design this around **lexicographic position strings** stored per item, scoped to their group within a board. Let me walk through the full flow.
>
> **Data model**: Each item has a `position` string and a `version` integer. Groups are ordered the same way within a board.
>
> **Write flow**: When a user drags item X between items A and B, the client immediately updates the UI (optimistic). It sends a GraphQL mutation `moveItem(itemId, afterId, beforeId)` to the backend. The Board Service reads the position strings of A and B, computes the lexicographic midpoint, checks the item's version for optimistic locking, writes the new position to Redis, publishes to Kafka, and returns success. Kafka consumers write to Cassandra for durability and fan out to WebSocket connections for other clients.
>
> **Concurrency**: Optimistic locking on the item version prevents lost updates. If two users move different items to the same gap, both succeed with distinct midpoints (statistically). If they move the same item, the second request fails the version check and the client retries after receiving the authoritative state via WebSocket.
>
> **Storage in mondayDB**: Redis sorted sets for the speed layer give us O(log n) insert and range queries. Cassandra with clustering on position gives ordered reads from durable storage. This is Monday.com's Lambda Architecture.
>
> **Edge cases**: Position string length growth is handled by periodic rebalancing. Cross-region is handled by board-level region affinity. Large boards use cursor-based pagination with virtual scrolling."

---

## Common Mistakes

| Mistake | Why It's Bad | What to Do Instead |
|---------|-------------|-------------------|
| Using integer positions (1, 2, 3...) | O(n) updates per move -- won't scale | Use lexicographic strings or fractional indexing |
| Ignoring concurrency entirely | This is half the question | Discuss optimistic locking, version vectors, or CRDTs |
| Treating it as a single-user problem | Monday.com is inherently collaborative | Always design for multi-client from the start |
| Proposing a linked list in the DB | Traversal requires N reads, no range queries | Use a sortable position column |
| Not mentioning the real-time update path | Interviewer expects end-to-end thinking | Include WebSocket/SSE push to other clients |
| Over-engineering with full CRDT from the start | Shows poor judgment on complexity tradeoffs | Start with lexicographic + optimistic locking, mention CRDT as an evolution |
| Forgetting about groups within a board | Monday.com boards have groups -- it's core UX | Scope ordering to group level |

---

## Connection to Monday.com's Actual Architecture

- **mondayDB**: Monday.com's eng blog describes their custom DB layer combining Redis (speed) and Cassandra (batch) in a Lambda Architecture. This exercise directly maps to it -- Redis sorted sets for hot boards, Cassandra for persistence.
- **GraphQL API**: Monday.com exposes a public GraphQL API. Item mutations like `move_item_to_group` and `change_item_position` are real endpoints -- your design should align with this.
- **Kafka**: Monday.com uses Kafka as the backbone for event propagation. The "position changed" event flowing through Kafka to WebSocket subscribers is consistent with their architecture.
- **Node.js/TypeScript**: The Board Service would be a Node.js microservice, consistent with their stack.
- **Multi-region**: Monday.com serves global customers with multi-region deployments. Discussing region affinity for boards shows awareness of their infrastructure.
- **Scale numbers**: Monday.com serves 225K+ customers. A popular board might have 100 concurrent users. Design for that concurrency level.
- **Real-time collaboration**: Monday.com's UI updates in real-time when other users make changes. The WebSocket fan-out pattern is core to their product experience.
