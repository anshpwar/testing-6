import ctypes
import unittest

from routekit import native


def diamond():
    g = native.Graph()
    for xy in ((0, 0), (500, 0), (250, 400), (1000, 0)):
        g.add_node(*xy)
    for a, b, s in ((0, 1, 60), (1, 3, 60), (0, 2, 50), (2, 3, 80), (1, 2, 20)):
        g.add_edge(a, b, s)
    return g


def grid(size=5, spacing=400):
    g = native.Graph()
    speeds = (30, 50, 70)
    for r in range(size):
        for c in range(size):
            g.add_node(c * spacing, r * spacing)
    for r in range(size):
        for c in range(size):
            n = r * size + c
            if c + 1 < size:
                g.add_road(n, n + 1, speeds[(r + c) % 3])
            if r + 1 < size:
                g.add_road(n, n + size, speeds[(2 * r + c) % 3])
    return g


class RouteTests(unittest.TestCase):
    def test_dijkstra_finds_the_quickest_path(self):
        g = diamond()
        path = g.dijkstra(0, 3)
        self.assertEqual(path.nodes, (0, 1, 3))
        self.assertEqual(path.hops, 2)
        self.assertEqual(path.cost, 120 + 2 * native.HOP_PENALTY_S)

    def test_astar_matches_dijkstra_on_a_grid(self):
        g = grid()
        for a in range(0, 25, 3):
            for b in range(25):
                self.assertEqual(g.astar(a, b).cost, g.dijkstra(a, b).cost)

    def test_route_to_self_is_free(self):
        path = diamond().dijkstra(2, 2)
        self.assertEqual((path.cost, path.hops, path.nodes), (0, 0, (2,)))

    def test_unreachable_target_raises(self):
        g = diamond()
        with self.assertRaises(native.NativeError) as ctx:
            g.dijkstra(3, 0)
        self.assertEqual(ctx.exception.code, native.ERR_NOPATH)
        with self.assertRaises(native.NativeError):
            g.astar(3, 0)

    def test_unknown_node_raises(self):
        with self.assertRaises(native.NativeError) as ctx:
            diamond().dijkstra(0, 9)
        self.assertEqual(ctx.exception.code, native.ERR_ARG)

    def test_distances_cover_every_node(self):
        g = diamond()
        d = g.distances(0)
        self.assertEqual(d[0], 0)
        self.assertEqual(d[1], 60 + native.HOP_PENALTY_S)
        self.assertEqual(d[3], g.dijkstra(0, 3).cost)
        self.assertEqual(g.distances(3)[0], native.COST_INF)

    def test_matrix_matches_point_to_point_costs(self):
        g = grid(4)
        stops = [0, 5, 10, 15]
        m = g.matrix(stops)
        for i, a in enumerate(stops):
            for j, b in enumerate(stops):
                self.assertEqual(m[i][j], g.dijkstra(a, b).cost)

    def test_matrix_rejects_unknown_stops(self):
        with self.assertRaises(native.NativeError):
            diamond().matrix([0, 12])

    def test_route_layout_offsets(self):
        self.assertEqual(ctypes.sizeof(native.Route), native.route_sizeof())
        self.assertEqual(native.Route.hops.offset, 4)
        self.assertEqual(native.Route.expanded.offset, 8)
        self.assertEqual(native.Route.nodes.offset, 12)

    def test_search_effort_is_reported(self):
        g = diamond()
        path = g.dijkstra(0, 3)
        self.assertGreaterEqual(path.expanded, path.hops + 1)

    def test_hop_penalty_matches_library(self):
        self.assertEqual(native.hop_penalty_s(), native.HOP_PENALTY_S)
