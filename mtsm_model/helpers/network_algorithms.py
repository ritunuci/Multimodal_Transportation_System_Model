import networkx as nx
import csv
import heapq
from mtsm_model import config
from mtsm_model import mtsm_global_parameters as gp

# link types of the super-networks: 0 walk, 1 FRT in-vehicle, 2 FRT waiting (boarding / alighting), 4 microtransit
# in-vehicle, 5 microtransit waiting, 7 car. Type 3 (FRT transfer link) was removed on 2026-11-11: no network had one;
# transfers are charged by the path search instead (enable_num_transfer_penalty, I-25).
KNOWN_LINK_TYPES = {0, 1, 2, 4, 5, 7}

class Link(object):


    def __init__(self, link_id=None, length=0,
                     from_node=0, to_node=0, flow=float(0.0), free_speed=0, free_flow_travel_time=0,
                     link_type=str(0),route=int(0)):
        self.link_id = link_id
        # self.link_id_text=link_id_text
        self.length = length # ft

        self.from_node = from_node
        self.to_node = to_node
        self.timestep = 0
        self.timesteps = 60
        self.timeinterval = 15.0  # seconds
        self.free_speed = free_speed  # ft/sec = 51.33*0.681818(converting fts to mph) = 34.9977 mph, 1.4667 (converting mph to fps)
        self.free_flow_time=free_flow_travel_time
        self._time = None
        self.density = 0.0  # veh/mile (ft to miles = ft*5280.0)
        # self.k_j = 160.002  # if we set this value to decimal, we can have a very low chance that fails to derivative.
        self.k_j = 160.002/5280.0  #0316 Siwei: k_j -> veh/ft
        self.v = 0.  # mph
        self.flow = flow  # vehicles, vph(bpr)
        self.k_t = 0.0
        self.use_exact = False
        self.truncate=False
        self.link_function = "m_Greenshield"  # "bpr", "m_Greenshield","triangularFD"
        self.SO = False
        self.random_init_vol = False

        self.u_max = self.free_speed  # mph
        # self.u_min = 10.0  # mph
        self.u_min = 10.0*1.4667  #Siwei: ft/s 10mph
        self.route = route
        self.link_type=link_type


class Agent(object):

    def __init__(self, rq_id=0, rq_O=0, rq_D=0, rq_time=0, bt_c_0=0, bt_c_ivt=0,bt_c_gas=0,bt_t_0=0, bt_t_wk=0, bt_m_wt=0,bt_f_wt=0,bt_m_ivt=0,
                 bt_f_ivt=0,bt_f_trfer=0,bt_t_fr=0,income=0,transit_15min_acc=0,transit_pass=0,parking_dur=0,
                 auto_available=True):

        # ['rq_time', 'start','end','request_id', "bt_c_0","bt_c_ivt","bt_c_gas","bt_t_0","bt_t_wk","bt_t_wt","bt_m_ivt","bt_f_ivt","bt_f_trfer","bt_t_fr"]
        #trip related attributes
        self.rq_id = rq_id
        self.rq_O = rq_O
        self.rq_D = rq_D
        self.rq_time = rq_time
        #car mode attributes
        self.bt_c_0 = bt_c_0
        self.bt_c_ivt = bt_c_ivt
        self.bt_c_gas = bt_c_gas
        #transit mode attributes
        self.bt_t_0 = bt_t_0
        self.bt_t_wk = bt_t_wk
        self.bt_m_wt = bt_m_wt
        self.bt_f_wt = bt_f_wt
        self.bt_m_ivt = bt_m_ivt
        self.bt_f_ivt = bt_f_ivt
        self.bt_f_trfer = bt_f_trfer
        self.bt_t_fr = bt_t_fr
        self.income = income
        self.transit_15min_acc = transit_15min_acc
        self.transit_pass = transit_pass
        self.parking_dur = parking_dur
        self.auto_available = auto_available  # False: no car, the traveler cannot choose the car (2026-11-24)


