"""Composite charges built from the policy tables."""
from . import rules


def combined_charge(x):
    """Total of the two base schedules for x."""
    return rules.delivery_fee_cents(x) + rules.fuel_surcharge_cents(x)
