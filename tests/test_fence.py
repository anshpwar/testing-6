import pathlib
import unittest

from routekit import fence, rules

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


class ZoneTests(unittest.TestCase):
    def setUp(self):
        self.zones = fence.ZoneSet.load(DATA / "metro.json")

    def test_zone_geometry(self):
        downtown = self.zones.get("downtown")
        self.assertEqual(downtown.area_m2(), 1200 * 1300)
        self.assertEqual(downtown.bbox(), ((600, -200), (1800, 1100)))
        self.assertEqual(self.zones.get("exclusion").area_m2(), 720000)

    def test_locate_exact_positions(self):
        self.assertEqual(self.zones.locate(1000, 500), ["downtown"])
        self.assertEqual(self.zones.locate(2450, 100), ["campus"])
        self.assertEqual(self.zones.locate(4000, 4000), [])

    def test_concave_exclusion_zone(self):
        self.assertEqual(self.zones.locate(2300, 2000), ["exclusion"])
        self.assertEqual(self.zones.locate(1700, 2000), [])

    def test_snapping_uses_the_policy_tolerance(self):
        accuracy = 10
        tol = rules.fence_snap_tolerance_m(accuracy)
        self.assertEqual(self.zones.locate(600 - tol, 500, accuracy), ["downtown"])
        self.assertEqual(self.zones.locate(600 - tol - 1, 500, accuracy), [])

    def test_no_snapping_without_reported_accuracy(self):
        self.assertEqual(self.zones.locate(599, 500, 0), [])

    def test_approaching_uses_the_zone_buffer(self):
        buf = rules.geofence_buffer_m(self.zones.get("exclusion").zone_class)
        self.assertEqual(self.zones.approaching(1400 - buf, 1600), ["exclusion"])
        self.assertEqual(self.zones.approaching(1400 - buf - 1, 1600), [])

    def test_inside_is_not_approaching(self):
        self.assertEqual(self.zones.approaching(1000, 500), [])

    def test_needs_three_vertices(self):
        with self.assertRaises(ValueError):
            fence.Zone("line", [(0, 0), (5, 5)])

    def test_duplicate_zone_name(self):
        with self.assertRaises(ValueError):
            self.zones.add(fence.Zone("campus", [(0, 0), (5, 0), (0, 5)]))
