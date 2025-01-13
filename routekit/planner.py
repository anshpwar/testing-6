"""Trip planning: split orders into trips that fit a vehicle, then order each trip by matrix cost."""
from dataclasses import dataclass, field

from . import fleet, timing


@dataclass(frozen=True)
class Order:
    ref: str
    stop: str
    weight_g: int
    parcels: int = 1
    window: tuple = (0, 1440)


@dataclass
class Trip:
    vehicle_class: int
    orders: list = field(default_factory=list)
    drive_s: int = 0
    service_s: int = 0

    @property
    def weight_g(self):
        return sum(o.weight_g for o in self.orders)

    @property
    def total_s(self):
        return self.drive_s + self.service_s

    def stops(self):
        return [o.stop for o in self.orders]

    def as_dict(self):
        return {"vehicle_class": self.vehicle_class, "orders": [o.ref for o in self.orders],
                "drive_s": self.drive_s, "service_s": self.service_s}


def tour_cost(matrix, order):
    """Cost of depot (index 0) -> order[0] -> ... -> back to the depot."""
    seq = [0, *order, 0]
    return sum(matrix[a][b] for a, b in zip(seq, seq[1:]))


def two_opt(matrix, order):
    """Improve a visiting order by reversing segments while that lowers the cost."""
    best = list(order)
    best_cost = tour_cost(matrix, best)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                cand = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                cost = tour_cost(matrix, cand)
                if cost < best_cost:
                    best, best_cost, improved = cand, cost, True
    return best


def sweep_order(network, depot, orders):
    """Global nearest-neighbour ordering used to cut orders into trips."""
    names = [depot] + [o.stop for o in orders]
    matrix = network.cost_matrix(names)
    remaining = list(range(1, len(names)))
    seq, here = [], 0
    while remaining:
        nxt = min(remaining, key=lambda k: (matrix[here][k], k))
        seq.append(nxt - 1)
        remaining.remove(nxt)
        here = nxt
    return [orders[i] for i in seq]


def split_trips(ordered, vehicle_class):
    """Cut an ordered list into consecutive trips that respect weight and stop limits."""
    trips, current = [], Trip(vehicle_class)
    for o in ordered:
        if o.weight_g > fleet.capacity_g(vehicle_class):
            raise ValueError(f"order {o.ref} is too heavy for vehicle class {vehicle_class}")
        if current.orders and not fleet.fits(vehicle_class, current.weight_g + o.weight_g, len(current.orders) + 1):
            trips.append(current)
            current = Trip(vehicle_class)
        current.orders.append(o)
    if current.orders:
        trips.append(current)
    return trips


def finish_trip(network, depot, trip):
    names = [depot] + trip.stops()
    matrix = network.cost_matrix(names)
    order = two_opt(matrix, list(range(1, len(names))))
    trip.orders = [trip.orders[i - 1] for i in order]
    trip.drive_s = tour_cost(matrix, order)
    trip.service_s = sum(timing.service_seconds(o.parcels) for o in trip.orders)
    return trip


def plan(network, depot, orders, vehicle_class):
    """Plan trips for all orders; every order lands in exactly one trip."""
    if not orders:
        return []
    ordered = sweep_order(network, depot, list(orders))
    return [finish_trip(network, depot, t) for t in split_trips(ordered, vehicle_class)]
