"""Split a traveler's least-cost path into its trip legs (restructuring step 4, docs/entry_script_refactor_plan.md).

The path code was written twice in run_examples_new_parking.py: for the fixed-route-only base case and for the
case with microtransit. The functions below are the loops of the microtransit case, unchanged; the base case uses
the same functions (its path has no microtransit links).

The functions do not add anything up: they return the per-link values in path order, and the caller adds them to
its totals one by one, in the same order as before, so that the floating-point sums stay identical.

Link types (network_algorithms.py): 0 walk, 1 fixed-route transit (FRT) in-vehicle, 2 FRT waiting, 3 FRT transfer,
4 microtransit in-vehicle, 5 microtransit waiting.
"""
from dataclasses import dataclass, field
from typing import List

from mtsm_model import config


@dataclass
class TimeLegs:
    M_legs: List[tuple] = field(default_factory=list)  # microtransit legs: (request_time, M_origin_node, M_dest_node)
    F_legs: List[tuple] = field(default_factory=list)  # FRT legs: (request_time, F_origin_node, F_dest_node)
    M_wait: List[float] = field(default_factory=list)  # microtransit waiting times (s)
    F_wait: List[float] = field(default_factory=list)  # FRT waiting times (s)
    walk: List[float] = field(default_factory=list)  # walking times (s)
    M_travel: List[float] = field(default_factory=list)  # microtransit in-vehicle times (s)
    F_travel: List[float] = field(default_factory=list)  # FRT in-vehicle and transfer times (s)
    walk_only: bool = False  # all links are walk links (the "pure walking trips")


@dataclass
class DistLegs:
    F_links: List[tuple] = field(default_factory=list)  # FRT links: (pre_node, node, miles)
    W_links: List[float] = field(default_factory=list)  # walk links: miles
    M_links: List[float] = field(default_factory=list)  # microtransit links: miles


def split_time_path(time_path, rq_time, iteration):
    """time_path: the path with arrival times, without its first and last element (path[1:-1]), as a list of
    (node, time, link_type, route). rq_time: the traveler's departure time (s).

    A leg's request time is set when the leg starts. An FRT leg starts at an in-vehicle link (1) that does not follow
    an FRT link (1 or 3). Before the change, an FRT leg whose first FRT link was a transfer link (3) would have
    reused the origin and request time of an earlier traveler; here it raises an error instead. The networks have no
    transfer links (checked 2026-11-09), so this cannot happen in the current model.
    """
    legs = TimeLegs()
    pre_link_type = None
    sum_link_type = 0  # recorde the pure walking trips
    # 11/07 Siwei: record the time of reaching the previous link
    pre_time = 0
    for (node, time, link_type, route) in time_path:
        # calculate the number of microtransit trip legs
        if (pre_link_type != 4) and (link_type == 4):  ##1228 testing!
            M_origin_node = node
            request_time = rq_time + round(time, 0)
        if (pre_link_type == 4) and (link_type != 4):  ##1228 testing!
            legs.M_legs.append((request_time, M_origin_node, pre_node))
        # calculate the number of fixed route transit trip legs
        if (pre_link_type != 1 and pre_link_type != 3) and (link_type == 1):
            F_origin_node = node
            request_time = rq_time + int(time)
        if (pre_link_type == 1) and (link_type != 1 and link_type != 3):
            legs.F_legs.append((request_time, F_origin_node, pre_node))
        # 11/07 Siwei: calculate the microtransit waiting time
        if (pre_link_type != 5) and (link_type == 5):
            M_wait_time = (time - pre_time)
            if iteration > 0 and M_wait_time == 180:
                print(f"MICRO WAIT TIME = {M_wait_time}")
            legs.M_wait.append(M_wait_time)
        # 11/07 Siwei: calculate the fixed route transit waiting time
        if (pre_link_type != 2) and (link_type == 2):
            legs.F_wait.append(time - pre_time)
        # 11/07 Siwei: calculate the walking time
        if link_type == 0:
            legs.walk.append(time - pre_time)
        # 12/22 Siwei: calculate the microtransit travel time
        if link_type == 4:
            M_travel_time = (time - pre_time)
            # 03/09/2026: Siwei add the following code for debug purpose
            if iteration > 0 and M_travel_time == 0:
                print(f"MICRO Link Travel Time = {M_travel_time}")
            legs.M_travel.append(M_travel_time)
        # 12/22 Siwei: calculate the fixed route transit travel time
        if link_type == 1 or link_type == 3:
            legs.F_travel.append(time - pre_time)

        pre_time = time
        sum_link_type += link_type
        pre_node = node
        pre_link_type = link_type
    legs.walk_only = (sum_link_type == 0)
    return legs


def split_dist_path(dist_path, first_pre_node):
    """dist_path: the path with cumulative distances (m), without its first and last element, as a list of
    (node, dist, link_type, route). first_pre_node: the "previous node" of the first link, used only in the key
    (pre_node, node) of an FRT link (the callers pass the first element of the microtransit path, also for the
    base case; the first link of a path is never an FRT link)."""
    legs = DistLegs()
    pre_dist = 0
    pre_node = first_pre_node
    for (node, dist, link_type, route) in dist_path:
        if link_type == 1:
            legs.F_links.append((pre_node, node, (dist - pre_dist) / config.MILE_METER))
        if link_type == 0:
            legs.W_links.append((dist - pre_dist) / config.MILE_METER)
        if link_type == 4:
            legs.M_links.append((dist - pre_dist) / config.MILE_METER)
        pre_dist = dist
        pre_node = node
    return legs


def count_transit_user(totals, num_M_trips, num_F_trips):
    """Count a transit traveler as pure microtransit, pure FRT, or microtransit + FRT user (IterationTotals)."""
    # calculate pure microtransit users:
    if num_M_trips != 0 and num_F_trips == 0:
        totals.pure_M_user += 1
    # calculate pure fixed route transit users:
    if num_M_trips == 0 and num_F_trips != 0:
        totals.pure_F_user += 1
    if num_M_trips != 0 and num_F_trips != 0:
        totals.M_F_user += 1


def free_request_id(rq_id, M_rq_id_list):
    """The first FleetPy request id from rq_id on that is not used yet (a traveler can have more than one
    microtransit trip)."""
    rq_id_fleetpy = rq_id
    while (rq_id_fleetpy in M_rq_id_list):
        rq_id_fleetpy += 1
    return rq_id_fleetpy
