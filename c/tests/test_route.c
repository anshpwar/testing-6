#include <stdlib.h>

#include "check.h"
#include "rk_route.h"

/* Diamond with a shortcut: 0 -> 1 -> 3 is the quickest, 0 -> 2 -> 3 the runner-up. */
static rk_graph *diamond(void) {
    rk_graph *g = rk_graph_new();
    rk_graph_add_node(g, 0, 0);
    rk_graph_add_node(g, 500, 0);
    rk_graph_add_node(g, 250, 400);
    rk_graph_add_node(g, 1000, 0);
    rk_graph_add_edge(g, 0, 1, 60);
    rk_graph_add_edge(g, 1, 3, 60);
    rk_graph_add_edge(g, 0, 2, 50);
    rk_graph_add_edge(g, 2, 3, 80);
    rk_graph_add_edge(g, 1, 2, 20);
    return g;
}

/* 5 x 5 grid with alternating road speeds. */
static rk_graph *grid(void) {
    static const int32_t speeds[3] = {30, 50, 70};
    rk_graph *g = rk_graph_new();
    int r;
    int c;
    for (r = 0; r < 5; r++) {
        for (c = 0; c < 5; c++) {
            rk_graph_add_node(g, c * 400, r * 400);
        }
    }
    for (r = 0; r < 5; r++) {
        for (c = 0; c < 5; c++) {
            int n = r * 5 + c;
            if (c < 4) {
                rk_graph_add_road(g, n, n + 1, speeds[(r + c) % 3], 1);
            }
            if (r < 4) {
                rk_graph_add_road(g, n, n + 5, speeds[(r * 2 + c) % 3], 1);
            }
        }
    }
    return g;
}

int main(void) {
    rk_graph *g = diamond();
    rk_graph *big = grid();
    rk_route rd;
    rk_route ra;
    int32_t dist[RK_MAX_NODES];
    int from;
    int to;

    /* layout */
    CHECK_EQ(rk_sizeof_route(), sizeof(rk_route));
    CHECK_EQ(sizeof(rk_route), 4 + 4 + 4 * RK_MAX_PATH);
    CHECK_EQ(rk_hop_penalty_s(), RK_HOP_PENALTY_S);

    /* quickest path 0 -> 1 -> 3 */
    CHECK_EQ(rk_route_dijkstra(g, 0, 3, &rd), RK_OK);
    CHECK_EQ(rd.cost, 180); /* 60 + 60 + 2 hops */
    CHECK_EQ(rd.hops, 2);
    CHECK_EQ(rd.nodes[0], 0);
    CHECK_EQ(rd.nodes[1], 1);
    CHECK_EQ(rd.nodes[2], 3);
    CHECK_EQ(rd.nodes[3], -1);
    CHECK_EQ(rk_route_astar(g, 0, 3, &ra), RK_OK);
    CHECK_EQ(ra.cost, 180);
    CHECK_EQ(ra.hops, 2);

    /* trivial, missing and invalid routes */
    CHECK_EQ(rk_route_dijkstra(g, 2, 2, &rd), RK_OK);
    CHECK_EQ(rd.cost, 0);
    CHECK_EQ(rd.hops, 0);
    CHECK_EQ(rk_route_dijkstra(g, 3, 0, &rd), RK_ERR_NOPATH);
    CHECK_EQ(rk_route_astar(g, 3, 0, &ra), RK_ERR_NOPATH);
    CHECK_EQ(rk_route_dijkstra(g, 0, 9, &rd), RK_ERR_ARG);
    CHECK_EQ(rk_route_dijkstra(g, -1, 1, &rd), RK_ERR_ARG);
    CHECK_EQ(rk_route_dijkstra(NULL, 0, 1, &rd), RK_ERR_ARG);
    CHECK_EQ(rk_route_dijkstra(g, 0, 1, NULL), RK_ERR_ARG);

    /* single-source costs */
    CHECK_EQ(rk_route_distances(g, 0, dist), RK_OK);
    CHECK_EQ(dist[0], 0);
    CHECK_EQ(dist[1], 90); /* 60 + 1 hop */
    CHECK_EQ(dist[2], 80); /* direct 50 + 1 hop beats 60 + 20 + 2 hops */
    CHECK_EQ(dist[3], 180);
    CHECK_EQ(rk_route_distances(g, 3, dist), RK_OK);
    CHECK_EQ(dist[0], RK_COST_INF);

    /* A* agrees with Dijkstra between every pair on a larger grid */
    for (from = 0; from < 25; from++) {
        for (to = 0; to < 25; to++) {
            CHECK_EQ(rk_route_dijkstra(big, from, to, &rd), RK_OK);
            CHECK_EQ(rk_route_astar(big, from, to, &ra), RK_OK);
            CHECK_EQ(ra.cost, rd.cost);
            if (ra.cost != rd.cost) {
                return 1;
            }
        }
    }
    CHECK_EQ(rk_route_dijkstra(big, 0, 24, &rd), RK_OK);
    CHECK_EQ(rd.hops, 8);
    CHECK_EQ(rd.nodes[8], 24);

    rk_graph_free(g);
    rk_graph_free(big);
    CHECK_DONE();
}
