import os
import csv
import random
import numpy as np
import pre_process.process_network as p_n
from collections import OrderedDict
import pandas as pd
import mtsm_paths as mtsm

# The demand-preparation functions below built the frozen demand file in mtsm_data/; the run uses none of them
# (synthesize_requests_with_trend_time moved to mtsm_model/helpers/synthetic_demand.py, 2026-11-23). Their source
# folders are outside the codebase.
# STALE: network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input"
# STALE: request_file=os.path.join(network_folder,"trips_nodes_study_area_with_beta.csv")
# STALE: new_input_demand=os.path.join(network_folder,"trips_nodes_study_area_with_beta.csv")
# STALE:
# STALE: lemon_grove_demand_folder = "D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove/demand_folder"
# STALE: lemon_grove_MGRA= os.path.join(lemon_grove_demand_folder,"Lemon_grove_MGRA.csv")
# STALE:
# STALE: lemon_grove_trip_file = os.path.join(lemon_grove_demand_folder,"larger_SANDAG_trips_in_MGRA.csv")
def select_trips(area_MGRA,trip_file,output_trip_file):
    study_area_MGRA_list=[]
    with open(area_MGRA) as f_MGRA:
        csvreader = csv.DictReader(f_MGRA)
        for data in csvreader:
            #             print(data)
            MGRA = int(data["MGRA"])
            if MGRA not in study_area_MGRA_list:
                study_area_MGRA_list.append(MGRA)
    f_MGRA.close()
    print("number of study_area_MGRA_list",len(study_area_MGRA_list))
    with open(output_trip_file, 'w+', newline='') as csvfile:
        fieldnames = ["depart_hr","second",'rq_time', 'start (MGRA)', 'end (MGRA)', 'mode']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        trips_MGRA_list=[]
        with open(trip_file) as f:
            csvreader = csv.DictReader(f)
            for data in csvreader:
                #depart	origin	destination	trip_mode

                depart = int(data["depart"])
                second = int(round(random.random()*3600,0))
                rq_time = depart *3600 + second
                origin = int(data["origin"])
                destination = int(data["destination"])
                trip_mode = str(data["trip_mode"])
                if (origin in study_area_MGRA_list) and (destination in study_area_MGRA_list):
                    if origin not in trips_MGRA_list:
                        trips_MGRA_list.append(origin)
                    if destination not in trips_MGRA_list:
                        trips_MGRA_list.append(destination)
                    writer.writerow({'depart_hr': depart, 'second': second, 'rq_time': rq_time, 'start (MGRA)': origin,  "end (MGRA)": destination, "mode": trip_mode})
        f.close()
    csvfile.close()
    print("number of trips_MGRA_list",len(trips_MGRA_list))

def most_frequent(List): # find the most frequent element of a list
    dict = {}
    count, itm = 0, ''
    for item in reversed(List):
        dict[item] = dict.get(item, 0) + 1
        if dict[item] >= count :
            count, itm = dict[item], item
    return(itm)

