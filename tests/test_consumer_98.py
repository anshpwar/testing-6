import ctypes
import unittest

from routekit import consumer_98, native


class RouteRecordTests(unittest.TestCase):
    def test_record_layout_matches_the_library(self):
        self.assertEqual(ctypes.sizeof(consumer_98.RouteRecordV1), native.route_sizeof())

    def test_pack_unpack_round_trip(self):
        raw = consumer_98.pack_record(180, 2, (0, 1, 3))
        self.assertEqual(len(raw), consumer_98.RECORD_SIZE)
        self.assertEqual(consumer_98.unpack_record(raw), (180, 2, (0, 1, 3)))

    def test_unpack_rejects_wrong_size(self):
        with self.assertRaises(ValueError):
            consumer_98.unpack_record(b"short")
