#include "check.h"
#include "rk_route.h"

int main(void) {
    rk_graph *g = rk_graph_new();
    int32_t stops[3] = {0, 1, 3};
    int32_t m[9];
    int32_t bad[2] = {0, 7};

    rk_graph_add_node(g, 0, 0);
    rk_graph_add_node(g, 500, 0);
    rk_graph_add_node(g, 250, 400);
    rk_graph_add_node(g, 1000, 0);
    rk_graph_add_edge(g, 0, 1, 60);
    rk_graph_add_edge(g, 1, 3, 60);
    rk_graph_add_edge(g, 3, 0, 150);
    rk_graph_add_edge(g, 0, 2, 50);

    CHECK_EQ(rk_matrix_build(g, stops, 3, m), RK_OK);
    CHECK_EQ(m[0], 0);
    CHECK_EQ(m[1], 75); /* 0 -> 1: 60 + 1 hop */
    CHECK_EQ(m[2], 150); /* 0 -> 3: 120 + 2 hops */
    CHECK_EQ(m[3], 240); /* 1 -> 0 goes round through 3 */
    CHECK_EQ(m[4], 0);
    CHECK_EQ(m[5], 75);
    CHECK_EQ(m[6], 165);
    CHECK_EQ(m[8], 0);

    /* a node the stops cannot reach is reported as infinite */
    stops[1] = 2;
    CHECK_EQ(rk_matrix_build(g, stops, 3, m), RK_OK);
    CHECK_EQ(m[3], RK_COST_INF);

    CHECK_EQ(rk_matrix_build(g, bad, 2, m), RK_ERR_ARG);
    CHECK_EQ(rk_matrix_build(g, stops, 0, m), RK_ERR_ARG);
    CHECK_EQ(rk_matrix_build(NULL, stops, 3, m), RK_ERR_ARG);

    rk_graph_free(g);
    CHECK_DONE();
}
