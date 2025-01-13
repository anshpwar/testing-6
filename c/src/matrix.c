#include "rk_route.h"

int rk_matrix_build(const rk_graph *g, const int32_t *stops, int32_t n, int32_t *out) {
    int32_t dist[RK_MAX_NODES];
    int32_t i;
    int32_t j;
    if (g == NULL || stops == NULL || out == NULL || n < 1 || n > RK_MAX_NODES) {
        return RK_ERR_ARG;
    }
    for (i = 0; i < n; i++) {
        if (stops[i] < 0 || stops[i] >= g->n_nodes) {
            return RK_ERR_ARG;
        }
    }
    for (i = 0; i < n; i++) {
        int rc = rk_route_distances(g, stops[i], dist);
        if (rc != RK_OK) {
            return rc;
        }
        for (j = 0; j < n; j++) {
            out[i * n + j] = dist[stops[j]];
        }
    }
    return RK_OK;
}
