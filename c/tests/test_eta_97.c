#include "check.h"
#include "rk_eta_97.h"

int main(void) {
    rk_graph *g = rk_graph_new();
    rk_graph_add_node(g, 0, 0);
    rk_graph_add_node(g, 500, 0);
    rk_graph_add_node(g, 250, 400);
    rk_graph_add_node(g, 1000, 0);
    rk_graph_add_edge(g, 0, 1, 60);
    rk_graph_add_edge(g, 1, 3, 60);
    rk_graph_add_edge(g, 0, 2, 50);
    rk_graph_add_edge(g, 2, 3, 80);

    CHECK_EQ(rk_eta_seconds(g, 0, 3, 120), 270); /* 150 s of driving including two hop penalties, plus 120 s dwell */
    CHECK_EQ(rk_eta_seconds(g, 0, 1, 0), 75);
    CHECK_EQ(rk_eta_seconds(g, 0, 2, 30), 95);
    CHECK_EQ(rk_eta_seconds(g, 3, 0, 10), RK_ERR_NOPATH);
    CHECK_EQ(rk_eta_seconds(g, 0, 3, -1), RK_ERR_RANGE);
    CHECK_EQ(rk_eta_seconds(g, 0, 3, RK_COST_INF), RK_ERR_RANGE);

    rk_graph_free(g);
    CHECK_DONE();
}
