"""
Email Subscription Scheduler
=============================
Source: Stripe onsite coding round (linkjob.ai, 1point3acres, 2025-2026)

Problem:
Design a system that schedules notification emails for subscription lifecycles.

Part 1: Given subscriptions, generate scheduled emails.
  - Each subscription: {name, plan, begin_date, duration_days}
  - Generate emails:
    - "welcome" on begin_date
    - "expiry_warning" 15 days before end_date
    - "expired" on end_date
  - Return emails sorted by date, then by name.

Part 2: Handle plan changes.
  - Plan changes: {name, new_plan, change_date}
  - On change_date: cancel old subscription, start new one (same duration remaining).
  - Regenerate all emails accounting for changes.

Part 3: Handle renewals.
  - Renewals: {name, renew_date} — extends the subscription by the original duration.
  - Push the end_date forward and regenerate expiry emails.

Dates are represented as integers (day numbers) for simplicity.

Complexity targets:
- O(N log N) where N = total emails generated (due to sorting)
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
    email_type: str  # "welcome", "expiry_warning", "expired"
    plan: str


def generate_emails(subscriptions: list[Subscription]) -> list[Email]:
    """
    Part 1: Generate scheduled emails for all subscriptions.
    Sort by date, then by name.
    """
    # TODO: Implement
    pass


def generate_emails_with_changes(
    subscriptions: list[Subscription],
    changes: list[PlanChange],
) -> list[Email]:
    """
    Part 2: Generate emails accounting for plan changes.
    A plan change cancels the old subscription and starts a new one
    with the remaining duration.
    """
    # TODO: Implement
    pass


def generate_emails_with_renewals(
    subscriptions: list[Subscription],
    renewals: list[Renewal],
) -> list[Email]:
    """
    Part 3: Generate emails accounting for renewals.
    A renewal extends the end_date by the original duration.
    """
    # TODO: Implement
    pass


# HINT 1: end_date = begin_date + duration_days. Warning = end_date - 15.
#         Skip warning if warning_date <= begin_date.

# HINT 2: For plan changes, compute remaining = original_end - change_date.
#         Create a new subscription starting at change_date with that remaining duration.

# HINT 3: For renewals, find the subscription and set new_end = old_end + original_duration.
#         Regenerate the expiry_warning and expired emails.


# ============ TESTS ============

def test_basic_emails():
    subs = [
        Subscription("Alice", "pro", 1, 30),
        Subscription("Bob", "free", 5, 60),
    ]
    emails = generate_emails(subs)
    # Alice: welcome(1), warning(16), expired(31)
    # Bob: welcome(5), warning(50), expired(65)
    assert len(emails) == 6
    assert emails[0] == Email(1, "Alice", "welcome", "pro")
    assert emails[1] == Email(5, "Bob", "welcome", "free")
    assert emails[2] == Email(16, "Alice", "expiry_warning", "pro")

def test_no_warning_short_sub():
    subs = [Subscription("Alice", "trial", 1, 10)]
    emails = generate_emails(subs)
    # Warning would be day -4 (1+10-15), skip it
    assert len(emails) == 2
    assert emails[0].email_type == "welcome"
    assert emails[1].email_type == "expired"

def test_plan_change():
    subs = [Subscription("Alice", "free", 1, 30)]
    changes = [PlanChange("Alice", "pro", 10)]
    emails = generate_emails_with_changes(subs, changes)
    # Original: begins 1, ends 31. Change at 10: remaining = 21 days.
    # New sub: pro, begins 10, ends 31 (same end date, different plan).
    # Emails: welcome(1, free), welcome(10, pro), warning(16, pro), expired(31, pro)
    types = [(e.date, e.email_type, e.plan) for e in emails]
    assert (1, "welcome", "free") in types
    assert (10, "welcome", "pro") in types
    assert (31, "expired", "pro") in types

def test_renewal():
    subs = [Subscription("Alice", "pro", 1, 30)]
    renewals = [Renewal("Alice", 25)]
    emails = generate_emails_with_renewals(subs, renewals)
    # Original end: 31. Renewal extends by 30: new end = 61.
    # Emails: welcome(1), warning(46), expired(61)
    assert any(e.date == 46 and e.email_type == "expiry_warning" for e in emails)
    assert any(e.date == 61 and e.email_type == "expired" for e in emails)

def test_same_date_sorting():
    subs = [
        Subscription("Bob", "free", 1, 30),
        Subscription("Alice", "pro", 1, 30),
    ]
    emails = generate_emails(subs)
    # Same dates: should be sorted by name
    assert emails[0].name == "Alice"
    assert emails[1].name == "Bob"


if __name__ == "__main__":
    test_basic_emails()
    test_no_warning_short_sub()
    test_plan_change()
    test_renewal()
    test_same_date_sorting()
    print("All tests passed!")
