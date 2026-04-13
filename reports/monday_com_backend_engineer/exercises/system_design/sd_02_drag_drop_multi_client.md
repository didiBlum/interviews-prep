# System Design Exercise 2: Drag-and-Drop with Multi-Client Support

## The Prompt (As Asked in Interview)

> "Design a system for drag-and-drop rows in a list. How to do it efficiently + how to handle multi-client support."

This overlaps with SD Exercise 1 (Row Ordering) but shifts focus toward the **real-time collaboration layer**, **optimistic UI updates**, and **conflict resolution** between concurrent clients.

---

## Time Budget (45 Minutes)

| Phase | Minutes | What to Cover |
|-------|---------|---------------|
| Clarify requirements | 5 | What "efficiently" means here, how many concurrent clients |
| Client-side drag UX architecture | 8 | Optimistic updates, drag state, animation |
| Server-side mutation flow | 7 | API contract, position calculation, persistence |
| Real-time multi-client sync | 12 | WebSocket architecture, event propagation, presence |
| Conflict resolution deep dive | 8 | What happens when two users drag at the same time |
| Performance & edge cases | 5 | Latency budget, offline, large lists |

---

## Clarifying Questions to Ask

1. **List characteristics** -- "Is this a flat list or a nested/grouped structure? How large can the list get?"
2. **Drag operations** -- "Just single-row drag, or also multi-select drag? Can items be dragged across different lists/groups?"
3. **Concurrency level** -- "What's the expected number of simultaneous editors on the same list? 2-5, or potentially hundreds?"
4. **Latency tolerance** -- "Should the drag feel instant locally (optimistic), or do we wait for server confirmation?"
5. **Conflict visibility** -- "When two users conflict, should the 'losing' user see a visual indication, or should it resolve silently?"
6. **Presence indicators** -- "Should users see who else is currently viewing or editing the list? Should they see another user's drag in progress?"
7. **Offline support** -- "Do we need to handle the case where a user goes offline mid-drag and comes back?"
8. **Undo requirements** -- "Does Ctrl+Z need to undo another user's move, or only your own?"

---

## Step-by-Step Framework

### Step 1: Client-Side Drag Architecture

**Drag Lifecycle on the Initiating Client**:

```
1. onDragStart(itemId)
   - Capture draggedItem and its original position
   - Store undo snapshot: { itemId, originalPosition, originalGroupId }
   - Apply CSS transform for visual feedback (not reflow -- performance)
   - Optional: broadcast "user is dragging" presence event

2. onDragOver(targetPosition)
   - Show drop indicator (insertion line between rows)
   - No server calls during drag -- purely local state
   - Throttle visual updates to 60fps using requestAnimationFrame

3. onDrop(itemId, afterItemId, beforeItemId)
   - IMMEDIATELY update local state (optimistic reorder)
   - Send mutation to server
   - If server confirms: done
   - If server rejects: rollback to undo snapshot, show brief flash

4. onDragCancel()
   - Restore original position
   - No server call needed
```

**Why optimistic updates matter**: The drag-drop interaction has a latency budget of ~50ms to feel responsive. Server round-trip is 50-200ms. Users must see the result instantly.

### Step 2: API Contract

```graphql
mutation MoveItem($input: MoveItemInput!) {
  moveItem(input: $input) {
    item {
      id
      position
      groupId
      version
    }
    conflictResolution {
      applied: Boolean
      serverPosition: String  # actual position assigned
    }
  }
}

input MoveItemInput {
  itemId: ID!
  targetGroupId: ID
  afterItemId: ID        # item to place after (null = first)
  beforeItemId: ID       # item to place before (null = last)
  expectedVersion: Int!  # optimistic concurrency
}
```

### Step 3: Server-Side Flow

```
GraphQL Mutation
  |
  v
Board Service (Node.js)
  |
  | 1. Validate: does the item exist? does the user have permission?
  | 2. Read afterItem.position and beforeItem.position from Redis
  | 3. Compute new position = lexicographicMidpoint(after, before)
  | 4. Compare-and-set: if item.version == expectedVersion, write new position + version++
  |    - If CAS fails: return conflict, include current server state
  | 5. Write to Redis (speed layer)
  | 6. Publish to Kafka: { event: "item.moved", itemId, newPosition, newGroup, actorUserId, boardId }
  |
  v
Kafka Consumer -> WebSocket Gateway
  |
  | 7. Fan out to all WebSocket connections subscribed to this board
  |    EXCEPT the actor (they already applied optimistic update)
  |
  v
Other Clients: receive event, animate item to new position
```

### Step 4: Multi-Client Real-Time Sync Architecture

**WebSocket Infrastructure**:

```
                    +-------------------+
                    |   Load Balancer   |
                    | (sticky sessions) |
                    +-------------------+
                     /        |        \
            +--------+  +--------+  +--------+
            |  WS    |  |  WS    |  |  WS    |
            | Server |  | Server |  | Server |
            |   1    |  |   2    |  |   3    |
            +--------+  +--------+  +--------+
                 \          |          /
                  +------- Redis Pub/Sub ------+
                  |    (or Kafka consumer      |
                  |     per WS server)         |
                  +----------------------------+
```

