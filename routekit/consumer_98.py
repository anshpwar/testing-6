"""Fixed-width cached route records added independently of the base-side change (scenario 98)."""
import ctypes

from . import native


class RouteRecordV1(ctypes.Structure):
    """Local mirror of rk_route as laid out when this module was written."""

    _fields_ = [
        ("cost", ctypes.c_int32),
        ("hops", ctypes.c_int32),
        ("nodes", ctypes.c_int32 * native.MAX_PATH),
    ]


RECORD_SIZE = ctypes.sizeof(RouteRecordV1)


def pack_record(cost, hops, nodes):
    rec = RouteRecordV1(cost, hops)
    for i in range(native.MAX_PATH):
        rec.nodes[i] = nodes[i] if i < len(nodes) else -1
    return bytes(rec)


def unpack_record(raw):
    if len(raw) != RECORD_SIZE:
        raise ValueError("record has the wrong size")
    rec = RouteRecordV1.from_buffer_copy(raw)
    return rec.cost, rec.hops, tuple(rec.nodes[: rec.hops + 1])
