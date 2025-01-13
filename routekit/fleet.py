"""Vehicle classes and parcel loading limits."""
from . import native, rules


def vehicle_class_for(weight_g):
    """Smallest vehicle class the heaviest parcel fits."""
    return rules.parcel_weight_class(weight_g)


def capacity_g(vehicle_class):
    return rules.vehicle_capacity_kg(vehicle_class) * 1000


def stop_limit(vehicle_class):
    """Stops per trip: the policy limit, capped by what one routing matrix can hold with the depot."""
    return max(1, min(rules.max_stops_per_route(vehicle_class), native.MAX_NODES - 1))


def fits(vehicle_class, total_weight_g, stops):
    return total_weight_g <= capacity_g(vehicle_class) and stops <= stop_limit(vehicle_class)
