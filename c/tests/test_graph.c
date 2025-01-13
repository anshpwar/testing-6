#include "check.h"
#include "rk_graph.h"

int main(void) {
    rk_graph *g = rk_graph_new();
    rk_point p;
    int32_t d = -1;
    int a;
    int b;
    int c;
    int i;

    CHECK(g != NULL);
    CHECK_EQ(rk_graph_node_count(g), 0);
    CHECK_EQ(rk_graph_nearest(g, 0, 0, &d), RK_ERR_ARG);

    a = rk_graph_add_node(g, 0, 0);
    b = rk_graph_add_node(g, 600, 0);
    c = rk_graph_add_node(g, 600, 800);
    CHECK_EQ(a, 0);
    CHECK_EQ(b, 1);
    CHECK_EQ(c, 2);
    CHECK_EQ(rk_graph_add_node(g, RK_COORD_LIMIT + 1, 0), RK_ERR_ARG);
    CHECK_EQ(rk_graph_add_node(NULL, 0, 0), RK_ERR_ARG);

    /* roads: 600 m at 36 km/h is 60 s, 800 m at 72 km/h is 40 s */
    CHECK_EQ(rk_graph_add_road(g, a, b, 36, 1), RK_OK);
    CHECK_EQ(rk_graph_edge_count(g), 2);
    CHECK_EQ(g->edges[g->head[a]].seconds, 60);
    CHECK_EQ(g->edges[g->head[b]].seconds, 60);
    CHECK_EQ(rk_graph_add_road(g, b, c, 72, 0), RK_OK);
    CHECK_EQ(rk_graph_edge_count(g), 3);
    CHECK_EQ(g->edges[g->head[b]].to, c);
    CHECK_EQ(g->edges[g->head[b]].seconds, 40);
    CHECK_EQ(g->head[c], -1);

    /* rejected roads and edges */
    CHECK_EQ(rk_graph_add_road(g, a, a, 50, 1), RK_ERR_ARG);
    CHECK_EQ(rk_graph_add_road(g, a, 9, 50, 1), RK_ERR_ARG);
    CHECK_EQ(rk_graph_add_road(g, a, c, 0, 1), RK_ERR_RANGE);
    CHECK_EQ(rk_graph_add_road(g, a, c, RK_MAX_SPEED_KMH + 1, 1), RK_ERR_RANGE);
    CHECK_EQ(rk_graph_add_edge(g, a, c, 0), RK_ERR_RANGE);
    CHECK_EQ(rk_graph_add_edge(g, a, c, 5), RK_ERR_RANGE); /* 1000 m cannot take 5 s */
    CHECK_EQ(rk_graph_add_edge(g, a, c, 90), RK_OK);
    CHECK_EQ(rk_graph_edge_count(g), 4);

    /* nearest node and point lookup */
    CHECK_EQ(rk_graph_nearest(g, 600, 700, &d), c);
    CHECK_EQ(d, 100);
    CHECK_EQ(rk_graph_nearest(g, 290, 0, NULL), a);
    CHECK_EQ(rk_graph_point(g, c, &p), RK_OK);
    CHECK_EQ(p.x, 600);
    CHECK_EQ(p.y, 800);
    CHECK_EQ(rk_graph_point(g, 3, &p), RK_ERR_ARG);

    /* lower bound on travel time */
    CHECK_EQ(rk_min_seconds(0), 0);
    CHECK_EQ(rk_min_seconds(1300), 36);
    CHECK_EQ(rk_min_seconds(-5), 0);

    /* capacity */
    for (i = 3; i < RK_MAX_NODES; i++) {
        CHECK(rk_graph_add_node(g, i, i) == i);
    }
    CHECK_EQ(rk_graph_add_node(g, 1, 1), RK_ERR_FULL);

    CHECK_EQ(rk_sizeof_point(), sizeof(rk_point));
    CHECK_EQ(rk_sizeof_graph(), sizeof(rk_graph));
    rk_graph_free(g);
    CHECK_DONE();
}
