"""Build an MTSM super-network from a road network (walk and microtransit) and an FRT network.

A representative script, written 2026-11-11 from the frozen Lemon Grove super-networks; no model code uses it yet
(docs/progress.md, "Super-network script"). It replaces the network construction of process_network.py, which reads
its inputs from outside folders.

The idea (that of the old construction code: standalone_scripts/pre_process/process_network_trial_edit.py and its
SacRT notebook): one network holds every way to travel without a car, so that a single least-cost path search finds
a trip that can mix walking, FRT and microtransit. Each mode has its own copy of the nodes (a layer). A trip starts
and ends on walk nodes, and the only way from one layer to another is a waiting link:
    - Walking is possible on every road edge, at the walk speed.
    - FRT runs only from stop to stop. A stop is entered and left at its nearest walk node. Boarding takes the
      expected waiting time, half the headway (one headway for all routes); alighting takes 0 s. A change of route
      at the same stop has no link of its own (the path search sees it from the route numbers of the two links).
    - Microtransit can drive on every road edge, in the car travel time times a factor, but it can be boarded and
      left only at a virtual stop (a walk node; 100 % of the nodes = door to door). The boarding time written here
      is a starting value: after each FleetPy run the model writes FleetPy's waiting times into its final networks.
    - The waiting links are also where the path search charges the fares and the transfer rules, so a transfer
      (FRT to FRT at another stop, FRT to microtransit, microtransit to FRT) is always alighting, walking (possibly
      0 m) and boarding again.
The networks of a study area differ only in three things: the headway (the boarding time of type 2), the virtual
stops (the links of type 5) and the modes present (the variant). The old code wrote one file per headway (10, 15,
20, 30, 60) and share of virtual stops (50, 75, 100 %); here one call writes one network.

The super-network has three layers on the same numbering:
    walk nodes          0 .. N-1                   the road nodes (FleetPy's node numbers)
    FRT stops           N .. N+S-1                 one per stop that has an FRT link, in stop_id order
    microtransit nodes  N+S .. N+S+N-1             a copy of the road nodes: walk node i = micro node N+S+i
and these link types (network_algorithms.KNOWN_LINK_TYPES):
    0 walk                    walk -> walk     every road edge; travel time = distance / walk speed
    1 FRT in-vehicle          stop -> stop     every FRT edge, with its route
    2 FRT waiting             walk -> stop     boarding: half the headway; stop -> walk: alighting, 0 s
    4 microtransit in-vehicle micro -> micro   every road edge; travel time = car travel time x factor
    5 microtransit waiting    walk -> micro    boarding at a virtual stop: the waiting time; micro -> walk: 0 s
Each stop is joined to its nearest walk node (by the coordinates); several stops can share a walk node. Variants:
"micro" has all these types, "non_micro" (no microtransit) types 0, 1 and 2, "micro_only" (no FRT) types 0, 4 and 5.
"micro_only" numbers the nodes like "micro" (the stops keep their numbers, without links), because the model has one
microtransit_node_offset for all networks. The links are written in the order of the frozen networks: walk links in
road-edge order; each FRT link, followed by the waiting links of a stop that appears for the first time; each
microtransit link, followed by the waiting links of a virtual stop that appears for the first time.

With --auto-out the car network is written too (the model reads it separately, as auto_edges.csv): every road edge
with its distance and car travel time, link type 7, in road-edge order.

Checked against the old code (2026-11-13): the notebook's own functions and this script, run on the same small
network (walk speed 1.6, the notebook's virtual stops), give the same links in the same order for all 15 files. What
is different here, on purpose:
    - Only the stops that have an FRT link get a number (old: every stop of the stop file); see above for
      "micro_only".
    - A tie between two nearest walk nodes goes to the smaller node number (old: the later one in the file).
    - The virtual stops of a share are drawn with a seed, so the same seed gives the same network, and with the same
      seed a smaller share is a part of a larger one (old: no seed, each share drawn separately).
    - The walk speed is an option, 1.251 m/s by default (old: 1.6 m/s in the walk links, then 1.251 m/s when the
      initial networks were written from them).
    - "non_micro" and "micro_only" are written directly (old: "non_micro" = the "micro" file cut at its first
      microtransit link; no "micro_only"); the car network is new.
Not done here, so the inputs must already have it (the old code did it in the same script):
    - the road network in FleetPy's form: nodes numbered 0 .. N-1, every road segment as two edges (one per
      direction), distance in m, car travel time = distance / speed limit;
    - the FRT network of the study area: only its stops, only the links with both stops in it, distance in m (the
      old inputs were in miles), one whole number as route per link (the old code took the first route of a link
      that had several, and gave routes with a name a number).

Inputs (CSV; other columns are ignored):
    road nodes   node_index,pos_x,pos_y                       node_index 0 .. N-1 (FleetPy's nodes.csv)
    road edges   from_node,to_node,distance,travel_time       m, s by car (FleetPy's edges.csv)
    FRT stops    stop_id,pos_x,pos_y
    FRT edges    from_stop,to_stop,distance,travel_time,route m, s, route number
    virtual stops (optional) node_index                       walk nodes with microtransit boarding
pos_x/pos_y of both networks must be in the same projected coordinates (distance = straight line), or longitude /
latitude with --latlon (distance on the sphere).

Usage (from the repository root):
    python pre_process/build_super_network.py --road-nodes nodes.csv --road-edges edges.csv \\
        --frt-stops stops.csv --frt-edges frt_edges.csv --variant micro --headway 10 \\
        --virtual-stop-share 75 --seed 0 --out super_network.csv --auto-out auto_edges.csv
The run prints num_walk_nodes and microtransit_node_offset for mtsm_constant_configurations.csv.
"""
import argparse
import csv
import math
import random
import sys

