import unittest

from routekit import fleet, planner, rules, timing
from routekit.network import Network


def orders_for(net, count, weight_g, parcels=1):
    stops = [s for s in net.stops if s != "r0c0"]
    return [planner.Order(f"RK-{i:03d}", stops[i % len(stops)], weight_g, parcels) for i in range(count)]


class TourTests(unittest.TestCase):
    def test_tour_cost_adds_the_legs(self):
        matrix = [[0, 10, 20], [10, 0, 5], [20, 5, 0]]
        self.assertEqual(planner.tour_cost(matrix, [1, 2]), 10 + 5 + 20)

    def test_two_opt_never_makes_a_tour_worse(self):
        net = Network.grid(4, 4)
        names = ["r0c0", "r3c3", "r0c3", "r3c0", "r1c2", "r2c1"]
        matrix = net.cost_matrix(names)
        start = [1, 2, 3, 4, 5]
        better = planner.two_opt(matrix, start)
        self.assertLessEqual(planner.tour_cost(matrix, better), planner.tour_cost(matrix, start))
        self.assertEqual(sorted(better), sorted(start))

    def test_two_opt_fixes_a_crossed_tour(self):
        net = Network.grid(1, 5)
        names = ["r0c0", "r0c1", "r0c2", "r0c3", "r0c4"]
        matrix = net.cost_matrix(names)
        crossed = [2, 1, 4, 3]
        fixed = planner.two_opt(matrix, crossed)
        self.assertLess(planner.tour_cost(matrix, fixed), planner.tour_cost(matrix, crossed))


class SplitTests(unittest.TestCase):
    def test_single_trip_when_everything_fits(self):
        net = Network.grid(5, 5)
        trips = planner.plan(net, "r0c0", orders_for(net, 3, 100), 2)
        self.assertEqual(len(trips), 1)
        self.assertEqual(trips[0].total_s, trips[0].drive_s + trips[0].service_s)

    def test_stop_limit_forces_extra_trips(self):
        net = Network.grid(6, 6)
        limit = fleet.stop_limit(1)
        orders = orders_for(net, limit + 3, 10)
        trips = planner.plan(net, "r0c0", orders, 1)
        self.assertGreater(len(trips), 1)
        for t in trips:
            self.assertLessEqual(len(t.orders), limit)

    def test_weight_limit_forces_extra_trips(self):
        net = Network.grid(5, 5)
        cap = fleet.capacity_g(2)
        per_order = cap // 2 + 1
        trips = planner.plan(net, "r0c0", orders_for(net, 4, per_order), 2)
        self.assertEqual(len(trips), 4)
        for t in trips:
            self.assertLessEqual(t.weight_g, cap)

    def test_every_order_is_planned_exactly_once(self):
        net = Network.grid(6, 6)
        orders = orders_for(net, fleet.stop_limit(1) + 2, 10)
        trips = planner.plan(net, "r0c0", orders, 1)
        planned = sorted(o.ref for t in trips for o in t.orders)
        self.assertEqual(planned, sorted(o.ref for o in orders))

    def test_too_heavy_order_is_rejected(self):
        net = Network.grid(3, 3)
        heavy = [planner.Order("RK-X", "r1c1", fleet.capacity_g(1) + 1)]
        with self.assertRaises(ValueError):
            planner.plan(net, "r0c0", heavy, 1)

    def test_service_time_follows_policy(self):
        net = Network.grid(3, 3)
        orders = [planner.Order("RK-1", "r1c1", 100, 2), planner.Order("RK-2", "r2c2", 100, 5)]
        trip = planner.plan(net, "r0c0", orders, 2)[0]
        self.assertEqual(trip.service_s, timing.service_seconds(2) + timing.service_seconds(5))

    def test_no_orders_no_trips(self):
        self.assertEqual(planner.plan(Network.grid(2, 2), "r0c0", [], 2), [])

    def test_vehicle_class_for_light_parcels(self):
        self.assertEqual(fleet.vehicle_class_for(400), rules.parcel_weight_class(400))
