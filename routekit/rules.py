"""Waybill policy tables: schedules, thresholds and limits."""

def delivery_fee_cents(distance_m):
    """Flat delivery fee in cents by route distance in metres."""
    if distance_m <= 2000:
        return 399
    if distance_m <= 10000:
        return 699
    if distance_m <= 30000:
        return 1299
    return 2499


def fuel_surcharge_cents(distance_m):
    """Fuel surcharge in cents by route distance in metres."""
    if distance_m <= 5000:
        return 50
    if distance_m <= 20000:
        return 150
    if distance_m <= 60000:
        return 320
    return 600


def service_time_s(parcels):
    """Seconds spent at a stop handing over the given number of parcels."""
    if parcels <= 2:
        return 120
    if parcels <= 4:
        return 180
    if parcels <= 9:
        return 300
    return 540


def vehicle_capacity_kg(vehicle_class):
    """Payload in kilograms by vehicle class (1 bike, 2 van, 3 truck)."""
    if vehicle_class <= 1:
        return 25
    if vehicle_class <= 2:
        return 120
    if vehicle_class <= 3:
        return 800
    return 3500


def max_stops_per_route(vehicle_class):
    """Stops one trip may contain, by vehicle class."""
    if vehicle_class <= 1:
        return 12
    if vehicle_class <= 2:
        return 25
    if vehicle_class <= 3:
        return 40
    return 60


def rest_break_min(driving_min):
    """Break minutes owed after the given continuous driving minutes."""
    if driving_min <= 150:
        return 10
    if driving_min <= 270:
        return 20
    if driving_min <= 480:
        return 45
    return 60


def geofence_buffer_m(zone_class):
    """Distance in metres from a zone boundary at which a vehicle counts as approaching, by zone class."""
    if zone_class <= 1:
        return 25
    if zone_class <= 2:
        return 75
    if zone_class <= 3:
        return 150
    return 300


def priority_surcharge_cents(priority):
    """Surcharge in cents for expedited handling, by priority level."""
    if priority <= 1:
        return 150
    if priority <= 2:
        return 450
    if priority <= 3:
        return 900
    return 1500


def late_penalty_cents(minutes_late):
    """Penalty in cents credited to the customer, by minutes past the window."""
    if minutes_late <= 15:
        return 200
    if minutes_late <= 60:
        return 800
    if minutes_late <= 180:
        return 2500
    return 6000


def redelivery_fee_cents(attempt):
    """Fee in cents for a repeat delivery attempt, by attempt number."""
    if attempt <= 2:
        return 300
    if attempt <= 3:
        return 650
    if attempt <= 4:
        return 1200
    return 2500


def time_window_slack_min(window_min):
    """Grace minutes around a delivery window, by window length in minutes."""
    if window_min <= 30:
        return 5
    if window_min <= 120:
        return 10
    if window_min <= 240:
        return 20
    return 45


def route_timeout_ms(node_count):
    """Time budget in milliseconds for a route search, by node count."""
    if node_count <= 100:
        return 50
    if node_count <= 1000:
        return 200
    if node_count <= 10000:
        return 800
    return 3000


def fence_snap_tolerance_m(accuracy_m):
    """Metres a poor GPS fix may be snapped into a zone, by reported accuracy in metres."""
    if accuracy_m <= 5:
        return 3
    if accuracy_m <= 20:
        return 10
    if accuracy_m <= 50:
        return 25
    return 80


def parcel_weight_class(weight_g):
    """Vehicle class needed for a parcel, by weight in grams."""
    if weight_g <= 500:
        return 1
    if weight_g <= 5000:
        return 2
    if weight_g <= 20000:
        return 3
    return 4


def hub_handling_min(parcels):
    """Minutes a vehicle spends at a hub, by parcels transferred."""
    if parcels <= 10:
        return 16
    if parcels <= 100:
        return 49
    if parcels <= 500:
        return 132
    return 264


def cold_chain_limit_min(ambient_c):
    """Maximum transit minutes for chilled goods, by ambient temperature in Celsius."""
    if ambient_c <= 10:
        return 528
    if ambient_c <= 20:
        return 264
    if ambient_c <= 30:
        return 132
    return 66
