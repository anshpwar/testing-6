import ctypes
import unittest

from routekit import native


class GraphTests(unittest.TestCase):
    def test_nodes_and_roads(self):
        with native.Graph() as g:
            a, b, c = g.add_node(0, 0), g.add_node(600, 0), g.add_node(600, 800)
            self.assertEqual((a, b, c), (0, 1, 2))
            g.add_road(a, b, 36)
            g.add_road(b, c, 72, two_way=False)
            self.assertEqual(g.node_count, 3)
            self.assertEqual(g.edge_count, 3)
            self.assertEqual(g.point(c), (600, 800))

    def test_road_time_comes_from_distance_and_speed(self):
        with native.Graph() as g:
            a, b = g.add_node(0, 0), g.add_node(600, 0)
            g.add_road(a, b, 36, two_way=False)
            path = g.dijkstra(a, b)
            self.assertEqual(path.cost, 60 + native.HOP_PENALTY_S)

    def test_edge_faster_than_the_speed_limit_is_rejected(self):
        with native.Graph() as g:
            a, b = g.add_node(0, 0), g.add_node(1000, 0)
            with self.assertRaises(native.NativeError) as ctx:
                g.add_edge(a, b, 5)
            self.assertEqual(ctx.exception.code, native.ERR_RANGE)
            g.add_edge(a, b, 90)

    def test_invalid_arguments(self):
        with native.Graph() as g:
            a = g.add_node(0, 0)
            with self.assertRaises(native.NativeError):
                g.add_road(a, a, 50)
            with self.assertRaises(native.NativeError):
                g.add_road(a, 7, 50)
            with self.assertRaises(native.NativeError):
                g.add_node(native.COORD_LIMIT + 1, 0)

    def test_nearest_node(self):
        with native.Graph() as g:
            g.add_node(0, 0)
            g.add_node(1000, 0)
            self.assertEqual(g.nearest(900, 30), (1, 104))
            self.assertEqual(g.nearest(10, 0), (0, 10))

    def test_node_capacity(self):
        with native.Graph() as g:
            for i in range(native.MAX_NODES):
                g.add_node(i, i)
            with self.assertRaises(native.NativeError) as ctx:
                g.add_node(1, 1)
            self.assertEqual(ctx.exception.code, native.ERR_FULL)

    def test_min_seconds_lower_bound(self):
        self.assertEqual(native.min_seconds(0), 0)
        self.assertEqual(native.min_seconds(1300), 36)

    def test_point_layout_matches_library(self):
        self.assertEqual(ctypes.sizeof(native.Point), native.point_sizeof())
        self.assertEqual(native.graph_sizeof() % 4, 0)
