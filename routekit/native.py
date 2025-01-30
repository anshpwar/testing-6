"""ctypes bindings for build/libroutekit.{dylib,so}.

Constants and struct layouts mirror c/include/*.h. Every prototype is declared explicitly, and the library
exports *_sizeof functions so tests can detect layout drift.
"""
import ctypes
import pathlib
import subprocess
import sys
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parent.parent
_EXT = "dylib" if sys.platform == "darwin" else "so"
LIB_PATH = ROOT / "build" / f"libroutekit.{_EXT}"

# --- mirrored constants (c/include/rk_config.h)
MAX_NODES = 128
MAX_EDGES = 1024
MAX_PATH = MAX_NODES
MAX_VERTS = 64
COORD_LIMIT = 1000000
MAX_SPEED_KMH = 130
COST_INF = 2**31 - 1
HOP_PENALTY_S = 30

OK = 0
ERR_ARG = -1
ERR_FULL = -2
ERR_NOPATH = -3
ERR_RANGE = -4
ERR_EMPTY = -5

ERRORS = {
    ERR_ARG: "invalid argument",
    ERR_FULL: "capacity exceeded",
    ERR_NOPATH: "no path",
    ERR_RANGE: "value out of range",
    ERR_EMPTY: "empty",
}

i32 = ctypes.c_int32
i64 = ctypes.c_int64
vp = ctypes.c_void_p


class NativeError(Exception):
    def __init__(self, code, what=""):
        self.code = code
        text = ERRORS.get(code, str(code))
        super().__init__(f"{what}: {text}" if what else text)


class Point(ctypes.Structure):
    _fields_ = [("x", i32), ("y", i32)]


class Polygon(ctypes.Structure):
    _fields_ = [("count", i32), ("v", Point * MAX_VERTS)]


class Route(ctypes.Structure):
    _fields_ = [("cost", i32), ("hops", i32), ("expanded", i32), ("nodes", i32 * MAX_PATH)]


PROTOTYPES = {
    "rk_graph_new": ([], vp),
    "rk_graph_free": ([vp], None),
    "rk_graph_add_node": ([vp, i32, i32], ctypes.c_int),
    "rk_graph_add_edge": ([vp, ctypes.c_int, ctypes.c_int, i32], ctypes.c_int),
    "rk_graph_add_road": ([vp, ctypes.c_int, ctypes.c_int, i32, ctypes.c_int], ctypes.c_int),
    "rk_graph_node_count": ([vp], ctypes.c_int),
    "rk_graph_edge_count": ([vp], ctypes.c_int),
    "rk_graph_point": ([vp, ctypes.c_int, ctypes.POINTER(Point)], ctypes.c_int),
    "rk_graph_nearest": ([vp, i32, i32, ctypes.POINTER(i32)], ctypes.c_int),
    "rk_distance_m": ([ctypes.POINTER(Point), ctypes.POINTER(Point)], i32),
    "rk_min_seconds": ([i32], i32),
    "rk_route_dijkstra": ([vp, ctypes.c_int, ctypes.c_int, ctypes.POINTER(Route)], ctypes.c_int),
    "rk_route_astar": ([vp, ctypes.c_int, ctypes.c_int, ctypes.POINTER(Route)], ctypes.c_int),
    "rk_route_distances": ([vp, ctypes.c_int, ctypes.POINTER(i32)], ctypes.c_int),
    "rk_matrix_build": ([vp, ctypes.POINTER(i32), i32, ctypes.POINTER(i32)], ctypes.c_int),
    "rk_hop_penalty_s": ([], i32),
    "rk_polygon_init": ([ctypes.POINTER(Polygon)], ctypes.c_int),
    "rk_polygon_add": ([ctypes.POINTER(Polygon), i32, i32], ctypes.c_int),
    "rk_polygon_contains": ([ctypes.POINTER(Polygon), i32, i32], ctypes.c_int),
    "rk_polygon_boundary_distance": ([ctypes.POINTER(Polygon), i32, i32, ctypes.POINTER(i32)], ctypes.c_int),
    "rk_polygon_near": ([ctypes.POINTER(Polygon), i32, i32, i32], ctypes.c_int),
    "rk_polygon_area2": ([ctypes.POINTER(Polygon), ctypes.POINTER(i64)], ctypes.c_int),
    "rk_polygon_bbox": ([ctypes.POINTER(Polygon), ctypes.POINTER(Point), ctypes.POINTER(Point)], ctypes.c_int),
    "rk_sizeof_point": ([], ctypes.c_size_t),
    "rk_sizeof_graph": ([], ctypes.c_size_t),
    "rk_sizeof_route": ([], ctypes.c_size_t),
    "rk_sizeof_polygon": ([], ctypes.c_size_t),
}

_LIB = None


def library_path():
    return LIB_PATH


