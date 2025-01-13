#include <math.h>

#include "rk_geo.h"

int32_t rk_distance_m(const rk_point *a, const rk_point *b) {
    double dx = (double)a->x - (double)b->x;
    double dy = (double)a->y - (double)b->y;
    return (int32_t)llround(sqrt(dx * dx + dy * dy));
}

int rk_polygon_init(rk_polygon *p) {
    if (p == NULL) {
        return RK_ERR_ARG;
    }
    p->count = 0;
    return RK_OK;
}

int rk_polygon_add(rk_polygon *p, int32_t x, int32_t y) {
    if (p == NULL || x < -RK_COORD_LIMIT || x > RK_COORD_LIMIT || y < -RK_COORD_LIMIT || y > RK_COORD_LIMIT) {
        return RK_ERR_ARG;
    }
    if (p->count >= RK_MAX_VERTS) {
        return RK_ERR_FULL;
    }
    p->v[p->count].x = x;
    p->v[p->count].y = y;
    p->count++;
    return RK_OK;
}

static int usable(const rk_polygon *p) {
    return p != NULL && p->count >= 3 && p->count <= RK_MAX_VERTS;
}

static int64_t cross(rk_point a, rk_point b, int32_t x, int32_t y) {
    return (int64_t)(b.x - a.x) * (y - a.y) - (int64_t)(x - a.x) * (b.y - a.y);
}

static int on_segment(rk_point a, rk_point b, int32_t x, int32_t y) {
    if (cross(a, b, x, y) != 0) {
        return 0;
    }
    return x >= (a.x < b.x ? a.x : b.x) && x <= (a.x > b.x ? a.x : b.x) &&
           y >= (a.y < b.y ? a.y : b.y) && y <= (a.y > b.y ? a.y : b.y);
}

int rk_polygon_contains(const rk_polygon *p, int32_t x, int32_t y) {
    int inside = 0;
    int32_t i;
    if (!usable(p)) {
        return RK_ERR_ARG;
    }
    for (i = 0; i < p->count; i++) {
        rk_point a = p->v[i];
        rk_point b = p->v[(i + 1) % p->count];
        if (on_segment(a, b, x, y)) {
            return 1;
        }
        if ((a.y > y) != (b.y > y)) {
            int64_t c = cross(a, b, x, y);
            if (b.y > a.y ? c > 0 : c < 0) {
                inside = !inside;
            }
        }
    }
    return inside;
}

static double segment_distance(rk_point a, rk_point b, int32_t x, int32_t y) {
    double dx = (double)b.x - a.x;
    double dy = (double)b.y - a.y;
    double len2 = dx * dx + dy * dy;
    double t = 0.0;
    double px;
    double py;
    if (len2 > 0.0) {
        t = (((double)x - a.x) * dx + ((double)y - a.y) * dy) / len2;
        t = t < 0.0 ? 0.0 : (t > 1.0 ? 1.0 : t);
    }
    px = a.x + t * dx - x;
    py = a.y + t * dy - y;
    return sqrt(px * px + py * py);
}

int rk_polygon_boundary_distance(const rk_polygon *p, int32_t x, int32_t y, int32_t *out) {
    double best = -1.0;
    int32_t i;
    if (!usable(p) || out == NULL) {
        return RK_ERR_ARG;
    }
    for (i = 0; i < p->count; i++) {
        double d = segment_distance(p->v[i], p->v[(i + 1) % p->count], x, y);
        if (best < 0.0 || d < best) {
            best = d;
        }
    }
    *out = (int32_t)llround(best);
    return RK_OK;
}

int rk_polygon_near(const rk_polygon *p, int32_t x, int32_t y, int32_t tol_m) {
    int32_t d = 0;
    int rc = rk_polygon_contains(p, x, y);
    if (rc != 0) {
        return rc;
    }
    if (tol_m < 0) {
        return RK_ERR_RANGE;
    }
    rc = rk_polygon_boundary_distance(p, x, y, &d);
    if (rc != RK_OK) {
        return rc;
    }
    return d <= tol_m;
}

int rk_polygon_area2(const rk_polygon *p, int64_t *out) {
    int64_t sum = 0;
    int32_t i;
    if (!usable(p) || out == NULL) {
        return RK_ERR_ARG;
    }
    for (i = 0; i < p->count; i++) {
        rk_point a = p->v[i];
        rk_point b = p->v[(i + 1) % p->count];
        sum += (int64_t)a.x * b.y - (int64_t)b.x * a.y;
    }
    *out = sum < 0 ? -sum : sum;
    return RK_OK;
}

int rk_polygon_bbox(const rk_polygon *p, rk_point *lo, rk_point *hi) {
    int32_t i;
    if (!usable(p) || lo == NULL || hi == NULL) {
        return RK_ERR_ARG;
    }
    *lo = p->v[0];
    *hi = p->v[0];
    for (i = 1; i < p->count; i++) {
        if (p->v[i].x < lo->x) lo->x = p->v[i].x;
        if (p->v[i].y < lo->y) lo->y = p->v[i].y;
        if (p->v[i].x > hi->x) hi->x = p->v[i].x;
        if (p->v[i].y > hi->y) hi->y = p->v[i].y;
    }
    return RK_OK;
}

size_t rk_sizeof_point(void) {
    return sizeof(rk_point);
}

size_t rk_sizeof_polygon(void) {
    return sizeof(rk_polygon);
}
