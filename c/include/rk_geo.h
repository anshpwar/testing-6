#ifndef RK_GEO_H
#define RK_GEO_H

#include "rk_graph.h"

/* Simple polygon in metres. Layout is mirrored by routekit/native.py. */
typedef struct {
    int32_t count;
    rk_point v[RK_MAX_VERTS];
} rk_polygon;

int rk_polygon_init(rk_polygon *p);
int rk_polygon_add(rk_polygon *p, int32_t x, int32_t y);
/* 1 when the point is inside or on the boundary, 0 when outside. */
int rk_polygon_contains(const rk_polygon *p, int32_t x, int32_t y);
/* Distance in metres from the point to the nearest edge. */
int rk_polygon_boundary_distance(const rk_polygon *p, int32_t x, int32_t y, int32_t *out);
/* 1 when inside, or outside by no more than tol_m metres. */
int rk_polygon_near(const rk_polygon *p, int32_t x, int32_t y, int32_t tol_m);
/* Twice the enclosed area in square metres (exact in integers). */
int rk_polygon_area2(const rk_polygon *p, int64_t *out);
int rk_polygon_bbox(const rk_polygon *p, rk_point *lo, rk_point *hi);

size_t rk_sizeof_polygon(void);

#endif
