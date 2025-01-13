import unittest

from routekit import calc


class CalcTests(unittest.TestCase):
    def test_combined_charge(self):
        self.assertEqual(calc.combined_charge(0), 449)
        self.assertEqual(calc.combined_charge(1), 449)
        self.assertEqual(calc.combined_charge(2000), 449)
        self.assertEqual(calc.combined_charge(2001), 749)
