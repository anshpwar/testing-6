#include <stdlib.h>

#include "rk_graph.h"

rk_graph *rk_graph_new(void) {
    return calloc(1, sizeof(rk_graph));
}

void rk_graph_free(rk_graph *g) {
    free(g);
}

static int valid_node(const rk_graph *g, int node) {
    return g != NULL && node >= 0 && node < g->n_nodes;
}

int32_t rk_min_seconds(int32_t dist_m) {
    if (dist_m < 0) {
        return 0;
    }
    return (int32_t)(((int64_t)dist_m * 36) / ((int64_t)RK_MAX_SPEED_KMH * 10));
}

int rk_graph_add_node(rk_graph *g, int32_t x, int32_t y) {
    if (g == NULL || x < -RK_COORD_LIMIT || x > RK_COORD_LIMIT || y < -RK_COORD_LIMIT || y > RK_COORD_LIMIT) {
        return RK_ERR_ARG;
    }
    if (g->n_nodes >= RK_MAX_NODES) {
        return RK_ERR_FULL;
    }
    g->pos[g->n_nodes].x = x;
    g->pos[g->n_nodes].y = y;
    g->head[g->n_nodes] = -1;
    return g->n_nodes++;
}

static void link_edge(rk_graph *g, int from, int to, int32_t seconds) {
    rk_edge *e = &g->edges[g->n_edges];
    e->to = to;
    e->seconds = seconds;
    e->next = g->head[from];
    g->head[from] = g->n_edges++;
}

int rk_graph_add_edge(rk_graph *g, int from, int to, int32_t seconds) {
    if (!valid_node(g, from) || !valid_node(g, to) || from == to) {
        return RK_ERR_ARG;
    }
    if (seconds < 1 || seconds > RK_MAX_EDGE_S) {
        return RK_ERR_RANGE;
    }
    if (seconds < rk_min_seconds(rk_distance_m(&g->pos[from], &g->pos[to]))) {
        return RK_ERR_RANGE;
    }
    if (g->n_edges >= RK_MAX_EDGES) {
        return RK_ERR_FULL;
    }
    link_edge(g, from, to, seconds);
    return RK_OK;
}

int rk_graph_add_road(rk_graph *g, int a, int b, int32_t speed_kmh, int two_way) {
    int need = two_way ? 2 : 1;
    int64_t divisor;
    int64_t seconds;
    if (!valid_node(g, a) || !valid_node(g, b) || a == b) {
        return RK_ERR_ARG;
    }
    if (speed_kmh < 1 || speed_kmh > RK_MAX_SPEED_KMH) {
        return RK_ERR_RANGE;
    }
    if (g->n_edges + need > RK_MAX_EDGES) {
        return RK_ERR_FULL;
    }
    divisor = (int64_t)speed_kmh * 10;
    seconds = ((int64_t)rk_distance_m(&g->pos[a], &g->pos[b]) * 36 + divisor - 1) / divisor;
    if (seconds < 1) {
        seconds = 1;
    }
    if (seconds > RK_MAX_EDGE_S) {
        return RK_ERR_RANGE;
    }
    link_edge(g, a, b, (int32_t)seconds);
    if (two_way) {
        link_edge(g, b, a, (int32_t)seconds);
    }
    return RK_OK;
}

int rk_graph_node_count(const rk_graph *g) {
    return g == NULL ? RK_ERR_ARG : g->n_nodes;
}

int rk_graph_edge_count(const rk_graph *g) {
    return g == NULL ? RK_ERR_ARG : g->n_edges;
}

int rk_graph_point(const rk_graph *g, int node, rk_point *out) {
    if (!valid_node(g, node) || out == NULL) {
        return RK_ERR_ARG;
    }
    *out = g->pos[node];
    return RK_OK;
}

int rk_graph_nearest(const rk_graph *g, int32_t x, int32_t y, int32_t *dist_m) {
    rk_point p;
    int best = -1;
    int32_t best_d = 0;
    int i;
    if (g == NULL || g->n_nodes == 0) {
        return RK_ERR_ARG;
    }
    p.x = x;
    p.y = y;
    for (i = 0; i < g->n_nodes; i++) {
        int32_t d = rk_distance_m(&g->pos[i], &p);
        if (best < 0 || d < best_d) {
            best = i;
            best_d = d;
        }
    }
    if (dist_m != NULL) {
        *dist_m = best_d;
    }
    return best;
}

size_t rk_sizeof_graph(void) {
    return sizeof(rk_graph);
}
