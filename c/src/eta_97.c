#include "rk_eta_97.h"

int32_t rk_eta_seconds(const rk_graph *g, int from, int to, int32_t dwell_s) {
    rk_route r;
    int rc;
    if (dwell_s < 0) {
        return RK_ERR_RANGE;
    }
    rc = rk_route_astar(g, from, to, &r);
    if (rc != RK_OK) {
        return rc;
    }
    if (r.cost > RK_COST_INF - dwell_s) {
        return RK_ERR_RANGE;
    }
    return r.cost + dwell_s;
}
