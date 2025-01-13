import io
import json
import pathlib
import unittest

from routekit import cli, native, rules

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
METRO = str(DATA / "metro.json")
ORDERS = str(DATA / "orders.json")


def run(*argv):
    out = io.StringIO()
    rc = cli.main(list(argv), out=out)
    return rc, json.loads(out.getvalue())


class CliTests(unittest.TestCase):
    def test_route(self):
        rc, data = run("route", METRO, "depot", "a2")
        self.assertEqual(rc, 0)
        self.assertEqual(data["stops"], ["depot", "a1", "a2"])
        self.assertEqual(data["cost_s"], 116 + 2 * native.HOP_PENALTY_S)

    def test_route_algorithm_flag(self):
        _, a = run("route", METRO, "depot", "airport", "--algorithm", "astar")
        _, d = run("route", METRO, "depot", "airport", "--algorithm", "dijkstra")
        self.assertEqual(a["cost_s"], d["cost_s"])

    def test_unknown_stop_exit_code(self):
        rc, data = run("route", METRO, "depot", "mars")
        self.assertEqual(rc, 2)
        self.assertIn("mars", data["error"])

    def test_unreachable_stop_exit_code(self):
        rc, data = run("route", METRO, "depot", "island")
        self.assertEqual(rc, 3)
        self.assertIn("no path", data["error"])

    def test_fence_inside(self):
        rc, data = run("fence", METRO, "1000", "500")
        self.assertEqual((rc, data["inside"]), (0, ["downtown"]))

    def test_fence_outside_uses_exit_code_one(self):
        rc, data = run("fence", METRO, "5000", "5000")
        self.assertEqual((rc, data["inside"]), (1, []))

    def test_quote(self):
        rc, data = run("quote", "--distance", "12000", "--priority", "1")
        self.assertEqual(rc, 0)
        self.assertEqual(data["priority_cents"], rules.priority_surcharge_cents(1))
        self.assertEqual(data["total_cents"], data["base_cents"] + data["priority_cents"])

    def test_plan_lists_every_order(self):
        rc, data = run("plan", METRO, ORDERS)
        self.assertEqual(rc, 0)
        refs = sorted(r for t in data["trips"] for r in t["orders"])
        self.assertEqual(refs, [f"RK-{n}" for n in range(1001, 1009)])
