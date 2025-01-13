"""Delivery quotes and penalty fees built from the policy tables."""
from dataclasses import dataclass

from . import calc, rules


@dataclass(frozen=True)
class Quote:
    distance_m: int
    base_cents: int
    priority_cents: int

    @property
    def total_cents(self):
        return self.base_cents + self.priority_cents


def quote(distance_m, priority=0):
    """Delivery fee plus fuel surcharge for the distance, and the priority surcharge when requested."""
    if distance_m < 0:
        raise ValueError("distance must not be negative")
    priority_cents = rules.priority_surcharge_cents(priority) if priority > 0 else 0
    return Quote(distance_m, calc.combined_charge(distance_m), priority_cents)


def late_fee_cents(minutes_late):
    return rules.late_penalty_cents(minutes_late) if minutes_late > 0 else 0


def redelivery_fee_cents(attempt):
    """Fee for a repeat attempt; the first attempt is free."""
    return rules.redelivery_fee_cents(attempt) if attempt > 1 else 0


def invoice(distance_m, priority=0, minutes_late=0, attempt=1):
    q = quote(distance_m, priority)
    return {
        "base_cents": q.base_cents,
        "priority_cents": q.priority_cents,
        "late_cents": late_fee_cents(minutes_late),
        "redelivery_cents": redelivery_fee_cents(attempt),
    }


def invoice_total(lines):
    return sum(lines.values())
