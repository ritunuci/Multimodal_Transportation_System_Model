"""Check a study area's inputs against docs/study_area_inputs.md before a run (Phase 4 of docs/study_area_plan.md,
2026-11-24).

    python tools/check_study_area.py [AREA]     default: the model file's study_area; exit code 1 on an error

The run calls check_study_area() at startup (config.check_run_config): an error stops it before any work, a warning
is printed. The node numbering (N walk nodes, first microtransit node M) is derived and checked by
config.derive_node_numbering before this check runs.

Errors (user's decision 2, 2026-11-24): missing files or columns, values of the wrong type, link types or node numbers
that break the numbering rule, FRT boarding links with 0 s or alighting links with more, trips that do not start and
end at walk nodes or a repeated request_id, negative travel coefficients, FRT links that differ between files 3, 4, 6
and 9 (by node pair and route; distances within 1 mm), a base-headway network (file 9) that is not file 4 at
base_frt_headway, a route table (file 10) that does not fit the FRT links, an FRT stop with no boarding link, road
edges that differ between FleetPy, the walk links and the microtransit links, or are missing from the car network,
trips that cannot reach their destination by walk + FRT or by car, FleetPy inputs that do not fit (vehicle start nodes
outside the network, probabilities not summing to 1, a constant config naming another network), an unknown
aggregation. Warnings: duplicate (from_node, to_node) pairs (decision E), departures after FleetPy's end_time
(decision 3). Not checked: whether a network is one strongly connected part (decision 4: TRA_input_data_prep builds
its networks that way; the trip-level rule is what the model needs).
"""
import csv
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mtsm_paths as mtsm

NETWORK_COLUMNS = ["from_node", "to_node", "distance", "travel_time", "link_type", "route"]
DEMAND_COLUMNS = ["rq_time", "start", "end", "request_id", "bt_c_0", "bt_c_ivt", "bt_c_gas", "bt_t_0", "bt_t_wk",
                  "bt_m_wt", "bt_f_wt", "bt_m_ivt", "bt_f_ivt", "bt_f_trfer", "bt_t_fr", "income"]
COEFFICIENTS = [c for c in DEMAND_COLUMNS if c.startswith("bt_")]
# optional demand column auto_available (2026-11-24): the values network_algorithms.to_bool accepts
AUTO_AVAILABLE_VALUES = {"true": True, "1": True, "1.0": True, "false": False, "0": False, "0.0": False}
DISTANCE_TOLERANCE_M = 1e-3  # FRT link distances: file 6 differs from the super-networks in the 7th decimal place
MAX_EXAMPLES = 3


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, text):
        self.errors.append(text)

    def warning(self, text):
        self.warnings.append(text)


def _examples(items):
    items = list(items)
    more = f" (and {len(items) - MAX_EXAMPLES} more)" if len(items) > MAX_EXAMPLES else ""
    return ", ".join(str(i) for i in items[:MAX_EXAMPLES]) + more


def _read_csv(path, columns, report, label):
    """rows of a csv file as dicts, or None (with an error) if the file or a column is missing"""
    if not os.path.isfile(path):
        report.error(f"{label}: file missing: {path}")
        return None
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in columns if c not in (reader.fieldnames or [])]
        if missing:
            report.error(f"{label}: missing columns {missing}: {path}")
            return None
        return list(reader)


def _convert(rows, columns, kind, report, label):
    """list of tuples with the columns converted (kind: int or float), or None (with an error) on a bad value"""
    out, bad = [], []
    for line_number, row in enumerate(rows, start=2):
        try:
            out.append(tuple(kind[c](row[c]) for c in columns))
        except (TypeError, ValueError):
            bad.append(line_number)
    if bad:
        report.error(f"{label}: values of the wrong type on lines {_examples(bad)}")
        return None
    return out


NETWORK_KIND = {"from_node": int, "to_node": int, "distance": float, "travel_time": float, "link_type": int, "route": int}


