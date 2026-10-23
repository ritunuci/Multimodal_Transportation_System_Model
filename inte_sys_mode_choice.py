import os
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
import scipy.integrate as integrate
import numpy as np
import random
from collections import OrderedDict
import matplotlib.pyplot as plt
import scipy
import random
import collections
from itertools import islice


import get_auto_skims as auto
import get_microtransit_skims as mt
import get_walk_transit_skims as wt
import network_algorithms as n_a

def get_demand_nodes():
    # pre_node_dir
    network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'
    pre_node_dir = os.path.join(network_folder, 'pre_nodes.csv')
    # census_tract	node_in_fleetpy	is_demand_node
    census_tract_node = OrderedDict()
    node_census_tract = OrderedDict()
    demand_nodes_fleetpy = []
    with open(pre_node_dir) as f:
        csvreader = csv.DictReader(f)
        for data in csvreader:
            is_demand_node = int(float(data["is_demand_node"]))
            if is_demand_node == 1:
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
    return demand_nodes_fleetpy,node_census_tract


def prepare_M_matrices(virtual_stop_list=None,walking_visited_temp_all=None,auto_visited_temp_all=None,auto_dist_visited_temp_all=None):
    M_walking_mat = OrderedDict()
    M_waiting_mat = OrderedDict()
    M_ivt_mat = OrderedDict()
    M_fare_mat = OrderedDict()
    M_reject_rate_mat = OrderedDict()

    # network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'
    # edges_dir = os.path.join(network_folder, 'edges.csv')
    #
    # walking_network_graph=n_a.read_walking_network(edges_dir)
    # walking_visited_temp_all,walk_path_all=n_a.dijsktra_all_to_all(walking_network_graph)

    demand_nodes_fleetpy,node_census_tract=get_demand_nodes()
    time_detour_ratio,census_tract_avg_wait_time,census_tract_reject_rate=mt.get_microtransit_skims()
    demand_node_vir_stop=mt.get_dmd_node_vir_stop(virtual_stop_list,walking_visited_temp_all)

    # auto_visited_temp_all=auto.get_auto_time_skims(edges_dir)
    # auto_dist_visited_temp_all = auto.get_auto_dist_skims(edges_dir)

    for time_period in ["AM", "MD", "PM", "EV"]:
        M_walking_mat[time_period] = OrderedDict()
        M_waiting_mat[time_period] = OrderedDict()
        M_ivt_mat[time_period] = OrderedDict()
        M_fare_mat[time_period] = OrderedDict()

        M_reject_rate_mat[time_period] = OrderedDict()
        for demand_node_origin in demand_nodes_fleetpy:
            #         M_walking_mat[time_period][demand_node_origin]=60
            # waiting time use census tract aggregation
            demand_node_ct = node_census_tract[demand_node_origin]
            M_waiting_mat[time_period][demand_node_origin] = census_tract_avg_wait_time[time_period][demand_node_ct]/60 ##convert the waiting time to minutes
            M_reject_rate_mat[time_period][demand_node_origin] = census_tract_reject_rate[time_period][demand_node_ct]
            # in-vehicle-travel time use direct travel time * detour ratio
            M_ivt_mat[time_period][demand_node_origin] = OrderedDict()
            M_fare_mat[time_period][demand_node_origin] = OrderedDict()
            # calculate walking distance from demand nodes and their closest virtual stop
            M_walking_mat[time_period][demand_node_origin] = OrderedDict()
            for demand_node_dest in demand_nodes_fleetpy:
                if demand_node_dest not in M_ivt_mat[time_period][demand_node_origin]:
                    M_ivt_mat[time_period][demand_node_origin][demand_node_dest] = time_detour_ratio[time_period] * auto_visited_temp_all[demand_node_origin][demand_node_dest]/60  ##convert the ivt time to minutes
                # distance based fare (auto_network_dist_graph)
                if demand_node_dest not in M_fare_mat[time_period][demand_node_origin]:
                    M_fare_mat[time_period][demand_node_origin][demand_node_dest] = max(2.5, 0.0015 *auto_dist_visited_temp_all[demand_node_origin][demand_node_dest]) #US Dallor
                #######################
                # calculate walking distance according to demand nodes and virtual stops
                ###################
                if demand_node_dest not in M_walking_mat[time_period][demand_node_origin]:
                    origin_vir_stop = list(demand_node_vir_stop[demand_node_origin].keys())[0]
                    origin_walk_time = demand_node_vir_stop[demand_node_origin][origin_vir_stop] #walking time (sec)
                    dest_vir_stop = list(demand_node_vir_stop[demand_node_dest].keys())[0]
                    dest_walk_time = demand_node_vir_stop[demand_node_dest][dest_vir_stop] #walking time (sec)
                    # if demand_node_origin == 40 and demand_node_dest == 135:
                    #     print("o_dmd_node", demand_node_origin, "o_virstop", origin_vir_stop, "o_walk_dist",
                    #           origin_walk_dist)
                    #     print("d_dmd_node", demand_node_dest, "d_virstop", dest_vir_stop, "d_walk_dist", dest_walk_dist)
                    M_walking_mat[time_period][demand_node_origin][demand_node_dest] = (origin_walk_time + dest_walk_time)/60 ##convert the walking time to minutes

    # for time_period in ["AM", "MD", "PM", "EV"]:
    #     M_walking_mat[time_period] = OrderedDict()
    #     M_waiting_mat[time_period] = OrderedDict()
    #     M_ivt_mat[time_period] = OrderedDict()
    #     M_fare_mat[time_period] = OrderedDict()
    #
    #     M_reject_rate_mat[time_period] = OrderedDict()
    #     for demand_node_origin in demand_nodes_fleetpy:
    #         M_walking_mat[time_period][demand_node_origin] = 60
    #         # waiting time use census tract aggregation
    #         demand_node_ct = node_census_tract[demand_node_origin]
    #         M_waiting_mat[time_period][demand_node_origin] = census_tract_avg_wait_time[time_period][demand_node_ct]
    #         M_reject_rate_mat[time_period][demand_node_origin] = census_tract_reject_rate[time_period][demand_node_ct]
    #         # in-vehicle-travel time use direct travel time * detour ratio
    #         M_ivt_mat[time_period][demand_node_origin] = OrderedDict()
    #         M_fare_mat[time_period][demand_node_origin] = OrderedDict()
    #         for demand_node_dest in demand_nodes_fleetpy:
    #             if demand_node_dest not in M_ivt_mat[time_period][demand_node_origin]:
    #                 M_ivt_mat[time_period][demand_node_origin][demand_node_dest] = time_detour_ratio[time_period] * \
    #                                                                                auto_visited_temp_all[
    #                                                                                    demand_node_origin][
    #                                                                                    demand_node_dest]
    #             # distance based fare (auto_network_dist_graph)
    #             if demand_node_dest not in M_fare_mat[time_period][demand_node_origin]:
    #                 M_fare_mat[time_period][demand_node_origin][demand_node_dest] = max(100, 0.1 *
    #                                                                                     auto_dist_visited_temp_all[
    #                                                                                         demand_node_origin][
    #                                                                                         demand_node_dest])

    return M_walking_mat,M_waiting_mat,M_ivt_mat,M_fare_mat,M_reject_rate_mat


