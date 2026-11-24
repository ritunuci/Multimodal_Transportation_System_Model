import os
import sys
import csv
from collections import OrderedDict
import pandas as pd
import mtsm_paths as mtsm
from mtsm_model import config
from mtsm_model import mtsm_global_parameters as gp

# The employment accessibility calculation (wghted_acc_emp_5/10/15_min, the per-zone acc_super_network files, and
# their inputs: land use, MGRA population/income and adjacency, node -> MGRA mapping) was removed on 2026-11-24
# (docs/progress.md); the last version is at git tag last-with-accessibility.
# time_periods = ["AM", "MD", "PM", "EV"]
# microtransit_scenarios = ["micro", "non_micro"]
microtransit_setup_scenarios = ["micro", "non_micro","micro_only"]
#
headway_scenarios = [20, 30, 60]
virtual_stop_scenarios = [50, 75, 100]


# Fleetpy_output_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/studies/example_study/results/example_pool_irsonly_sc_1"


def get_fleetpy_eval_output_metrics(repositioning):
    if repositioning == True:
        Fleetpy_output_folder = os.path.join(mtsm.FLEETPY_RESULTS_DIR, "example_pool_repo_AM_sc_1")
    else:
        Fleetpy_output_folder = os.path.join(mtsm.FLEETPY_RESULTS_DIR, "example_pool_irsonly_sc_1")
    # folder = 'D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/studies/example_study/results/example_pool_repo_AM_sc_1'
    filename = 'standard_eval.csv' #-3/22/26 Siwei
    # full_path = os.path.join(folder, filename)
    Fleetpy_eval_file = os.path.join(Fleetpy_output_folder, filename) #3/22/26 Siweib
    df = pd.read_csv(Fleetpy_eval_file, index_col=0, header=0)
    util_rate=df.loc["% fleet utilization"]["MoD_0"]
    # util_rate_=util_rate["MoD_0"]
    veh_occ = df.loc["occupancy"]["MoD_0"]
    total_vkm = df.loc["total vkm"]["MoD_0"]
    # km -> miles with meters_per_mile (until 2026-11-23 a separate 1.609 km per mile; I-21)
    km_per_mile = config.MILE_METER / 1000
    total_vmt = total_vkm/km_per_mile
    empty_vkm = df.loc["% empty vkm"]["MoD_0"]
    avg_speed_kmh = df.loc["avg driving velocity [km/h]"]["MoD_0"]
    avg_speed_mph = avg_speed_kmh/km_per_mile
    print("util_rate(%)",util_rate,"veh_occ",veh_occ,"total_vmt (miles)",total_vmt,"empty_vkm(%)",empty_vkm,"avg_speed (vmp)",avg_speed_mph)
    return util_rate,veh_occ,total_vmt,empty_vkm,avg_speed_mph

def get_transit_line_dist(study_area):
    """The FRT route table networks/frt_routes.csv (docs/study_area_inputs.md, file 10; the format of
    TRA_input_data_prep's frt_routes.csv): one row per route variant, i.e. route x direction. Returns
    [(route, direction, length (mi), stops)] in the file's order; other columns are not read.

    Since 2026-11-24 (docs/study_area_plan.md, Phase 3 step 1; I-34 item 1). Until then the length of a route was the
    sum of its distinct link distances in frt_links.csv and the stops its distinct from-nodes, one row per route, and
    the costs doubled it for the two directions; the distinct-distance rule lost links of the same length (Lemon Grove
    routes 856 and 916: 3,508 m instead of 3,702 m and 1,647 m instead of 1,844 m)."""
    paths = mtsm.area_paths(study_area)
    route_file = paths.frt_routes_file
    if not os.path.isfile(route_file):
        sys.exit(f"ERROR: the FRT route table is missing: {route_file} (docs/study_area_inputs.md, file 10)")
    transit_line_dist_list = []
    problems = []
    with open(route_file, newline="") as f:
        reader = csv.DictReader(f)
        missing = {"route", "direction", "n_stops", "length_m"} - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"ERROR: {route_file}: missing columns {sorted(missing)}")
        seen = set()
        for line_number, data in enumerate(reader, start=2):
            route_id, direction = int(data["route"]), int(data["direction"])
            length_m, num_stops = float(data["length_m"]), int(data["n_stops"])
            if (route_id, direction) in seen:
                problems.append(f"line {line_number}: route {route_id} direction {direction} is repeated")
            if length_m <= 0 or num_stops < 2:
                problems.append(f"line {line_number}: length_m must be > 0 and n_stops >= 2")
            seen.add((route_id, direction))
            transit_line_dist_list.append((route_id, direction, length_m / config.MILE_METER, num_stops))
    with open(paths.frt_links_file, newline="") as f:
        link_routes = {int(data["route"]) for data in csv.DictReader(f)}
    table_routes = {route_id for (route_id, direction, dist, num_stops) in transit_line_dist_list}
    if link_routes != table_routes:
        problems.append(f"the routes differ from those of {paths.frt_links_file}: only in the table "
                        f"{sorted(table_routes - link_routes)}, only in the links {sorted(link_routes - table_routes)}")
    if problems:
        sys.exit(f"ERROR: {route_file}:\n  " + "\n  ".join(problems))

    print("transit_line_dist_list (route_id,direction,miles,num_stops)",transit_line_dist_list)

    return transit_line_dist_list