def _read_network(path, report, label, distance_column="distance"):
    columns = [distance_column if c == "distance" else c for c in NETWORK_COLUMNS]
    rows = _read_csv(path, columns, report, label)
    if rows is None:
        return None
    kind = dict(NETWORK_KIND)
    kind[distance_column] = float
    links = _convert(rows, columns, kind, report, label)
    if links is None:
        return None
    negative = [i + 2 for i, l in enumerate(links) if l[2] < 0 or l[3] < 0]
    if negative:
        report.error(f"{label}: negative distance or travel time on lines {_examples(negative)}")
    return links  # (from, to, distance, travel_time, link_type, route)


def _check_link_types(links, allowed, n, m, report, label):
    """the link types of a file and the node ranges of each type (docs/study_area_inputs.md, link types)"""
    walk = range(0, n)
    stops = range(n, m)
    micro = range(m, m + n)
    problems = defaultdict(list)
    for i, (a, b, dist, tt, lt, route) in enumerate(links, start=2):
        if lt not in allowed:
            problems[f"link type {lt} (allowed here: {sorted(allowed)})"].append(i)
        elif lt in (0, 7) and not (a in walk and b in walk):
            problems[f"type {lt} link not between walk nodes 0..{n - 1}"].append(i)
        elif lt == 1 and not (a in stops and b in stops):
            problems[f"type 1 link not between FRT stop nodes {n}..{m - 1}"].append(i)
        elif lt == 2:
            if a in walk and b in stops:
                if not tt > 0:
                    problems["FRT boarding link (type 2, walk -> stop) with travel time 0"].append(i)
            elif a in stops and b in walk:
                if tt != 0:
                    problems["FRT alighting link (type 2, stop -> walk) with travel time above 0"].append(i)
            else:
                problems["type 2 link not between a walk node and an FRT stop node"].append(i)
        elif lt == 4 and not (a in micro and b in micro):
            problems[f"type 4 link not between microtransit nodes {m}..{m + n - 1}"].append(i)
    for text, lines in problems.items():
        report.error(f"{label}: {text}, lines {_examples(lines)}")


def _duplicates(links, report, label, known=frozenset()):
    """warn about (from_node, to_node) pairs that appear more than once, except the pairs in `known` (the road
    network's own duplicates, reported once for FleetPy's edges)"""
    counts = Counter((l[0], l[1]) for l in links)
    dup = sorted(pair for pair, k in counts.items() if k > 1 and pair not in known)
    if dup:
        report.warning(f"{label}: {len(dup)} (from_node, to_node) pairs appear more than once; the run keeps the last "
                       f"link of each (decision E): {_examples(dup)}")


def _same_edges(a, b, tolerance=1e-6):
    """two lists of (from, to, distance): the same edges (with repeats) and distances"""
    if len(a) != len(b):
        return False
    return all(x[:2] == y[:2] and abs(x[2] - y[2]) <= tolerance for x, y in zip(sorted(a), sorted(b)))


