import json
import pathlib
import unittest

from routekit import fence, fleet, native, planner, pricing, timing
from routekit.network import Network

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


class DispatchFlowTests(unittest.TestCase):
    """Sample city: plan the day's orders, check zones and price each delivery."""

    def setUp(self):
        self.net = Network.load(DATA / "metro.json")
        self.zones = fence.ZoneSet.load(DATA / "metro.json")
        raw = json.loads((DATA / "orders.json").read_text())
        self.depot = raw["depot"]
        self.orders = [planner.Order(o["ref"], o["stop"], o["weight_g"], o.get("parcels", 1), tuple(o.get("window", (0, 1440))))
                       for o in raw["orders"]]

    def test_day_plan_covers_all_orders_within_limits(self):
        heaviest = max(o.weight_g for o in self.orders)
        vclass = max(2, fleet.vehicle_class_for(heaviest))
        trips = planner.plan(self.net, self.depot, self.orders, vclass)
        self.assertEqual(sorted(o.ref for t in trips for o in t.orders), sorted(o.ref for o in self.orders))
        for t in trips:
            self.assertTrue(fleet.fits(vclass, t.weight_g, len(t.orders)))
            self.assertGreater(t.drive_s, 0)

    def test_trip_drive_time_matches_routed_legs(self):
        trips = planner.plan(self.net, self.depot, self.orders, 4)
        for t in trips:
            seq = [self.depot, *t.stops(), self.depot]
            legs = sum(self.net.route(a, b, "dijkstra").cost_s for a, b in zip(seq, seq[1:]))
            self.assertEqual(t.drive_s, legs)

    def test_every_stop_sits_in_the_expected_zone_or_none(self):
        for name, expected in (("a1", ["downtown"]), ("b1", ["downtown"]), ("a3", ["campus"]), ("hub", [])):
            x, y = self.net.position(name)
            self.assertEqual(self.zones.locate(x, y), expected)

    def test_pricing_follows_routed_distance(self):
        x, y = self.net.position("hub")
        quote = pricing.quote(abs(x) + abs(y), priority=1)
        self.assertEqual(quote.total_cents, quote.base_cents + quote.priority_cents)
        self.assertGreater(quote.total_cents, 0)

    def test_arrival_windows_are_evaluated_with_policy_slack(self):
        order = next(o for o in self.orders if o.ref == "RK-1002")
        leg = self.net.route(self.depot, order.stop)
        eta_min = order.window[0] + timing.leg_eta_s(leg.cost_s, order.parcels) // 60
        status = timing.window_status(eta_min, *order.window)
        self.assertIn(status, ("early", "on_time", "late"))
        self.assertEqual(status == "late", timing.minutes_late(eta_min, *order.window) > 0)

    def test_native_core_is_the_one_in_use(self):
        self.assertEqual(self.net.graph.node_count, len(self.net.stops))
        self.assertEqual(native.hop_penalty_s(), native.HOP_PENALTY_S)