WALK, FRT, FRT_WAIT, MICRO, MICRO_WAIT, CAR = 0, 1, 2, 4, 5, 7
NO_ROUTE = -1
FIELDS = ["from_node", "to_node", "distance", "travel_time", "link_type", "route"]


def read_rows(path, columns):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in columns if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit("%s: missing column(s) %s" % (path, ", ".join(missing)))
        return list(reader)


def non_negative(value, what):
    x = float(value)
    if not math.isfinite(x) or x < 0:
        sys.exit("%s: %s is not a number >= 0" % (what, value))
    return x


def read_road(nodes_file, edges_file):
    """returns {node: (x, y)} and [(from, to, distance, travel time)]; nodes must be 0 .. N-1"""
    nodes = {}
    for r in read_rows(nodes_file, ["node_index", "pos_x", "pos_y"]):
        nodes[int(r["node_index"])] = (float(r["pos_x"]), float(r["pos_y"]))
    if sorted(nodes) != list(range(len(nodes))):
        sys.exit("%s: node_index must be 0 .. N-1 without gaps (they become the walk node numbers)" % nodes_file)
    edges = []
    for r in read_rows(edges_file, ["from_node", "to_node", "distance", "travel_time"]):
        a, b = int(r["from_node"]), int(r["to_node"])
        if a not in nodes or b not in nodes:
            sys.exit("%s: edge %s -> %s has a node that is not in %s" % (edges_file, a, b, nodes_file))
        edges.append((a, b, non_negative(r["distance"], edges_file), non_negative(r["travel_time"], edges_file)))
    return nodes, edges


def read_frt(stops_file, edges_file):
    """returns {stop_id: (x, y)} and [(from, to, distance, travel time, route)]"""
    stops = {}
    for r in read_rows(stops_file, ["stop_id", "pos_x", "pos_y"]):
        stops[int(r["stop_id"])] = (float(r["pos_x"]), float(r["pos_y"]))
    edges = []
    for r in read_rows(edges_file, ["from_stop", "to_stop", "distance", "travel_time", "route"]):
        a, b = int(r["from_stop"]), int(r["to_stop"])
        if a not in stops or b not in stops:
            sys.exit("%s: edge %s -> %s has a stop that is not in %s" % (edges_file, a, b, stops_file))
        edges.append((a, b, non_negative(r["distance"], edges_file), non_negative(r["travel_time"], edges_file),
                      int(r["route"])))
    return stops, edges


def distance(p, q, latlon):
    if not latlon:
        return math.hypot(p[0] - q[0], p[1] - q[1])
    (lon1, lat1), (lon2, lat2) = [(math.radians(x), math.radians(y)) for x, y in (p, q)]
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371000.0 * math.asin(math.sqrt(h))  # m


def nearest_walk_nodes(stops, nodes, latlon):
    """{stop_id: (walk node, distance)}; on a tie the smaller node number"""
    result = {}
    for s, p in stops.items():
        best = min(nodes, key=lambda n: (distance(p, nodes[n], latlon), n))
        result[s] = (best, distance(p, nodes[best], latlon))
    return result


def virtual_stops(nodes, file, share, seed):
    """the walk nodes with microtransit boarding: from a file, or each node with probability share / 100"""
    if file:
        chosen = {int(r["node_index"]) for r in read_rows(file, ["node_index"])}
        unknown = sorted(chosen - set(nodes))
        if unknown:
            sys.exit("%s: not road nodes: %s" % (file, unknown[:10]))
        return chosen
    rng = random.Random(seed)
    return {n for n in sorted(nodes) if rng.random() < share / 100}


