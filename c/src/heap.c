#include "rk_heap.h"

void rk_heap_init(rk_heap *h) {
    h->size = 0;
}

static int less(const rk_heap_item *a, const rk_heap_item *b) {
    if (a->key != b->key) {
        return a->key < b->key;
    }
    return a->val < b->val;
}

int rk_heap_push(rk_heap *h, int32_t key, int32_t val) {
    int32_t i;
    if (h == NULL) {
        return RK_ERR_ARG;
    }
    if (h->size >= RK_HEAP_CAP) {
        return RK_ERR_FULL;
    }
    i = h->size++;
    h->items[i].key = key;
    h->items[i].val = val;
    while (i > 0) {
        int32_t parent = (i - 1) / 2;
        rk_heap_item tmp;
        if (!less(&h->items[i], &h->items[parent])) {
            break;
        }
        tmp = h->items[i];
        h->items[i] = h->items[parent];
        h->items[parent] = tmp;
        i = parent;
    }
    return RK_OK;
}

int rk_heap_pop(rk_heap *h, int32_t *key, int32_t *val) {
    int32_t i = 0;
    if (h == NULL || key == NULL || val == NULL) {
        return RK_ERR_ARG;
    }
    if (h->size == 0) {
        return RK_ERR_EMPTY;
    }
    *key = h->items[0].key;
    *val = h->items[0].val;
    h->size--;
    h->items[0] = h->items[h->size];
    for (;;) {
        int32_t left = 2 * i + 1;
        int32_t right = left + 1;
        int32_t smallest = i;
        rk_heap_item tmp;
        if (left < h->size && less(&h->items[left], &h->items[smallest])) {
            smallest = left;
        }
        if (right < h->size && less(&h->items[right], &h->items[smallest])) {
            smallest = right;
        }
        if (smallest == i) {
            break;
        }
        tmp = h->items[i];
        h->items[i] = h->items[smallest];
        h->items[smallest] = tmp;
        i = smallest;
    }
    return RK_OK;
}