# Optional columns of the demand file (2026-11-19). If a column is missing, every traveler gets the default and one
# notice is printed; if it is there, every value must be a number. (The demand generator in pre_process/ writes no
# parking_dur_min column.)
OPTIONAL_DEMAND_COLUMNS = {
    # column: (default, what the default means)
    "parking_dur_min": (0.0, "parking duration 0 for every traveler (no parking cost)"),
    "transit_15min_acc": (None, "agent_transit_15min_acc is left empty in the individual results"),
    "transit_pass": (None, "not set (the model does not use it)"),
    # 2026-11-24 (docs/period_networks_and_car_availability_plan.md, step 2): True / False or 1 / 0
    "auto_available": (True, "every traveler has a car"),
}


def to_bool(value):
    """True / False or 1 / 0 (any case, also 1.0 / 0.0) -> bool; anything else -> ValueError"""
    text = str(value).strip().lower()  # str(): a short row gives None
    if text in ("true", "1", "1.0"):
        return True
    if text in ("false", "0", "0.0"):
        return False
    raise ValueError(value)


def demand_columns(request_file):
    """the column names of the demand file"""
    with open(request_file, newline="") as f:
        return next(csv.reader(f), [])


def demand_value(data, column, convert, request_file, line_number):
    """The value of an optional demand column in one row (data: a csv.DictReader row): the default if the file has no
    such column, else the converted value; stops with the row's line number if the value is empty or not valid (not a
    number; for auto_available not True / False / 1 / 0)."""
    if column not in data:
        return OPTIONAL_DEMAND_COLUMNS[column][0]
    value = data[column]
    try:
        return convert(value)
    except (TypeError, ValueError):
        raise ValueError("%s, line %d: %s = '%s' is not valid" % (request_file, line_number, column, value))


def read_request(request_file):
    with open(request_file) as f:
        csvreader = csv.DictReader(f)
        agent_list = []
        for column, (default, meaning) in OPTIONAL_DEMAND_COLUMNS.items():
            if column not in (csvreader.fieldnames or []):
                print("Note: the demand file has no column %s: %s (%s)" % (column, meaning, request_file))

        #rq_time	start	end	request_id	bt_0	bt_wk	bt_wt	bt_m_ivt	bt_f_ivt	bt_f_trfer	bt_fr

        # ['rq_time', 'start','end','request_id', "bt_c_0","bt_c_ivt","bt_c_gas","bt_t_0","bt_t_wk","bt_t_wt","bt_m_ivt","bt_f_ivt","bt_f_trfer","bt_t_fr"]

        for data in csvreader:
            #read trip related attributes
            rq_time = int(data["rq_time"])
            start = int(data["start"])
            end = int(data["end"])
            request_id = int(float(data["request_id"]))
            #read car mode attributes
            bt_c_0 = float(data["bt_c_0"])
            bt_c_ivt = float(data["bt_c_ivt"])
            bt_c_gas = float(data["bt_c_gas"])
            #read transit mode attributes
            bt_t_0 = float(data["bt_t_0"])
            bt_t_wk = float(data["bt_t_wk"])
            bt_m_wt = float(data["bt_m_wt"])
            bt_f_wt = float(data["bt_f_wt"])

            bt_m_ivt = float(data["bt_m_ivt"])
            bt_f_ivt = float(data["bt_f_ivt"])
            bt_f_trfer = float(data["bt_f_trfer"])
            bt_t_fr = float(data["bt_t_fr"])

            income = int(float(data["income"]))
            # optional columns (OPTIONAL_DEMAND_COLUMNS); csvreader.line_num: the file line of this row
            transit_15min_acc = demand_value(data, "transit_15min_acc", float, request_file, csvreader.line_num)
            transit_pass = demand_value(data, "transit_pass", lambda v: int(float(v)), request_file, csvreader.line_num)
            parking_dur = demand_value(data, "parking_dur_min", float, request_file, csvreader.line_num)
            auto_available = demand_value(data, "auto_available", to_bool, request_file, csvreader.line_num)

            agent_ = Agent(rq_id=request_id, rq_O=start, rq_D=end, rq_time=rq_time, bt_c_0=bt_c_0, bt_c_ivt=bt_c_ivt,
                           bt_c_gas=bt_c_gas,bt_t_0=bt_t_0, bt_t_wk=bt_t_wk, bt_m_wt=bt_m_wt,bt_f_wt=bt_f_wt,bt_m_ivt=bt_m_ivt,
                          bt_f_ivt=bt_f_ivt,bt_f_trfer=bt_f_trfer, bt_t_fr=bt_t_fr,income=income,
                           transit_15min_acc=transit_15min_acc,transit_pass=transit_pass,parking_dur=parking_dur,
                           auto_available=auto_available)
            agent_list.append(agent_)

    return agent_list