def get_transit_line_duration(study_area,transit_line_dist_list):
    """{(route, direction): duration of one run (h)}: length / speed + stops x dwell time + dead-end time.
    (Keyed by route only until 2026-11-24.)"""
    transit_line_duration = OrderedDict()
    dwell_time = config.PARAMETERS[gp.G_FRT_DWELL_TIME_MIN] / 60  # unit hour
    dead_end_time = config.PARAMETERS[gp.G_FRT_DEAD_END_TIME_MIN] / 60  # unit hour - (10min) on one end
    # every study area since 2026-11-24 (only "lemon_grove" before)
    avg_speed = config.PARAMETERS[gp.G_FRT_SPEED_MPH]
    for (route_id, direction, dist, num_stops) in transit_line_dist_list:
        transit_line_duration[(route_id, direction)] = dist / avg_speed + num_stops * dwell_time + dead_end_time  # dwell time (3min/stop), dead-end times (10min)

    return transit_line_duration

def get_transit_link_info(study_area):
    # networks/frt_links.csv (until 2026-11-24 transit/super_network_transit_edges.csv, only for "lemon_grove")
    new_transit_network_file = mtsm.area_paths(study_area).frt_links_file

    transit_link_list=[]
    with open(new_transit_network_file) as transit_network:
        csvreader = csv.DictReader(transit_network)
        routes=[]
        for data in csvreader:
            # route_id = int(data["route"])
            from_node = int(data["from_node"])
            to_node = int(data["to_node"])
            transit_link_list.append((from_node,to_node))
    transit_network.close()



    return transit_link_list

def vmt_and_link_dict_creation(time_periods,transit_link_list):
    transit_link_vmt = OrderedDict()
    transit_link_pax = OrderedDict()
    off_micro_transit_link_pax = OrderedDict()
    off_micro_transit_link_vmt = OrderedDict()
    for time_period in time_periods:
        transit_link_vmt[time_period] = OrderedDict()
        off_micro_transit_link_vmt[time_period] = OrderedDict()
        transit_link_pax[time_period] = OrderedDict()
        off_micro_transit_link_pax[time_period] = OrderedDict()
        for (from_node, to_node) in transit_link_list:
            transit_link_vmt[time_period][(from_node, to_node)] = 0
            off_micro_transit_link_vmt[time_period][(from_node, to_node)] = 0
            transit_link_pax[time_period][(from_node, to_node)] = 0
            off_micro_transit_link_pax[time_period][(from_node, to_node)] = 0

    return transit_link_vmt,transit_link_pax,off_micro_transit_link_pax,off_micro_transit_link_vmt

def write_fixed_transit_link_vmt(study_area,fleet_size,M_operating_hrs,headway,virstop,transit_link_vmt,transit_link_pax,test_scenario,microtransit):
    # until 2026-11-24 only for "lemon_grove" (LG_TRANSIT_DIR, LG_OUTPUT_DIR); networks/frt_links.csv was
    # transit/super_network_transit_edges.csv
    paths = mtsm.area_paths(study_area)
    new_transit_network_file = paths.frt_links_file
    # output_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/output_folder"
    # transit_link_vmt_output = os.path.join(output_folder, "debug_%s_%s_%s_%s_op_hr_%s_hw_%s_virstop_%s_transit_edges_rders.csv" % (str(debug_mode),str(study_area),str(microtransit),str(fleet_size),str(M_operating_hrs), str(headway), str(virstop)))
    output_folder = paths.output_dir
    transit_link_vmt_output = os.path.join(output_folder,"debug_False_%s_%s_%s_op_hr_%s_hw_%s_virstop_%s_transit_edges_rders_scen_%s.csv" % (str(study_area), str(microtransit),str(fleet_size), str(M_operating_hrs), str(headway),str(virstop), str(test_scenario)))


    transit_link_list = []
    with open(transit_link_vmt_output, 'w+', newline='') as csvfile:
        #from_node	to_node	distance (meters)	travel_time	link_type	route

        fieldnames = ["from_node", "to_node", "distance (meters)","travel_time","link_type","route",
                      "rdrs_AM","rdrs_MD","rdrs_PM","rdrs_EV","tt_rdrs"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        with open(new_transit_network_file) as transit_network:
            csvreader = csv.DictReader(transit_network)
            routes = []
            for data in csvreader:
                # route_id = int(data["route"])
                from_node = int(data["from_node"])
                to_node = int(data["to_node"])
                distance = float(data["distance (meters)"])
                travel_time = float(data["travel_time"])  # every study area since 2026-11-24 (only "lemon_grove" before)
                link_type = int(1)
                route = int(data["route"])
                vmt_AM = float(transit_link_vmt["AM"][(from_node, to_node)])
                vmt_MD = float(transit_link_vmt["MD"][(from_node, to_node)])
                vmt_PM = float(transit_link_vmt["PM"][(from_node, to_node)])
                vmt_EV = float(transit_link_vmt["EV"][(from_node, to_node)])

                rdrs_AM = float(transit_link_pax["AM"][(from_node, to_node)])
                rdrs_MD = float(transit_link_pax["MD"][(from_node, to_node)])
                rdrs_PM = float(transit_link_pax["PM"][(from_node, to_node)])
                rdrs_EV = float(transit_link_pax["EV"][(from_node, to_node)])
                tt_rdrs = rdrs_AM + rdrs_MD + rdrs_PM + rdrs_EV

                writer.writerow({"from_node": from_node, "to_node": to_node, "distance (meters)": distance,"travel_time": travel_time,"link_type": link_type,
                                 "route": route,"rdrs_AM": rdrs_AM,"rdrs_MD": rdrs_MD,"rdrs_PM": rdrs_PM,"rdrs_EV": rdrs_EV,"tt_rdrs":tt_rdrs})

        transit_network.close()
    csvfile.close()
    # return
