import unittest

from routekit import contract, consumer_83


class ExportTests(unittest.TestCase):
    def test_export_line(self):
        rec = contract.Record("RK-9", 700, "open")
        self.assertEqual(consumer_83.export_line(rec), "RK-9,700")
