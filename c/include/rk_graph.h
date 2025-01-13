#ifndef RK_GRAPH_H
#define RK_GRAPH_H

#include "rk_config.h"

/* Position in metres on a local planar grid. Mirrored by routekit/native.py. */
typedef struct {
    int32_t x;
    int32_t y;
} rk_point;

typedef struct {
    int32_t to;
    int32_t seconds;
    int32_t next;
} rk_edge;

/* Directed weighted graph stored as per-node linked lists of edges. */
typedef struct rk_graph {
    int32_t n_nodes;
    int32_t n_edges;
    rk_point pos[RK_MAX_NODES];
    int32_t head[RK_MAX_NODES];
    rk_edge edges[RK_MAX_EDGES];
} rk_graph;

rk_graph *rk_graph_new(void);
void rk_graph_free(rk_graph *g);

/* Returns the new node index. */
int rk_graph_add_node(rk_graph *g, int32_t x, int32_t y);
/* Edge weight in seconds; rejected when faster than RK_MAX_SPEED_KMH allows. */
int rk_graph_add_edge(rk_graph *g, int from, int to, int32_t seconds);
/* Edge weight derived from the distance between the two nodes at speed_kmh. */
int rk_graph_add_road(rk_graph *g, int a, int b, int32_t speed_kmh, int two_way);

int rk_graph_node_count(const rk_graph *g);
int rk_graph_edge_count(const rk_graph *g);
int rk_graph_point(const rk_graph *g, int node, rk_point *out);
/* Index of the node closest to (x, y); distance in metres goes to dist_m when given. */
int rk_graph_nearest(const rk_graph *g, int32_t x, int32_t y, int32_t *dist_m);

/* Straight-line distance in metres, rounded to nearest. */
int32_t rk_distance_m(const rk_point *a, const rk_point *b);
/* Fastest possible travel time in seconds over dist_m (lower bound used by A*). */
int32_t rk_min_seconds(int32_t dist_m);

size_t rk_sizeof_point(void);
size_t rk_sizeof_graph(void);

#endif
