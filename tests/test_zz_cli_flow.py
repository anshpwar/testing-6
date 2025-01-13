import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
METRO = str(ROOT / "data" / "metro.json")


def cli(*argv):
    proc = subprocess.run([sys.executable, "-m", "routekit.cli", *argv], cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, proc.stdout


class CliProcessTests(unittest.TestCase):
    def test_route_as_a_subprocess(self):
        rc, out = cli("route", METRO, "depot", "hub")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["stops"][0], "depot")
        self.assertEqual(data["stops"][-1], "hub")
        self.assertEqual(data["hops"], len(data["stops"]) - 1)

    def test_exit_code_for_unknown_stop(self):
        rc, out = cli("route", METRO, "depot", "mars")
        self.assertEqual(rc, 2)
        self.assertIn("error", json.loads(out))

    def test_missing_subcommand_is_a_usage_error(self):
        rc, _ = cli()
        self.assertEqual(rc, 2)