def map_mgra_to_nodes(MGRA_contain_Node_file,MGRA_intersect_Node_file,nodes_fleetpy,NODE_MGRA_write_dir,MGRA_NODE_write_dir):
    MGRA_node_matching = OrderedDict()
    Node_MGRA_matching = OrderedDict()

    effective_rows = 0

    # MGRA_Node_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/MGRA_nodes_mapping"
    # MGRA_contain_Node_file = os.path.join(MGRA_Node_folder, "MGRA_Contains_nodes.csv")
    with open(MGRA_contain_Node_file) as f_MGRA:
        csvreader = csv.DictReader(f_MGRA)
        for data in csvreader:
            # MGRA	FNODE	TNODE
            #         print("data",data)
            MGRA = int(data["MGRA"])
            if data["FNODE"] != "":
                # if FNODE

                FNODE = int(data["FNODE"])
                TNODE = int(data["TNODE"])
                if (FNODE+TNODE)>0:
                    effective_rows += 1
                    if MGRA not in MGRA_node_matching:
                        MGRA_node_matching[MGRA] = []
                    if FNODE not in MGRA_node_matching[MGRA]:
                        MGRA_node_matching[MGRA].append(FNODE)
                    if TNODE not in MGRA_node_matching[MGRA]:
                        MGRA_node_matching[MGRA].append(TNODE)

                    if FNODE not in Node_MGRA_matching:
                        Node_MGRA_matching[FNODE] = MGRA
                    if TNODE not in Node_MGRA_matching:
                        Node_MGRA_matching[TNODE] = MGRA
            else:
                continue

    f_MGRA.close()
    print("number of effective rows:", effective_rows)
    tot_num_node = 0
    for MGRA in MGRA_node_matching:
        num_nodes = len(MGRA_node_matching[MGRA])
        tot_num_node += num_nodes

    MGRA_NODE_List = []
    for node in Node_MGRA_matching:
        MGRA = Node_MGRA_matching[node]
        if MGRA not in MGRA_NODE_List:
            MGRA_NODE_List.append(MGRA)
    print("num of MGRA:", len(MGRA_node_matching))
    print("total number of nodes in MGRA dictionary:", tot_num_node)
    print("num of nodes:", len(Node_MGRA_matching))
    print("total number of MGRA in node dictionary:", len(MGRA_NODE_List))

    # MGRA_intersect_Node_file = os.path.join(MGRA_Node_folder, "MGRA_Nodes_match.csv")
    effective_rows = 0
    NODE_MGRA_Occurence_dict = OrderedDict()
    with open(MGRA_intersect_Node_file) as f_MGRA:
        csvreader = csv.DictReader(f_MGRA)
        for data in csvreader:
            if data["FNODE"] != "":
                effective_rows += 1

                MGRA = int(data["MGRA"])
                if MGRA>0:
                    FNODE = int(data["FNODE"])
                    TNODE = int(data["TNODE"])
                    if FNODE not in Node_MGRA_matching:
                        if FNODE not in NODE_MGRA_Occurence_dict:
                            NODE_MGRA_Occurence_dict[FNODE] = []
                            NODE_MGRA_Occurence_dict[FNODE].append(MGRA)
                        else:
                            NODE_MGRA_Occurence_dict[FNODE].append(MGRA)

                    if TNODE not in Node_MGRA_matching:
                        if TNODE not in NODE_MGRA_Occurence_dict:
                            NODE_MGRA_Occurence_dict[TNODE] = []
                            NODE_MGRA_Occurence_dict[TNODE].append(MGRA)
                        else:
                            NODE_MGRA_Occurence_dict[TNODE].append(MGRA)
            else:
                continue

    f_MGRA.close()

    for node in NODE_MGRA_Occurence_dict:
        node_list = NODE_MGRA_Occurence_dict[node]
        most_frequent_MGRA = most_frequent(node_list)
        if node not in Node_MGRA_matching:
            Node_MGRA_matching[node] = most_frequent_MGRA
        if most_frequent_MGRA not in MGRA_node_matching:
            MGRA_node_matching[most_frequent_MGRA] = []
            MGRA_node_matching[most_frequent_MGRA].append(node)
        else:
            MGRA_node_matching[most_frequent_MGRA].append(node)

    print("number of effective rows:", effective_rows)
    tot_num_node = 0
    for MGRA in MGRA_node_matching:
        num_nodes = len(MGRA_node_matching[MGRA])
        tot_num_node += num_nodes

    MGRA_NODE_List = []
    for node in Node_MGRA_matching:
        MGRA = Node_MGRA_matching[node]
        if MGRA not in MGRA_NODE_List:
            MGRA_NODE_List.append(MGRA)
    print("num of MGRA:", len(MGRA_node_matching))
    print("total number of nodes in MGRA dictionary:", tot_num_node)
    print("num of nodes:", len(Node_MGRA_matching))
    print("total number of MGRA in node dictionary:", len(MGRA_NODE_List))

    MGRA_NODE_match_new = OrderedDict()
    for node in Node_MGRA_matching:
        MGRA = Node_MGRA_matching[node]
        try:
            node_id_fleetpy = nodes_fleetpy[node]
        except:
            print("node",node,"Node_MGRA_matching",Node_MGRA_matching)
        if MGRA not in MGRA_NODE_match_new:
            MGRA_NODE_match_new[MGRA] = []
            MGRA_NODE_match_new[MGRA].append(node_id_fleetpy)
        else:
            MGRA_NODE_match_new[MGRA].append(node_id_fleetpy)

    print("total number of MGRA in node dictionary:", len(MGRA_NODE_match_new))

    # NODE_MGRA_write_dir = os.path.join(MGRA_Node_folder, "Nodes_MGRA_mapping.csv")
    with open(NODE_MGRA_write_dir, 'w+', newline='') as csvfile:
        fieldnames = ["node", "MGRA"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for node in Node_MGRA_matching:
            MGRA = Node_MGRA_matching[node]
            node_id_fleetpy = nodes_fleetpy[node]
            writer.writerow({'node': node_id_fleetpy, 'MGRA': MGRA})

    csvfile.close()

    # MGRA_NODE_write_dir = os.path.join(MGRA_Node_folder, "MGRA_Nodes_mapping.csv")
    with open(MGRA_NODE_write_dir, 'w+', newline='') as csvfile:
        fieldnames = ["MGRA", "nodes"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for MGRA in MGRA_NODE_match_new:
            nodes = MGRA_NODE_match_new[MGRA]
            writer.writerow({'MGRA': MGRA, 'nodes': nodes})

    csvfile.close()

def create_tt_demand_file(trip_file,NODE_MGRA_write_dir,total_demand_file,demand_nodes):

    # fieldnames = ["depart_hr", "second", 'rq_time', 'start (MGRA)', 'end (MGRA)', 'mode']
    MGRA_demand_Node_dict=OrderedDict()
    with open(NODE_MGRA_write_dir) as f:
        csvreader = csv.DictReader(f)
        for data in csvreader:
            # depart	origin	destination	trip_mode
            node = int(data["node"])
            MGRA = int(data["MGRA"])
            if node in demand_nodes:
                if MGRA not in MGRA_demand_Node_dict:
                    MGRA_demand_Node_dict[MGRA]=[]
                    MGRA_demand_Node_dict[MGRA].append(node)
                else:
                    MGRA_demand_Node_dict[MGRA].append(node)
    f.close()

    with open(total_demand_file, 'w+', newline='') as csvfile:
        fieldnames = ['rq_time', 'start', 'end', 'request_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        with open(trip_file) as f_MGRA_trip:
            csvreader = csv.DictReader(f_MGRA_trip)
            sortedlist = sorted(csvreader, key=lambda row: (row['rq_time']), reverse=False)

            # rq_time	start	end	request_id	bt_c_0	bt_c_ivt	bt_c_gas	bt_t_0	bt_t_wk	bt_t_wt	bt_m_ivt	bt_f_ivt	bt_f_trfer	bt_t_fr
            #  fieldnames = ["depart_hr","second",'rq_time', 'start (MGRA)', 'end (MGRA)', 'mode']
            request_id = 0
            for data in sortedlist:
                rq_time=int(data["rq_time"])
                start_MGRA = int(data["start (MGRA)"])
                end_MGRA = int(data["end (MGRA)"])
                if start_MGRA in MGRA_demand_Node_dict:
                    start_node_list=MGRA_demand_Node_dict[start_MGRA]
                    start_node = random.choice(start_node_list)
                else:
                    start_node = random.choice(demand_nodes)

                if end_MGRA in MGRA_demand_Node_dict:
                    end_node_list = MGRA_demand_Node_dict[end_MGRA]
                    end_node = random.choice(end_node_list)
                else:
                    end_node = random.choice(demand_nodes)

                writer.writerow({'rq_time': rq_time, 'start': start_node, 'end': end_node, 'request_id': request_id})
                request_id += 1
        f_MGRA_trip.close()

    csvfile.close()





def generate_1_per_demand():
    mtsm.not_self_contained("generate_1_per_demand (preprocessing)")
    # Generate 10% demand
    debug_input_demand = os.path.join(network_folder, "debug_trips_nodes_study_area_with_beta.csv")
    with open(debug_input_demand, 'w+', newline='') as csvfile:
        fieldnames = ['rq_time', 'start', 'end', 'request_id', "bt_c_0", "bt_c_ivt", "bt_c_gas", "bt_t_0", "bt_t_wk",
                      "bt_t_wt", "bt_m_ivt", "bt_f_ivt", "bt_f_trfer", "bt_t_fr"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        with open(request_file) as f:
            csvreader = csv.DictReader(f)
            # depart_time	start	end	trip_id

            for data in csvreader:
                #             print(data)
                rq_time = int(data["rq_time"])
                start = int(data["start"])
                end = int(data["end"])
                request_id = int(float(data["request_id"]))
                # read car mode attributes
                bt_c_0 = float(data["bt_c_0"])
                bt_c_ivt = float(data["bt_c_ivt"])
                bt_c_gas = float(data["bt_c_gas"])
                # read transit mode attributes
                bt_t_0 = float(data["bt_t_0"])
                bt_t_wk = float(data["bt_t_wk"])
                bt_t_wt = float(data["bt_t_wt"])
                bt_m_ivt = float(data["bt_m_ivt"])
                bt_f_ivt = float(data["bt_f_ivt"])
                bt_f_trfer = float(data["bt_f_trfer"])
                bt_t_fr = float(data["bt_t_fr"])

                ran_num = random.random()
                if ran_num <= 0.01:
                    writer.writerow({'rq_time': rq_time, 'start': start, 'end': end, 'request_id': request_id,
                                     "bt_c_0": bt_c_0, "bt_c_ivt": bt_c_ivt, "bt_c_gas": bt_c_gas, "bt_t_0": bt_t_0,
                                     "bt_t_wk": bt_t_wk, "bt_t_wt": bt_t_wt, "bt_m_ivt": bt_m_ivt, "bt_f_ivt": bt_f_ivt,
                                     "bt_f_trfer": bt_f_trfer, "bt_t_fr": bt_t_fr})
        f.close()
    csvfile.close()



def create_user_profile(input_trip_file,demand_profile_beta_file,debug_demand_profile):
    # Generate 10% demand

    # total_demand_file = os.path.join(network_folder, "trips_nodes_study_area.csv")
    # new_input_demand = os.path.join(network_folder, "trips_nodes_study_area_with_beta.csv")

    with open(demand_profile_beta_file, 'w+', newline='') as csvfile:
        fieldnames = ['rq_time', 'start', 'end', 'request_id', "bt_c_0", "bt_c_ivt", "bt_c_gas", "bt_t_0", "bt_t_wk",
                      "bt_t_wt", "bt_m_ivt", "bt_f_ivt", "bt_f_trfer", "bt_t_fr"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        with open(debug_demand_profile, 'w+', newline='') as csvfile_debug:
            fieldnames = ['rq_time', 'start', 'end', 'request_id', "bt_c_0", "bt_c_ivt", "bt_c_gas", "bt_t_0","bt_t_wk","bt_t_wt", "bt_m_ivt", "bt_f_ivt", "bt_f_trfer", "bt_t_fr"]
            writer_debug = csv.DictWriter(csvfile_debug, fieldnames=fieldnames)
            writer_debug.writeheader()

            with open(input_trip_file) as f:
                csvreader = csv.DictReader(f)
                # depart_time	start	end	trip_id

                for data in csvreader:
                    #             print(data)
                    rq_time = int(data["rq_time"])
                    request_id = float(data["request_id"])
                    start_node = int(data["start"])
                    end_node = int(data["end"])

                    ##specify customers characteristics
                    # "bt_c_0","bt_c_ivt","bt_c_gas","bt_t_0","bt_t_wk","bt_t_wt","bt_m_ivt","bt_f_ivt","bt_f_trfer","bt_t_fr"]

                    bt_c_0 = max(np.random.normal(0, 0),
                                 0)  # beta_car_0 - alternative specific constant as a reference mode
                    bt_c_ivt = max(np.random.normal(0.103, 0.047), 0.01)  # beta_car_ivt
                    bt_c_gas = max(np.random.normal(0.554, 0.377), 0.05)  # beta_car_ivt

                    bt_t_0 = max(np.random.normal(0.432, 0.04),
                                 0)  # beta_car_0 - alternative specific constant as a reference mode
                    bt_t_wk = max(np.random.normal(0.164, 0.140), 0.01)  # beta_t_walking
                    bt_t_wt = max(np.random.normal(0.104, 0.022), 0.01)  # beta_t_waiting

                    bt_m_ivt = max(np.random.normal(0.134, 0.022), 0.01)  # bt_m_ivt
                    bt_f_ivt = max(np.random.normal(0.116, 0.029), 0.01)  # bt_f_ivt
                    bt_f_trfer = max(np.random.normal(0.504, 0.022), 0.01)  # bt_f_trfer

                    bt_t_fr = max(np.random.normal(0.554, 0.377), 0.05)  # bt_f_trfer



                    writer.writerow({'rq_time': rq_time, 'start': start_node, 'end': end_node, 'request_id': request_id,
                                     "bt_c_0": bt_c_0, "bt_c_ivt": bt_c_ivt, "bt_c_gas": bt_c_gas, "bt_t_0": bt_t_0,
                                     "bt_t_wk": bt_t_wk, "bt_t_wt": bt_t_wt, "bt_m_ivt": bt_m_ivt, "bt_f_ivt": bt_f_ivt,
                                     "bt_f_trfer": bt_f_trfer, "bt_t_fr": bt_t_fr})
                    ran_num = random.random()
                    if ran_num <= 0.01:
                        writer_debug.writerow({'rq_time': rq_time, 'start': start_node, 'end': end_node, 'request_id': request_id,
                                     "bt_c_0": bt_c_0, "bt_c_ivt": bt_c_ivt, "bt_c_gas": bt_c_gas, "bt_t_0": bt_t_0,
                                     "bt_t_wk": bt_t_wk, "bt_t_wt": bt_t_wt, "bt_m_ivt": bt_m_ivt, "bt_f_ivt": bt_f_ivt,
                                     "bt_f_trfer": bt_f_trfer, "bt_t_fr": bt_t_fr})
            f.close()

        csvfile_debug.close()
    csvfile.close()


def select_demand_nodes():
    mtsm.not_self_contained("select_demand_nodes (preprocessing)")
    demand_nodes_check = []
    with open(new_input_demand) as f:
        csvreader = csv.DictReader(f)
        # depart_time	start	end	trip_id

        for data in csvreader:
            #             print(data)
            rq_time = int(data["rq_time"])
            request_id = int(data["request_id"])
            start_node = int(data["start"])
            end_node = int(data["end"])

            if start_node not in demand_nodes_check:
                demand_nodes_check.append(start_node)
            if end_node not in demand_nodes_check:
                demand_nodes_check.append(end_node)
    f.close()

    print("number of demand ndoes:", len(demand_nodes_check))


def modify_ind_parameter(study_area,debug_mode,bt_c_0_m=0,bt_c_ivt_m = 0.103,
                         bt_c_gas_m = 0.554,bt_t_0_m = 0.432,bt_t_wk_m = 0.164,bt_m_wt_m=0.104,bt_f_wt_m=0.104,bt_m_ivt_m = 0.134,
                         bt_f_ivt_m = 0.116,bt_f_trfer_m = 0.504,bt_t_fr_m = 0.554):

    mtsm.not_self_contained("modify_ind_parameter (preprocessing)")
    #D:\Siwei_Micro_Transit\Data\0719_input\lemon_grove\demand_folder
    if study_area=="lemon_grove":
        # STALE: new_lemon_grove_demand_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/demand_folder"
        if debug_mode==True:
            debug="debug_"
            demand_profile_beta_file = os.path.join(lemon_grove_demand_folder,"%s_%strips_nodes_study_area_with_beta.csv" % (str(study_area),str(debug)))
            #lemon_grove_debug_trips_nodes_study_area_with_beta.csv
            demand_profile_beta_file_new = os.path.join(new_lemon_grove_demand_folder, "%s_%strips_nodes_study_area_with_beta.csv" % (str(study_area),str(debug)))
        else:
            debug = ""
            demand_profile_beta_file_new=os.path.join(new_lemon_grove_demand_folder,"%s_%strips_nodes_study_area_with_beta.csv" % (str(study_area),str(debug)))
            demand_profile_beta_file = os.path.join(lemon_grove_demand_folder, "%s_%strips_nodes_study_area_with_beta.csv" % (str(study_area),str(debug)))


    with open(demand_profile_beta_file_new, 'w+', newline='') as csvfile_modify:
        fieldnames = ['rq_time', 'start', 'end', 'request_id', "bt_c_0", "bt_c_ivt", "bt_c_gas", "bt_t_0","bt_t_wk","bt_m_wt","bt_f_wt", "bt_m_ivt", "bt_f_ivt", "bt_f_trfer", "bt_t_fr"]
        writer = csv.DictWriter(csvfile_modify, fieldnames=fieldnames)
        writer.writeheader()

        with open(demand_profile_beta_file) as f:
            csvreader = csv.DictReader(f)
            # depart_time	start	end	trip_id

            for data in csvreader:
                #             print(data)
                rq_time = int(data["rq_time"])
                request_id = float(data["request_id"])
                start_node = int(data["start"])
                end_node = int(data["end"])

                ##specify customers characteristics
                # "bt_c_0","bt_c_ivt","bt_c_gas","bt_t_0","bt_t_wk","bt_t_wt","bt_m_ivt","bt_f_ivt","bt_f_trfer","bt_t_fr"]

                bt_c_0 = max(np.random.normal(bt_c_0_m, 0),
                             0)  # beta_car_0 - alternative specific constant as a reference mode
                bt_c_ivt = max(np.random.normal(bt_c_ivt_m, 0.047), 0.01)  # beta_car_ivt
                bt_c_gas = max(np.random.normal(bt_c_gas_m, 0.377), 0.05)  # beta_car_ivt

                bt_t_0 = max(np.random.normal(bt_t_0_m, 0.04), 0)  # beta_car_0 - alternative specific constant as a reference mode
                bt_t_wk = max(np.random.normal(bt_t_wk_m, 0.140), 0.01)  # beta_t_walking
                # bt_t_wt = max(np.random.normal(bt_t_wt_m, 0.022), 0.01)  # beta_t_waiting
                bt_m_wt = max(np.random.normal(bt_m_wt_m, 0.022), 0.01)  # beta_microtransit_waiting
                bt_f_wt = max(np.random.normal(bt_f_wt_m, 0.022), 0.01)  # beta_fixed_route_transit_waiting

                bt_m_ivt = max(np.random.normal(bt_m_ivt_m, 0.022), 0.01)  # bt_m_ivt
                bt_f_ivt = max(np.random.normal(bt_f_ivt_m, 0.029), 0.01)  # bt_f_ivt
                bt_f_trfer = max(np.random.normal(bt_f_trfer_m, 0.022), 0.01)  # bt_f_trfer

                bt_t_fr = max(np.random.normal(bt_t_fr_m, 0.377), 0.05)  # bt_f_trfer


                writer.writerow({'rq_time': rq_time, 'start': start_node, 'end': end_node, 'request_id': request_id,
                                 "bt_c_0": bt_c_0, "bt_c_ivt": bt_c_ivt, "bt_c_gas": bt_c_gas, "bt_t_0": bt_t_0,
                                 "bt_t_wk": bt_t_wk, "bt_m_wt":bt_m_wt,"bt_f_wt":bt_f_wt, "bt_m_ivt": bt_m_ivt, "bt_f_ivt": bt_f_ivt,
                                 "bt_f_trfer": bt_f_trfer, "bt_t_fr": bt_t_fr})
                ran_num = random.random()
        f.close()

    csvfile_modify.close()


def TRPartA_demand_files(study_area,debug_mode):
    mtsm.not_self_contained("TRPartA_demand_files (preprocessing)")

    # STALE: trip_file_folder="D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/demand_data/%s" % (study_area)
    trip_file_dir=os.path.join(trip_file_folder,"%s_trips.csv" % (study_area))
    new_trip_file_dir = os.path.join(trip_file_folder, "%s_trips_new.csv" % (study_area))

    if debug_mode == True:
        debug = "debug_"
        demand_profile_beta_file = os.path.join(trip_file_folder,"%s_%strips_nodes_study_area_with_beta_old.csv" % (str(study_area), str(debug)))
        new_demand_profile_beta_file = os.path.join(trip_file_folder, "%s_%strips_nodes_study_area_with_beta.csv" % (str(study_area), str(debug)))
        # demand_profile_beta_file_new = os.path.join(trip_file_folder,"%s_%strips_nodes_study_area_with_beta.csv" % (str(study_area), str(debug)))
    else:
        debug = ""
        # demand_profile_beta_file_new = os.path.join(trip_file_folder,"%s_%strips_nodes_study_area_with_beta.csv" % (str(study_area), str(debug)))
        demand_profile_beta_file = os.path.join(trip_file_folder,"%s_%strips_nodes_study_area_with_beta_old.csv" % (str(study_area), str(debug)))
        new_demand_profile_beta_file = os.path.join(trip_file_folder, "%s_%strips_nodes_study_area_with_beta.csv" % (str(study_area), str(debug)))



    if study_area=="lemon_grove":
        # STALE: MGRA_Node_folder = "D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove/MGRA_Node_Mapping"
        # STALE: study_area_network_folder = "D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove/Network_folder"
        mean_income = 70679.3

    pre_node_dir = os.path.join(study_area_network_folder, "pre_nodes.csv")
    pre_edges_dir = os.path.join(study_area_network_folder, "pre_edges.csv")
    node_dir = os.path.join(study_area_network_folder, "nodes.csv")
    edges_dir = os.path.join(study_area_network_folder, "edges.csv")
    raw_fleetpy_nodes_dict, demand_nodes = p_n.write_node_edge_from_pre_node_edge(node_dir, edges_dir,pre_node_dir, pre_edges_dir)
    NODE_MGRA_write_dir = os.path.join(MGRA_Node_folder, "Nodes_MGRA_mapping.csv")
    MGRA_demand_Node_dict=OrderedDict()
    with open(NODE_MGRA_write_dir) as f:
        csvreader = csv.DictReader(f)
        for data in csvreader:
            # depart	origin	destination	trip_mode
            node = int(data["node"])
            MGRA = int(data["MGRA"])
            if node in demand_nodes:
                if MGRA not in MGRA_demand_Node_dict:
                    MGRA_demand_Node_dict[MGRA]=[]
                    MGRA_demand_Node_dict[MGRA].append(node)
                else:
                    MGRA_demand_Node_dict[MGRA].append(node)
    f.close()


    with open(demand_profile_beta_file, 'w+', newline='') as csvfile_modify:
        fieldnames = ['rq_time', 'start', 'end', 'request_id', "bt_c_0", "bt_c_ivt", "bt_c_gas", "bt_t_0", "bt_t_wk",
                      "bt_m_wt", "bt_f_wt", "bt_m_ivt", "bt_f_ivt", "bt_f_trfer", "bt_t_fr","income","transit_15min_acc","transit_pass"]
        writer = csv.DictWriter(csvfile_modify, fieldnames=fieldnames)
        writer.writeheader()
        request_id=0
        with open(trip_file_dir) as f:
            csvreader = csv.DictReader(f)
            # depart_time	start	end	trip_id

            for data in csvreader:
                #             print(data)
                depart=int(float(data["depart"]))
                second = int(round(random.random() * 3600, 0))
                rq_time = depart * 3600 + second
                # rq_time = int(data["depart"])
                # request_id = float(data["request_id"])
                start_MGRA = int(float(data["origin"]))
                end_MGRA = int(float(data["destination"]))

                if start_MGRA in MGRA_demand_Node_dict:
                    start_node_list = MGRA_demand_Node_dict[start_MGRA]
                    start_node = random.choice(start_node_list)
                else:
                    start_node = random.choice(demand_nodes)

                if end_MGRA in MGRA_demand_Node_dict:
                    end_node_list = MGRA_demand_Node_dict[end_MGRA]
                    end_node = random.choice(end_node_list)
                else:
                    end_node = random.choice(demand_nodes)

                ##specify customers characteristics
                # "bt_c_0","bt_c_ivt","bt_c_gas","bt_t_0","bt_t_wk","bt_t_wt","bt_m_ivt","bt_f_ivt","bt_f_trfer","bt_t_fr"]
                income=float(data["income"])

                if study_area=="lemon_grove":

                    bt_c_0_m = 0  # beta_car_0 - alternative specific constant as a reference mode
                    bt_c_ivt_m = 0.198  # beta_car_ivt
                    bt_c_gas_m = 0.579 * (mean_income /income) # beta_car_GAS

                    bt_t_0_m = 0.242  # beta_car_0 - alternative specific constant as a reference mode
                    bt_t_wk_m = 0.349  # beta_t_walking
                    bt_m_wt_m = 0.094  # beta_microtransit_waiting
                    bt_f_wt_m = 0.082  # beta_fixed_route_transit_waiting

                    bt_m_ivt_m = 0.104  # bt_m_ivt
                    bt_f_ivt_m = 0.106  # bt_f_ivt
                    bt_f_trfer_m = 0.504  # bt_f_trfer

                    bt_t_fr_m = bt_c_gas_m  # bt_f_trfer


                ##########

                bt_c_0 = max(np.random.normal(bt_c_0_m, 0),0)  # beta_car_0 - alternative specific constant as a reference mode
                bt_c_ivt = max(np.random.normal(bt_c_ivt_m, 0.047), 0.01)  # beta_car_ivt
                bt_c_gas = max(np.random.normal(bt_c_gas_m, 0.377), 0.05)  # beta_car_ivt

                bt_t_0 = max(np.random.normal(bt_t_0_m, 0.04),0)  # beta_car_0 - alternative specific constant as a reference mode
                bt_t_wk = max(np.random.normal(bt_t_wk_m, 0.140), 0.01)  # beta_t_walking
                # bt_t_wt = max(np.random.normal(bt_t_wt_m, 0.022), 0.01)  # beta_t_waiting
                bt_m_wt = max(np.random.normal(bt_m_wt_m, 0.022), 0.01)  # beta_microtransit_waiting
                bt_f_wt = max(np.random.normal(bt_f_wt_m, 0.022), 0.01)  # beta_fixed_route_transit_waiting

                bt_m_ivt = max(np.random.normal(bt_m_ivt_m, 0.022), 0.01)  # bt_m_ivt
                bt_f_ivt = max(np.random.normal(bt_f_ivt_m, 0.029), 0.01)  # bt_f_ivt
                bt_f_trfer = max(np.random.normal(bt_f_trfer_m, 0.022), 0.01)  # bt_f_trfer

                bt_t_fr = bt_c_gas  # bt_t_fr  transit fare should be the same as the gas

                # income = float(data["income"])

                transit_15min_acc=float(data["emp_15min"])
                ran_num = random.random()
                if ran_num<=0.1:
                    transit_pass=1
                else:
                    transit_pass = 0
                ran_num_2 = random.random()
                if debug_mode==True:
                    if ran_num_2<=0.05:
                        writer.writerow({'rq_time': rq_time, 'start': start_node, 'end': end_node, 'request_id': request_id,
                                     "bt_c_0": bt_c_0, "bt_c_ivt": bt_c_ivt, "bt_c_gas": bt_c_gas, "bt_t_0": bt_t_0,
                                     "bt_t_wk": bt_t_wk, "bt_m_wt": bt_m_wt, "bt_f_wt": bt_f_wt, "bt_m_ivt": bt_m_ivt,
                                     "bt_f_ivt": bt_f_ivt,
                                     "bt_f_trfer": bt_f_trfer, "bt_t_fr": bt_t_fr, "income": income,
                                     "transit_15min_acc": transit_15min_acc,
                                     "transit_pass": transit_pass})
                else:
                    writer.writerow({'rq_time': rq_time, 'start': start_node, 'end': end_node, 'request_id': request_id,
                                 "bt_c_0": bt_c_0, "bt_c_ivt": bt_c_ivt, "bt_c_gas": bt_c_gas, "bt_t_0": bt_t_0,
                                 "bt_t_wk": bt_t_wk, "bt_m_wt": bt_m_wt, "bt_f_wt": bt_f_wt, "bt_m_ivt": bt_m_ivt,
                                 "bt_f_ivt": bt_f_ivt,
                                 "bt_f_trfer": bt_f_trfer, "bt_t_fr": bt_t_fr,"income":income,"transit_15min_acc":transit_15min_acc,
                                 "transit_pass":transit_pass})


                request_id+=1
        f.close()

    csvfile_modify.close()

    # Sort the CSV file
    with open(demand_profile_beta_file, 'r', newline='') as f_input:
        csv_input = csv.DictReader(f_input)
        data = sorted(csv_input, key=lambda row: (row['rq_time'], row['start']))

    with open(new_demand_profile_beta_file, 'w', newline='') as f_output:
        csv_output = csv.DictWriter(f_output, fieldnames=csv_input.fieldnames)
        csv_output.writeheader()
        request_id=0
        for row in data:
            rq_time = int(row["rq_time"])
            start = int(row["start"])
            end = int(row["end"])
            request_id = int(request_id)
            # read car mode attributes
            bt_c_0 = float(row["bt_c_0"])
            bt_c_ivt = float(row["bt_c_ivt"])
            bt_c_gas = float(row["bt_c_gas"])
            # read transit mode attributes
            bt_t_0 = float(row["bt_t_0"])
            bt_t_wk = float(row["bt_t_wk"])
            bt_m_wt = float(row["bt_m_wt"])
            bt_f_wt = float(row["bt_f_wt"])
            bt_m_ivt = float(row["bt_m_ivt"])
            bt_f_ivt = float(row["bt_f_ivt"])
            bt_f_trfer = float(row["bt_f_trfer"])
            bt_t_fr = float(row["bt_t_fr"])
            income = float(row["income"])
            transit_15min_acc = float(row["transit_15min_acc"])
            transit_pass = float(row["transit_pass"])
            csv_output.writerow({'rq_time': rq_time, 'start': start, 'end': end, 'request_id': request_id,
                                 "bt_c_0": bt_c_0, "bt_c_ivt": bt_c_ivt, "bt_c_gas": bt_c_gas, "bt_t_0": bt_t_0,
                                 "bt_t_wk": bt_t_wk, "bt_m_wt": bt_m_wt, "bt_f_wt": bt_f_wt, "bt_m_ivt": bt_m_ivt,
                                 "bt_f_ivt": bt_f_ivt,
                                 "bt_f_trfer": bt_f_trfer, "bt_t_fr": bt_t_fr,"income":income,"transit_15min_acc":transit_15min_acc,
                                 "transit_pass":transit_pass})
            request_id+=1
    aaa=0
    return aaa


def sample_20_percent(folder_dir,study_area):
    mtsm.not_self_contained("sample_20_percent (preprocessing)")
    # STALE: folder_dir="D:\Siwei_Micro_Transit\Bayesian_Optimization\demand_data\%s" % str(study_area)
    full_demand_file_dir=os.path.join(folder_dir,"%s_trips_nodes_study_area_with_beta_old.csv" % str(study_area))
    sample_demand_file_dir=os.path.join(folder_dir,"%s_trips_nodes_study_area_with_beta.csv" % str(study_area))
    df=pd.read_csv(full_demand_file_dir)
    df_new=df.sample(frac=0.25, replace=False, random_state=1)
    df_new.to_csv(sample_demand_file_dir, index=False)


# make_time_sampler and synthesize_requests_with_trend_time ("Ritun added", for FleetPy demand upscaling) moved
# unchanged to mtsm_model/helpers/synthetic_demand.py on 2026-11-23 (I-14).

if __name__ == '__main__':

    create_from_scratch=False
    test_area = ["downtown_sd","lemon_grove"]

    debug_mode_list=[True,False]

    # STALE: folder_dir = "D:\Siwei_Micro_Transit\Bayesian_Optimization\demand_data\lemon_grove"
    folder_dir = None  # sample_20_percent() stops: its folder is outside the codebase
    study_area = "lemon_grove"
    sample_20_percent(folder_dir,study_area)

    '''
    for study_area in test_area:
        for debug_mode in debug_mode_list:
            TRPartA_demand_files(study_area, debug_mode)
            
    '''
            # if study_area=="lemon_grove":
            #
            #     bt_c_0_m = 0  # beta_car_0 - alternative specific constant as a reference mode
            #     bt_c_ivt_m = 0.198  # beta_car_ivt
            #     bt_c_gas_m = 0.579  # beta_car_GAS
            #
            #     bt_t_0_m = 0.292  # beta_car_0 - alternative specific constant as a reference mode
            #     bt_t_wk_m = 0.329  # beta_t_walking
            #     bt_m_wt_m = 0.094  # beta_microtransit_waiting
            #     bt_f_wt_m = 0.082  # beta_fixed_route_transit_waiting
            #
            #     bt_m_ivt_m = 0.104  # bt_m_ivt
            #     bt_f_ivt_m = 0.106  # bt_f_ivt
            #     bt_f_trfer_m = 0.504  # bt_f_trfer
            #
            #     bt_t_fr_m = 0.554  # bt_f_trfer
            #
            #     if create_from_scratch ==True:
            #         lemon_grove_MGRA = os.path.join(lemon_grove_demand_folder, "Lemon_grove_MGRA.csv")
            #         large_MGRA_trip_file = os.path.join(lemon_grove_demand_folder, "larger_SANDAG_trips_in_MGRA.csv")
            #         lemon_grove_trip_file = os.path.join(lemon_grove_demand_folder, "lemon_grove_trips_in_MGRA.csv")
            #         # select_trips(lemon_grove_MGRA,large_MGRA_trip_file,lemon_grove_trip_file)
            #
            #         lenmon_grove_network_folder = "D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove/Network_folder"
            #         raw_network_file= os.path.join(lenmon_grove_network_folder,"Lemon_grove_raw_edges.csv")
            #         pre_node_dir = os.path.join(lenmon_grove_network_folder, "pre_nodes.csv")
            #         pre_edges_dir = os.path.join(lenmon_grove_network_folder, "pre_edges.csv")
            #
            #         p_n.create_network_from_raw_edges(raw_network_file,pre_node_dir,pre_edges_dir)
            #
            #         node_dir = os.path.join(lenmon_grove_network_folder, "nodes.csv")
            #         edges_dir = os.path.join(lenmon_grove_network_folder, "edges.csv")
            #         raw_fleetpy_nodes_dict,fleetpy_demand_node=p_n.write_node_edge_from_pre_node_edge(node_dir,edges_dir,pre_node_dir,pre_edges_dir)
            #
            #         MGRA_Node_folder = "D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove/MGRA_Node_Mapping"
            #         MGRA_contain_Node_file = os.path.join(MGRA_Node_folder, "MGRA_Roads_contains.csv")
            #         MGRA_intersect_Node_file = os.path.join(MGRA_Node_folder, "Roads_MGRA_intersects.csv")
            #         # NODE_MGRA_write_dir = os.path.join(MGRA_Node_folder, "Nodes_MGRA_mapping.csv")
            #         NODE_MGRA_write_dir = os.path.join(MGRA_Node_folder, "Nodes_MGRA_mapping.csv")
            #         MGRA_NODE_write_dir = os.path.join(MGRA_Node_folder, "MGRA_Nodes_mapping.csv")
            #         map_mgra_to_nodes(MGRA_contain_Node_file, MGRA_intersect_Node_file, raw_fleetpy_nodes_dict, NODE_MGRA_write_dir,MGRA_NODE_write_dir)
            #
            #         total_demand_file = os.path.join(lemon_grove_demand_folder, "lemon_grove_trips_in_nodes.csv")
            #         create_tt_demand_file(lemon_grove_trip_file, NODE_MGRA_write_dir, total_demand_file, fleetpy_demand_node)
            #
            #         demand_profile_beta_file = os.path.join(lemon_grove_demand_folder,"demand_profile_lemon_grove_with_beta.csv")
            #         debug_demand_profile_beta_file = os.path.join(lemon_grove_demand_folder,"debug_demand_profile_lemon_grove_with_beta.csv")
            #
            #         create_user_profile(total_demand_file, demand_profile_beta_file,debug_demand_profile_beta_file)
            #     else:
            #         print("study_area",study_area,"debug_mode",debug_mode)
            #         modify_ind_parameter(study_area, debug_mode, bt_c_0_m=bt_c_0_m, bt_c_ivt_m=bt_c_ivt_m,
            #                              bt_c_gas_m=bt_c_gas_m, bt_t_0_m=bt_t_0_m, bt_t_wk_m=bt_t_wk_m,
            #                              bt_m_wt_m=bt_m_wt_m, bt_f_wt_m=bt_f_wt_m,bt_m_ivt_m=bt_m_ivt_m,
            #                              bt_f_ivt_m=bt_f_ivt_m, bt_f_trfer_m=bt_f_trfer_m, bt_t_fr_m=bt_t_fr_m)
            #
            #
            #
