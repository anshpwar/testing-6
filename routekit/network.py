"""Named road network on top of the C routing core."""
import json

from . import native, rules


class UnknownStop(KeyError):
    pass


class Leg:
    """One routed trip between two named stops."""

    def __init__(self, names, path):
        self.names = list(names)
        self.cost_s = path.cost
        self.hops = path.hops

    def as_dict(self):
        return {"stops": self.names, "cost_s": self.cost_s, "hops": self.hops}


class Network:
    def __init__(self):
        self.graph = native.Graph()
        self._index = {}
        self._names = []

    # ------------------------------------------------------------------ building
    def add_stop(self, name, x, y):
        if name in self._index:
            raise ValueError(f"duplicate stop {name!r}")
        self._index[name] = self.graph.add_node(x, y)
        self._names.append(name)
        return self._index[name]

    def add_road(self, a, b, speed_kmh=50, two_way=True):
        self.graph.add_road(self.node(a), self.node(b), speed_kmh, two_way)

    @classmethod
    def from_dict(cls, data):
        net = cls()
        for n in data["nodes"]:
            net.add_stop(n["id"], n["x"], n["y"])
        for r in data["roads"]:
            net.add_road(r["from"], r["to"], r.get("speed_kmh", 50), r.get("two_way", True))
        return net

    @classmethod
    def load(cls, path):
        with open(path) as fh:
            return cls.from_dict(json.load(fh))

    @classmethod
    def grid(cls, rows, cols, spacing_m=400, speed_kmh=50):
        """Rectangular street grid with stops named r<row>c<col>."""
        net = cls()
        for r in range(rows):
            for c in range(cols):
                net.add_stop(f"r{r}c{c}", c * spacing_m, r * spacing_m)
        for r in range(rows):
            for c in range(cols):
                if c + 1 < cols:
                    net.add_road(f"r{r}c{c}", f"r{r}c{c + 1}", speed_kmh)
                if r + 1 < rows:
                    net.add_road(f"r{r}c{c}", f"r{r + 1}c{c}", speed_kmh)
        return net

    # ------------------------------------------------------------------ lookups
    def node(self, name):
        try:
            return self._index[name]
        except KeyError:
            raise UnknownStop(name) from None

    def name(self, node):
        return self._names[node]

    @property
    def stops(self):
        return list(self._names)

    def position(self, name):
        return self.graph.point(self.node(name))

    def nearest_stop(self, x, y):
        node, dist = self.graph.nearest(x, y)
        return self._names[node], dist

    # ------------------------------------------------------------------ routing
    def route(self, a, b, algorithm="astar"):
        search = {"astar": self.graph.astar, "dijkstra": self.graph.dijkstra}[algorithm]
        path = search(self.node(a), self.node(b))
        return Leg([self._names[i] for i in path.nodes], path)

    def reachable(self, a, b):
        return self.graph.distances(self.node(a))[self.node(b)] != native.COST_INF

    def cost_matrix(self, names):
        return self.graph.matrix([self.node(n) for n in names])