**Subscription model**:
- When a client opens a board, it subscribes: `ws.subscribe("board:{boardId}")`
- The WS server tracks: `Map<boardId, Set<connectionId>>`
- Cross-server fanout via Redis Pub/Sub or Kafka consumer groups (each WS server in its own consumer group for broadcast semantics)

**Event types pushed to clients**:

| Event | Payload | Purpose |
|-------|---------|---------|
| `item.moved` | itemId, newPosition, newGroupId, actorId | Another user moved an item |
| `item.moved.batch` | [{itemId, newPosition}...] | Bulk reorder / rebalancing |
| `user.dragging` | userId, itemId, currentHoverPosition | Live drag presence (optional) |
| `user.drag_ended` | userId | Clear drag presence indicator |

### Step 5: Conflict Resolution Scenarios

**Scenario A: Two users move DIFFERENT items to the same gap**

```
Initial order: [A, B, C, D]

User 1: moves D between A and B
User 2: moves C between A and B (simultaneously)

Server processes User 1 first:
  - D.position = midpoint(A.pos, B.pos) = "m"
  - Order: [A, D, B, C]  (but User 2 doesn't know about D's move yet)

Server processes User 2:
  - C's mutation says afterItemId=A, beforeItemId=B
  - Server re-reads: A.pos and B.pos. D is now between them.
  - Server places C at midpoint(A.pos, B.pos) which might equal D.pos
  - TIE-BREAKING: use itemId comparison. C.id < D.id -> C goes first.
  - Or: server notices D is now at midpoint and places C at midpoint(A.pos, D.pos)

Final order: [A, C, D, B] -- both moves honored, deterministic result.
All clients receive both events and converge.
```

**Scenario B: Two users move THE SAME item to different places**

```
Initial order: [A, B, C, D]

User 1: moves B after C  (expectedVersion: 5)
User 2: moves B after D  (expectedVersion: 5)

Server processes User 1 first:
  - version check passes (5 == 5), writes B.position = after C, version = 6

Server processes User 2:
  - version check FAILS (5 != 6)
  - Returns: { applied: false, serverPosition: <B's actual position after C> }

User 2's client:
  - Receives conflict response
  - Sees their drag was overridden
  - Animates B to its server-authoritative position (after C)
  - Optional: shows toast "Another user moved this item"
```

**Scenario C: User moves an item that was just deleted by another user**

```
Server returns: 404 or { applied: false, reason: "ITEM_DELETED" }
Client removes the item from local state, shows brief notification.
```

### Step 6: Presence -- Showing Live Drags (Advanced)

For high-collaboration scenarios, show other users' drags in real-time:

- On `dragStart`: client sends lightweight presence event via WebSocket (not through API/Kafka -- too slow)
- WS server broadcasts directly to board subscribers via Redis Pub/Sub
- Other clients show a ghost/shadow of the item being dragged with the user's avatar
- On `dragEnd` or timeout (3s): clear presence
- This is **ephemeral** -- no persistence needed, no Kafka, no DB write

**Important**: Presence events are fire-and-forget. Losing one is fine. Do NOT route through the same pipeline as mutations.

---

## Key Components to Draw

1. **Client state machine**: IDLE -> DRAGGING -> DROPPED (optimistic) -> CONFIRMED / ROLLBACK
2. **Sequence diagram for successful move**: Client A drags -> Server -> Kafka -> WS -> Client B animates
3. **Sequence diagram for conflict**: Client A and B drag same item -> Server accepts A, rejects B -> B rolls back
4. **WebSocket fanout architecture**: Load balancer -> WS servers -> Redis Pub/Sub crossbar -> clients
5. **Presence vs. mutation event pipeline**: Show two separate paths -- fast ephemeral (WS direct) vs. durable (API -> Kafka -> WS)

---

## Deep Dive Areas (Where Interviewer Probes)

### 1. "How do you make the drag feel instant?"
- **Optimistic UI**: Update local list order on drop, before server response.
- **No reflows during drag**: Use CSS `transform: translate()` for the dragged element, not layout changes.
- **Batch DOM updates**: Use React's batched state updates or `requestAnimationFrame`.
- **Debounce presence events**: Send hover position updates at most every 100ms, not every mouse move.

### 2. "What if a WebSocket connection drops mid-operation?"
- The mutation is sent via HTTP (GraphQL), not WebSocket. WS is only for receiving updates.
- If WS drops: client reconnects, requests current board state (full refresh or delta since last known version).
- Board version counter: client sends `lastSeenVersion` on reconnect, server sends all events since then (stored in Kafka or a short Redis list).
- Monday.com likely uses a **catch-up** mechanism: on reconnect, fetch board snapshot + replay missed events.

