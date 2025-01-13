#include "check.h"
#include "rk_heap.h"

int main(void) {
    rk_heap h;
    int32_t key = 0;
    int32_t val = 0;
    int32_t i;
    int32_t last;

    rk_heap_init(&h);
    CHECK_EQ(rk_heap_pop(&h, &key, &val), RK_ERR_EMPTY);
    CHECK_EQ(rk_heap_push(NULL, 1, 1), RK_ERR_ARG);

    /* pops come out ordered by key */
    CHECK_EQ(rk_heap_push(&h, 50, 5), RK_OK);
    CHECK_EQ(rk_heap_push(&h, 10, 1), RK_OK);
    CHECK_EQ(rk_heap_push(&h, 30, 3), RK_OK);
    CHECK_EQ(rk_heap_push(&h, 20, 2), RK_OK);
    CHECK_EQ(rk_heap_pop(&h, &key, &val), RK_OK);
    CHECK_EQ(key, 10);
    CHECK_EQ(val, 1);
    CHECK_EQ(rk_heap_pop(&h, &key, &val), RK_OK);
    CHECK_EQ(key, 20);

    /* equal keys fall back to the value */
    rk_heap_init(&h);
    rk_heap_push(&h, 7, 9);
    rk_heap_push(&h, 7, 2);
    rk_heap_push(&h, 7, 5);
    rk_heap_pop(&h, &key, &val);
    CHECK_EQ(val, 2);
    rk_heap_pop(&h, &key, &val);
    CHECK_EQ(val, 5);

    /* a long pseudo-random run stays sorted */
    rk_heap_init(&h);
    for (i = 0; i < 1000; i++) {
        CHECK_EQ(rk_heap_push(&h, (i * 7919) % 1009, i), RK_OK);
    }
    last = -1;
    for (i = 0; i < 1000; i++) {
        rk_heap_pop(&h, &key, &val);
        if (key < last) {
            CHECK(key >= last);
        }
        last = key;
    }
    CHECK_EQ(h.size, 0);

    /* capacity is enforced */
    rk_heap_init(&h);
    for (i = 0; i < RK_HEAP_CAP; i++) {
        rk_heap_push(&h, i, i);
    }
    CHECK_EQ(rk_heap_push(&h, 1, 1), RK_ERR_FULL);

    CHECK_DONE();
}
