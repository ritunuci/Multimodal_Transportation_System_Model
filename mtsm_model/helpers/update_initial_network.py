# Used by every run: sets the FRT headway in the Lemon Grove initial super-networks. Moved unchanged from
# pre_process/process_network.py (2026-11-08), which holds the one-time network preprocessing.
import os
import csv
import shutil

import mtsm_paths as mtsm


def update_initial_net_with_bayesian_headway(headway, study_area):

    if study_area=="lemon_grove":
        initial_net_folder = mtsm.LG_INITIAL_NETWORK_DIR
        base_initial_net_file_micro = os.path.join(initial_net_folder, "base_super_network_lemon_grove_micro_hw_10_virstop_75.csv")
        updated_initial_net_file_micro = os.path.join(initial_net_folder, f"initial_super_network_micro_hw_{headway}_virstop_75.csv")

        base_initial_net_file_non_micro = os.path.join(initial_net_folder,
                                                   "base_super_network_lemon_grove_non_micro_hw_10.csv")
        updated_initial_net_file_non_micro = os.path.join(initial_net_folder,
                                                f"initial_super_network_non_micro_hw_{headway}.csv")

        copy_folder = mtsm.LG_INITIAL_NETWORK_0719_DIR
    else:
        mtsm.not_self_contained("study_area=%s" % study_area)

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

    shutil.copy(updated_initial_net_file_micro, copy_folder)

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
                    travel_time_1 = (headway * 60) / 2

                writer_1.writerow({'from_node': from_node_1, 'to_node': to_node_1, 'distance': distance_1,
                                   'travel_time': travel_time_1, "link_type": link_type_1,
                                   "route": route_1})

    shutil.copy(updated_initial_net_file_micro, copy_folder)

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

    shutil.copy(updated_initial_net_file_non_micro, copy_folder)
