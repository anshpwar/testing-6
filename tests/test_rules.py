import unittest

from routekit import rules


class RuleTests(unittest.TestCase):
    def test_delivery_fee_cents(self):
        self.assertEqual(rules.delivery_fee_cents(0), 399)
        self.assertEqual(rules.delivery_fee_cents(1), 399)
        self.assertEqual(rules.delivery_fee_cents(2000), 399)
        self.assertEqual(rules.delivery_fee_cents(2001), 699)
        self.assertEqual(rules.delivery_fee_cents(10000), 699)
        self.assertEqual(rules.delivery_fee_cents(10001), 1299)
        self.assertEqual(rules.delivery_fee_cents(30000), 1299)
        self.assertEqual(rules.delivery_fee_cents(30001), 2499)

    def test_fuel_surcharge_cents(self):
        self.assertEqual(rules.fuel_surcharge_cents(0), 50)
        self.assertEqual(rules.fuel_surcharge_cents(1), 50)
        self.assertEqual(rules.fuel_surcharge_cents(5000), 50)
        self.assertEqual(rules.fuel_surcharge_cents(5001), 150)
        self.assertEqual(rules.fuel_surcharge_cents(20000), 150)
        self.assertEqual(rules.fuel_surcharge_cents(20001), 320)
        self.assertEqual(rules.fuel_surcharge_cents(60000), 320)
        self.assertEqual(rules.fuel_surcharge_cents(60001), 600)

    def test_service_time_s(self):
        self.assertEqual(rules.service_time_s(0), 120)
        self.assertEqual(rules.service_time_s(1), 120)
        self.assertEqual(rules.service_time_s(2), 180)
        self.assertEqual(rules.service_time_s(3), 180)
        self.assertEqual(rules.service_time_s(4), 300)
        self.assertEqual(rules.service_time_s(8), 300)
        self.assertEqual(rules.service_time_s(9), 540)

    def test_vehicle_capacity_kg(self):
        self.assertEqual(rules.vehicle_capacity_kg(0), 25)
        self.assertEqual(rules.vehicle_capacity_kg(1), 25)
        self.assertEqual(rules.vehicle_capacity_kg(2), 120)
        self.assertEqual(rules.vehicle_capacity_kg(3), 800)
        self.assertEqual(rules.vehicle_capacity_kg(4), 3500)

    def test_max_stops_per_route(self):
        self.assertEqual(rules.max_stops_per_route(0), 12)
        self.assertEqual(rules.max_stops_per_route(1), 12)
        self.assertEqual(rules.max_stops_per_route(2), 25)
        self.assertEqual(rules.max_stops_per_route(3), 40)
        self.assertEqual(rules.max_stops_per_route(4), 60)

    def test_rest_break_min(self):
        self.assertEqual(rules.rest_break_min(0), 10)
        self.assertEqual(rules.rest_break_min(1), 10)
        self.assertEqual(rules.rest_break_min(150), 10)
        self.assertEqual(rules.rest_break_min(151), 20)
        self.assertEqual(rules.rest_break_min(270), 20)
        self.assertEqual(rules.rest_break_min(271), 45)
        self.assertEqual(rules.rest_break_min(480), 45)
        self.assertEqual(rules.rest_break_min(481), 60)

    def test_geofence_buffer_m(self):
        self.assertEqual(rules.geofence_buffer_m(0), 25)
        self.assertEqual(rules.geofence_buffer_m(1), 25)
        self.assertEqual(rules.geofence_buffer_m(2), 75)
        self.assertEqual(rules.geofence_buffer_m(3), 150)
        self.assertEqual(rules.geofence_buffer_m(4), 300)

    def test_priority_surcharge_cents(self):
        self.assertEqual(rules.priority_surcharge_cents(0), 150)
        self.assertEqual(rules.priority_surcharge_cents(1), 150)
        self.assertEqual(rules.priority_surcharge_cents(2), 450)
        self.assertEqual(rules.priority_surcharge_cents(3), 900)
        self.assertEqual(rules.priority_surcharge_cents(4), 1500)

    def test_late_penalty_cents(self):
        self.assertEqual(rules.late_penalty_cents(0), 200)
        self.assertEqual(rules.late_penalty_cents(1), 200)
        self.assertEqual(rules.late_penalty_cents(15), 200)
        self.assertEqual(rules.late_penalty_cents(16), 800)
        self.assertEqual(rules.late_penalty_cents(60), 800)
        self.assertEqual(rules.late_penalty_cents(61), 2500)
        self.assertEqual(rules.late_penalty_cents(180), 2500)
        self.assertEqual(rules.late_penalty_cents(181), 6000)

    def test_redelivery_fee_cents(self):
        self.assertEqual(rules.redelivery_fee_cents(0), 300)
        self.assertEqual(rules.redelivery_fee_cents(1), 300)
        self.assertEqual(rules.redelivery_fee_cents(2), 300)
        self.assertEqual(rules.redelivery_fee_cents(3), 650)
        self.assertEqual(rules.redelivery_fee_cents(4), 1200)
        self.assertEqual(rules.redelivery_fee_cents(5), 2500)

    def test_time_window_slack_min(self):
        self.assertEqual(rules.time_window_slack_min(0), 5)
        self.assertEqual(rules.time_window_slack_min(1), 5)
        self.assertEqual(rules.time_window_slack_min(30), 5)
        self.assertEqual(rules.time_window_slack_min(31), 10)
        self.assertEqual(rules.time_window_slack_min(120), 10)
        self.assertEqual(rules.time_window_slack_min(121), 20)
        self.assertEqual(rules.time_window_slack_min(240), 20)
        self.assertEqual(rules.time_window_slack_min(241), 45)

    def test_route_timeout_ms(self):
        self.assertEqual(rules.route_timeout_ms(0), 44)
        self.assertEqual(rules.route_timeout_ms(1), 44)
        self.assertEqual(rules.route_timeout_ms(100), 44)
        self.assertEqual(rules.route_timeout_ms(101), 175)
        self.assertEqual(rules.route_timeout_ms(1000), 175)
        self.assertEqual(rules.route_timeout_ms(1001), 700)
        self.assertEqual(rules.route_timeout_ms(10000), 700)
        self.assertEqual(rules.route_timeout_ms(10001), 2625)

    def test_fence_snap_tolerance_m(self):
        self.assertEqual(rules.fence_snap_tolerance_m(0), 3)
        self.assertEqual(rules.fence_snap_tolerance_m(1), 3)
        self.assertEqual(rules.fence_snap_tolerance_m(5), 3)
        self.assertEqual(rules.fence_snap_tolerance_m(6), 10)
        self.assertEqual(rules.fence_snap_tolerance_m(20), 10)
        self.assertEqual(rules.fence_snap_tolerance_m(21), 25)
        self.assertEqual(rules.fence_snap_tolerance_m(50), 25)
        self.assertEqual(rules.fence_snap_tolerance_m(51), 80)

    def test_parcel_weight_class(self):
        self.assertEqual(rules.parcel_weight_class(0), 1)
        self.assertEqual(rules.parcel_weight_class(1), 1)
        self.assertEqual(rules.parcel_weight_class(500), 1)
        self.assertEqual(rules.parcel_weight_class(501), 2)
        self.assertEqual(rules.parcel_weight_class(5000), 2)
        self.assertEqual(rules.parcel_weight_class(5001), 3)
        self.assertEqual(rules.parcel_weight_class(20000), 3)
        self.assertEqual(rules.parcel_weight_class(20001), 4)

    def test_hub_handling_min(self):
        self.assertEqual(rules.hub_handling_min(0), 15)
        self.assertEqual(rules.hub_handling_min(1), 15)
        self.assertEqual(rules.hub_handling_min(10), 15)
        self.assertEqual(rules.hub_handling_min(11), 45)
        self.assertEqual(rules.hub_handling_min(100), 45)
        self.assertEqual(rules.hub_handling_min(101), 120)
        self.assertEqual(rules.hub_handling_min(500), 120)
        self.assertEqual(rules.hub_handling_min(501), 240)

    def test_cold_chain_limit_min(self):
        self.assertEqual(rules.cold_chain_limit_min(0), 480)
        self.assertEqual(rules.cold_chain_limit_min(1), 480)
        self.assertEqual(rules.cold_chain_limit_min(10), 480)
        self.assertEqual(rules.cold_chain_limit_min(11), 240)
        self.assertEqual(rules.cold_chain_limit_min(20), 240)
        self.assertEqual(rules.cold_chain_limit_min(21), 120)
        self.assertEqual(rules.cold_chain_limit_min(30), 120)
        self.assertEqual(rules.cold_chain_limit_min(31), 60)