def _reach(adjacency, origins_to_destinations):
    """[(origin, destination)] that cannot be reached (directed), one search per origin"""
    unreachable = []
    for origin, destinations in origins_to_destinations.items():
        seen, stack = {origin}, [origin]
        while stack:
            for nxt in adjacency.get(stack.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        unreachable += [(origin, d) for d in destinations if d not in seen]
    return unreachable


def _adjacency(links):
    adjacency = defaultdict(list)
    for l in links:
        adjacency[l[0]].append(l[1])
    return adjacency


def _period_of(t, params):
    """the time period of a departure at t (s), as config.period_of: the first whose end is at or after t, else the
    last"""
    periods, ends = params["time_periods"], params["period_end_h"]
    for period, end_h in zip(periods[:-1], ends[:-1]):
        if t <= end_h * 3600:
            return period
    return periods[-1]


def check_study_area(area, params, n, m):
    """Check the inputs of `area`. params: the run's parameters (config.PARAMETERS); n, m: the number of walk nodes and
    the first microtransit node (config.derive_node_numbering). Returns a Report (errors, warnings)."""
    report = Report()
    paths = mtsm.area_paths(area)
    virstops = params["virtual_stop_scenarios"]
    base_headway = params["base_frt_headway"]
    aggregation = params["aggregation"]
    if aggregation not in ("whole_region", "census_track"):
        report.error(f"aggregation must be whole_region or census_track, not {aggregation!r}")

    # ---- super-networks (files 3, 4, 9), car network (5), FRT links (6) ----
    # FleetPy's road edges first: their duplicate pairs are reported once, here, and not again for the walk, car
    # and microtransit links copied from them
    fleet_nodes_file = os.path.join(paths.fleetpy_inputs_dir, *paths.fleetpy_staged[0].split("/"))
    fleet_edges_file = os.path.join(paths.fleetpy_inputs_dir, *paths.fleetpy_staged[1].split("/"))
    rows = _read_csv(fleet_edges_file, ["from_node", "to_node", "distance", "travel_time"], report, "FleetPy edges.csv")
    fleet = None
    if rows is not None:
        fleet = _convert(rows, ["from_node", "to_node", "distance", "travel_time"],
                         {"from_node": int, "to_node": int, "distance": float, "travel_time": float},
                         report, "FleetPy edges.csv")
    road_duplicates = frozenset()
    if fleet is not None:
        _duplicates(fleet, report, "road network (FleetPy edges.csv; also in the walk, car and microtransit links)")
        counts = Counter((a, b) for a, b, d, t in fleet)
        pairs = {pair for pair, k in counts.items() if k > 1}
        road_duplicates = frozenset(pairs | {(a + m, b + m) for a, b in pairs})

    # files 3 and 5: one network for the whole day or one per time period (since 2026-11-24;
    # docs/period_networks_and_car_availability_plan.md, step 4); each distinct file is checked
    periods = params["time_periods"]
    micro = {}  # {label: links}: file 3 of each virtual-stop share, and of each period when given per period
    for v in virstops:
        try:
            files = paths.micro_network_files(v, periods)
        except ValueError as e:
            report.error(f"file 3 (virstop {v}): {e}")
            continue
        for p, f in files.items():
            label = f"file 3 (virstop {v})" if f == paths.super_network_micro_file(v) else f"file 3 (virstop {v}, {p})"
            if label in micro:
                continue
            micro[label] = _read_network(f, report, label)
            if micro[label] is not None:
                _check_link_types(micro[label], {0, 1, 2, 4, 5}, n, m, report, label)
                _duplicates(micro[label], report, label, road_duplicates)
    car = {}  # {period: links} of file 5
    car_files = {}  # {file: (label, links)}, each distinct file once
    try:
        car_by_period = paths.car_network_files(periods)
    except ValueError as e:
        report.error(f"file 5: {e}")
        car_by_period = {}
    for p, f in car_by_period.items():
        if f not in car_files:
            label = "file 5" if f == paths.car_network_file else f"file 5 ({p})"
            car_files[f] = (label, _read_network(f, report, label))
        car[p] = car_files[f][1]
    frt = _read_network(paths.super_network_frt_file, report, "file 4")
    base = _read_network(paths.super_network_frt_base_headway_file, report, "file 9")
    links6 = _read_network(paths.frt_links_file, report, "file 6", distance_column="distance (meters)")
    for links, allowed, label in ([(frt, {0, 1, 2}, "file 4"), (base, {0, 1, 2}, "file 9"), (links6, {1}, "file 6")]
                                  + [(links, {7}, label) for label, links in car_files.values()]):
        if links is not None:
            _check_link_types(links, allowed, n, m, report, label)
            if label != "file 6":
                _duplicates(links, report, label, road_duplicates)

    # FRT links (type 1) the same in files 3, 4, 6, 9 (node pair and route; distance within 1 mm)
    def frt_links(links):
        return sorted((l[0], l[1], l[5], l[2]) for l in links if l[4] == 1)
    reference = frt_links(links6) if links6 is not None else None
    if reference is not None:
        for label, links in list(micro.items()) + [("file 4", frt), ("file 9", base)]:
            if links is None:
                continue
            other = frt_links(links)
            if len(other) != len(reference) or any(x[:3] != y[:3] or abs(x[3] - y[3]) > DISTANCE_TOLERANCE_M
                                                   for x, y in zip(other, reference)):
                report.error(f"{label}: its FRT links (type 1) differ from file 6 (node pairs, routes or distances)")
    # file 9 = file 4 with every boarding time = base_frt_headway x 60 / 2
    if frt is not None and base is not None:
        expected = [(a, b, d, (base_headway * 60) / 2 if (lt == 2 and tt != 0) else tt, lt, r)
                    for a, b, d, tt, lt, r in frt]
        if sorted(expected) != sorted(base):
            report.error(f"file 9 is not file 4 with every FRT boarding time set to base_frt_headway x 60 / 2 "
                         f"({base_headway} min)")
    # every FRT stop with an in-vehicle link has a boarding link from a walk node
    if frt is not None:
        stops = {x for l in frt if l[4] == 1 for x in l[:2]}
        boarded = {l[1] for l in frt if l[4] == 2 and l[0] < n}
        lonely = sorted(stops - boarded)
        if lonely:
            report.error(f"file 4: FRT stop nodes without a boarding link from a walk node: {_examples(lonely)}")

    # ---- FRT route table (file 10) ----
    rows = _read_csv(paths.frt_routes_file, ["route", "direction", "n_stops", "length_m"], report, "file 10")
    if rows is not None:
        table = _convert(rows, ["route", "direction", "n_stops", "length_m"],
                         {"route": int, "direction": int, "n_stops": int, "length_m": float}, report, "file 10")
        if table is not None:
            repeated = [k for k, c in Counter((r, d) for r, d, s, l in table).items() if c > 1]
            if repeated:
                report.error(f"file 10: repeated (route, direction): {_examples(sorted(repeated))}")
            if any(l <= 0 or s < 2 for r, d, s, l in table):
                report.error("file 10: length_m must be > 0 and n_stops >= 2")
            if links6 is not None and {r for r, d, s, l in table} != {l[5] for l in links6}:
                report.error("file 10: its routes differ from those of file 6")

    # ---- road edges: FleetPy = walk links = microtransit links (shifted by M); all of them in the car network ----
    rows = _read_csv(fleet_nodes_file, ["node_index", "pos_x", "pos_y"], report, "FleetPy nodes.csv")
    if rows is not None:
        _convert(rows, ["node_index", "pos_x", "pos_y"], {"node_index": int, "pos_x": float, "pos_y": float},
                 report, "FleetPy nodes.csv")
    if fleet is not None:
        if any(not (0 <= a < n and 0 <= b < n) for a, b, d, t in fleet):
            report.error(f"FleetPy edges.csv: an edge has a node outside 0..{n - 1}")
        road = [(a, b, d) for a, b, d, t in fleet]
        for label, links in list(micro.items()) + [("file 4", frt)]:
            if links is None:
                continue
            if not _same_edges([(l[0], l[1], l[2]) for l in links if l[4] == 0], road):
                report.error(f"{label}: its walk links (type 0) are not FleetPy's road edges (node pairs, distances)")
            if label.startswith("file 3") and not _same_edges(
                    [(l[0] - m, l[1] - m, l[2]) for l in links if l[4] == 4], road):
                report.error(f"{label}: its microtransit links (type 4, minus {m}) are not FleetPy's road edges")
        for label, links in car_files.values():
            if links is None:
                continue
            car_edges = Counter((l[0], l[1], round(l[2], 6)) for l in links)
            missing = Counter((a, b, round(d, 6)) for a, b, d in road) - car_edges
            if missing:
                report.error(f"{label}: {sum(missing.values())} of FleetPy's road edges are missing from the car network: "
                             f"{_examples(sorted(missing))}")

    # ---- demand (file 2) ----
    rows = _read_csv(paths.demand_file, DEMAND_COLUMNS, report, "file 2")
    trips = None
    if rows is not None:
        kind = {c: float for c in DEMAND_COLUMNS}
        kind.update({"rq_time": int, "start": int, "end": int, "request_id": lambda v: int(float(v)),
                     "income": lambda v: int(float(v))})
        trips = _convert(rows, DEMAND_COLUMNS, kind, report, "file 2")
    if trips is not None:
        col = {c: i for i, c in enumerate(DEMAND_COLUMNS)}
        outside = [i + 2 for i, t in enumerate(trips) if not (0 <= t[col["start"]] < n and 0 <= t[col["end"]] < n)]
        if outside:
            report.error(f"file 2: trips that do not start and end at walk nodes 0..{n - 1}, lines {_examples(outside)}")
        repeated = [k for k, c in Counter(t[col["request_id"]] for t in trips).items() if c > 1]
        if repeated:
            report.error(f"file 2: repeated request_id: {_examples(sorted(repeated))}")
        negative = [i + 2 for i, t in enumerate(trips) if any(t[col[c]] < 0 for c in COEFFICIENTS)]
        if negative:
            report.error(f"file 2: negative travel coefficients (bt_*) on lines {_examples(negative)}")
        if any(t[col["rq_time"]] < 0 for t in trips):
            report.error("file 2: negative rq_time")
        # optional auto_available (2026-11-24): True / False or 1 / 0; missing column = every traveler has a car
        has_car = [True] * len(trips)
        if rows and "auto_available" in rows[0]:
            values = [AUTO_AVAILABLE_VALUES.get(str(r["auto_available"]).strip().lower()) for r in rows]
            invalid = [i + 2 for i, v in enumerate(values) if v is None]
            if invalid:
                report.error(f"file 2: auto_available must be True / False or 1 / 0, lines {_examples(invalid)}")
            else:
                has_car = values
        # every trip reaches its destination by walk + FRT (file 4), and by car (file 5 of its time period) if the
        # traveler has one
        if not outside:
            wanted_frt = defaultdict(set)
            wanted_car = defaultdict(lambda: defaultdict(set))  # {car file: {origin: destinations}}
            for t, car_available in zip(trips, has_car):
                if t[col["start"]] != t[col["end"]]:
                    wanted_frt[t[col["start"]]].add(t[col["end"]])
                    if car_available and car:
                        f = car_by_period[_period_of(t[col["rq_time"]], params)]
                        wanted_car[f][t[col["start"]]].add(t[col["end"]])
            checks = [(frt, "walk + FRT (file 4)", wanted_frt)]
            checks += [(car_files[f][1], f"car ({car_files[f][0]})", w) for f, w in wanted_car.items()]
            for links, label, wanted in checks:
                if links is not None:
                    unreachable = _reach(_adjacency(links), wanted)
                    if unreachable:
                        report.error(f"{len(unreachable)} trips cannot reach their destination by {label}: "
                                     f"(origin, destination) {_examples(sorted(unreachable))}")

    # ---- FleetPy inputs ----
    for staged in paths.fleetpy_staged[2:]:
        p = os.path.join(paths.fleetpy_inputs_dir, *staged.split("/"))
        if not os.path.isfile(p):
            report.error(f"FleetPy input missing: {p}")
    imbalanced = os.path.join(paths.fleetpy_inputs_dir, *paths.fleetpy_staged[3].split("/"))
    rows = _read_csv(imbalanced, ["node_index", "probability"], report, "imbalanced.csv")
    if rows is not None:
        start = _convert(rows, ["node_index", "probability"], {"node_index": int, "probability": float},
                         report, "imbalanced.csv")
        if start is not None:
            if any(not 0 <= node < n for node, p in start):
                report.error(f"imbalanced.csv: vehicle start nodes outside 0..{n - 1}")
            elif fleet is not None:
                # a vehicle placed on a node without a road edge (e.g. a freeway node, I-33) can never move
                on_edges = {x for a, b, d, t in fleet for x in (a, b)}
                stuck = sorted(node for node, p in start if node not in on_edges)
                if stuck:
                    report.error(f"imbalanced.csv: vehicle start nodes without a road edge in FleetPy's edges.csv: "
                                 f"{_examples(stuck)}")
            if any(p < 0 for node, p in start) or not math.isclose(sum(p for node, p in start), 1.0, abs_tol=1e-6):
                report.error("imbalanced.csv: the probabilities must be >= 0 and sum to 1")
    end_time = None
    for repositioning in params["repositioning_list"]:
        name = "%s_constant_config_ir_repo.csv" % area if repositioning else "%s_constant_config_ir.csv" % area
        p = os.path.join(paths.fleetpy_scenarios_dir, name)
        rows = _read_csv(p, ["Input_Parameter_Name", "Parameter_Value"], report, f"FleetPy {name}")
        if rows is None:
            continue
        values = {r["Input_Parameter_Name"]: r["Parameter_Value"] for r in rows}
        for key, expected in (("network_name", f"{area}_example_network"), ("demand_name", f"{area}_example_demand")):
            if values.get(key) != expected:
                report.error(f"FleetPy {name}: {key} must be {expected}, not {values.get(key)!r}")
        if values.get("op_init_veh_distribution") not in (None, "", "imbalanced.csv"):
            report.error(f"FleetPy {name}: op_init_veh_distribution must be imbalanced.csv")
        try:
            end_time = float(values.get("end_time"))
        except (TypeError, ValueError):
            report.error(f"FleetPy {name}: end_time is not a number")
    if trips is not None and end_time is not None:
        late = sum(1 for t in trips if t[0] >= end_time)
        if late:
            report.warning(f"file 2: {late} trips depart at or after FleetPy's end_time ({end_time:g} s); FleetPy does "
                           f"not simulate them (decision 3; time periods: I-35)")

    # ---- node file (file 7), read only with census_track ----
    if aggregation == "census_track":
        rows = _read_csv(paths.nodes_file, ["node_in_fleetpy", "census_tract"], report, "file 7")
        if rows is not None:
            nodes = _convert(rows, ["node_in_fleetpy", "census_tract"],
                             {"node_in_fleetpy": lambda v: int(float(v)), "census_tract": lambda v: int(float(v))},
                             report, "file 7")
            if nodes is not None and set(range(n)) - {a for a, b in nodes}:
                report.error("file 7: node_in_fleetpy does not cover every walk node (aggregation census_track)")
    return report


def print_report(area, report):
    for text in report.errors:
        print(f"ERROR: {text}")
    for text in report.warnings:
        print(f"WARNING: {text}")
    print(f"study area {area}: {len(report.errors)} errors, {len(report.warnings)} warnings")


if __name__ == "__main__":
    from mtsm_model import config  # reads the model file and the area file, derives the node numbering
    area = sys.argv[1] if len(sys.argv) > 1 else config.PARAMETERS["study_area"]
    if area != config.PARAMETERS["study_area"]:
        sys.exit(f"the parameters are those of study area {config.PARAMETERS['study_area']}; run with that area, or "
                 f"with MTSM_CONFIG_FILE pointing at a model file whose study_area is {area}")
    result = check_study_area(area, config.PARAMETERS, config.NUM_WALK_NODES, config.MICROTRANSIT_NODE_OFFSET)
    print_report(area, result)
    sys.exit(1 if result.errors else 0)