def read_super_network(Network_file):
    with open(Network_file) as f:
        csvreader = csv.DictReader(f)
        links = []

        for data in csvreader:
            origin_node = int(data["from_node"])
            to_node = int(data["to_node"])
            length = float(data["distance"]) #meter
            free_flow_travel_time_ = float(data["travel_time"])  # in second
            link_type_ = int(data["link_type"])  # link_type
            if link_type_ not in KNOWN_LINK_TYPES:  # the path search has a cost only for these
                raise ValueError("unknown link type %s in %s (link %s -> %s); known: %s"
                                 % (link_type_, Network_file, origin_node, to_node, sorted(KNOWN_LINK_TYPES)))
            route_ = int(data["route"])
            l = Link(link_id=len(links),length=length,
                     from_node=origin_node, to_node=to_node, flow=float(0.0),
                     free_flow_travel_time=free_flow_travel_time_, link_type=link_type_,route=route_)
            links.append(l)

    graph = nx.DiGraph()
    print("number of links:",len(links))
    for l in links:
        graph.add_edge(l.from_node, l.to_node, object=l, time=l.free_flow_time,link_type=l.link_type,route=l.route)

    return graph


def getTrajectory_O_to_D(origin, destination, path, t_visited, currenttime=0, timeinterval=5.0):

    rtrajectory = []
    prenode = destination
    rtrajectory.append(prenode)

    # path[node] = (previous node, cost / time / distance at node, link type, route)
    for k in range(0, len(path)):


        if prenode != origin:
            try:
                nextnode = path[prenode][0]
            except Exception as e:
                print("prenode", prenode, "path", path, "origin", origin, "destination", destination, "t_visited",
                      t_visited)
                raise e
            if nextnode == origin:
                rtrajectory.append(path[prenode])
                break
            rtrajectory.append(path[prenode])
            prenode = nextnode

    destination_ = rtrajectory[0]
    rtrajectory_ = []
    pre_node = destination_
    for node, time, link_type,route in rtrajectory[1:]:
        rtrajectory_.append((pre_node, time, link_type,route))
        pre_node = node

    rtrajectory_.append(origin)
    rtrajectory_.reverse()
    rtrajectory_.append(destination)
    return rtrajectory_


class Heap_Node:
    """Heap entry of generalized_cost_dijsktra_OD_heap: a node and its generalized cost so far. Compared by the cost
    only, so on equal costs the heap's internal order decides, as before."""
    __slots__ = ("node_id", "temp")

    def __init__(self, v, temp):
        self.node_id = v
        self.temp = temp

    # define a comparator method to compare distance of two nodes
    def __lt__(self, other):
        return self.temp < other.temp


def out_links(graph):
    """The outgoing links of each node: [(to_node, travel time (s), link type, length (m), route)], in the graph's
    order. Built at the first call for a network and kept on the graph (a network is not changed after reading)."""
    links = graph.graph.get("out_links")
    if links is None:
        links = {}
        for node, nbrs in graph.adjacency():
            links[node] = [(to_node, d["object"].free_flow_time, d["object"].link_type, d["object"].length, d["object"].route)
                           for to_node, d in nbrs.items()]
        graph.graph["out_links"] = links
    return links


