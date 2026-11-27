"""Synthetic microtransit requests for a run on a sample of the travelers (demand_upscaling; docs/open_issues.md I-32,
I-45).

When the demand file is a sample, a share s of all travelers, FleetPy would serve only the sample's microtransit
requests, and the fleet would be less busy than with all travelers. add_synthetic_requests() therefore adds
1 / s - 1 copies of each request of the sample to FleetPy's demand file before FleetPy runs (3 for s = 0.25, 9 for
s = 0.1): each request of the sample stands for 1 / s requests of all travelers. A copy is like a neighbor making a
similar trip at a similar time:
- its time is the request's time shifted at random by up to +-time_shift_s, kept inside the request's time period;
- its origin and its destination are each a random virtual stop within stop_radius_m walking distance of the
  request's (NearbyStops; the request's own stop is one of them), so the copies do not repeat the request's exact
  stops: exact repeats close in time would let FleetPy pool them for free (I-45);
- the direction is the request's.
The copies of a request are drawn with their own random generator, seeded with (the run's random_seed, the request
id), so they change only when that request changes. Their only purpose is to make the fleet as busy as with all
travelers: they are not travelers of MTSM (no trips, fares or logsums), but FleetPy's waiting times, rejection rate
and fleet results include them, as they should.

History: written by the user as synthesize_requests_with_trend_time (pre_process/generate_demand_files.py,
removed on the branch 2026-11-26; moved here on 2026-11-23, I-14), called by a commented-out block in
mtsm_model/microtransit.py: 3 synthetic requests per request
(for a 25 % sample), each with a time drawn from the 5-minute time-of-day profile of the iteration's requests
(smoothing 0.5 per bin) and one of their stop pairs (reversed with probability 0.5); ids from 60005; appended after
the sample's rows. 2026-11-25 (I-32): the switch demand_upscaling, ids from synthetic_id_start, times in the operating
periods, the file sorted. 2026-11-25 (I-45, user's decision): the copies described above replace the drawing from the
profile (which flattened the peaks, lost the direction of the trips over the day, and gave other numbers per period
than the factor); the old functions are in the git history.
"""
import heapq
import math
import sys

import numpy as np
import pandas as pd

FLEETPY_DEMAND_COLUMNS = ["rq_time", "start", "end", "request_id"]
WALK_LINK, MICRO_ACCESS_LINK = 0, 5  # link types of the super-network (docs/study_area_inputs.md)
MAX_DRAWS = 10  # draws of a copy's stops before it keeps the request's (origin and destination must differ)


def synthetic_id_start(traveler_ids, share):
    """The first request id of the synthetic requests: the smallest power of ten that is at least ten times the larger
    of (the largest traveler id + 1) and (the number of travelers / share, the size of the full demand). So the
    synthetic ids stay clear of every traveler's id, also of the travelers left out of the sample (as long as the full
    demand's ids stay below ten times that), and of the ids just above a traveler's own that MTSM gives to a second
    microtransit leg (trip_legs.free_request_id; add_synthetic_requests checks this in every iteration). Lemon Grove
    (3,742 travelers, ids up to 15,047, share 0.25): 1,000,000."""
    ids = list(traveler_ids)
    bound = max(max(ids) + 1, math.ceil(len(ids) / share))
    start = 1
    while start < 10 * bound:
        start *= 10
    return start


class NearbyStops:
    """The virtual stops of a super-network with microtransit (the walk nodes of its microtransit access links,
    type 5; FleetPy node = walk node) within radius_m of a node, by walking distance on its walk links (type 0;
    distance in m). The node itself is among them when it is a stop; an empty list when no stop is that close."""

    def __init__(self, network_file, num_walk_nodes, radius_m):
        self.radius_m = radius_m
        links = pd.read_csv(network_file, usecols=["from_node", "to_node", "distance", "link_type"])
        access = links[links["link_type"] == MICRO_ACCESS_LINK]
        self.stops = {int(a if a < num_walk_nodes else b) for a, b in zip(access["from_node"], access["to_node"])}
        self.adjacency = {}
        walk = links[links["link_type"] == WALK_LINK]
        for a, b, d in zip(walk["from_node"], walk["to_node"], walk["distance"]):
            self.adjacency.setdefault(int(a), []).append((int(b), float(d)))
        self._within = {}

    def within(self, node):
        node = int(node)
        if node not in self._within:
            dist = {node: 0.0}
            heap = [(0.0, node)]
            while heap:
                d, a = heapq.heappop(heap)
                if d > dist.get(a, math.inf):
                    continue
                for b, length in self.adjacency.get(a, ()):
                    nd = d + length
                    if nd <= self.radius_m and nd < dist.get(b, math.inf):
                        dist[b] = nd
                        heapq.heappush(heap, (nd, b))
            self._within[node] = sorted(x for x in dist if x in self.stops)
        return self._within[node]