def library():
    """Load the shared library once, building it first when it is missing."""
    global _LIB
    if _LIB is None:
        if not LIB_PATH.exists():
            subprocess.run(["make", "-C", str(ROOT), "-s", "build"], check=True, capture_output=True)
        lib = ctypes.CDLL(str(LIB_PATH))
        for name, (argtypes, restype) in PROTOTYPES.items():
            fn = getattr(lib, name)
            fn.argtypes = argtypes
            fn.restype = restype
        _LIB = lib
    return _LIB


def check(rc, what=""):
    if rc < 0:
        raise NativeError(rc, what)
    return rc


def point_sizeof():
    return library().rk_sizeof_point()


def route_sizeof():
    return library().rk_sizeof_route()


def polygon_sizeof():
    return library().rk_sizeof_polygon()


def graph_sizeof():
    return library().rk_sizeof_graph()


def hop_penalty_s():
    return library().rk_hop_penalty_s()


@dataclass(frozen=True)
class Path:
    cost: int
    hops: int
    nodes: tuple
    expanded: int = 0


def _path(r):
    return Path(r.cost, r.hops, tuple(r.nodes[: r.hops + 1]), r.expanded)


class Graph:
    """Owning handle for a C rk_graph."""

    def __init__(self):
        self._h = library().rk_graph_new()
        if not self._h:
            raise MemoryError("rk_graph_new failed")

    def close(self):
        if self._h:
            library().rk_graph_free(self._h)
            self._h = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def add_node(self, x, y):
        return check(library().rk_graph_add_node(self._h, int(x), int(y)), "add node")

    def add_edge(self, a, b, seconds):
        check(library().rk_graph_add_edge(self._h, a, b, int(seconds)), "add edge")

    def add_road(self, a, b, speed_kmh, two_way=True):
        check(library().rk_graph_add_road(self._h, a, b, int(speed_kmh), 1 if two_way else 0), "add road")

    @property
    def node_count(self):
        return check(library().rk_graph_node_count(self._h))

    @property
    def edge_count(self):
        return check(library().rk_graph_edge_count(self._h))

    def point(self, node):
        p = Point()
        check(library().rk_graph_point(self._h, node, ctypes.byref(p)), "point")
        return p.x, p.y

    def nearest(self, x, y):
        d = i32()
        node = check(library().rk_graph_nearest(self._h, int(x), int(y), ctypes.byref(d)), "nearest")
        return node, d.value

    def dijkstra(self, a, b):
        r = Route()
        check(library().rk_route_dijkstra(self._h, a, b, ctypes.byref(r)), "dijkstra")
        return _path(r)

    def astar(self, a, b):
        r = Route()
        check(library().rk_route_astar(self._h, a, b, ctypes.byref(r)), "astar")
        return _path(r)

    def distances(self, source):
        out = (i32 * max(self.node_count, 1))()
        check(library().rk_route_distances(self._h, source, out), "distances")
        return list(out)[: self.node_count]

    def matrix(self, stops):
        n = len(stops)
        arr = (i32 * n)(*stops)
        out = (i32 * (n * n))()
        check(library().rk_matrix_build(self._h, arr, n, out), "matrix")
        return [list(out[i * n:(i + 1) * n]) for i in range(n)]


def distance_m(a, b):
    pa, pb = Point(*a), Point(*b)
    return library().rk_distance_m(ctypes.byref(pa), ctypes.byref(pb))


def min_seconds(dist_m):
    return library().rk_min_seconds(int(dist_m))


def make_polygon(points):
    poly = Polygon()
    lib = library()
    check(lib.rk_polygon_init(ctypes.byref(poly)), "polygon init")
    for x, y in points:
        check(lib.rk_polygon_add(ctypes.byref(poly), int(x), int(y)), "polygon add")
    return poly


def polygon_contains(poly, x, y):
    return bool(check(library().rk_polygon_contains(ctypes.byref(poly), int(x), int(y)), "contains"))


def polygon_boundary_distance(poly, x, y):
    out = i32()
    check(library().rk_polygon_boundary_distance(ctypes.byref(poly), int(x), int(y), ctypes.byref(out)), "boundary distance")
    return out.value


def polygon_near(poly, x, y, tol_m):
    return bool(check(library().rk_polygon_near(ctypes.byref(poly), int(x), int(y), int(tol_m)), "near"))


def polygon_area2(poly):
    out = i64()
    check(library().rk_polygon_area2(ctypes.byref(poly), ctypes.byref(out)), "area")
    return out.value


def polygon_bbox(poly):
    lo, hi = Point(), Point()
    check(library().rk_polygon_bbox(ctypes.byref(poly), ctypes.byref(lo), ctypes.byref(hi)), "bbox")
    return (lo.x, lo.y), (hi.x, hi.y)
