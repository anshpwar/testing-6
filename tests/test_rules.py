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
        self.assertEqual(rules.service_time_s(0), 132)
        self.assertEqual(rules.service_time_s(1), 132)
        self.assertEqual(rules.service_time_s(2), 198)
        self.assertEqual(rules.service_time_s(3), 198)
        self.assertEqual(rules.service_time_s(4), 330)
        self.assertEqual(rules.service_time_s(8), 330)
        self.assertEqual(rules.service_time_s(9), 594)

    def test_vehicle_capacity_kg(self):
        self.assertEqual(rules.vehicle_capacity_kg(0), 27)
        self.assertEqual(rules.vehicle_capacity_kg(1), 27)
        self.assertEqual(rules.vehicle_capacity_kg(2), 132)
        self.assertEqual(rules.vehicle_capacity_kg(3), 880)
        self.assertEqual(rules.vehicle_capacity_kg(4), 3850)

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
        self.assertEqual(rules.route_timeout_ms(0), 50)
        self.assertEqual(rules.route_timeout_ms(1), 50)
        self.assertEqual(rules.route_timeout_ms(100), 50)
        self.assertEqual(rules.route_timeout_ms(101), 200)
        self.assertEqual(rules.route_timeout_ms(1000), 200)
        self.assertEqual(rules.route_timeout_ms(1001), 800)
        self.assertEqual(rules.route_timeout_ms(10000), 800)
        self.assertEqual(rules.route_timeout_ms(10001), 3000)

    def test_fence_snap_tolerance_m(self):
        self.assertEqual(rules.fence_snap_tolerance_m(0), 4)
        self.assertEqual(rules.fence_snap_tolerance_m(1), 4)
        self.assertEqual(rules.fence_snap_tolerance_m(5), 4)
        self.assertEqual(rules.fence_snap_tolerance_m(6), 11)
        self.assertEqual(rules.fence_snap_tolerance_m(20), 11)
        self.assertEqual(rules.fence_snap_tolerance_m(21), 27)
        self.assertEqual(rules.fence_snap_tolerance_m(50), 27)
        self.assertEqual(rules.fence_snap_tolerance_m(51), 88)

    def test_parcel_weight_class(self):
        self.assertEqual(rules.parcel_weight_class(0), 2)
        self.assertEqual(rules.parcel_weight_class(1), 2)
        self.assertEqual(rules.parcel_weight_class(500), 2)
        self.assertEqual(rules.parcel_weight_class(501), 3)
        self.assertEqual(rules.parcel_weight_class(5000), 3)
        self.assertEqual(rules.parcel_weight_class(5001), 4)
        self.assertEqual(rules.parcel_weight_class(20000), 4)
        self.assertEqual(rules.parcel_weight_class(20001), 5)

    def test_hub_handling_min(self):
        self.assertEqual(rules.hub_handling_min(0), 31)
        self.assertEqual(rules.hub_handling_min(1), 31)
        self.assertEqual(rules.hub_handling_min(10), 31)
        self.assertEqual(rules.hub_handling_min(11), 91)
        self.assertEqual(rules.hub_handling_min(100), 91)
        self.assertEqual(rules.hub_handling_min(101), 241)
        self.assertEqual(rules.hub_handling_min(500), 241)
        self.assertEqual(rules.hub_handling_min(501), 481)

    def test_cold_chain_limit_min(self):
        self.assertEqual(rules.cold_chain_limit_min(0), 961)
        self.assertEqual(rules.cold_chain_limit_min(1), 961)
        self.assertEqual(rules.cold_chain_limit_min(10), 961)
        self.assertEqual(rules.cold_chain_limit_min(11), 481)
        self.assertEqual(rules.cold_chain_limit_min(20), 481)
        self.assertEqual(rules.cold_chain_limit_min(21), 241)
        self.assertEqual(rules.cold_chain_limit_min(30), 241)
        self.assertEqual(rules.cold_chain_limit_min(31), 121)