def prepare_D_matrices(auto_visited_temp_all=None,auto_dist_visited_temp_all=None):
    demand_nodes_fleetpy, node_census_tract = get_demand_nodes()
    D_ivt_mat = OrderedDict()
    D_gas_mat = OrderedDict()

    # network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'
    # edges_dir = os.path.join(network_folder, 'edges.csv')

    # auto_visited_temp_all=auto.get_auto_time_skims(edges_dir)
    # auto_dist_visited_temp_all=auto.get_auto_dist_skims(edges_dir)
    for time_period in ["AM", "MD", "PM", "EV"]:
        D_ivt_mat[time_period] = OrderedDict()
        D_gas_mat[time_period] = OrderedDict()
        for demand_node_origin in demand_nodes_fleetpy:
            # path based on different time period and OD-based
            D_ivt_mat[time_period][demand_node_origin] = OrderedDict()
            D_gas_mat[time_period][demand_node_origin] = OrderedDict()
            for demand_node_dest in demand_nodes_fleetpy:
                if demand_node_dest not in D_ivt_mat[time_period][demand_node_origin]:
                    if time_period in ["AM", "PM"]:
                        D_ivt_mat[time_period][demand_node_origin][demand_node_dest] = auto_visited_temp_all[demand_node_origin][demand_node_dest] * 1/60 #convert the seconds to minutes
                    elif time_period in ["MD"]:
                        D_ivt_mat[time_period][demand_node_origin][demand_node_dest] = auto_visited_temp_all[demand_node_origin][demand_node_dest] * 1/60 #convert the seconds to minutes
                    else:
                        D_ivt_mat[time_period][demand_node_origin][demand_node_dest] = auto_visited_temp_all[demand_node_origin][demand_node_dest] * 1/60 #convert the seconds to minutes
                # assumed gas is distance based
                # $0.00012 per meter for efficiency=25 milie/gallon and $5/gallon
                if demand_node_dest not in D_gas_mat[time_period][demand_node_origin]:
                    D_gas_mat[time_period][demand_node_origin][demand_node_dest] = auto_dist_visited_temp_all[demand_node_origin][demand_node_dest] * 0.00012
    return D_ivt_mat,D_gas_mat


def prepare_F_matrices(walk_transit_network):
    # microtransit service
    # network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'
    # walk_transit_network=os.path.join(network_folder,'walk_transit_edges.csv')
    walk_transit_visited_temp_all=wt.get_walk_transit_skims(walk_transit_network)


    F_path_mat = OrderedDict()
    F_fare_mat = OrderedDict()

    demand_nodes_fleetpy,node_census_tract=get_demand_nodes()
    for time_period in ["AM", "MD", "PM", "EV"]:
        F_path_mat[time_period] = OrderedDict()
        F_fare_mat[time_period] = OrderedDict()
        for demand_node_origin in demand_nodes_fleetpy:
            # path based on different time period and OD-based
            F_path_mat[time_period][demand_node_origin] = OrderedDict()
            F_fare_mat[time_period][demand_node_origin] = OrderedDict()
            for demand_node_dest in demand_nodes_fleetpy:
                if demand_node_dest not in F_path_mat[time_period][demand_node_origin]:
                    if time_period in ["AM", "PM"]:
                        F_path_mat[time_period][demand_node_origin][demand_node_dest] = walk_transit_visited_temp_all[demand_node_origin][demand_node_dest] * 1/60 #convert walk_transit travel time to minutes
                    elif time_period in ["MD"]:
                        F_path_mat[time_period][demand_node_origin][demand_node_dest] = walk_transit_visited_temp_all[demand_node_origin][demand_node_dest] * 1/60  #convert walk_transit travel time to minutes
                    else:
                        F_path_mat[time_period][demand_node_origin][demand_node_dest] = walk_transit_visited_temp_all[demand_node_origin][demand_node_dest] * 1/60  #convert walk_transit travel time to minutes
                # distance based fare (auto_network_dist_graph)
                if demand_node_dest not in F_fare_mat[time_period][demand_node_origin]:
                    F_fare_mat[time_period][demand_node_origin][demand_node_dest] = 2.5 #US Dallor

    return F_path_mat,F_fare_mat


