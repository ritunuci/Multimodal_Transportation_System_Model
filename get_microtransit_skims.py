import random
import math
import os

import pandas as pd
import numpy as np
import os
import networkx as nx

import networkx as nx
import csv
import math
# from scipy.misc import derivative
from scipy.optimize import approx_fprime
import scipy.integrate as integrate
import numpy as np
import random
from collections import OrderedDict
import matplotlib.pyplot as plt
import scipy
import random
import collections
from itertools import islice


import inte_sys_mode_choice
import network_algorithms as n_a
import mtsm_paths as mtsm

def get_node_ct(study_area):
    # pre_node_dir
    # census_tract	node_in_fleetpy	is_demand_node
    census_tract_node = OrderedDict()
    node_census_tract = OrderedDict()
    demand_nodes_fleetpy = []
    if study_area == "downtown_sd":
        network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'

    if study_area == "lemon_grove":
        network_folder = mtsm.LG_TRANSIT_NETWORK_DIR
    pre_node_dir = os.path.join(network_folder, 'pre_nodes.csv')

    with open(pre_node_dir) as f:
        csvreader = csv.DictReader(f)
        for data in csvreader:
#             is_demand_node = int(float(data["is_demand_node"]))
#             if is_demand_node == 1:
            census_tract = int(float(data["census_tract"]))
            if census_tract not in census_tract_node:
                census_tract_node[census_tract] = []
            node_id = int(float(data["node_in_fleetpy"]))
            if node_id not in census_tract_node[census_tract]:
                census_tract_node[census_tract].append(node_id)

            if node_id not in node_census_tract:
                node_census_tract[node_id] = census_tract

            if node_id not in demand_nodes_fleetpy:
                demand_nodes_fleetpy.append(node_id)
    f.close()

    return census_tract_node,node_census_tract

