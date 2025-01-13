import ctypes
import unittest

from routekit import native

SQUARE = [(0, 0), (100, 0), (100, 100), (0, 100)]
ELL = [(0, 0), (200, 0), (200, 100), (100, 100), (100, 200), (0, 200)]


class PolygonTests(unittest.TestCase):
    def test_contains_inside_outside_and_boundary(self):
        sq = native.make_polygon(SQUARE)
        self.assertTrue(native.polygon_contains(sq, 50, 50))
        self.assertFalse(native.polygon_contains(sq, 150, 50))
        self.assertTrue(native.polygon_contains(sq, 100, 40))
        self.assertTrue(native.polygon_contains(sq, 0, 0))

    def test_concave_shape(self):
        ell = native.make_polygon(ELL)
        self.assertTrue(native.polygon_contains(ell, 150, 50))
        self.assertTrue(native.polygon_contains(ell, 50, 150))
        self.assertFalse(native.polygon_contains(ell, 150, 150))

    def test_ray_through_a_vertex(self):
        sq = native.make_polygon(SQUARE)
        self.assertFalse(native.polygon_contains(sq, -50, 100))
        self.assertFalse(native.polygon_contains(sq, -50, 0))

    def test_boundary_distance(self):
        sq = native.make_polygon(SQUARE)
        self.assertEqual(native.polygon_boundary_distance(sq, 50, -30), 30)
        self.assertEqual(native.polygon_boundary_distance(sq, 150, 150), 71)
        self.assertEqual(native.polygon_boundary_distance(sq, 40, 50), 40)

    def test_near_uses_the_tolerance(self):
        sq = native.make_polygon(SQUARE)
        self.assertTrue(native.polygon_near(sq, 110, 50, 10))
        self.assertFalse(native.polygon_near(sq, 111, 50, 10))
        with self.assertRaises(native.NativeError):
            native.polygon_near(sq, 111, 50, -1)

    def test_area_and_bbox(self):
        ell = native.make_polygon(ELL)
        self.assertEqual(native.polygon_area2(ell), 60000)
        self.assertEqual(native.polygon_bbox(ell), ((0, 0), (200, 200)))

    def test_degenerate_polygon_is_rejected(self):
        line = native.make_polygon([(0, 0), (10, 10)])
        with self.assertRaises(native.NativeError):
            native.polygon_contains(line, 1, 1)

    def test_vertex_capacity(self):
        with self.assertRaises(native.NativeError) as ctx:
            native.make_polygon([(i, i % 7) for i in range(native.MAX_VERTS + 1)])
        self.assertEqual(ctx.exception.code, native.ERR_FULL)

    def test_polygon_layout_matches_library(self):
        self.assertEqual(ctypes.sizeof(native.Polygon), native.polygon_sizeof())
        self.assertEqual(native.Polygon.v.offset, 4)

    def test_distance_helper(self):
        self.assertEqual(native.distance_m((0, 0), (300, 400)), 500)
