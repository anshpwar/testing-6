#ifndef RK_ROUTE_H
#define RK_ROUTE_H

#include "rk_graph.h"

/* Result of a point-to-point search. nodes[0..hops] is the path, the rest is -1.
 * Layout is mirrored by routekit/native.py. */
typedef struct {
    int32_t cost;
    int32_t hops;
    int32_t expanded; /* nodes taken off the queue by the search */
    int32_t nodes[RK_MAX_PATH];
} rk_route;

int rk_route_dijkstra(const rk_graph *g, int from, int to, rk_route *out);
int rk_route_astar(const rk_graph *g, int from, int to, rk_route *out);
/* Single-source costs for every node; RK_COST_INF marks unreachable nodes. */
int rk_route_distances(const rk_graph *g, int from, int32_t *out);
/* Cost matrix between n stops (row-major, n * n values). */
int rk_matrix_build(const rk_graph *g, const int32_t *stops, int32_t n, int32_t *out);

int32_t rk_hop_penalty_s(void);
size_t rk_sizeof_route(void);

#endif
