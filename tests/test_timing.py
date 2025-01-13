import unittest

from routekit import rules, timing


class TimingTests(unittest.TestCase):
    def test_leg_eta_adds_service_time(self):
        self.assertEqual(timing.leg_eta_s(300, 4), 300 + rules.service_time_s(4))

    def test_shift_includes_the_break(self):
        self.assertEqual(timing.shift_minutes(300, 60), 360 + rules.rest_break_min(300))

    def test_window_status_respects_slack(self):
        open_m, close_m = 600, 720
        slack = rules.time_window_slack_min(close_m - open_m)
        self.assertEqual(timing.window_status(660, open_m, close_m), "on_time")
        self.assertEqual(timing.window_status(close_m + slack, open_m, close_m), "on_time")
        self.assertEqual(timing.window_status(close_m + slack + 1, open_m, close_m), "late")
        self.assertEqual(timing.window_status(open_m - slack - 1, open_m, close_m), "early")

    def test_minutes_late_only_counts_beyond_the_slack(self):
        slack = rules.time_window_slack_min(120)
        self.assertEqual(timing.minutes_late(720 + slack, 600, 720), 0)
        self.assertEqual(timing.minutes_late(720 + slack + 7, 600, 720), 7)

    def test_cold_chain(self):
        limit = rules.cold_chain_limit_min(25)
        self.assertTrue(timing.cold_chain_ok(25, limit))
        self.assertFalse(timing.cold_chain_ok(25, limit + 1))

    def test_hub_dwell(self):
        self.assertEqual(timing.hub_dwell_min(50), rules.hub_handling_min(50))