def get_microtransit_skims():
    from itertools import islice

    # Read FleetPy's output into choice model

    census_tract_tt_wait_time = OrderedDict()
    census_tract_num_rq = OrderedDict()
    census_tract_avg_wait_time = OrderedDict()

    #model rejection rate from time of day and census tract level
    census_tract_rq_served_num=OrderedDict()
    census_tract_rq_reject_num=OrderedDict()
    census_tract_reject_rate=OrderedDict()

    time_tt_drive_time = OrderedDict()
    time_tt_direct_time = OrderedDict()
    time_detour_ratio = OrderedDict()
    # "AM"=5-10AM
    # "MD"=10-15
    # "PM"=15-20
    # "EV"=20-24

    census_tract_node,node_census_tract=get_node_ct()

    for time_period in ["AM", "MD", "PM", "EV"]:
        census_tract_tt_wait_time[time_period] = OrderedDict()
        census_tract_num_rq[time_period] = OrderedDict()
        census_tract_avg_wait_time[time_period] = OrderedDict()
        time_tt_drive_time[time_period] = 0
        time_tt_direct_time[time_period] = 0
        time_detour_ratio[time_period] = 0

        #model the rejection probability in each census tract 
        census_tract_rq_served_num[time_period]=OrderedDict()
        census_tract_rq_reject_num[time_period]=OrderedDict()
        census_tract_reject_rate[time_period]=OrderedDict()

        for census_tract in census_tract_node.keys():
            census_tract_tt_wait_time[time_period][census_tract] = 0
            census_tract_num_rq[time_period][census_tract] = 0
            census_tract_avg_wait_time[time_period][census_tract] = 0
            #model the rejection probability in each census tract 
            census_tract_rq_served_num[time_period][census_tract]=0
            census_tract_rq_reject_num[time_period][census_tract]=0
            census_tract_reject_rate[time_period][census_tract]=0

    # D:\Siwei_Micro_Transit\FleetPy_SanDiego\studies\example_study\results\example_pool_irsonly_sc_1
    # D:\Siwei_Micro_Transit\Data\0719_input\FleetPy_output
    Fleetpy_output_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/studies/example_study/results/example_pool_irsonly_sc_1"
    # Fleetpy_output_folder="D:/Ritun/Siwei_Micro_Transit/Data/0719_input/FleetPy_output/"
    Fleetpy_user_stats = os.path.join(Fleetpy_output_folder, "1_user-stats.csv")

    # lines_number=10
    # i=0
    num_rq_served = 0
    with open(Fleetpy_user_stats) as f:
        #     head = list(islice(f, lines_number))# read the first 10 lines for now
        #     csvreader = csv.DictReader(head)

        csvreader = csv.DictReader(f)
        for data in csvreader:
            #         print("line:",i)
            #             print(data)
            rq_time = int(float(data["rq_time"]))
            #         request_id=float(data["start"])
            start_node = data["start"]
            start_node = int(start_node.split(';')[0])
            end_node = data["end"]
            end_node = int(end_node.split(';')[0])
            direct_route_travel_time = float(data["direct_route_travel_time"])
            direct_route_distance = float(data["direct_route_distance"])
            offers = data["offers"]
            if len(offers) > 2:
                num_rq_served += 1
                #             wait_time=offers.split(';')[0]
                #             wait_time=wait_time.split(':')[2]
                #             wait_time_=float(wait_time)

                try:
                    wait_time = offers.split(';')[0]
                    wait_time = wait_time.split(':')[2]
                    wait_time_ = float(wait_time)
                except Exception as e:
                    print("offers:", offers, "len of offers", len(offers), "\t", "wait time:", wait_time, "\t",
                          "wait_time_", wait_time_)
                    raise e

                drive_time = offers.split(';')[1]
                drive_time = drive_time.split(':')[1]
                drive_time_ = float(drive_time)

                fare = offers.split(';')[2]
                fare = fare.split(':')[1]
                fare_ = float(fare)

                #         print("rq_time","start_node","end_node","direct_route_travel_time","direct_route_distance","offers","wait_time","drive_time","fare")
                #         print(rq_time,start_node,end_node,direct_route_travel_time,direct_route_distance,"\t",offers,"\t",wait_time,drive_time,fare,"\n")
                #         i+=1

                ########################################################
                # Calculate the average waiting time by census tract
                #######################################################
                start_node_ct = node_census_tract[start_node]
                if rq_time <= (10 * 3600):
                    time_period = "AM"
                    census_tract_tt_wait_time[time_period][start_node_ct] += wait_time_
                    census_tract_num_rq[time_period][start_node_ct] += 1
                     #model rejection rate
                    census_tract_rq_served_num[time_period][start_node_ct]+=1
                elif rq_time <= (15 * 3600):
                    time_period = "MD"
                    census_tract_tt_wait_time[time_period][start_node_ct] += wait_time_
                    census_tract_num_rq[time_period][start_node_ct] += 1
                    #model rejection rate
                    census_tract_rq_served_num[time_period][start_node_ct]+=1
                elif rq_time <= (20 * 3600):
                    time_period = "PM"
                    census_tract_tt_wait_time[time_period][start_node_ct] += wait_time_
                    census_tract_num_rq[time_period][start_node_ct] += 1
                    #model rejection rate
                    census_tract_rq_served_num[time_period][start_node_ct]+=1
                else:
                    time_period = "EV"
                    census_tract_tt_wait_time[time_period][start_node_ct] += wait_time_
                    census_tract_num_rq[time_period][start_node_ct] += 1
                    #model rejection rate
                    census_tract_rq_served_num[time_period][start_node_ct]+=1


                ########################################################
                # Calculate the average time detour ratio by time of day
                #######################################################
                start_node_ct = node_census_tract[start_node]
                if rq_time <= (10 * 3600):
                    time_period = "AM"
                    time_tt_drive_time[time_period] += drive_time_
                    time_tt_direct_time[time_period] += direct_route_travel_time

                elif rq_time <= (15 * 3600):
                    time_period = "MD"
                    time_tt_drive_time[time_period] += drive_time_
                    time_tt_direct_time[time_period] += direct_route_travel_time
                elif rq_time <= (20 * 3600):
                    time_period = "PM"
                    time_tt_drive_time[time_period] += drive_time_
                    time_tt_direct_time[time_period] += direct_route_travel_time
                else:
                    time_period = "EV"
                    time_tt_drive_time[time_period] += drive_time_
                    time_tt_direct_time[time_period] += direct_route_travel_time
            else:
                start_node_ct=node_census_tract[start_node]
                if rq_time<=(10*3600): 
                    time_period="AM"
                    #model rejection rate
                    census_tract_rq_reject_num[time_period][start_node_ct]+=1
                elif rq_time<=(15*3600):
                    time_period="MD"
                    #model rejection rate
                    census_tract_rq_reject_num[time_period][start_node_ct]+=1
                elif rq_time<=(20*3600):
                    time_period="PM"
                    #model rejection rate
                    census_tract_rq_reject_num[time_period][start_node_ct]+=1
                else:
                    time_period="EV"
                    #model rejection rate
                    census_tract_rq_reject_num[time_period][start_node_ct]+=1
    total_demand_=0 
    for time_period in ["AM", "MD", "PM", "EV"]:
        if time_tt_direct_time[time_period]==0:
            time_detour_ratio[time_period]=1
        else:
            time_detour_ratio[time_period] = time_tt_drive_time[time_period] / time_tt_direct_time[time_period]
        for census_tract in census_tract_node.keys():
            if census_tract_num_rq[time_period][census_tract] == 0:
                census_tract_avg_wait_time[time_period][census_tract] = 180
            else:
                census_tract_avg_wait_time[time_period][census_tract] = census_tract_tt_wait_time[time_period][census_tract]/census_tract_num_rq[time_period][census_tract]

             #calculate the rejection rate
            reject_num=census_tract_rq_reject_num[time_period][census_tract]
            served_num=census_tract_rq_served_num[time_period][census_tract]
            total_demand_+=reject_num
            total_demand_+=served_num
    #         print("time_period",time_period,"census_tract",census_tract,"reject_num",reject_num,"served_num",served_num)
            if (reject_num+served_num)==0:
                census_tract_reject_rate[time_period][census_tract]=0
            else:
                census_tract_reject_rate[time_period][census_tract]=reject_num/(reject_num+served_num)

    print("total microtransit demand",total_demand_,"number of requests served:",num_rq_served,"rejection rate:",census_tract_reject_rate)

    return time_detour_ratio,census_tract_avg_wait_time,census_tract_reject_rate