#############################################################
#Multi-modal generalized cost shortest path algorithm
############################################################
# Transit fare rules (since 2026-11-25; docs/open_issues.md I-22, I-24 and I-44, docs/pathfinding_code_update.md):
# - Every FRT boarding (link type 2, walk node -> stop) pays the FRT fare, also a boarding right after an alighting at
#   the same walk node (free until 2026-11-25). A route change at a shared stop node has no boarding link and pays no
#   fare (I-44).
# - The first FRT boarding after a microtransit ride pays the fare x micro2fixed_factor, but at least the FRT fare
#   minus the microtransit fare paid since the last FRT boarding (the floor):
#       F - min(M, (1 - micro2fixed_factor) x F)
#   so microtransit + FRT never cost less in fare than the FRT alone. Until 2026-11-25 every FRT boarding after any
#   microtransit link of the trip got the factor, without a floor.
# - The distance fare of the first microtransit ride after an FRT ride is x fixed2micro_factor (until 2026-11-25 every
#   microtransit link after any FRT link). The start fare is always x fixed2micro_factor (I-19).
# A link's cost then depends on the path before it, so the transit search keeps the least-cost path per label, not per
# node (I-22; until 2026-11-25 a Dijkstra search over nodes, which missed cheaper paths). The car search has no such
# link costs and is a Dijkstra search over nodes, as before.


class _Label:
    """Heap entry of transit_label_search: a label instance and its generalized cost so far. Compared by the cost
    only, as Heap_Node."""
    __slots__ = ("node_id", "temp")

    def __init__(self, v, temp):
        self.node_id = v
        self.temp = temp

    def __lt__(self, other):
        return self.temp < other.temp


