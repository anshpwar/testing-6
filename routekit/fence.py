"""Geofences: delivery zones as polygons checked by the C point-in-polygon routines."""
import json

from . import native, rules


class Zone:
    def __init__(self, name, points, zone_class=1):
        if len(points) < 3:
            raise ValueError("a zone needs at least three vertices")
        self.name = name
        self.zone_class = zone_class
        self.points = [tuple(p) for p in points]
        self._poly = native.make_polygon(self.points)

    def contains(self, x, y):
        return native.polygon_contains(self._poly, x, y)

    def boundary_distance(self, x, y):
        return native.polygon_boundary_distance(self._poly, x, y)

    def near(self, x, y, tolerance_m):
        return native.polygon_near(self._poly, x, y, tolerance_m)

    def area_m2(self):
        return native.polygon_area2(self._poly) / 2

    def bbox(self):
        return native.polygon_bbox(self._poly)

    def buffer_m(self):
        """Distance from the boundary at which a vehicle counts as approaching the zone."""
        return rules.geofence_buffer_m(self.zone_class)


class ZoneSet:
    def __init__(self, zones=()):
        self.zones = []
        for z in zones:
            self.add(z)

    def add(self, zone):
        if any(z.name == zone.name for z in self.zones):
            raise ValueError(f"duplicate zone {zone.name!r}")
        self.zones.append(zone)

    @classmethod
    def from_dict(cls, data):
        return cls(Zone(z["name"], z["points"], z.get("class", 1)) for z in data["zones"])

    @classmethod
    def load(cls, path):
        with open(path) as fh:
            return cls.from_dict(json.load(fh))

    def locate(self, x, y, accuracy_m=0):
        """Zones holding the position. A fix with poor accuracy snaps to zones within the policy tolerance."""
        tol = rules.fence_snap_tolerance_m(accuracy_m)
        inside = []
        for z in self.zones:
            if z.contains(x, y) or (accuracy_m > 0 and z.near(x, y, tol)):
                inside.append(z.name)
        return inside

    def approaching(self, x, y):
        """Zones the position is outside of but within the zone's alert buffer."""
        out = []
        for z in self.zones:
            if not z.contains(x, y) and z.boundary_distance(x, y) <= z.buffer_m():
                out.append(z.name)
        return out

    def get(self, name):
        for z in self.zones:
            if z.name == name:
                return z
        raise KeyError(name)
