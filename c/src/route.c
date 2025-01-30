#include <string.h>

#include "rk_heap.h"
#include "rk_route.h"

/* Cost of traversing one edge: its travel time plus the per-hop handling penalty. */
static int32_t edge_cost(int32_t seconds) {
    return seconds + RK_HOP_PENALTY_S;
}

static int32_t heuristic(const rk_graph *g, int node, int goal) {
    return rk_min_seconds(rk_distance_m(&g->pos[node], &g->pos[goal]));
}

/* Label-correcting search. goal < 0 explores everything; use_h turns it into A*. */
static int search(const rk_graph *g, int from, int goal, int use_h, int32_t *dist, int32_t *prev, int32_t *expanded) {
    rk_heap heap;
    int i;

    *expanded = 0;
    if (g == NULL || from < 0 || from >= g->n_nodes || goal >= g->n_nodes) {
        return RK_ERR_ARG;
    }
    for (i = 0; i < g->n_nodes; i++) {
        dist[i] = RK_COST_INF;
        prev[i] = -1;
    }
    dist[from] = 0;
    rk_heap_init(&heap);
    if (rk_heap_push(&heap, use_h ? heuristic(g, from, goal) : 0, from) != RK_OK) {
        return RK_ERR_FULL;
    }
    for (;;) {
        int32_t key;
        int32_t u;
        int e;
        if (rk_heap_pop(&heap, &key, &u) != RK_OK) {
            return goal < 0 ? RK_OK : RK_ERR_NOPATH;
        }
        if (key > dist[u] + (use_h ? heuristic(g, u, goal) : 0)) {
            continue; /* stale queue entry */
        }
        (*expanded)++;
        if (u == goal) {
            return RK_OK;
        }
        for (e = g->head[u]; e >= 0; e = g->edges[e].next) {
            int32_t v = g->edges[e].to;
            int32_t cand = dist[u] + edge_cost(g->edges[e].seconds);
            if (cand < dist[v]) {
                dist[v] = cand;
                prev[v] = u;
                if (rk_heap_push(&heap, cand + (use_h ? heuristic(g, v, goal) : 0), v) != RK_OK) {
                    return RK_ERR_FULL;
                }
            }
        }
    }
}

static int build_path(const int32_t *dist, const int32_t *prev, int to, rk_route *out) {
    int32_t tmp[RK_MAX_PATH];
    int n = 0;
    int v = to;
    int i;
    while (v != -1) {
        if (n >= RK_MAX_PATH) {
            return RK_ERR_FULL;
        }
        tmp[n++] = v;
        v = prev[v];
    }
    memset(out, 0, sizeof(*out));
    out->cost = dist[to];
    out->hops = n - 1;
    for (i = 0; i < RK_MAX_PATH; i++) {
        out->nodes[i] = i < n ? tmp[n - 1 - i] : -1;
    }
    return RK_OK;
}

static int route(const rk_graph *g, int from, int to, int use_h, rk_route *out) {
    int32_t dist[RK_MAX_NODES];
    int32_t prev[RK_MAX_NODES];
    int32_t expanded = 0;
    int rc;
    if (out == NULL || to < 0) {
        return RK_ERR_ARG;
    }
    rc = search(g, from, to, use_h, dist, prev, &expanded);
    if (rc != RK_OK) {
        return rc;
    }
    rc = build_path(dist, prev, to, out);
    if (rc == RK_OK) {
        out->expanded = expanded;
    }
    return rc;
}

int rk_route_dijkstra(const rk_graph *g, int from, int to, rk_route *out) {
    return route(g, from, to, 0, out);
}

int rk_route_astar(const rk_graph *g, int from, int to, rk_route *out) {
    return route(g, from, to, 1, out);
}

int rk_route_distances(const rk_graph *g, int from, int32_t *out) {
    int32_t prev[RK_MAX_NODES];
    int32_t expanded = 0;
    if (out == NULL) {
        return RK_ERR_ARG;
    }
    return search(g, from, -1, 0, out, prev, &expanded);
}

int32_t rk_hop_penalty_s(void) {
    return RK_HOP_PENALTY_S;
}

size_t rk_sizeof_route(void) {
    return sizeof(rk_route);
}
