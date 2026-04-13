"""
Exercise 4: Notify Function (Team/User Resolution)
====================================================
Difficulty: Medium | Monday.com Real Interview Question

PROBLEM:
Implement a notification system where you can send a message to a list of IDs.
Each ID can refer to either a user or a team. Teams contain members, which can
be individual users OR other teams (nested teams).

You must:
1. Resolve all team IDs to their constituent user IDs (recursively for nested teams)
2. Avoid sending duplicate notifications (each user gets notified at most once)
3. Handle circular team references gracefully (team A contains team B, team B contains team A)
4. Be efficient - don't re-resolve teams you've already resolved

EXAMPLE:
    Given:
        users = {"u1": "Alice", "u2": "Bob", "u3": "Charlie", "u4": "Diana"}
        teams = {
            "t1": ["u1", "u2"],           # Team 1: Alice, Bob
            "t2": ["u2", "u3"],           # Team 2: Bob, Charlie
            "t3": ["t1", "u4"],           # Team 3: Team1 + Diana (nested)
            "t4": ["t1", "t2"],           # Team 4: Team1 + Team2 (nested teams)
        }

    notify(["t1", "u3"], "Hello!")
    -> Should notify: Alice, Bob, Charlie (no duplicates)

    notify(["t3"], "Hi!")
    -> Should notify: Alice, Bob, Diana (t3 -> t1 -> u1, u2 + u4)

    notify(["t4"], "Hey!")
    -> Should notify: Alice, Bob, Charlie (t4 -> t1, t2 -> u1, u2, u3)

CONSTRAINTS:
- Users and teams are identified by string IDs
- User IDs start with 'u', team IDs start with 't' (for clarity, but don't rely on prefix)
- Teams can be nested arbitrarily deep
- Circular references between teams must not cause infinite loops
- Each user should be notified exactly once regardless of how many teams they belong to
"""

from typing import Optional


class NotificationSystem:
    """
    A notification system that resolves teams to users and sends notifications.
    """

    def __init__(
        self,
        users: dict[str, str],      # {user_id: user_name}
        teams: dict[str, list[str]]  # {team_id: [member_ids]} (members can be users or teams)
    ):
        self.users = users
        self.teams = teams
        self.notifications_log: list[tuple[str, str, str]] = []  # [(user_id, user_name, message)]

    def resolve_members(self, entity_id: str) -> set[str]:
        """
        Given an entity ID (user or team), return the set of all user IDs
        that should be notified.

        Must handle:
        - Direct user IDs (return as-is)
        - Team IDs (resolve to member users, recursively)
        - Nested teams (teams containing other teams)
        - Circular references (don't infinite loop)

        Returns:
            set[str]: Set of user IDs
        """
        # TODO: Implement recursive resolution with cycle detection
        pass

    def notify(self, ids: list[str], message: str) -> list[str]:
        """
        Send a notification message to all users resolved from the given IDs.

        Args:
            ids: List of user IDs and/or team IDs
            message: The notification message

        Returns:
            list[str]: Sorted list of user IDs that were notified

        Must:
        - Resolve all team IDs to user IDs
        - Deduplicate so each user is notified exactly once
        - Log each notification in self.notifications_log
        - Return sorted list of notified user IDs
        """
        # TODO: Implement notification with deduplication
        pass


# ---------------------------------------------------------------------------
# Tests (run with: pytest 04_notify_users_teams.py -v)
# ---------------------------------------------------------------------------
import pytest


@pytest.fixture
def basic_system():
    """Basic notification system with users and teams."""
    users = {
        "u1": "Alice",
        "u2": "Bob",
        "u3": "Charlie",
        "u4": "Diana",
        "u5": "Eve",
    }
    teams = {
        "t1": ["u1", "u2"],
        "t2": ["u2", "u3"],
        "t3": ["t1", "u4"],        # nested: Team1 + Diana
        "t4": ["t1", "t2"],        # nested teams: Team1 + Team2
        "t5": ["t3", "u5"],        # deeply nested: Team3 + Eve
    }
    return NotificationSystem(users, teams)


@pytest.fixture
def circular_system():
    """System with circular team references."""
    users = {"u1": "Alice", "u2": "Bob", "u3": "Charlie"}
    teams = {
        "t1": ["u1", "t2"],        # t1 -> t2 -> t1 (circular)
        "t2": ["u2", "t1"],
        "t3": ["t1", "t2", "u3"],  # references both circular teams
    }
    return NotificationSystem(users, teams)


