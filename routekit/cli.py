"""Command line.   python -m routekit.cli route FILE FROM TO | fence FILE X Y | quote | plan FILE ORDERS"""
import argparse
import json
import sys

from . import fence, native, planner, pricing
from .network import Network, UnknownStop


def _dump(obj, out):
    json.dump(obj, out, indent=2, sort_keys=True)
    out.write("\n")


def cmd_route(args, out):
    net = Network.load(args.file)
    try:
        leg = net.route(args.origin, args.dest, args.algorithm)
    except UnknownStop as exc:
        _dump({"error": f"unknown stop {exc.args[0]}"}, out)
        return 2
    except native.NativeError as exc:
        _dump({"error": str(exc)}, out)
        return 3
    _dump(leg.as_dict(), out)
    return 0


def cmd_fence(args, out):
    with open(args.file) as fh:
        zones = fence.ZoneSet.from_dict(json.load(fh))
    inside = zones.locate(args.x, args.y, args.accuracy)
    _dump({"inside": inside, "approaching": zones.approaching(args.x, args.y)}, out)
    return 0 if inside else 1


def cmd_quote(args, out):
    q = pricing.quote(args.distance, args.priority)
    _dump({"base_cents": q.base_cents, "priority_cents": q.priority_cents, "total_cents": q.total_cents}, out)
    return 0


def cmd_plan(args, out):
    net = Network.load(args.file)
    with open(args.orders) as fh:
        raw = json.load(fh)
    orders = [planner.Order(o["ref"], o["stop"], o["weight_g"], o.get("parcels", 1), tuple(o.get("window", (0, 1440))))
              for o in raw["orders"]]
    try:
        trips = planner.plan(net, raw.get("depot", "depot"), orders, args.vehicle_class)
    except ValueError as exc:
        _dump({"error": str(exc)}, out)
        return 2
    _dump({"trips": [t.as_dict() for t in trips]}, out)
    return 0


def build_parser():
    ap = argparse.ArgumentParser(prog="routekit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("route")
    r.add_argument("file")
    r.add_argument("origin")
    r.add_argument("dest")
    r.add_argument("--algorithm", choices=["astar", "dijkstra"], default="astar")
    r.set_defaults(fn=cmd_route)
    f = sub.add_parser("fence")
    f.add_argument("file")
    f.add_argument("x", type=int)
    f.add_argument("y", type=int)
    f.add_argument("--accuracy", type=int, default=0)
    f.set_defaults(fn=cmd_fence)
    q = sub.add_parser("quote")
    q.add_argument("--distance", type=int, required=True)
    q.add_argument("--priority", type=int, default=0)
    q.set_defaults(fn=cmd_quote)
    p = sub.add_parser("plan")
    p.add_argument("file")
    p.add_argument("orders")
    p.add_argument("--vehicle-class", type=int, default=2)
    p.set_defaults(fn=cmd_plan)
    return ap


def main(argv=None, out=None):
    out = out or sys.stdout
    args = build_parser().parse_args(argv)
    return args.fn(args, out)


if __name__ == "__main__":
    sys.exit(main())