def transit_label_search(graph, agent, transit_fare_set, microtransit_start_fare, microtransit_dist_based_rate,
                         peak_factor, Fixed2MicroFactor, Micro2FixedFactor, total_rejection_penalty, iteration):
    """Least generalized cost transit path (mode "T") under the fare rules above; exact.

    A label is a node with what a later link cost reads about the path so far:
      - ready_f: a microtransit ride since the last FRT boarding (the next FRT boarding gets the discount); only if
        micro2fixed_factor != 1;
      - ready_m: an FRT ride since the last microtransit alighting (the next microtransit ride gets fixed2micro_factor
        on its distance fare); only if fixed2micro_factor != 1;
      - with the transfer penalty on (I-25): whether transit was used, and the route of the FRT link into the node.
    Two paths with the same label are compared on two values, the cost and the cost minus bt_t_fr x min(M, D) (M: the
    microtransit fare since the last FRT boarding, D: the largest FRT discount); a path is dropped only if another one
    is at most as large on both (with the floor a dearer path with a larger M can still win). The first destination
    label that leaves the heap is the least-cost path.

    Returns the nine values of generalized_cost_dijsktra_OD_heap: the six values at the destination as one-entry dicts
    {destination: value} and the cost, time and distance trajectories [origin, (node, value at the node, link type
    into the node, route), ..., destination] (the format of getTrajectory_O_to_D)."""
    initial, dest = agent.rq_O, agent.rq_D
    bt_t_0, bt_t_wk = agent.bt_t_0, agent.bt_t_wk
    bt_m_wt, bt_f_wt = agent.bt_m_wt, agent.bt_f_wt
    bt_m_ivt, bt_f_ivt = agent.bt_m_ivt, agent.bt_f_ivt
    bt_f_trfer, bt_t_fr = agent.bt_f_trfer, agent.bt_t_fr
    bt_c_ivt, bt_c_gas = agent.bt_c_ivt, agent.bt_c_gas

    links = out_links(graph)
    last_walk_node = config.LAST_WALK_NODE
    first_frt_stop, last_frt_stop = config.FIRST_FRT_STOP, config.LAST_FRT_STOP
    first_micro_node, last_micro_node = config.MICROTRANSIT_NODE_OFFSET, config.LAST_MICROTRANSIT_NODE
    car_gas_cost_per_meter = config.PARAMETERS[gp.G_CAR_GAS_COST_PER_METER]  # $/m
    # transfer penalty: bt_f_trfer per transit boarding after the first and per route change at a shared stop (I-25)
    penalty_on = config.PARAMETERS[gp.G_ENABLE_NUM_TRANSFER_PENALTY]

    max_discount = (1 - Micro2FixedFactor) * transit_fare_set  # D
    key_ready_f = Micro2FixedFactor != 1
    key_ready_m = Fixed2MicroFactor != 1

    def key_of(node, lt_in, route_in, transit_used, ready_f, ready_m):
        return (node, ready_f if key_ready_f else None, ready_m if key_ready_m else None,
                transit_used if penalty_on else None, route_in if (penalty_on and lt_in == 1) else None)

    # label instances (parallel lists); index 0 is the origin
    L_node, L_pred, L_lt, L_route = [initial], [-1], [0], [None]
    L_cost, L_time, L_dist, L_fare, L_ffare, L_mfare = [bt_t_0], [0], [0], [0], [0], [0]
    L_state = [(False, False, False, 0.0)]  # transit used, ready_f, ready_m, microtransit fare since last FRT boarding
    L_adj = [bt_t_0]
    L_key = [key_of(initial, 0, None, False, False, False)]
    front = {L_key[0]: [(bt_t_0, bt_t_0)]}  # (cost, cost - bt_t_fr x min(M, D)) of the labels pushed, per key
    settled_adj = {}  # per key: the least second value of the labels taken from the heap
    heap = [_Label(0, bt_t_0)]
    dest_label = None

    while heap:
        i = heapq.heappop(heap).node_id
        k, a_i = L_key[i], L_adj[i]
        s = settled_adj.get(k)
        if s is not None and s <= a_i:  # a label taken earlier is at most as large on both values
            continue
        settled_adj[k] = a_i
        node = L_node[i]
        if node == dest:
            dest_label = i
            break
        out = links.get(node)
        if not out:
            continue
        cost_i, time_i, dist_i = L_cost[i], L_time[i], L_dist[i]
        fare_i, ffare_i, mfare_i = L_fare[i], L_ffare[i], L_mfare[i]
        transit_used, ready_f, ready_m, m_since = L_state[i]
        lt_pre, route_pre = L_lt[i], L_route[i]
        for edge, link_travel_time, link_type_, link_length, route in out:  # link length in meters
            transit_fare = 0
            micro_fare = 0
            n_used, n_ready_f, n_ready_m, n_m = transit_used, ready_f, ready_m, m_since
            if link_type_ == 0:  # walking link
                g = bt_t_wk * link_travel_time / 60  # time parameter transfer from sec to min
            elif link_type_ == 1:  # FRT in-vehicle link
                g = bt_f_ivt * link_travel_time / 60
                if penalty_on and lt_pre == 1 and route != route_pre:  # route change at a shared stop
                    g += bt_f_trfer
                n_used, n_ready_m = True, True
            elif link_type_ == 2:  # FRT waiting link (boarding or alighting)
                if node <= last_walk_node and first_frt_stop <= edge <= last_frt_stop:  # boarding: the FRT fare
                    if ready_f:  # the first boarding after a microtransit ride: the discount, with the floor
                        transit_fare = transit_fare_set - min(m_since, max_discount)
                    else:
                        transit_fare = transit_fare_set
                    n_ready_f, n_m = False, 0.0
                g = bt_f_wt * link_travel_time / 60 + bt_t_fr * transit_fare
                if penalty_on and node <= last_walk_node and transit_used:  # FRT boarding after a transit leg
                    g += bt_f_trfer
            elif link_type_ == 4:  # microtransit in-vehicle link
                micro_fare = microtransit_dist_based_rate * link_length * peak_factor  # $ per meter
                if ready_m:  # the first microtransit ride after an FRT ride
                    micro_fare = micro_fare * Fixed2MicroFactor
                g = bt_m_ivt * link_travel_time / 60 + bt_t_fr * micro_fare
                n_used, n_ready_f, n_m = True, True, m_since + micro_fare
            elif link_type_ == 5:  # microtransit waiting link (boarding or alighting)
                if node <= last_walk_node and first_micro_node <= edge <= last_micro_node:  # boarding: start fare
                    micro_fare = microtransit_start_fare * Fixed2MicroFactor * peak_factor  # Ritun (I-19)
                    n_m = m_since + micro_fare
                else:  # alighting: the ride after an FRT ride ends
                    n_ready_m = False
                if iteration > 0:
                    if link_travel_time == 180:
                        print(f"WAITING LINK = {link_travel_time}")
                # the rejection penalty on both microtransit waiting links, as before 2026-11-25
                g = bt_m_wt * link_travel_time / 60 + bt_t_fr * micro_fare + bt_t_fr * total_rejection_penalty
                if penalty_on and node <= last_walk_node and transit_used:  # microtransit boarding after a transit leg
                    g += bt_f_trfer
            elif link_type_ == 7:  # car link ("micro_only" outside the operating periods searches the car network)
                gas_cost = car_gas_cost_per_meter * link_length
                g = bt_c_ivt * link_travel_time / 60 + bt_c_gas * gas_cost  # the gas is not a transit fare
            else:
                raise ValueError("link type %s on link %s -> %s is not handled by the transit search"
                                 % (link_type_, node, edge))

            if g < 0:  # the search needs link costs >= 0 (a label taken from the heap is final)
                raise ValueError("negative generalized link cost %s on link %s -> %s (link type %s), traveler %s"
                                 % (g, node, edge, link_type_, agent.rq_id))
            c = cost_i + g
            a = c - bt_t_fr * min(n_m, max_discount) if key_ready_f else c
            nk = key_of(edge, link_type_, route, n_used, n_ready_f, n_ready_m)
            pushed = front.get(nk)
            if pushed is None:
                front[nk] = [(c, a)]
            else:
                if any(c0 <= c and a0 <= a for c0, a0 in pushed):
                    continue
                pushed[:] = [(c0, a0) for c0, a0 in pushed if not (c <= c0 and a <= a0)]
                pushed.append((c, a))
            L_node.append(edge)
            L_pred.append(i)
            L_lt.append(link_type_)
            L_route.append(route)
            L_cost.append(c)
            L_time.append(time_i + link_travel_time)
            L_dist.append(dist_i + link_length)
            L_fare.append(fare_i + transit_fare + micro_fare)
            L_ffare.append(ffare_i + transit_fare)
            L_mfare.append(mfare_i + micro_fare)
            L_state.append((n_used, n_ready_f, n_ready_m, n_m))
            L_adj.append(a)
            L_key.append(nk)
            heapq.heappush(heap, _Label(len(L_node) - 1, c))

    if dest_label is None:
        raise KeyError("traveler %s: destination %s cannot be reached from %s" % (agent.rq_id, dest, initial))

    def trajectory(values):
        rows = []
        j = dest_label
        while L_pred[j] != -1:
            rows.append((L_node[j], values[j], L_lt[j], L_route[j]))
            j = L_pred[j]
        rows.append(initial)
        rows.reverse()
        rows.append(dest)
        return rows

    d = dest_label
    return ({dest: L_cost[d]}, {dest: L_time[d]}, {dest: L_dist[d]}, {dest: L_fare[d]}, {dest: L_ffare[d]},
            {dest: L_mfare[d]}, trajectory(L_cost), trajectory(L_time), trajectory(L_dist))


