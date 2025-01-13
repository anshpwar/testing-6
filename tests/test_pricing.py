import unittest

from routekit import pricing, rules


class QuoteTests(unittest.TestCase):
    def test_base_is_fee_plus_fuel_surcharge(self):
        for d in (0, 1500, 2001, 12000, 45000, 90000):
            q = pricing.quote(d)
            self.assertEqual(q.base_cents, rules.delivery_fee_cents(d) + rules.fuel_surcharge_cents(d))
            self.assertEqual(q.priority_cents, 0)
            self.assertEqual(q.total_cents, q.base_cents)

    def test_priority_adds_a_surcharge(self):
        q = pricing.quote(5000, priority=2)
        self.assertEqual(q.priority_cents, rules.priority_surcharge_cents(2))
        self.assertEqual(q.total_cents, q.base_cents + rules.priority_surcharge_cents(2))

    def test_negative_distance_is_rejected(self):
        with self.assertRaises(ValueError):
            pricing.quote(-1)

    def test_no_late_fee_when_on_time(self):
        self.assertEqual(pricing.late_fee_cents(0), 0)
        self.assertEqual(pricing.late_fee_cents(-10), 0)
        self.assertEqual(pricing.late_fee_cents(45), rules.late_penalty_cents(45))

    def test_first_attempt_is_free(self):
        self.assertEqual(pricing.redelivery_fee_cents(1), 0)
        self.assertEqual(pricing.redelivery_fee_cents(3), rules.redelivery_fee_cents(3))

    def test_invoice_total(self):
        lines = pricing.invoice(8000, priority=1, minutes_late=20, attempt=2)
        expected = (pricing.quote(8000, 1).total_cents + rules.late_penalty_cents(20) + rules.redelivery_fee_cents(2))
        self.assertEqual(pricing.invoice_total(lines), expected)