def build(nodes, road_edges, stops, frt_edges, variant, headway_min, virtual, walk_speed, micro_time_factor,
          micro_wait_s, latlon):
    """returns the links (dicts in FIELDS order), the numbering and a summary"""
    n_walk = len(nodes)
    used = sorted({a for a, *_ in frt_edges} | {b for _, b, *_ in frt_edges})
    stop_node = {s: n_walk + i for i, s in enumerate(used)}  # stops without FRT links get no number
    offset = n_walk + len(used)  # first microtransit node
    stop_walk = nearest_walk_nodes({s: stops[s] for s in used}, nodes, latlon)
    links = []

    def add(a, b, dist, tt, link_type, route=NO_ROUTE):
        links.append({"from_node": a, "to_node": b, "distance": float(dist), "travel_time": float(tt),
                      "link_type": link_type, "route": route})

    for a, b, dist, tt in road_edges:
        add(a, b, dist, dist / walk_speed, WALK)
    if variant in ("micro", "non_micro"):
        frt_wait = headway_min * 60 / 2
        joined = set()
        for a, b, dist, tt, route in frt_edges:
            add(stop_node[a], stop_node[b], dist, tt, FRT, route)
            for s in (a, b):
                if s not in joined:
                    joined.add(s)
                    add(stop_walk[s][0], stop_node[s], 0, frt_wait, FRT_WAIT)  # boarding
                    add(stop_node[s], stop_walk[s][0], 0, 0, FRT_WAIT)  # alighting
    if variant in ("micro", "micro_only"):
        boarded = set()
        for a, b, dist, tt in road_edges:
            add(offset + a, offset + b, dist, tt * micro_time_factor, MICRO)
            for n in (a, b):
                if n in virtual and n not in boarded:
                    boarded.add(n)
                    add(n, offset + n, 0, micro_wait_s, MICRO_WAIT)  # boarding
                    add(offset + n, n, 0, 0, MICRO_WAIT)  # alighting
    summary = {
        "num_walk_nodes": n_walk,
        "microtransit_node_offset": offset,
        "FRT stops with links": len(used),
        "FRT stops without links (not numbered)": sorted(set(stops) - set(used)),
        "walk nodes with an FRT stop": len({w for w, _ in stop_walk.values()}),
        "largest stop -> walk node distance": max((d for _, d in stop_walk.values()), default=0),
        "virtual stops": len(virtual) if variant != "non_micro" else 0,
        "links per type": {t: sum(1 for l in links if l["link_type"] == t) for t in sorted({l["link_type"] for l in links})},
    }
    return links, stop_node, summary


def car_links(road_edges):
    """the car network: every road edge with its car travel time"""
    return [{"from_node": a, "to_node": b, "distance": float(dist), "travel_time": float(tt), "link_type": CAR,
             "route": NO_ROUTE} for a, b, dist, tt in road_edges]


def write_links(path, links):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)  # CRLF, as the frozen networks
        w.writeheader()
        w.writerows(links)
    print("wrote %s (%d links)" % (path, len(links)))


def main(argv=None):
    p = argparse.ArgumentParser(description="Build an MTSM super-network (see the module docstring).")
    p.add_argument("--road-nodes", required=True)
    p.add_argument("--road-edges", required=True)
    p.add_argument("--frt-stops", required=True)
    p.add_argument("--frt-edges", required=True)
    p.add_argument("--variant", choices=["micro", "non_micro", "micro_only"], required=True)
    p.add_argument("--headway", type=int, required=True, help="FRT headway (min); boarding waits half of it")
    p.add_argument("--virtual-stops", help="CSV with node_index: the walk nodes with microtransit boarding")
    p.add_argument("--virtual-stop-share", type=float, help="instead: share of the walk nodes (%%), drawn with --seed")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--walk-speed", type=float, default=1.251, help="m/s (frozen Lemon Grove networks: 1.251)")
    p.add_argument("--micro-time-factor", type=float, default=1.4, help="microtransit time = car time x this")
    p.add_argument("--micro-wait", type=float, default=180, help="microtransit waiting time at boarding (s)")
    p.add_argument("--latlon", action="store_true", help="pos_x / pos_y are longitude / latitude")
    p.add_argument("--out", required=True)
    p.add_argument("--auto-out", help="also write the car network (auto_edges.csv) to this file")
    args = p.parse_args(argv)
    if args.variant != "non_micro" and (args.virtual_stops is None) == (args.virtual_stop_share is None):
        p.error("--variant %s needs one of --virtual-stops or --virtual-stop-share" % args.variant)

    nodes, road_edges = read_road(args.road_nodes, args.road_edges)
    stops, frt_edges = read_frt(args.frt_stops, args.frt_edges)
    virtual = set()
    if args.variant != "non_micro":
        virtual = virtual_stops(nodes, args.virtual_stops, args.virtual_stop_share, args.seed)
    links, stop_node, summary = build(nodes, road_edges, stops, frt_edges, args.variant, args.headway, virtual,
                                      args.walk_speed, args.micro_time_factor, args.micro_wait, args.latlon)
    write_links(args.out, links)
    if args.auto_out:
        write_links(args.auto_out, car_links(road_edges))
    for k, v in summary.items():
        print("  %s: %s" % (k, v))


if __name__ == "__main__":
    main()