def MNL_choice(F_path_mat,F_fare_mat,D_ivt_mat,D_gas_mat,walking_visited_temp_all,auto_visited_temp_all,auto_dist_visited_temp_all,debug_mode=False,operating_periods=["AM", "MD", "PM", "EV"],virtual_stop_list=None,iteration=None,agent_choice_prob_pre=None,agent_selected_mode_pre=None):
    beta_M_vec = [-0.173, -0.119, -0.104, -0.134, -0.554, -5]
    #            [1,M_walking,M_waiting,M_ivt,M_fare,rejection]
    beta_D_vec = [0, -0.132, -0.554]
    #            [1, D_ivt, D_gas]
    beta_F_vec = [0.010, -0.106, -0.504]
    #             [1,F_path,F_fare]


    mode_switch_threshold=0.10

    M_walking_mat, M_waiting_mat, M_ivt_mat, M_fare_mat, M_reject_rate_mat = prepare_M_matrices(virtual_stop_list,walking_visited_temp_all,auto_visited_temp_all,auto_dist_visited_temp_all)

    # for i in range(10):
    M_numb = 0
    D_numb = 0
    F_numb = 0

    D_numb_bf = 0
    F_numb_bf = 0

    agent_choice_prob = OrderedDict()
    agent_selected_mode =OrderedDict()
    # lines_number=20
    M_number = OrderedDict()
    D_number = OrderedDict()
    F_number = OrderedDict()
    tot_number = OrderedDict()

    D_number_bf = OrderedDict()
    D_number_bf = OrderedDict()
    F_number_bf = OrderedDict()

    for time_period in ["AM", "MD", "PM", "EV"]:
        M_number[time_period] = 0
        D_number[time_period] = 0
        F_number[time_period] = 0
        tot_number[time_period] = 0
        D_number_bf[time_period] = 0
        F_number_bf[time_period] = 0

    mobility_sum_after_M = 0
    mobility_sum_before_M = 0
    mobility_diff_sum = 0

    selected_mode_user_exper = 0
    selected_mode_user_exper_bf = 0

    # operating_period_1 = ["AM", "PM"]
    # operating_period_2 = ["AM", "MD", "PM"]
    # operating_period_3 = ["AM", "MD", "PM", "EV"]

    revenue_M = 0
    revenue_F = 0
    revenue_total_af = 0
    # revenue_M=0
    # revenue_F_bf=0
    revenue_total_bf = 0

    #these two matrices does not need to be calculate each time
    # F_path_mat,F_fare_mat=prepare_F_matrices()
    # D_ivt_mat,D_gas_mat=prepare_D_matrices()

    demand_node_vir_stop=mt.get_dmd_node_vir_stop(virtual_stop_list,walking_visited_temp_all)


    for time_period in ["AM", "MD", "PM", "EV"]:
        M_number[time_period] = 0
        D_number[time_period] = 0
        F_number[time_period] = 0
        tot_number[time_period] = 0

    network_folder="D:/Ritun/Siwei_Micro_Transit/Data/0719_input"
    fleetpy_input_demand_folder="D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/example_demand/matched/example_network"
    if debug_mode==True:
        input_demand_file = os.path.join(network_folder, "debug_trips_nodes_study_area.csv")
        output_demand_file = os.path.join(fleetpy_input_demand_folder,"debug_fleetpy_demand.csv")  # this directory goes directly to fleetpy's input
    else:
        input_demand_file = os.path.join(network_folder,"trips_nodes_study_area.csv")
        output_demand_file = os.path.join(fleetpy_input_demand_folder,"fleetpy_demand.csv")  # this directory goes directly to fleetpy's input
    # output_demand_file=os.path.join(network_folder,'fleetpy_demand.csv')
    with open(input_demand_file) as f:
        #     head = list(islice(f, lines_number))# read the first 10 lines for now
        #     csvreader = csv.DictReader(head)
        csvreader = csv.DictReader(f)
        nodes = {}
        links = []
        node_list = []
        mode_switch_pax=0
        with open(output_demand_file, 'w+', newline='') as csvfile:
            fieldnames = ['rq_time', 'start', 'end', 'request_id']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in csvreader:
                #   depart_time	start	end	trip_id
                rq_time = int(data["depart_time"])
                request_id = int(float(data["trip_id"]))
                start_node = int(data["start"])
                end_node = int(data["end"])

                ###################################################
                # use virtual stop as an input of the calculation
                ##################################################
                origin_vir_stop = list(demand_node_vir_stop[start_node].keys())[0]
                dest_vir_stop = list(demand_node_vir_stop[end_node].keys())[0]

                #             if origin_vir_stop==594 or dest_vir_stop==594:
                #                 print("o_vir_stop",origin_vir_stop,"o_dmd_node",start_node,"d_vir_stop",dest_vir_stop,"d_dmd_node",end_node)
                if rq_time <= (10 * 3600):
                    time_period = "AM"
                elif rq_time <= (15 * 3600):
                    time_period = "MD"
                elif rq_time <= (20 * 3600):
                    time_period = "PM"
                else:
                    time_period = "EV"

                # read microtransit mode table
                M_walking = M_walking_mat[time_period][start_node][end_node]  # *****
                M_waiting = M_waiting_mat[time_period][origin_vir_stop]  # *****
                M_ivt = M_ivt_mat[time_period][origin_vir_stop][dest_vir_stop]
                M_fare = M_fare_mat[time_period][origin_vir_stop][dest_vir_stop]
                M_rejct_rate = M_reject_rate_mat[time_period][origin_vir_stop]

                M_vec = [1, M_walking, M_waiting, M_ivt, M_fare, M_rejct_rate]
                # read drive alone free mode table
                D_ivt = D_ivt_mat[time_period][start_node][end_node]
                D_gas = D_gas_mat[time_period][start_node][end_node]
                D_vec = [1, D_ivt, D_gas]

                # read fixed route transit mode table
                F_path = F_path_mat[time_period][start_node][end_node]
                F_fare = F_fare_mat[time_period][start_node][end_node]
                F_vec = [1, F_path, F_fare]

                Logsum_M = math.exp(np.dot(beta_M_vec, M_vec))
                Logsum_D = math.exp(np.dot(beta_D_vec, D_vec))
                Logsum_F = math.exp(np.dot(beta_F_vec, F_vec))

                # calculate the probability of choosing each mode
                prob_M = Logsum_M / (Logsum_M + Logsum_D + Logsum_F)
                prob_D = Logsum_D / (Logsum_M + Logsum_D + Logsum_F)
                prob_F = Logsum_F / (Logsum_M + Logsum_D + Logsum_F)

                #################################################
                # 0727 calculate performance metrics: mobility
                #################################################
                mobility_metric_after_M = math.log(Logsum_M + Logsum_D + Logsum_F)  # mobility for each individual after Microtransit
                mobility_sum_after_M += mobility_metric_after_M

                mobility_metric_before_M = math.log(Logsum_D + Logsum_F)  # mobility for each individual before Microtransit
                mobility_sum_before_M += mobility_metric_before_M

                mobility_diff = (mobility_metric_after_M - mobility_metric_before_M)
                mobility_diff_sum += mobility_diff

                ran_num = random.random()

                if iteration ==0:
                    if time_period in operating_periods:  # if Microtransit service is operating in this time_period, then assign passengers to microtransit service
                        agent_choice_prob[request_id] = [prob_M, prob_D, prob_F]  ####0728: probably have problem here
                        if ran_num < prob_M:
                            M_numb += 1
                            M_number[time_period] += 1
                            demand_row = [rq_time, int(start_node), int(end_node), request_id]
                            selected_mode_user_exper += Logsum_M
                            revenue_M += M_fare  ##microtransit fare revenue under operating hours
                            agent_selected_mode[request_id]=0 # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                            writer.writerow({'rq_time': rq_time, 'start': origin_vir_stop, 'end': dest_vir_stop,
                                             'request_id': request_id})
                        elif (prob_M) <= ran_num < (prob_M + prob_D):
                            D_numb += 1
                            D_number[time_period] += 1
                            selected_mode_user_exper += Logsum_D
                            agent_selected_mode[request_id]=1 # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        else:
                            F_numb += 1
                            F_number[time_period] += 1
                            revenue_F += F_fare  ##fixed route transit fare revenue under microtransit operating hours
                            selected_mode_user_exper += Logsum_F
                            agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                    else:
                        prob_D_off_hr = Logsum_D / (Logsum_D + Logsum_F)
                        prob_F_off_hr = Logsum_F / (Logsum_D + Logsum_F)
                        agent_choice_prob[request_id] = [0, prob_D_off_hr, prob_F_off_hr]  ####
                        if ran_num < prob_D_off_hr:
                            D_numb += 1
                            D_number[time_period] += 1
                            selected_mode_user_exper += Logsum_D
                            agent_selected_mode[request_id] = 1  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        else:
                            F_numb += 1
                            F_number[time_period] += 1
                            revenue_F += F_fare  ##fixed route transit fare revenue under microtransit off hours
                            selected_mode_user_exper += Logsum_F
                            agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                else:# when iteration >=1, then we start compare the current mode prob with the previous iteration's mode prob
                    ################################################################
                    # 0728: this part deals with mode switching bounded rationality
                    ################################################################
                    if time_period in operating_periods:  # if Microtransit service is operating in this time_period, then assign passengers to microtransit service
                        agent_choice_prob[request_id] = [prob_M, prob_D, prob_F]
                        selected_mode_index_pre = agent_selected_mode_pre[request_id]  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        prob_M_pre = agent_choice_prob_pre[request_id][0]  # read microtransit probability from previous iteration
                        prob_M_current=agent_choice_prob[request_id][0] # read microtransit probability from current iteration

                        prob_M_abs_diff = abs(prob_M_pre - prob_M_current)
                        if prob_M_abs_diff <= mode_switch_threshold: #0728: not switching modes
                            if selected_mode_index_pre == 0:
                                M_numb += 1
                                M_number[time_period] += 1
                                demand_row = [rq_time, int(start_node), int(end_node), request_id]
                                selected_mode_user_exper += Logsum_M
                                revenue_M += M_fare  ##microtransit fare revenue under operating hours
                                agent_selected_mode[request_id] = 0  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                                writer.writerow({'rq_time': rq_time, 'start': origin_vir_stop, 'end': dest_vir_stop,
                                                 'request_id': request_id})
                            elif selected_mode_index_pre == 1:
                                D_numb += 1
                                D_number[time_period] += 1
                                selected_mode_user_exper += Logsum_D
                                agent_selected_mode[request_id] = 1  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                            else:
                                F_numb += 1
                                F_number[time_period] += 1
                                revenue_F += F_fare  ##fixed route transit fare revenue under microtransit operating hours
                                selected_mode_user_exper += Logsum_F
                                agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        else: # switch modes
                            mode_switch_pax+=1
                            if ran_num < prob_M:
                                M_numb += 1
                                M_number[time_period] += 1
                                demand_row = [rq_time, int(start_node), int(end_node), request_id]
                                selected_mode_user_exper += Logsum_M
                                revenue_M += M_fare  ##microtransit fare revenue under operating hours
                                agent_selected_mode[request_id] = 0  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                                writer.writerow({'rq_time': rq_time, 'start': origin_vir_stop, 'end': dest_vir_stop,
                                                 'request_id': request_id})
                            elif (prob_M) <= ran_num < (prob_M + prob_D):
                                D_numb += 1
                                D_number[time_period] += 1
                                selected_mode_user_exper += Logsum_D
                                agent_selected_mode[request_id] = 1  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                            else:
                                F_numb += 1
                                F_number[time_period] += 1
                                revenue_F += F_fare  ##fixed route transit fare revenue under microtransit operating hours
                                selected_mode_user_exper += Logsum_F
                                agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                    else: #if microtransit service is off-hour
                        prob_D_off_hr = Logsum_D / (Logsum_D + Logsum_F)
                        prob_F_off_hr = Logsum_F / (Logsum_D + Logsum_F)
                        agent_choice_prob[request_id] = [0, prob_D_off_hr, prob_F_off_hr]  ####
                        selected_mode_index_pre = agent_selected_mode_pre[request_id]  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        # prob_selected_pre = agent_choice_prob_pre[request_id][selected_mode_index_pre]  # read agent selected mode choice probability from last iteration
                        # prob_selected_current = agent_choice_prob[request_id][selected_mode_index_pre]
                        # if microtransit service is off-hour, then mode won't switch, because auto and fixed route transit skims are fixed.
                        if selected_mode_index_pre == 1:
                            D_numb += 1
                            D_number[time_period] += 1
                            selected_mode_user_exper += Logsum_D
                            agent_selected_mode[request_id] = 1  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        else:
                            F_numb += 1
                            F_number[time_period] += 1
                            revenue_F += F_fare  ##fixed route transit fare revenue under microtransit operating hours
                            selected_mode_user_exper += Logsum_F
                            agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"


                ###########################################################
                # 0727: calculate the selected mode experience without implementing the microtransit mode
                ###############################################################
                prob_D_bf = Logsum_D / (Logsum_D + Logsum_F)
                prob_F_bf = Logsum_F / (Logsum_D + Logsum_F)
                if ran_num < prob_D_bf:
                    D_numb_bf += 1
                    selected_mode_user_exper_bf += math.log(Logsum_D)
                #                 print("selected_mode_user_exper_bf",Logsum_D)
                else:
                    F_numb_bf += 1
                    revenue_total_bf += F_fare  ##fixed route transit fare revenue without microtransit service
                    selected_mode_user_exper_bf += math.log(Logsum_F)
            #                 print("selected_mode_user_exper_bf",Logsum_F)
            csvfile.close()
    f.close()

    total_numbers_modes = M_numb + D_numb + F_numb
    # for time_period in ["AM", "MD", "PM", "EV"]:
    #     tot_number[time_period] = M_number[time_period] + D_number[time_period] + F_number[time_period]
    #     print("time period:", time_period, "total travelers", tot_number[time_period])
    #     print("number of users microtransit:", M_number[time_period], "auto:", D_number[time_period],
    #           "fixed route transit:", F_number[time_period])
    #     print("percentage of users microtransit:", M_number[time_period] / tot_number[time_period],
    #           "number of drive alone:", D_number[time_period] / tot_number[time_period],
    #           "number of fixed route transit:", F_number[time_period] / tot_number[time_period], "\n")
    print("iteration", iteration,"number of people switch modes:",mode_switch_pax)
    print("total_trips:", total_numbers_modes, "number of microtransit:", M_numb, "drive alone:", D_numb,"fixed route transit:", F_numb)
    M_share=M_numb / total_numbers_modes
    D_share = D_numb / total_numbers_modes
    F_share = F_numb / total_numbers_modes
    mode_split=[M_share,D_share,F_share]
    print("percentage of microtransit:", M_share, "number of drive alone:",D_share, "number of fixed route transit:", F_share)

    print("total trips before implementation of microtransit:", (D_numb_bf + F_numb_bf), "drive alone:", D_numb_bf,"fixed route transit:", F_numb_bf)
    print("performance metrics - mobility - before:", mobility_sum_before_M, "after:", mobility_sum_after_M, "diff:",mobility_diff_sum)
    # selected_mode_user_exper_bf=math.log(selected_mode_user_exper_bf)
    # selected_mode_user_exper=math.log(selected_mode_user_exper)
    selected_mode_user_exper_diff=selected_mode_user_exper-selected_mode_user_exper_bf
    print("performance metrics - selected mode user experience - before:", selected_mode_user_exper_bf, "after:",selected_mode_user_exper, "diff:", selected_mode_user_exper_diff)

    revenue_total_af = revenue_M + revenue_F
    print("Revenue after implementing microtransit service:", "M_mode", revenue_M, "F_mode", revenue_F, "total", revenue_total_af, "before microtransit service:", revenue_total_bf)

        #     demand_fields=["rq_time", "start", "end", "request_id"]

    #     with open(output_demand_file, 'w+', newline='') as csvfile:
    #         fieldnames = ['rq_time', 'start', 'end', 'request_id']
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #         writer.writeheader()
    #         for data in csvreader:
    #             #   depart_time	start	end	trip_id
    #             rq_time = int(data["depart_time"])
    #             request_id = int(float(data["trip_id"]))
    #             start_node = int(data["start"])
    #             end_node = int(data["end"])
    #
    #
    #
    #             if rq_time <= (10 * 3600):
    #                 time_period = "AM"
    #             elif rq_time <= (15 * 3600):
    #                 time_period = "MD"
    #             elif rq_time <= (20 * 3600):
    #                 time_period = "PM"
    #             else:
    #                 time_period = "EV"
    #
    #             # read microtransit mode table
    #             M_walking = M_walking_mat[time_period][start_node]
    #             M_waiting = M_waiting_mat[time_period][start_node]
    #             M_ivt = M_ivt_mat[time_period][start_node][end_node]
    #             M_fare = M_fare_mat[time_period][start_node][end_node]
    #             M_rejct_rate = M_reject_rate_mat[time_period][start_node]
    #             M_vec = [1, M_walking, M_waiting, M_ivt, M_fare, M_rejct_rate]
    #             # read drive alone free mode table
    #             D_ivt = D_ivt_mat[time_period][start_node][end_node]
    #             D_gas = D_gas_mat[time_period][start_node][end_node]
    #             D_vec = [1, D_ivt, D_gas]
    #
    #             # read fixed route transit mode table
    #             F_path = F_path_mat[time_period][start_node][end_node]
    #
    #             F_fare = F_fare_mat[time_period][start_node][end_node]
    #
    #             F_vec = [1, F_path, F_fare]
    #
    #             Logsum_M = math.exp(np.dot(beta_M_vec, M_vec))
    #             Logsum_D = math.exp(np.dot(beta_D_vec, D_vec))
    #             Logsum_F = math.exp(np.dot(beta_F_vec, F_vec))
    #
    #             # calculate the probability of choosing each mode
    #             prob_M = Logsum_M / (Logsum_M + Logsum_D + Logsum_F)
    #             prob_D = Logsum_D / (Logsum_M + Logsum_D + Logsum_F)
    #             prob_F = Logsum_F / (Logsum_M + Logsum_D + Logsum_F)
    #
    #             agent_choice_prob[request_id] = [prob_M,prob_D,prob_F]
    #             # agent_choice_prob[request_id].append(prob_M)
    #
    #             #             print("Logsum_M:",np.dot(beta_M_vec, M_vec),"Logsum_D:",np.dot(beta_D_vec, D_vec),"Logsum_F:",np.dot(beta_F_vec, F_vec))
    #
    #             #             print("request_id:",request_id,"prob of choosing M:",prob_M,"prob of choosing D:",prob_D,"prob of choosing F:",prob_F)
    #             ran_num = random.random()
    #             if ran_num < prob_M:
    #                 M_numb += 1
    #                 M_number[time_period] += 1
    #                 demand_row = [rq_time, int(start_node), int(end_node), request_id]
    #                 writer.writerow({'rq_time': rq_time, 'start': start_node, 'end': end_node, 'request_id': request_id})
    #             elif (prob_M) <= ran_num < (prob_M + prob_D):
    #                 D_numb += 1
    #                 D_number[time_period] += 1
    #             else:
    #                 F_numb += 1
    #                 F_number[time_period] += 1
    #         csvfile.close()
    # f.close()
    #
    # total_numbers_modes = M_numb + D_numb + F_numb
    # for time_period in ["AM", "MD", "PM", "EV"]:
    #     tot_number[time_period] = M_number[time_period] + D_number[time_period] + F_number[time_period]
    #     print("time period:", time_period, "total travelers", tot_number[time_period])
    #     print("number of users microtransit:", M_number[time_period], "auto:", D_number[time_period],
    #           "fixed route transit:", F_number[time_period])
    #     print("percentage of users microtransit:", M_number[time_period] / tot_number[time_period],
    #           "number of drive alone:", D_number[time_period] / tot_number[time_period],
    #           "number of fixed route transit:", F_number[time_period] / tot_number[time_period], "\n")
    #
    # print("total_trips:", total_numbers_modes, "number of microtransit:", M_numb, "drive alone:", D_numb,
    #       "fixed route transit:", F_numb)
    # M_share=M_numb / total_numbers_modes
    # D_share = D_numb / total_numbers_modes
    # F_share = F_numb / total_numbers_modes
    # print("percentage of microtransit:", M_share, "number of drive alone:",
    #       D_numb / total_numbers_modes, "number of fixed route transit:", F_numb / total_numbers_modes)
    return agent_choice_prob,agent_selected_mode,total_numbers_modes,mode_split,revenue_total_af,revenue_total_bf,mobility_sum_after_M,mobility_sum_before_M,mobility_diff_sum,selected_mode_user_exper,selected_mode_user_exper_bf,selected_mode_user_exper_diff



