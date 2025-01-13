import unittest

from routekit import fleet, rules


class FleetTests(unittest.TestCase):
    def test_class_comes_from_the_weight_table(self):
        for w in (100, 500, 501, 5000, 25000):
            self.assertEqual(fleet.vehicle_class_for(w), rules.parcel_weight_class(w))

    def test_capacity_in_grams(self):
        self.assertEqual(fleet.capacity_g(2), rules.vehicle_capacity_kg(2) * 1000)

    def test_stop_limit_follows_policy(self):
        self.assertEqual(fleet.stop_limit(1), rules.max_stops_per_route(1))

    def test_fits_checks_weight_and_stops(self):
        cap = fleet.capacity_g(2)
        limit = fleet.stop_limit(2)
        self.assertTrue(fleet.fits(2, cap, limit))
        self.assertFalse(fleet.fits(2, cap + 1, 1))
        self.assertFalse(fleet.fits(2, 1, limit + 1))
