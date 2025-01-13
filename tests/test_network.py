import pathlib
import unittest

from routekit import native
from routekit.network import Network, UnknownStop

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.net = Network.load(DATA / "metro.json")

    def test_direct_road_cost(self):
        leg = self.net.route("depot", "a1")
        self.assertEqual(leg.names, ["depot", "a1"])
        self.assertEqual(leg.cost_s, 58 + native.HOP_PENALTY_S)

    def test_two_hop_route(self):
        leg = self.net.route("depot", "a2")
        self.assertEqual(leg.names, ["depot", "a1", "a2"])
        self.assertEqual(leg.cost_s, 2 * 58 + 2 * native.HOP_PENALTY_S)

    def test_algorithms_agree_between_all_reachable_pairs(self):
        names = [n for n in self.net.stops if n != "island"]
        for a in names:
            for b in names:
                self.assertEqual(self.net.route(a, b, "astar").cost_s, self.net.route(a, b, "dijkstra").cost_s)

    def test_isolated_stop_is_unreachable(self):
        self.assertFalse(self.net.reachable("depot", "island"))
        with self.assertRaises(native.NativeError):
            self.net.route("depot", "island")

    def test_unknown_stop(self):
        with self.assertRaises(UnknownStop):
            self.net.route("depot", "nowhere")

    def test_duplicate_stop_is_rejected(self):
        with self.assertRaises(ValueError):
            self.net.add_stop("depot", 1, 1)

    def test_nearest_stop(self):
        self.assertEqual(self.net.nearest_stop(1650, 40), ("a2", 64))

    def test_cost_matrix_is_consistent_with_routes(self):
        names = ["depot", "b2", "hub"]
        m = self.net.cost_matrix(names)
        for i, a in enumerate(names):
            for j, b in enumerate(names):
                self.assertEqual(m[i][j], 0 if a == b else self.net.route(a, b).cost_s)

    def test_grid_builder(self):
        net = Network.grid(3, 3)
        leg = net.route("r0c0", "r2c2")
        self.assertEqual(leg.hops, 4)
        self.assertEqual(len(net.stops), 9)
