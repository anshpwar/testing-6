#ifndef RK_CONFIG_H
#define RK_CONFIG_H

#include <stddef.h>
#include <stdint.h>

/* Capacity limits. Mirrored by routekit/native.py. */
#define RK_MAX_NODES 128
#define RK_MAX_EDGES 1024
#define RK_MAX_PATH RK_MAX_NODES
#define RK_MAX_VERTS 64
#define RK_COORD_LIMIT 1000000
#define RK_MAX_EDGE_S 86400
#define RK_MAX_SPEED_KMH 130
#define RK_COST_INF INT32_MAX

/* Seconds added to every edge traversal for signals, turns and kerbside handling. */
#define RK_HOP_PENALTY_S 15

enum {
    RK_OK = 0,
    RK_ERR_ARG = -1,
    RK_ERR_FULL = -2,
    RK_ERR_NOPATH = -3,
    RK_ERR_RANGE = -4,
    RK_ERR_EMPTY = -5
};

#endif
