#ifndef RK_HEAP_H
#define RK_HEAP_H

#include "rk_config.h"

#define RK_HEAP_CAP 4096

typedef struct {
    int32_t key;
    int32_t val;
} rk_heap_item;

/* Binary min-heap ordered by key, then by value so pops are deterministic. */
typedef struct {
    int32_t size;
    rk_heap_item items[RK_HEAP_CAP];
} rk_heap;

void rk_heap_init(rk_heap *h);
int rk_heap_push(rk_heap *h, int32_t key, int32_t val);
int rk_heap_pop(rk_heap *h, int32_t *key, int32_t *val);

#endif
