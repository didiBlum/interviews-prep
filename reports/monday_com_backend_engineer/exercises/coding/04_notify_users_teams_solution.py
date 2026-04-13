"""
Exercise 4: Notify Function (Team/User Resolution) - SOLUTION
===============================================================
Difficulty: Medium | Monday.com Real Interview Question

Time Complexity:  O(U + T) where U = total users, T = total team membership edges
Space Complexity: O(U + T) for visited set and result set
"""

from typing import Optional


class NotificationSystem:
    """
    A notification system that resolves teams to users and sends notifications.

    Design decisions:
    - Uses iterative DFS (stack-based) for team resolution to avoid recursion depth issues
    - Tracks visited teams to handle circular references and avoid redundant work
    - Collects all resolved users into a set for O(1) deduplication
    """

    def __init__(
        self,
        users: dict[str, str],      # {user_id: user_name}
        teams: dict[str, list[str]]  # {team_id: [member_ids]}
    ):
        self.users = users
        self.teams = teams
        self.notifications_log: list[tuple[str, str, str]] = []

    def resolve_members(self, entity_id: str) -> set[str]:
        """
        Resolve an entity ID (user or team) to a set of user IDs.

        Uses iterative DFS with a visited set to:
        1. Handle nested teams (arbitrary depth)
        2. Prevent infinite loops from circular references
        3. Avoid re-processing already-resolved teams
        """
        resolved_users: set[str] = set()
        visited_teams: set[str] = set()

        # Stack-based iterative DFS -- avoids recursion depth limits
        stack: list[str] = [entity_id]

        while stack:
            current_id = stack.pop()

            # Case 1: It's a known user -- add directly
            if current_id in self.users:
                resolved_users.add(current_id)

            # Case 2: It's a team we haven't visited yet -- expand its members
            elif current_id in self.teams and current_id not in visited_teams:
                visited_teams.add(current_id)
                # Push all team members onto the stack for processing
                for member_id in self.teams[current_id]:
                    stack.append(member_id)

            # Case 3: Already-visited team (circular ref) or unknown ID -- skip

        return resolved_users

    def notify(self, ids: list[str], message: str) -> list[str]:
        """
        Send a notification to all users resolved from the given IDs.

        Steps:
        1. Resolve each input ID to user IDs (handles teams, nesting, cycles)
        2. Union all resolved users into a single set (deduplication)
        3. Send notification to each unique user exactly once
        4. Return sorted list of notified user IDs
        """
        # Collect all unique user IDs across all input IDs
        all_users: set[str] = set()
        for entity_id in ids:
            all_users |= self.resolve_members(entity_id)

        # Notify each user exactly once, in sorted order for determinism
        notified: list[str] = []
        for user_id in sorted(all_users):
            user_name = self.users[user_id]
            self.notifications_log.append((user_id, user_name, message))
            notified.append(user_id)

        return notified


# ---------------------------------------------------------------------------
# Alternative approach: Recursive with memoization (cache)
# ---------------------------------------------------------------------------
class NotificationSystemRecursive:
    """
    Alternative implementation using recursive resolution with memoization.

    Tradeoff vs iterative:
    + Slightly more readable for some developers
    + Memoization cache speeds up repeated queries
    - Recursion depth limit for deeply nested teams (Python default: 1000)
    - Cache invalidation needed if teams change
    """

    def __init__(self, users: dict[str, str], teams: dict[str, list[str]]):
        self.users = users
        self.teams = teams
        self.notifications_log: list[tuple[str, str, str]] = []
        self._cache: dict[str, set[str]] = {}  # Memoization cache

    def resolve_members(self, entity_id: str, _visiting: Optional[set[str]] = None) -> set[str]:
        # Check cache first
        if entity_id in self._cache:
            return self._cache[entity_id]

        # Track which teams we're currently visiting (cycle detection)
        if _visiting is None:
            _visiting = set()

        # Base case: it's a user
        if entity_id in self.users:
            return {entity_id}

        # It's a team
        if entity_id in self.teams:
            # Cycle detection
            if entity_id in _visiting:
                return set()

            _visiting.add(entity_id)
            result: set[str] = set()
            for member_id in self.teams[entity_id]:
                result |= self.resolve_members(member_id, _visiting)
            _visiting.discard(entity_id)

            # Cache the result
            self._cache[entity_id] = result
            return result

        # Unknown ID
        return set()

    def notify(self, ids: list[str], message: str) -> list[str]:
        all_users: set[str] = set()
        for entity_id in ids:
            all_users |= self.resolve_members(entity_id)

        notified: list[str] = []
        for user_id in sorted(all_users):
            user_name = self.users[user_id]
            self.notifications_log.append((user_id, user_name, message))
            notified.append(user_id)
        return notified


