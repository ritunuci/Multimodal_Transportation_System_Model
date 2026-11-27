"""Split a traveler's least-cost path into its trip legs (restructuring step 4, docs/entry_script_refactor_plan.md).

The path code was written twice in run_examples_new_parking.py: for the fixed-route-only base case and for the
case with microtransit. The functions below are the loops of the microtransit case, unchanged; the base case uses
the same functions (its path has no microtransit links).

The functions do not add anything up: they return the per-link values in path order, and the caller adds them to
its totals one by one, in the same order as before, so that the floating-point sums stay identical.

Link types (network_algorithms.KNOWN_LINK_TYPES): 0 walk, 1 fixed-route transit (FRT) in-vehicle, 2 FRT waiting,
4 microtransit in-vehicle, 5 microtransit waiting (type 3, an FRT transfer link that no network had, was removed on
2026-11-11).
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
    F_travel: List[float] = field(default_factory=list)  # FRT in-vehicle times (s)
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
    an in-vehicle link; a route change at a shared stop stays in the same leg.

    Since 2026-11-27 (I-46, branch TRA_resubmission, user's decisions) a leg starts at its boarding stop, the node
    before its first in-vehicle link, and its request time is the rider's arrival at the stop, the time before the
    boarding link (microtransit: the waiting link 5 that does not follow a ride link 4, which would be the 0-s
    alighting link; FRT: the link 2 that does not follow an FRT link 1). Until then the origin was the node after
    the first in-vehicle link and the request time the time there, after the modelled wait and the first link.
    """
    legs = TimeLegs()
    pre_link_type = None
    sum_link_type = 0  # recorde the pure walking trips
    # 11/07 Siwei: record the time of reaching the previous link
    pre_time = 0
    pre_node = None
    M_stop_arrival = F_stop_arrival = None  # the time (s after departure) the rider reached the boarding stop (I-46)
    for (node, time, link_type, route) in time_path:
        # the rider reaches a stop: the time before its boarding link (I-46, 2026-11-27)
        if link_type == 5 and pre_link_type != 4:
            M_stop_arrival = pre_time
        if link_type == 2 and pre_link_type != 1:
            F_stop_arrival = pre_time
        # calculate the number of microtransit trip legs
        if (pre_link_type != 4) and (link_type == 4):  ##1228 testing!
            if pre_link_type != 5:
                raise ValueError(f"a microtransit ride starts at node {node} without a waiting link before it")
            # the boarding stop and the arrival there (until 2026-11-27: node and round(time, 0), I-46)
            M_origin_node = pre_node
            request_time = rq_time + round(M_stop_arrival, 0)
        if (pre_link_type == 4) and (link_type != 4):  ##1228 testing!
            legs.M_legs.append((request_time, M_origin_node, pre_node))
        # calculate the number of fixed route transit trip legs
        if (pre_link_type != 1) and (link_type == 1):
            if pre_link_type != 2:
                raise ValueError(f"an FRT ride starts at node {node} without a boarding link before it")
            # the boarding stop and the arrival there (until 2026-11-27: node and int(time), I-46)
            F_origin_node = pre_node
            request_time = rq_time + int(F_stop_arrival)
        if (pre_link_type == 1) and (link_type != 1):
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
        if link_type == 1:
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
