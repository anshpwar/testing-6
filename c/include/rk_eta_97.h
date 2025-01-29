#ifndef RK_ETA_97_H
#define RK_ETA_97_H

#include "rk_route.h"

/* Seconds until a parcel is handed over: routed travel time plus dwell at the stop.
 * Negative status code on error. */
int32_t rk_eta_seconds(const rk_graph *g, int from, int to, int32_t dwell_s);

#endif