# ---------------------------------------------------------------------------
# COMPLEXITY ANALYSIS
# ---------------------------------------------------------------------------
#
# Iterative DFS approach:
#   Time:  O(U + E) per call, where U = users, E = total membership edges
#          Each team is visited at most once, each edge traversed at most once.
#   Space: O(U + T) for the stack, visited set, and result set
#          T = number of teams, U = number of users
#
# Recursive with memoization:
#   Time:  O(U + E) for first call, O(1) for cached lookups thereafter
#   Space: O(U + T) for recursion stack + O(U * T) worst case for cache
#
# ---------------------------------------------------------------------------
# WHAT INTERVIEWERS LOOK FOR
# ---------------------------------------------------------------------------
#
# 1. CYCLE DETECTION: This is the main trap. Many candidates write naive recursion
#    that infinite-loops on circular team references. Mention it before they ask.
#
# 2. DEDUPLICATION: Using a set is the natural choice. Candidates who use lists
#    and check "if user not in list" get O(n^2) -- interviewers notice.
#
# 3. SEPARATION OF CONCERNS: resolve_members does resolution, notify does
#    notification. Don't mix them into one tangled function.
#
# 4. EDGE CASES: Empty teams, unknown IDs, duplicate input IDs, self-referencing
#    teams. Mention these proactively.
#
# 5. SCALABILITY DISCUSSION: What if there are millions of users/teams?
#    -> Caching resolved teams (memoization)
#    -> Lazy resolution (resolve on demand, not upfront)
#    -> Pre-compute and materialize team memberships in a database
#
# ---------------------------------------------------------------------------
# COMMON INTERVIEWER FOLLOW-UPS
# ---------------------------------------------------------------------------
#
# Q: "What if teams can change dynamically? How do you handle cache invalidation?"
# A: Use a dirty-flag per team. When a team's members change, mark it and all
#    ancestor teams as dirty. Alternatively, use a TTL cache or event-driven
#    invalidation. In practice, Monday.com likely uses an event bus -- when team
#    membership changes, publish an event that clears affected caches.
#
# Q: "How would you make this work at Monday.com's scale (millions of users)?"
# A: - Store team memberships in a graph database or adjacency table
#    - Pre-compute transitive closures for hot teams (materialized view)
#    - Use async notification with a message queue (Kafka/RabbitMQ)
#    - Batch notifications to avoid thundering herd
#    - Rate limiting per user to avoid notification spam
#
# Q: "What if we need to support 'exclude' lists or notification preferences?"
# A: After resolving all users, apply a filter step:
#    - Remove users in the exclude list
#    - Check each user's notification preferences (muted, DND, channel prefs)
#    - This is a post-resolution filter, keeping resolution logic clean
#
# Q: "How would you test this in production?"
# A: - Unit tests (as shown) for correctness
#    - Property-based tests (hypothesis) for random team structures
#    - Integration tests with real database
#    - Shadow mode: resolve but don't send, compare with expected output
#    - Monitoring: alert if resolution takes > N ms or returns > N users
#
# ---------------------------------------------------------------------------
# ALTERNATIVE APPROACHES
# ---------------------------------------------------------------------------
#
# 1. BFS instead of DFS:
#    - Use a queue instead of a stack
#    - Same complexity, slightly different traversal order
#    - No practical difference for this problem
#
# 2. Pre-computation (materialized transitive closure):
#    - At team creation/update time, compute and store all resolved users
#    - O(1) lookup at notification time
#    - Tradeoff: write-heavy, stale data risk, more storage
#    - Best for: read-heavy workloads (many notifications, rare team changes)
#
# 3. Union-Find (Disjoint Set Union):
#    - Not a natural fit here because teams can overlap
#    - Union-Find works best for disjoint partitions
#    - Mentioning why it doesn't fit shows depth of knowledge