class TestResolveMembers:
    """Tests for the resolve_members method."""

    def test_resolve_single_user(self, basic_system):
        """A single user ID should resolve to itself."""
        result = basic_system.resolve_members("u1")
        assert result == {"u1"}

    def test_resolve_simple_team(self, basic_system):
        """A simple team should resolve to its member users."""
        result = basic_system.resolve_members("t1")
        assert result == {"u1", "u2"}

    def test_resolve_nested_team(self, basic_system):
        """A team containing another team should resolve recursively."""
        result = basic_system.resolve_members("t3")
        assert result == {"u1", "u2", "u4"}

    def test_resolve_deeply_nested_team(self, basic_system):
        """A deeply nested team (3 levels) should resolve all users."""
        result = basic_system.resolve_members("t5")
        assert result == {"u1", "u2", "u4", "u5"}

    def test_resolve_overlapping_teams(self, basic_system):
        """A team containing overlapping sub-teams should deduplicate."""
        result = basic_system.resolve_members("t4")
        assert result == {"u1", "u2", "u3"}

    def test_resolve_unknown_id(self, basic_system):
        """An unknown ID should return an empty set."""
        result = basic_system.resolve_members("unknown_id")
        assert result == set()


class TestNotify:
    """Tests for the notify method."""

    def test_notify_single_user(self, basic_system):
        """Notifying a single user."""
        result = basic_system.notify(["u1"], "Hello!")
        assert result == ["u1"]
        assert len(basic_system.notifications_log) == 1

    def test_notify_team(self, basic_system):
        """Notifying a team should reach all team members."""
        result = basic_system.notify(["t1"], "Team message")
        assert result == ["u1", "u2"]
        assert len(basic_system.notifications_log) == 2

    def test_notify_mixed_ids_deduplication(self, basic_system):
        """Mixing user and team IDs should not cause duplicate notifications."""
        result = basic_system.notify(["t1", "u2", "u3"], "Mixed")
        assert result == ["u1", "u2", "u3"]
        assert len(basic_system.notifications_log) == 3  # u2 only once

    def test_notify_overlapping_teams_deduplication(self, basic_system):
        """Overlapping teams should not cause duplicate notifications."""
        result = basic_system.notify(["t1", "t2"], "Overlap")
        assert result == ["u1", "u2", "u3"]
        assert len(basic_system.notifications_log) == 3  # u2 only once

    def test_notify_nested_team(self, basic_system):
        """Nested team notification should resolve all levels."""
        result = basic_system.notify(["t5"], "Deep")
        assert result == ["u1", "u2", "u4", "u5"]
        assert len(basic_system.notifications_log) == 4

    def test_notify_empty_list(self, basic_system):
        """Notifying with an empty list should notify nobody."""
        result = basic_system.notify([], "Nobody")
        assert result == []
        assert len(basic_system.notifications_log) == 0


class TestCircularReferences:
    """Tests for handling circular team references."""

    def test_circular_does_not_loop(self, circular_system):
        """Circular team references should not cause infinite loops."""
        result = circular_system.resolve_members("t1")
        assert result == {"u1", "u2"}

    def test_circular_both_teams(self, circular_system):
        """Both teams in a circular reference should resolve correctly."""
        result = circular_system.resolve_members("t2")
        assert result == {"u1", "u2"}

    def test_circular_with_extra_member(self, circular_system):
        """A team referencing circular teams plus an extra user."""
        result = circular_system.notify(["t3"], "Circular")
        assert result == ["u1", "u2", "u3"]


class TestEdgeCases:
    """Additional edge case tests."""

    def test_empty_team(self):
        """A team with no members."""
        system = NotificationSystem({"u1": "Alice"}, {"t1": []})
        result = system.notify(["t1"], "Empty team")
        assert result == []

    def test_duplicate_ids_in_input(self, basic_system):
        """Duplicate IDs in the input list should still notify once."""
        result = basic_system.notify(["u1", "u1", "u1"], "Dupes")
        assert result == ["u1"]
        assert len(basic_system.notifications_log) == 1

    def test_notification_log_content(self, basic_system):
        """Check that the notification log contains correct data."""
        basic_system.notify(["u1"], "Test message")
        assert basic_system.notifications_log[0] == ("u1", "Alice", "Test message")


# ---------------------------------------------------------------------------
# HINTS (reveal progressively if stuck)
# ---------------------------------------------------------------------------

# HINT 1: Use a set called `visited` to track which team IDs you've already
#          started resolving. Before resolving a team, check if it's in visited.
#          This handles both circular references and avoids redundant work.

# HINT 2: resolve_members can be implemented iteratively with a stack/queue
#          or recursively. The key is:
#          - If the ID is a user, add to result set
#          - If the ID is a team (and not visited), mark visited, then process members
#          - If the ID is unknown, skip it

# HINT 3: For the notify method, collect all user IDs from resolve_members for
#          each input ID, union them into a single set, then iterate the sorted
#          set to send notifications and build the log.

# ---------------------------------------------------------------------------
# COMPLEXITY TARGETS
# ---------------------------------------------------------------------------
# Time:  O(U + T) where U = total users, T = total team memberships
#         (each user and team membership edge is visited at most once)
# Space: O(U + T) for the visited set and result set
