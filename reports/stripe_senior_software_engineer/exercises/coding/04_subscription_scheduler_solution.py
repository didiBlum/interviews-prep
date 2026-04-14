"""
Email Subscription Scheduler — Solution
=========================================

Approach: Generate emails per subscription, handle mutations, sort.
"""

from dataclasses import dataclass


@dataclass
class Subscription:
    name: str
    plan: str
    begin_date: int
    duration_days: int


@dataclass
class PlanChange:
    name: str
    new_plan: str
    change_date: int


@dataclass
class Renewal:
    name: str
    renew_date: int


@dataclass
class Email:
    date: int
    name: str
    email_type: str
    plan: str


def _emails_for_sub(sub: Subscription) -> list[Email]:
    """Generate emails for a single subscription."""
    end_date = sub.begin_date + sub.duration_days
    warning_date = end_date - 15

    emails = [Email(sub.begin_date, sub.name, "welcome", sub.plan)]

    if warning_date > sub.begin_date:
        emails.append(Email(warning_date, sub.name, "expiry_warning", sub.plan))

    emails.append(Email(end_date, sub.name, "expired", sub.plan))
    return emails


def _sort_emails(emails: list[Email]) -> list[Email]:
    return sorted(emails, key=lambda e: (e.date, e.name))


def generate_emails(subscriptions: list[Subscription]) -> list[Email]:
    all_emails = []
    for sub in subscriptions:
        all_emails.extend(_emails_for_sub(sub))
    return _sort_emails(all_emails)


def generate_emails_with_changes(
    subscriptions: list[Subscription],
    changes: list[PlanChange],
) -> list[Email]:
    # Index changes by name
    change_map: dict[str, PlanChange] = {}
    for c in changes:
        change_map[c.name] = c

    all_emails = []
    for sub in subscriptions:
        if sub.name in change_map:
            change = change_map[sub.name]
            original_end = sub.begin_date + sub.duration_days
            remaining = original_end - change.change_date

            # Old subscription: only welcome (truncated at change_date)
            all_emails.append(
                Email(sub.begin_date, sub.name, "welcome", sub.plan)
            )

            # New subscription from change_date
            new_sub = Subscription(
                sub.name, change.new_plan, change.change_date, remaining
            )
            all_emails.extend(_emails_for_sub(new_sub))
        else:
            all_emails.extend(_emails_for_sub(sub))

    return _sort_emails(all_emails)


def generate_emails_with_renewals(
    subscriptions: list[Subscription],
    renewals: list[Renewal],
) -> list[Email]:
    # Index renewals by name
    renewal_map: dict[str, Renewal] = {}
    for r in renewals:
        renewal_map[r.name] = r

    all_emails = []
    for sub in subscriptions:
        if sub.name in renewal_map:
            # Extend end_date by original duration
            new_duration = sub.duration_days + sub.duration_days
            extended_sub = Subscription(
                sub.name, sub.plan, sub.begin_date, new_duration
            )
            all_emails.extend(_emails_for_sub(extended_sub))
        else:
            all_emails.extend(_emails_for_sub(sub))

    return _sort_emails(all_emails)


# ============ Complexity Analysis ============
# Time: O(N log N) where N = total emails generated
#   - Each subscription generates O(1) emails
#   - Sorting dominates
# Space: O(N) for the email list

# ============ Common Interviewer Follow-ups ============
# Q: "What if a user has multiple plan changes?"
# A: Process changes in chronological order. Each change truncates
#    the current sub and starts a new one. Chain them.
#
# Q: "What if a renewal happens before the original end date?"
# A: Clarify: does it extend from the renewal date or the original end?
#    The problem says extend from the original end date.
#
# Q: "How would you handle timezones?"
# A: Store all dates in UTC. Convert to user timezone for display.

# ============ What Interviewers Look For ============
# 1. Clean helper function for generating emails per subscription
# 2. Correct handling of edge cases (short subscriptions, warning before start)
# 3. Immutable approach: create new subscriptions, don't mutate
# 4. Sort stability (date, then name)
# 5. Clear data model (Email dataclass with all relevant fields)


# ============ TESTS ============

def test_basic_emails():
    subs = [
        Subscription("Alice", "pro", 1, 30),
        Subscription("Bob", "free", 5, 60),
    ]
    emails = generate_emails(subs)
    assert len(emails) == 6
    assert emails[0] == Email(1, "Alice", "welcome", "pro")
    assert emails[1] == Email(5, "Bob", "welcome", "free")
    assert emails[2] == Email(16, "Alice", "expiry_warning", "pro")

def test_no_warning_short_sub():
    subs = [Subscription("Alice", "trial", 1, 10)]
    emails = generate_emails(subs)
    assert len(emails) == 2
    assert emails[0].email_type == "welcome"
    assert emails[1].email_type == "expired"

def test_plan_change():
    subs = [Subscription("Alice", "free", 1, 30)]
    changes = [PlanChange("Alice", "pro", 10)]
    emails = generate_emails_with_changes(subs, changes)
    types = [(e.date, e.email_type, e.plan) for e in emails]
    assert (1, "welcome", "free") in types
    assert (10, "welcome", "pro") in types
    assert (31, "expired", "pro") in types

def test_renewal():
    subs = [Subscription("Alice", "pro", 1, 30)]
    renewals = [Renewal("Alice", 25)]
    emails = generate_emails_with_renewals(subs, renewals)
    assert any(e.date == 46 and e.email_type == "expiry_warning" for e in emails)
    assert any(e.date == 61 and e.email_type == "expired" for e in emails)

def test_same_date_sorting():
    subs = [
        Subscription("Bob", "free", 1, 30),
        Subscription("Alice", "pro", 1, 30),
    ]
    emails = generate_emails(subs)
    assert emails[0].name == "Alice"
    assert emails[1].name == "Bob"


if __name__ == "__main__":
    test_basic_emails()
    test_no_warning_short_sub()
    test_plan_change()
    test_renewal()
    test_same_date_sorting()
    print("All tests passed!")
