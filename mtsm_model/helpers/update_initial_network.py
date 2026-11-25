# Used by every run: sets the FRT headway in the study area's super-networks. Moved unchanged from
# pre_process/process_network.py (2026-11-08), which holds the one-time network preprocessing.
# Until 2026-11-24 it also copied the files into initial_network_0719/ for the accessibility calculation (removed).
# Since 2026-11-24 (docs/study_area_plan.md, Phase 1 step 2) it reads the templates from networks/ and writes into
# initial_network/, which holds only what the run writes; one network with microtransit per virtual-stop share
# (until then the Lemon Grove file names with virstop 75, and the microtransit network was written twice, identically).
import os
import csv

import mtsm_paths as mtsm
from mtsm_model import config


def initial_micro_files(study_area, headway, virstop):
    """{period: the scenario network with microtransit at `headway` and `virstop`}, in initial_network/: one file
    initial_super_network_micro_hw_<h>_virstop_<v>.csv for every period when file 3 is one network for the whole day,
    else one file per period, initial_super_network_micro_hw_<h>_virstop_<v>_<P>.csv (since 2026-11-24;
    docs/period_networks_and_car_availability_plan.md, step 4)"""
    paths = mtsm.area_paths(study_area)
    templates = paths.micro_network_files(virstop, config.TIME_PERIODS)
    base = os.path.join(paths.initial_network_dir, f"initial_super_network_micro_hw_{headway}_virstop_{virstop}")
    whole_day = paths.super_network_micro_file(virstop)
    return {p: (base + ".csv" if src == whole_day else f"{base}_{p}.csv") for p, src in templates.items()}


def initial_frt_file(study_area, headway):
    """the scenario's FRT-only network at `headway`, in initial_network/: initial_super_network_non_micro_hw_<h>.csv.
    Read since 2026-11-24 (I-38) for the scenario's travelers outside the microtransit operating periods."""
    return os.path.join(mtsm.area_paths(study_area).initial_network_dir,
                        f"initial_super_network_non_micro_hw_{headway}.csv")


def update_initial_net_with_bayesian_headway(headway, study_area, virstops):
    """Write the scenario networks of `headway`: every FRT boarding link (type 2, travel time not 0) gets
    headway x 60 / 2 s. The micro network for each share in `virstops`, the FRT-only network once."""
    paths = mtsm.area_paths(study_area)
    initial_net_folder = paths.initial_network_dir

    for virstop in virstops:
        # file 3 for the whole day or per time period (since 2026-11-24): one scenario network per distinct file
        templates = paths.micro_network_files(virstop, config.TIME_PERIODS)  # was base_super_network_lemon_grove_micro_hw_10_virstop_75.csv
        outputs = initial_micro_files(study_area, headway, virstop)
        for base_initial_net_file_micro, updated_initial_net_file_micro in dict.fromkeys(
                zip(templates.values(), outputs.values())):
            with open(updated_initial_net_file_micro, 'w+', newline='') as updated_file_1:
                fieldnames_1 = ["from_node", "to_node", "distance", "travel_time", "link_type", "route"]
                writer_1 = csv.DictWriter(updated_file_1, fieldnames=fieldnames_1)
                writer_1.writeheader()

                with open(base_initial_net_file_micro) as base_file_1:
                    csvreader = csv.DictReader(base_file_1)
                    for data in csvreader:
                        from_node_1 = int(data["from_node"])
                        to_node_1 = int(data["to_node"])
                        distance_1 = float(data["distance"])
                        travel_time_1 = float(data["travel_time"])
                        link_type_1 = int(data["link_type"])
                        route_1 = int(data["route"])

                        if (link_type_1 == 2) and (travel_time_1 != 0):
                            travel_time_1 = (headway*60)/2

                        writer_1.writerow({'from_node': from_node_1, 'to_node': to_node_1, 'distance': distance_1,
                                         'travel_time': travel_time_1, "link_type": link_type_1,
                                         "route": route_1})

    base_initial_net_file_non_micro = paths.super_network_frt_file  # was base_super_network_lemon_grove_non_micro_hw_10.csv
    updated_initial_net_file_non_micro = initial_frt_file(study_area, headway)

    with open(updated_initial_net_file_non_micro, 'w+', newline='') as updated_file_2:
        fieldnames_2 = ["from_node", "to_node", "distance", "travel_time", "link_type", "route"]
        writer_2 = csv.DictWriter(updated_file_2, fieldnames=fieldnames_2)
        writer_2.writeheader()

        with open(base_initial_net_file_non_micro) as base_file_2:
            csvreader = csv.DictReader(base_file_2)
            for data in csvreader:
                from_node_2 = int(data["from_node"])
                to_node_2 = int(data["to_node"])
                distance_2 = float(data["distance"])
                travel_time_2 = float(data["travel_time"])
                link_type_2 = int(data["link_type"])
                route_2 = int(data["route"])

                if (link_type_2 == 2) and (travel_time_2 != 0):
                    travel_time_2 = (headway*60)/2

                writer_2.writerow({'from_node': from_node_2, 'to_node': to_node_2, 'distance': distance_2,
                                 'travel_time': travel_time_2, "link_type": link_type_2,
                                 "route": route_2})