def generalized_cost_dijsktra_OD_heap(study_area,graph, agent,transit_fare_set,microtransit_start_fare,microtransit_dist_based_rate, PkFareFactor,OffPkFareFactor,Fixed2MicroFactor,Micro2FixedFactor,mode,verbose=False, total_rejection_penalty=0, iteration=0):  # mode="T" or mode="C"
    """Least generalized cost path. mode "T": transit (transit_label_search; since 2026-11-25 the values at the
    destination and the finished trajectories). mode "C": car, a Dijkstra search over nodes (car links only; the values
    of every visited node and the predecessor dicts, for getTrajectory_O_to_D)."""

    ########################################
    # Peak and off-peak factor of the microtransit fares. The model has one fare structure, the former fare
    # scenario 10 (docs/progress.md, "Only fare scenario 10").
    #########################################
    # the study area's periods (config.period_of; until 2026-11-24 AM / MD / PM / EV and the peak periods ["AM","PM"]
    # were written here)
    time_period = config.period_of(agent.rq_time)
    if time_period in config.PEAK_PERIODS:
        peak_factor = PkFareFactor
    else:
        peak_factor = OffPkFareFactor

    if mode == "T":
        return transit_label_search(graph, agent, transit_fare_set, microtransit_start_fare,
                                    microtransit_dist_based_rate, peak_factor, Fixed2MicroFactor, Micro2FixedFactor,
                                    total_rejection_penalty, iteration)
    if mode != "C":
        raise ValueError("mode must be T or C, not %r" % mode)

    # agent attributes
    initial = agent.rq_O
    dest = agent.rq_D
    # car mode attributes
    bt_c_0 = agent.bt_c_0
    bt_c_ivt = agent.bt_c_ivt  #
    bt_c_gas = agent.bt_c_gas  #
    bt_t_0 = agent.bt_t_0  # (the first heap entry carries bt_t_0, as before; it is alone in the heap)

    parking_dur = agent.parking_dur

    # define a priority queue as the heap
    heap_q = []
    visited_temp = {initial: bt_c_0}  # dictionary: {node: the weights from source to a visited node}
    heapq.heappush(heap_q, Heap_Node(initial, bt_t_0))
    time_visited_temp = {initial: 0}  # document the travel time
    dist_visited_temp = {initial: 0}  # document the travel distance
    fare_visited_temp = {initial: 0}  # document the travel fare (the gas cost)
    F_fare_visited_temp = {initial: 0}  # no FRT fare by car
    M_fare_visited_temp = {initial: 0}  # no microtransit fare by car

    path = {}
    time_path = {}
    dist_path = {}
    links = out_links(graph)
    car_gas_cost_per_meter = config.PARAMETERS[gp.G_CAR_GAS_COST_PER_METER]  # $/m
    settled = set()  # nodes taken from the heap: their least cost and path are final (link costs >= 0)

    while heap_q:  # while there exist an element in the heap
        smallest_node = heapq.heappop(heap_q)  # get the smallest value item from the heap
        min_node = smallest_node.node_id
        if min_node in settled:  # an outdated heap entry of a settled node
            continue
        settled.add(min_node)
        permanent = visited_temp[min_node] #generalized cost at generalized cost minimum node
        time_permanent = time_visited_temp[min_node] # cumulative travel time at generalized cost minimum node
        dist_permanent = dist_visited_temp[min_node] # cumulative distance at generalized cost minimum node
        fare_permanent = fare_visited_temp[min_node]  # cumulative fare at generalized cost minimum node

        if min_node == dest:  # OD shortest path
            break

        if min_node in links:
            for edge, link_travel_time, link_type_, link_length, route in links[min_node]:  # link length in meters
                if link_type_ != 7:
                    raise ValueError("link type %s on link %s -> %s: the car search handles car links (7) only"
                                     % (link_type_, min_node, edge))
                gas_cost = car_gas_cost_per_meter * link_length  # gasoline cost: 0.00019 dollar per meter, 0.305 dollar per mile # Ritun: set it to 0.4 ($/mile)
                generalized_link_travel_time = bt_c_ivt * link_travel_time / 60 + bt_c_gas * gas_cost       # Ritun

                if generalized_link_travel_time < 0:  # the search needs link costs >= 0 (settled nodes are final)
                    raise ValueError("negative generalized link cost %s on link %s -> %s (link type %s), traveler %s"
                                     % (generalized_link_travel_time, min_node, edge, link_type_, agent.rq_id))
                temp = permanent + generalized_link_travel_time
                time_temp = time_permanent + link_travel_time
                dist_temp = dist_permanent + link_length
                fare_temp = fare_permanent + gas_cost

                if edge not in visited_temp or temp < visited_temp[edge]:
                    visited_temp[edge] = temp
                    path[edge] = (min_node, temp, link_type_,route)
                    heapq.heappush(heap_q,Heap_Node(edge, temp))  # 11/02: Heap: push the new calculated nodes into heap

                    time_visited_temp[edge] = time_temp
                    dist_visited_temp[edge] = dist_temp
                    fare_visited_temp[edge] = fare_temp
                    F_fare_visited_temp[edge] = 0
                    M_fare_visited_temp[edge] = 0

                    time_path[edge] = (min_node, time_temp, link_type_,route)
                    dist_path[edge] = (min_node, dist_temp, link_type_,route)

    return parking_dur, bt_c_gas, visited_temp, time_visited_temp,dist_visited_temp,fare_visited_temp,F_fare_visited_temp,M_fare_visited_temp, path, time_path, dist_path