'''
def Nested_Logit_choice(genlzd_auto_cost,genlzd_M_cost,genlzd_F_cost,genlzd_M_F_cost,T_fare,auto_fare,agent,debug_mode=False,operating_periods=["AM", "MD", "PM", "EV"],virtual_stop_list=None,iteration=None,agent_choice_prob_pre=None,agent_selected_mode_pre=None):
    beta_M_vec = [-0.173, -0.119, -0.104, -0.134, -0.554, -5]
    #            [1,M_walking,M_waiting,M_ivt,M_fare,rejection]
    beta_D_vec = [0, -0.132, -0.554]
    #            [1, D_ivt, D_gas]
    beta_F_vec = [0.010, -0.106, -0.504]
    #             [1,F_path,F_fare]


    mode_switch_threshold=0.10

    # for i in range(10):
    M_numb = 0
    D_numb = 0
    F_numb = 0

    D_numb_bf = 0
    F_numb_bf = 0

    agent_choice_prob = OrderedDict()
    agent_selected_mode =OrderedDict()
    # lines_number=20
    M_number = OrderedDict()
    D_number = OrderedDict()
    F_number = OrderedDict()
    tot_number = OrderedDict()

    D_number_bf = OrderedDict()
    D_number_bf = OrderedDict()
    F_number_bf = OrderedDict()

    for time_period in ["AM", "MD", "PM", "EV"]:
        M_number[time_period] = 0
        D_number[time_period] = 0
        F_number[time_period] = 0
        tot_number[time_period] = 0
        D_number_bf[time_period] = 0
        F_number_bf[time_period] = 0

    mobility_sum_after_M = 0
    mobility_sum_before_M = 0
    mobility_diff_sum = 0

    selected_mode_user_exper = 0
    selected_mode_user_exper_bf = 0


    revenue_M = 0
    revenue_F = 0
    revenue_total_af = 0
    # revenue_M=0
    # revenue_F_bf=0
    revenue_total_bf = 0






                Logsum_M = math.exp(np.dot(beta_M_vec, M_vec))
                Logsum_D = math.exp(np.dot(beta_D_vec, D_vec))
                Logsum_F = math.exp(np.dot(beta_F_vec, F_vec))

                # calculate the probability of choosing each mode
                prob_M = Logsum_M / (Logsum_M + Logsum_D + Logsum_F)
                prob_D = Logsum_D / (Logsum_M + Logsum_D + Logsum_F)
                prob_F = Logsum_F / (Logsum_M + Logsum_D + Logsum_F)

                #################################################
                # 0727 calculate performance metrics: mobility
                #################################################
                mobility_metric_after_M = math.log(Logsum_M + Logsum_D + Logsum_F)  # mobility for each individual after Microtransit
                mobility_sum_after_M += mobility_metric_after_M

                mobility_metric_before_M = math.log(Logsum_D + Logsum_F)  # mobility for each individual before Microtransit
                mobility_sum_before_M += mobility_metric_before_M

                mobility_diff = (mobility_metric_after_M - mobility_metric_before_M)
                mobility_diff_sum += mobility_diff

                ran_num = random.random()

                if iteration ==0:
                    if time_period in operating_periods:  # if Microtransit service is operating in this time_period, then assign passengers to microtransit service
                        agent_choice_prob[request_id] = [prob_M, prob_D, prob_F]  ####0728: probably have problem here
                        if ran_num < prob_M:
                            M_numb += 1
                            M_number[time_period] += 1
                            demand_row = [rq_time, int(start_node), int(end_node), request_id]
                            selected_mode_user_exper += Logsum_M
                            revenue_M += M_fare  ##microtransit fare revenue under operating hours
                            agent_selected_mode[request_id]=0 # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                            writer.writerow({'rq_time': rq_time, 'start': origin_vir_stop, 'end': dest_vir_stop,
                                             'request_id': request_id})
                        elif (prob_M) <= ran_num < (prob_M + prob_D):
                            D_numb += 1
                            D_number[time_period] += 1
                            selected_mode_user_exper += Logsum_D
                            agent_selected_mode[request_id]=1 # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        else:
                            F_numb += 1
                            F_number[time_period] += 1
                            revenue_F += F_fare  ##fixed route transit fare revenue under microtransit operating hours
                            selected_mode_user_exper += Logsum_F
                            agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                    else:
                        prob_D_off_hr = Logsum_D / (Logsum_D + Logsum_F)
                        prob_F_off_hr = Logsum_F / (Logsum_D + Logsum_F)
                        agent_choice_prob[request_id] = [0, prob_D_off_hr, prob_F_off_hr]  ####
                        if ran_num < prob_D_off_hr:
                            D_numb += 1
                            D_number[time_period] += 1
                            selected_mode_user_exper += Logsum_D
                            agent_selected_mode[request_id] = 1  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        else:
                            F_numb += 1
                            F_number[time_period] += 1
                            revenue_F += F_fare  ##fixed route transit fare revenue under microtransit off hours
                            selected_mode_user_exper += Logsum_F
                            agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                else:# when iteration >=1, then we start compare the current mode prob with the previous iteration's mode prob
                    ################################################################
                    # 0728: this part deals with mode switching bounded rationality
                    ################################################################
                    if time_period in operating_periods:  # if Microtransit service is operating in this time_period, then assign passengers to microtransit service
                        agent_choice_prob[request_id] = [prob_M, prob_D, prob_F]
                        selected_mode_index_pre = agent_selected_mode_pre[request_id]  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        prob_M_pre = agent_choice_prob_pre[request_id][0]  # read microtransit probability from previous iteration
                        prob_M_current=agent_choice_prob[request_id][0] # read microtransit probability from current iteration

                        prob_M_abs_diff = abs(prob_M_pre - prob_M_current)
                        if prob_M_abs_diff <= mode_switch_threshold: #0728: not switching modes
                            if selected_mode_index_pre == 0:
                                M_numb += 1
                                M_number[time_period] += 1
                                demand_row = [rq_time, int(start_node), int(end_node), request_id]
                                selected_mode_user_exper += Logsum_M
                                revenue_M += M_fare  ##microtransit fare revenue under operating hours
                                agent_selected_mode[request_id] = 0  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                                writer.writerow({'rq_time': rq_time, 'start': origin_vir_stop, 'end': dest_vir_stop,
                                                 'request_id': request_id})
                            elif selected_mode_index_pre == 1:
                                D_numb += 1
                                D_number[time_period] += 1
                                selected_mode_user_exper += Logsum_D
                                agent_selected_mode[request_id] = 1  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                            else:
                                F_numb += 1
                                F_number[time_period] += 1
                                revenue_F += F_fare  ##fixed route transit fare revenue under microtransit operating hours
                                selected_mode_user_exper += Logsum_F
                                agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        else: # switch modes
                            mode_switch_pax+=1
                            if ran_num < prob_M:
                                M_numb += 1
                                M_number[time_period] += 1
                                demand_row = [rq_time, int(start_node), int(end_node), request_id]
                                selected_mode_user_exper += Logsum_M
                                revenue_M += M_fare  ##microtransit fare revenue under operating hours
                                agent_selected_mode[request_id] = 0  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                                writer.writerow({'rq_time': rq_time, 'start': origin_vir_stop, 'end': dest_vir_stop,
                                                 'request_id': request_id})
                            elif (prob_M) <= ran_num < (prob_M + prob_D):
                                D_numb += 1
                                D_number[time_period] += 1
                                selected_mode_user_exper += Logsum_D
                                agent_selected_mode[request_id] = 1  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                            else:
                                F_numb += 1
                                F_number[time_period] += 1
                                revenue_F += F_fare  ##fixed route transit fare revenue under microtransit operating hours
                                selected_mode_user_exper += Logsum_F
                                agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                    else: #if microtransit service is off-hour
                        prob_D_off_hr = Logsum_D / (Logsum_D + Logsum_F)
                        prob_F_off_hr = Logsum_F / (Logsum_D + Logsum_F)
                        agent_choice_prob[request_id] = [0, prob_D_off_hr, prob_F_off_hr]  ####
                        selected_mode_index_pre = agent_selected_mode_pre[request_id]  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        # prob_selected_pre = agent_choice_prob_pre[request_id][selected_mode_index_pre]  # read agent selected mode choice probability from last iteration
                        # prob_selected_current = agent_choice_prob[request_id][selected_mode_index_pre]
                        # if microtransit service is off-hour, then mode won't switch, because auto and fixed route transit skims are fixed.
                        if selected_mode_index_pre == 1:
                            D_numb += 1
                            D_number[time_period] += 1
                            selected_mode_user_exper += Logsum_D
                            agent_selected_mode[request_id] = 1  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"
                        else:
                            F_numb += 1
                            F_number[time_period] += 1
                            revenue_F += F_fare  ##fixed route transit fare revenue under microtransit operating hours
                            selected_mode_user_exper += Logsum_F
                            agent_selected_mode[request_id] = 2  # select mode "0-microtransit; 1-drive alone; 2-fixed route transit"


                ###########################################################
                # 0727: calculate the selected mode experience without implementing the microtransit mode
                ###############################################################
                prob_D_bf = Logsum_D / (Logsum_D + Logsum_F)
                prob_F_bf = Logsum_F / (Logsum_D + Logsum_F)
                if ran_num < prob_D_bf:
                    D_numb_bf += 1
                    selected_mode_user_exper_bf += math.log(Logsum_D)
                #                 print("selected_mode_user_exper_bf",Logsum_D)
                else:
                    F_numb_bf += 1
                    revenue_total_bf += F_fare  ##fixed route transit fare revenue without microtransit service
                    selected_mode_user_exper_bf += math.log(Logsum_F)
            #                 print("selected_mode_user_exper_bf",Logsum_F)


    total_numbers_modes = M_numb + D_numb + F_numb


    return agent_choice_prob,agent_selected_mode,total_numbers_modes,mode_split,revenue_total_af,revenue_total_bf,mobility_sum_after_M,mobility_sum_before_M,mobility_diff_sum,selected_mode_user_exper,selected_mode_user_exper_bf,selected_mode_user_exper_diff
    
    '''