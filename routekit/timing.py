"""Time estimates: service time at stops, driver breaks, delivery windows and cold-chain limits."""
from . import rules


def service_seconds(parcels):
    return rules.service_time_s(parcels)


def leg_eta_s(route_cost_s, parcels):
    """Seconds from leaving the previous stop until the parcels are handed over."""
    return route_cost_s + service_seconds(parcels)


def hub_dwell_min(parcels):
    return rules.hub_handling_min(parcels)


def rest_breaks_min(driving_min):
    """Break minutes owed after the given continuous driving time."""
    return rules.rest_break_min(driving_min)


def shift_minutes(driving_min, service_min):
    """Shift length including the break owed for the driving."""
    return driving_min + service_min + rest_breaks_min(driving_min)


def window_status(arrival_min, open_min, close_min):
    """'early', 'on_time' or 'late'; the policy slack widens the window at both ends."""
    slack = rules.time_window_slack_min(close_min - open_min)
    if arrival_min < open_min - slack:
        return "early"
    if arrival_min > close_min + slack:
        return "late"
    return "on_time"


def minutes_late(arrival_min, open_min, close_min):
    """Minutes past the window close once the policy slack is used up."""
    slack = rules.time_window_slack_min(close_min - open_min)
    return max(0, arrival_min - close_min - slack)


def cold_chain_ok(ambient_c, transit_min):
    return transit_min <= rules.cold_chain_limit_min(ambient_c)
