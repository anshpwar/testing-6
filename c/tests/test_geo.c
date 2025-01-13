#include "check.h"
#include "rk_geo.h"

static rk_polygon square(void) {
    rk_polygon p;
    rk_polygon_init(&p);
    rk_polygon_add(&p, 0, 0);
    rk_polygon_add(&p, 100, 0);
    rk_polygon_add(&p, 100, 100);
    rk_polygon_add(&p, 0, 100);
    return p;
}

/* L-shaped (concave) area: the notch is the square x > 100, y > 100 inside [0, 200]^2. */
static rk_polygon ell(void) {
    rk_polygon p;
    rk_polygon_init(&p);
    rk_polygon_add(&p, 0, 0);
    rk_polygon_add(&p, 200, 0);
    rk_polygon_add(&p, 200, 100);
    rk_polygon_add(&p, 100, 100);
    rk_polygon_add(&p, 100, 200);
    rk_polygon_add(&p, 0, 200);
    return p;
}

int main(void) {
    rk_polygon sq = square();
    rk_polygon l = ell();
    rk_polygon bad;
    rk_point lo;
    rk_point hi;
    int32_t d = -1;
    int64_t a2 = 0;
    int i;

    CHECK_EQ(rk_sizeof_polygon(), sizeof(rk_polygon));
    CHECK_EQ(sizeof(rk_polygon), 4 + 8 * RK_MAX_VERTS);
    CHECK_EQ(rk_distance_m(&sq.v[0], &sq.v[2]), 141);

    /* point in polygon: inside, outside, boundary and vertices */
    CHECK_EQ(rk_polygon_contains(&sq, 50, 50), 1);
    CHECK_EQ(rk_polygon_contains(&sq, 150, 50), 0);
    CHECK_EQ(rk_polygon_contains(&sq, -1, 50), 0);
    CHECK_EQ(rk_polygon_contains(&sq, 100, 50), 1);
    CHECK_EQ(rk_polygon_contains(&sq, 0, 0), 1);
    CHECK_EQ(rk_polygon_contains(&sq, 100, 100), 1);

    /* rays that pass exactly through vertices */
    CHECK_EQ(rk_polygon_contains(&sq, -50, 100), 0);
    CHECK_EQ(rk_polygon_contains(&sq, -50, 0), 0);
    CHECK_EQ(rk_polygon_contains(&l, 150, 100), 1);
    CHECK_EQ(rk_polygon_contains(&l, 50, 100), 1);
    CHECK_EQ(rk_polygon_contains(&l, -10, 100), 0);

    /* concave notch */
    CHECK_EQ(rk_polygon_contains(&l, 150, 50), 1);
    CHECK_EQ(rk_polygon_contains(&l, 50, 150), 1);
    CHECK_EQ(rk_polygon_contains(&l, 150, 150), 0);

    /* degenerate polygons are rejected */
    rk_polygon_init(&bad);
    rk_polygon_add(&bad, 0, 0);
    rk_polygon_add(&bad, 10, 10);
    CHECK_EQ(rk_polygon_contains(&bad, 1, 1), RK_ERR_ARG);
    CHECK_EQ(rk_polygon_contains(NULL, 1, 1), RK_ERR_ARG);

    /* distance to the boundary */
    CHECK_EQ(rk_polygon_boundary_distance(&sq, 50, -30, &d), RK_OK);
    CHECK_EQ(d, 30);
    CHECK_EQ(rk_polygon_boundary_distance(&sq, 150, 150, &d), RK_OK);
    CHECK_EQ(d, 71);
    CHECK_EQ(rk_polygon_boundary_distance(&sq, 40, 50, &d), RK_OK);
    CHECK_EQ(d, 40);
    CHECK_EQ(rk_polygon_boundary_distance(&sq, 1, 1, NULL), RK_ERR_ARG);

    /* tolerance check */
    CHECK_EQ(rk_polygon_near(&sq, 50, 50, 0), 1);
    CHECK_EQ(rk_polygon_near(&sq, 110, 50, 10), 1);
    CHECK_EQ(rk_polygon_near(&sq, 111, 50, 10), 0);
    CHECK_EQ(rk_polygon_near(&sq, 111, 50, -1), RK_ERR_RANGE);

    /* area and bounding box */
    CHECK_EQ(rk_polygon_area2(&sq, &a2), RK_OK);
    CHECK_EQ(a2, 20000);
    CHECK_EQ(rk_polygon_area2(&l, &a2), RK_OK);
    CHECK_EQ(a2, 60000);
    CHECK_EQ(rk_polygon_bbox(&l, &lo, &hi), RK_OK);
    CHECK_EQ(lo.x, 0);
    CHECK_EQ(hi.x, 200);
    CHECK_EQ(hi.y, 200);

    /* capacity */
    rk_polygon_init(&bad);
    for (i = 0; i < RK_MAX_VERTS; i++) {
        CHECK_EQ(rk_polygon_add(&bad, i, i * i % 97), RK_OK);
    }
    CHECK_EQ(rk_polygon_add(&bad, 0, 0), RK_ERR_FULL);
    CHECK_EQ(rk_polygon_add(&bad, RK_COORD_LIMIT + 1, 0), RK_ERR_ARG);

    CHECK_DONE();
}