### 3. "How do you handle 100 users on the same board?"
- WebSocket fanout must be efficient. Don't serialize per-connection -- serialize once per event, send to all.
- Rate-limit mutations: if the same item is moved 10 times in 1 second, coalesce on the server or reject rapid-fire.
- Presence events: throttle to 1/second per user. 100 users * 1 event/s = manageable.
- Consider: at 100 users, do you even show individual drags? Maybe switch to "N users editing" aggregate.

### 4. "How does this work across Monday.com's multi-region deployment?"
- Board affinity: each board is "owned" by a region. All mutations route to the owner region.
- WebSocket connections from other regions proxy to the owner or consume from cross-region Kafka replication.
- Tradeoff: adds ~50-100ms latency for users not in the owner region, but avoids split-brain ordering conflicts.

### 5. "What about accessibility?"
- Drag-and-drop must have keyboard alternatives: select item, arrow keys to move, Enter to confirm.
- Keyboard moves go through the same mutation path.
- Screen readers: announce "Item X moved to position Y" via ARIA live regions.
- Monday.com's public accessibility commitment means this is not optional.

---

## Sample Answer Outline (Strong Skeleton)

> "I'll design this in three layers: the client drag UX, the server mutation path, and the multi-client sync layer.
>
> **Client**: On drag start, I capture the item's original position for potential rollback. During the drag, everything is local -- CSS transforms, no server calls. On drop, I immediately reorder the local list (optimistic update) and fire a GraphQL mutation with `afterItemId`, `beforeItemId`, and `expectedVersion`. If the server confirms, we're done. If it rejects due to a version conflict, the client rolls back and applies the server's authoritative state.
>
> **Server**: The Board Service computes a lexicographic midpoint position string between the two neighbors. It uses compare-and-set on the item's version for concurrency control. On success, it writes to Redis (speed layer), publishes an `item.moved` event to Kafka, and Kafka consumers in Cassandra write for durability.
>
> **Multi-client sync**: Each board has a set of WebSocket subscribers. Kafka events are consumed by WS gateway servers, which fan out to all subscribers except the actor. For live drag presence (showing a ghost of another user's drag), I use a separate fast path: WebSocket -> Redis Pub/Sub -> other WS servers -> clients. This is ephemeral and fire-and-forget.
>
> **Conflict resolution**: If two users move different items to the same gap, both succeed -- lexicographic midpoints with item ID tiebreaking ensure deterministic ordering. If two users move the same item, optimistic locking means the second one fails and gets corrected by the server's authoritative response plus the WebSocket event.
>
> **Scale**: Redis Pub/Sub for WebSocket cross-server fanout. Board-level region affinity for multi-region consistency. Throttled presence events to handle high-collaboration boards."

---

## Common Mistakes

| Mistake | Why It's Bad | What to Do Instead |
|---------|-------------|-------------------|
| Waiting for server before updating UI | Makes drag feel laggy (200ms+) | Optimistic update on drop, rollback on conflict |
| Sending server requests during drag (on every hover) | Floods the server with useless intermediate states | Only send on drop. Presence is separate + throttled |
| Using WebSocket for mutations | Unreliable delivery, hard to handle errors | Use HTTP (GraphQL) for mutations, WS only for receiving broadcasts |
| Ignoring the "what if WS disconnects" case | Clients get permanently out of sync | Implement reconnect + catch-up (delta or full refresh) |
| Designing only for 2 users | Monday.com boards can have many concurrent users | Design for N users, discuss throttling and coalescing |
| Not separating presence from persistence | Routing ephemeral drag-hover through Kafka adds unnecessary latency | Two pipelines: fast (presence via Pub/Sub) and durable (mutations via Kafka) |
| Forgetting about non-drag reordering | Sort, filter, bulk operations also change visible order | Discuss how manual position persists beneath view-level sorts |

---

## Connection to Monday.com's Actual Architecture

- **Real-time collaboration**: Monday.com's core product value is real-time team collaboration. Every board update propagates instantly to all viewers. This question tests whether you can build that.
- **GraphQL API**: Monday.com's API is GraphQL-based. The mutation contract you design should feel natural alongside their existing `change_column_value`, `move_item_to_group` mutations.
- **WebSocket infrastructure**: Monday.com uses WebSockets for live board updates. Their engineering has discussed the challenge of scaling WS connections across their user base.
- **Kafka as event backbone**: All state changes flow through Kafka, enabling decoupled consumers (WS fanout, search indexing, audit logs, automations, integrations).
- **mondayDB speed layer (Redis)**: Redis sorted sets serve the "current board state" for active boards. This is why reads feel instant despite Cassandra being the source of truth.
- **React frontend**: Monday.com's frontend is React. Optimistic state management (likely using something like Apollo Client's cache or a custom state manager) is central to their UX.
- **Multi-region**: Their global deployment means you must consider where mutations are processed relative to where users are connected. Board affinity avoids distributed consensus overhead.
- **Performance culture**: Monday.com eng blog posts emphasize performance -- they measure interaction-to-paint latency carefully. Showing awareness of the 50ms budget for drag responsiveness resonates.