def get_dmd_node_vir_stop(virtual_stop_list,walking_visited_temp_all):
    demand_node_vir_stop=OrderedDict()
    demand_nodes_fleetpy,node_census_tract=inte_sys_mode_choice.get_demand_nodes()

    # network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'
    # edges_dir = os.path.join(network_folder, 'edges.csv')

    # walking_network_graph=n_a.read_walking_network(edges_dir)
    # walking_visited_temp_all,walk_path_all=n_a.dijsktra_all_to_all(walking_network_graph)
    for demand_node in demand_nodes_fleetpy:
        min_dist=math.inf
        min_vir_stop=0
        demand_node_vir_stop[demand_node]=OrderedDict()
        for virtual_stop in virtual_stop_list:
            # print("demand_node",demand_node,"virtual_stop",virtual_stop)
            walk_dist=walking_visited_temp_all[demand_node][virtual_stop]
            if walk_dist<min_dist:
                min_dist=walk_dist
                min_vir_stop=virtual_stop
        demand_node_vir_stop[demand_node][min_vir_stop]=min_dist
    return demand_node_vir_stop
        
    
def read_virtual_stop(virtual_stop_dir):
    virtual_stop_list=[]
    with open(virtual_stop_dir) as f:
        csvreader = csv.DictReader(f)
        for data in csvreader:
            #             print(data)
            virtual_stop = int(data["virtual_stop"])

            if virtual_stop not in virtual_stop_list:
                virtual_stop_list.append(virtual_stop)
    f.close()

    return virtual_stop_list