_NEARBY = {}


def nearby_stops(network_file, num_walk_nodes, radius_m):
    """NearbyStops of a network file, made once per file and radius."""
    key = (network_file, num_walk_nodes, radius_m)
    if key not in _NEARBY:
        _NEARBY[key] = NearbyStops(network_file, num_walk_nodes, radius_m)
    return _NEARBY[key]


def _period_bounds(t, periods):
    """(lowest, highest) time of a copy of a request at t: the bounds of t's time period, periods = [(start, end)] in
    s, in order (a trip at t belongs to the first period with t <= end, else the last; config.period_of), widened to
    include t itself (t before the first start or after the last end)."""
    for i, (start, end) in enumerate(periods):
        if t <= end or i == len(periods) - 1:
            return min(start + 1, t), max(end, t)


def _shifted(t, shift, low, high):
    """t + shift, reflected into [low, high] (and cut to it if the shift is longer than the period)."""
    x = t + shift
    if x < low:
        x = 2 * low - x
    if x > high:
        x = 2 * high - x
    return min(max(x, low), high)


def synthesize_requests(df, factor, first_id, periods, nearby_by_period, period_names, time_shift_s, seed):
    """The copies of the requests df (columns rq_time, start, end, request_id; FleetPy's demand file), factor
    (1 / share - 1) per request: a DataFrame with the columns of the file, ids first_id, first_id + 1, ... in the
    order of df. With a factor that is not whole, a request gets floor(factor) copies and one more with probability
    factor - floor(factor). periods: [(start, end)] in s of the time periods, in order; nearby_by_period: {period
    name: NearbyStops}, period_names in the order of periods."""
    whole, fraction = int(math.floor(factor)), factor - math.floor(factor)
    rows = []
    for t, start, end, rq_id in zip(df["rq_time"], df["start"], df["end"], df["request_id"]):
        rng = np.random.default_rng([int(seed), int(rq_id)])
        copies = whole + (1 if fraction > 0 and rng.random() < fraction else 0)
        low, high = _period_bounds(t, periods)
        period = period_names[next(i for i, (s, e) in enumerate(periods) if t <= e or i == len(periods) - 1)]
        nearby = nearby_by_period[period]
        near_start, near_end = nearby.within(start), nearby.within(end)
        for _ in range(copies):
            x = _shifted(t, int(rng.integers(-time_shift_s, time_shift_s + 1)), low, high)
            s, e = int(start), int(end)
            for _draw in range(MAX_DRAWS):
                s2 = near_start[int(rng.integers(len(near_start)))] if near_start else int(start)
                e2 = near_end[int(rng.integers(len(near_end)))] if near_end else int(end)
                if s2 != e2:
                    s, e = s2, e2
                    break
            rows.append((x, s, e))
    out = pd.DataFrame(rows, columns=["rq_time", "start", "end"])
    out["request_id"] = np.arange(first_id, first_id + len(out), dtype=np.int64)
    return out


def add_synthetic_requests(fleetpy_demand_file, share, id_start, periods, nearby_by_period, period_names,
                           time_shift_s, seed):
    """Add the copies of one iteration to FleetPy's demand file (written by iteration.run_iteration with the sample's
    microtransit legs): synthesize_requests with factor 1 / share - 1, ids from id_start. All rows are written sorted by
    rq_time (a stable sort): FleetPy takes the requests of one time step in the order of the file (I-32). Stops if a
    request id of the file reaches id_start. Returns (the number of requests of the sample, the number added)."""
    df = pd.read_csv(fleetpy_demand_file)
    if list(df.columns) != FLEETPY_DEMAND_COLUMNS:
        sys.exit(f"ERROR: {fleetpy_demand_file}: the columns must be {FLEETPY_DEMAND_COLUMNS}, not {list(df.columns)}")
    n_real = len(df)
    if n_real == 0:
        return 0, 0  # no microtransit request in the sample
    if int(df["request_id"].max()) >= id_start:
        sys.exit(f"ERROR: {fleetpy_demand_file}: request id {int(df['request_id'].max())} reaches the first id of the "
                 f"synthetic requests ({id_start}); synthetic_demand.synthetic_id_start must give a larger one")
    new_df = synthesize_requests(df, 1 / share - 1, id_start, periods, nearby_by_period, period_names, time_shift_s,
                                 seed)
    out = pd.concat([df, new_df], ignore_index=True) if len(new_df) else df
    out = out.sort_values("rq_time", kind="mergesort")
    out.to_csv(fleetpy_demand_file, index=False)
    return n_real, len(new_df)
