
from pyproj import Transformer
import os
import csv
from math import radians, cos, sin, asin, sqrt
from collections import OrderedDict
import math
import random

mile_meter=1609.34



if __name__ == '__main__':

    aaa=0
    study_area="lemon_grove"
    if study_area=="downtown_sd":
        set_lat = 32.715736
        set_lon = -117.161087
        micro_nodes_start=872
    else:
        set_lat = 32.727798
        set_lon = -117.035611
        micro_nodes_start=1171

    if study_area == "downtown_sd":
        node_file_folder="D:/Ritun/Siwei_Micro_Transit/Data/Downtown_SD_New_Transit_network/Road_network"
    else:
        node_file_folder="D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove"
    node_file=os.path.join(node_file_folder,"new_nodes_for_fleetpy_input.csv")
    zonal_nodes=OrderedDict()
    tt_num_nodes=0
    for i in range(1,5):
        zonal_nodes[i]=[]
    with open(node_file) as microtransit_nodes_f:
        # from_node	to_node	distance	travel_time	link_type	route_id	route_type
        csvreader = csv.DictReader(microtransit_nodes_f)

        for data in csvreader:
            #node_index	is_stop_only	node_lat	node_lon

            transit_route = OrderedDict()

            node_lat = float(data["node_lat"])
            node_lon = float(data["node_lon"])
            node_id = int(data["node_index"])+micro_nodes_start

            if node_lat>=set_lat:
                if node_lon<= set_lon: #upper left part (northwest)
                    zonal_nodes[1].append(node_id)
                else: #upper right part (northeast)
                    zonal_nodes[2].append(node_id)
            else:
                if node_lon<= set_lon: #lower left part (southwest)
                    zonal_nodes[3].append(node_id)
                else: #lower right part (southeast)
                    zonal_nodes[4].append(node_id)

        for i in range(1, 5):
            print("Study_area",study_area,"zone:",i,"num of nodes:",len(zonal_nodes[i]))
            tt_num_nodes += len(zonal_nodes[i])

    microtransit_nodes_f.close()
    print("Study_area",study_area,"tt_num_nodes",tt_num_nodes,)

    #D:\Siwei_Micro_Transit\Data\0719_input\initial_full_transit_network
    if study_area == "downtown_sd":
        initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/initial_full_transit_network"
        initial_network_4_zones_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/initial_full_transit_network_4_zones"
    else:
        #D:\Siwei_Micro_Transit\Data\0719_input\lemon_grove\initial_network_4_zones
        initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/initial_network"
        initial_network_4_zones_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/initial_network_4_zones"

    # initial_network_folder="D:/Ritun/Siwei_Micro_Transit/Data/0719_input/initial_full_transit_network"
    # initial_network_4_zones_folder="D:/Ritun/Siwei_Micro_Transit/Data/0719_input/initial_full_transit_network_4_zones"
    headway_scenarios = [10, 15, 20, 30, 60]
    microtransit_scenarios = ["micro", "non_micro", "micro_only"]
    time_periods = ["AM", "MD", "PM", "EV"]
    for virstop in [50, 75, 100]:
        for headway in headway_scenarios:
            for microtransit in microtransit_scenarios:

                if microtransit == "micro":
                    initial_network_scen_dir = os.path.join(initial_network_folder,"initial_super_network_%s_hw_%s_virstop_%s.csv" % (str(microtransit), str(headway), str(virstop)))
                    initial_network_4_zones_scen_dir = os.path.join(initial_network_4_zones_folder,"initial_super_network_%s_hw_%s_virstop_%s.csv" % (str(microtransit), str(headway), str(virstop)))
                elif microtransit == "micro_only":
                    initial_network_scen_dir = os.path.join(initial_network_folder,"initial_super_network_%s_virstop_%s.csv" % (str(microtransit), str(virstop)))
                    initial_network_4_zones_scen_dir = os.path.join(initial_network_4_zones_folder,"initial_super_network_%s_virstop_%s.csv" % (str(microtransit), str(virstop)))
                else:
                    initial_network_scen_dir = os.path.join(initial_network_folder,"initial_super_network_%s_hw_%s.csv" % (str(microtransit), str(headway)))
                    initial_network_4_zones_scen_dir = os.path.join(initial_network_4_zones_folder,"initial_super_network_%s_hw_%s.csv" % (str(microtransit), str(headway)))

                with open(initial_network_4_zones_scen_dir, 'w+', newline='') as csvfile:
                    #from_node	to_node	distance	travel_time	link_type	route

                    fieldnames = ["from_node", "to_node", "distance", "travel_time", "link_type","route"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    input_num_of_links=0
                    output_num_of_links = 0
                    with open(initial_network_scen_dir) as super_network_f:
                        # from_node	to_node	distance	travel_time	link_type	route_id	route_type
                        csvreader = csv.DictReader(super_network_f)

                        for data in csvreader:
                            # node_index	is_stop_only	node_lat	node_lon

                            transit_route = OrderedDict()

                            from_node = int(data["from_node"])
                            to_node = int(data["to_node"])
                            distance = float(data["distance"])
                            travel_time = float(data["travel_time"])
                            link_type = int(data["link_type"])
                            route = int(data["route"])
                            input_num_of_links+=1

                            if link_type==4: #if it is a microtransit link
                                if from_node in zonal_nodes[1] and to_node in zonal_nodes[1]:
                                    aaa=0
                                elif from_node in zonal_nodes[2] and to_node in zonal_nodes[2]:
                                    aaa = 0
                                elif from_node in zonal_nodes[3] and to_node in zonal_nodes[3]:
                                    aaa=0
                                elif from_node in zonal_nodes[4] and to_node in zonal_nodes[4]:
                                    aaa = 0
                                else: # if microtransit links cross zones, then drop this link
                                    continue

                            writer.writerow({'from_node': from_node, 'to_node': to_node, 'distance': distance,
                                             'travel_time': travel_time, "link_type": link_type,"route": route})
                            output_num_of_links+=1

                    super_network_f.close()
                print("microtransit, headway, virstop",(str(microtransit), str(headway), str(virstop)),"input_links:",input_num_of_links,"output_links:",output_num_of_links)