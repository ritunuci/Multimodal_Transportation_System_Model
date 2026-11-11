"""Build an MTSM super-network from a road network (walk and microtransit) and an FRT network.

A representative script, written 2026-11-11 from the frozen Lemon Grove super-networks; no model code uses it yet
(docs/progress.md, "Super-network script"). It replaces the network construction of process_network.py, which reads
its inputs from outside folders.

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
Each stop is joined to its nearest walk node (by the coordinates); several stops can share a walk node. Only the
"micro" variant has the microtransit layer; "non_micro" has types 0, 1 and 2. The links are written in the order of
the frozen networks: walk links in road-edge order; each FRT link, followed by the waiting links of a stop that
appears for the first time; each microtransit link, followed by the waiting links of a virtual stop that appears
for the first time.

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
        --virtual-stop-share 75 --seed 0 --out super_network.csv
The run prints num_walk_nodes and microtransit_node_offset for mtsm_constant_configurations.csv.
"""
import argparse
import csv
import math
import random
import sys

WALK, FRT, FRT_WAIT, MICRO, MICRO_WAIT = 0, 1, 2, 4, 5
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
    frt_wait = headway_min * 60 / 2
    joined = set()
    for a, b, dist, tt, route in frt_edges:
        add(stop_node[a], stop_node[b], dist, tt, FRT, route)
        for s in (a, b):
            if s not in joined:
                joined.add(s)
                add(stop_walk[s][0], stop_node[s], 0, frt_wait, FRT_WAIT)  # boarding
                add(stop_node[s], stop_walk[s][0], 0, 0, FRT_WAIT)  # alighting
    if variant == "micro":
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
        "virtual stops": len(virtual) if variant == "micro" else 0,
        "links per type": {t: sum(1 for l in links if l["link_type"] == t) for t in sorted({l["link_type"] for l in links})},
    }
    return links, stop_node, summary


def main(argv=None):
    p = argparse.ArgumentParser(description="Build an MTSM super-network (see the module docstring).")
    p.add_argument("--road-nodes", required=True)
    p.add_argument("--road-edges", required=True)
    p.add_argument("--frt-stops", required=True)
    p.add_argument("--frt-edges", required=True)
    p.add_argument("--variant", choices=["micro", "non_micro"], required=True)
    p.add_argument("--headway", type=int, required=True, help="FRT headway (min); boarding waits half of it")
    p.add_argument("--virtual-stops", help="CSV with node_index: the walk nodes with microtransit boarding")
    p.add_argument("--virtual-stop-share", type=float, help="instead: share of the walk nodes (%%), drawn with --seed")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--walk-speed", type=float, default=1.251, help="m/s (frozen Lemon Grove networks: 1.251)")
    p.add_argument("--micro-time-factor", type=float, default=1.4, help="microtransit time = car time x this")
    p.add_argument("--micro-wait", type=float, default=180, help="microtransit waiting time at boarding (s)")
    p.add_argument("--latlon", action="store_true", help="pos_x / pos_y are longitude / latitude")
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    if args.variant == "micro" and (args.virtual_stops is None) == (args.virtual_stop_share is None):
        p.error("--variant micro needs one of --virtual-stops or --virtual-stop-share")

    nodes, road_edges = read_road(args.road_nodes, args.road_edges)
    stops, frt_edges = read_frt(args.frt_stops, args.frt_edges)
    virtual = set()
    if args.variant == "micro":
        virtual = virtual_stops(nodes, args.virtual_stops, args.virtual_stop_share, args.seed)
    links, stop_node, summary = build(nodes, road_edges, stops, frt_edges, args.variant, args.headway, virtual,
                                      args.walk_speed, args.micro_time_factor, args.micro_wait, args.latlon)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)  # CRLF, as the frozen networks
        w.writeheader()
        w.writerows(links)
    print("wrote %s (%d links)" % (args.out, len(links)))
    for k, v in summary.items():
        print("  %s: %s" % (k, v))


if __name__ == "__main__":
    main()
