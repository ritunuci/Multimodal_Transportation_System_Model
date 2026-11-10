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
from math import radians, cos, sin, asin, sqrt
import heapq
import datetime
import mtsm_paths as mtsm

from setuptools import setup
from Cython.Build import cythonize

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


class Node(object):
    """
    Class for handling node object in Transportation Networks

    Parameters
    ----------
    node_id:    int
                identifier of a node

    """

    def __init__(self, node_id=0, node_XCOORD=0, node_YCOORD=0, is_stop_only=False, census_tract=0, node_in_fleetpy=0,
                 is_demand_node=0):

        self.node_id = node_id
        self.node_XCOORD = node_XCOORD
        self.node_YCOORD = node_YCOORD
        self.is_stop_only = is_stop_only
        self.census_tract = census_tract
        self.node_in_fleetpy = node_in_fleetpy
        self.is_demand_node = is_demand_node

class Agent(object):

    def __init__(self, rq_id=0, rq_O=0, rq_D=0, rq_time=0, bt_c_0=0, bt_c_ivt=0,bt_c_gas=0,bt_t_0=0, bt_t_wk=0, bt_m_wt=0,bt_f_wt=0,bt_m_ivt=0,
                 bt_f_ivt=0,bt_f_trfer=0,bt_t_fr=0,income=0,transit_15min_acc=0,transit_pass=0,parking_dur=0):
    # def __init__(self, rq_id=0, rq_O=0, rq_D=0, rq_time=0, bt_c_0=0, bt_c_ivt=0, bt_c_gas=0, bt_t_0=0, bt_t_wk=0,
    #              bt_m_wt=0, bt_f_wt=0, bt_m_ivt=0,
    #              bt_f_ivt=0, bt_f_trfer=0, bt_t_fr=0, income=0, transit_15min_acc=0, transit_pass=0):

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
        # self.bt_t_wt = bt_t_wt
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


def read_request(request_file):
    with open(request_file) as f:
        csvreader = csv.DictReader(f)
        agent_list = []

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
            # bt_t_wt = float(data["bt_t_wt"])
            bt_m_wt = float(data["bt_m_wt"])
            bt_f_wt = float(data["bt_f_wt"])

            bt_m_ivt = float(data["bt_m_ivt"])
            bt_f_ivt = float(data["bt_f_ivt"])
            bt_f_trfer = float(data["bt_f_trfer"])
            bt_t_fr = float(data["bt_t_fr"])

            income = int(float(data["income"]))
            transit_15min_acc = float(data["transit_15min_acc"])
            transit_pass = int(float(data["transit_pass"]))
            parking_dur = float(data["parking_dur_min"])

            agent_ = Agent(rq_id=request_id, rq_O=start, rq_D=end, rq_time=rq_time, bt_c_0=bt_c_0, bt_c_ivt=bt_c_ivt,
                           bt_c_gas=bt_c_gas,bt_t_0=bt_t_0, bt_t_wk=bt_t_wk, bt_m_wt=bt_m_wt,bt_f_wt=bt_f_wt,bt_m_ivt=bt_m_ivt,
                          bt_f_ivt=bt_f_ivt,bt_f_trfer=bt_f_trfer, bt_t_fr=bt_t_fr,income=income,
                           transit_15min_acc=transit_15min_acc,transit_pass=transit_pass,parking_dur=parking_dur)
            # agent_ = Agent(rq_id=request_id, rq_O=start, rq_D=end, rq_time=rq_time, bt_c_0=bt_c_0, bt_c_ivt=bt_c_ivt,
            #                bt_c_gas=bt_c_gas, bt_t_0=bt_t_0, bt_t_wk=bt_t_wk, bt_m_wt=bt_m_wt, bt_f_wt=bt_f_wt,
            #                bt_m_ivt=bt_m_ivt,
            #                bt_f_ivt=bt_f_ivt, bt_f_trfer=bt_f_trfer, bt_t_fr=bt_t_fr, income=income,
            #                transit_15min_acc=transit_15min_acc, transit_pass=transit_pass)
            agent_list.append(agent_)

    return agent_list

def read_network(Network_file):
    with open(Network_file) as f:
        csvreader = csv.DictReader(f)
        nodes = {}
        links = []
        node_list = []

        for data in csvreader:
            origin_node = str(int(data["from_node"]))
            to_node = str(int(data["to_node"]))
            #                 length = float(data["distance"]) #length (ft)
            free_flow_travel_time_ = float(data["travel_time"])  # change mph to ft/s
            # link_type_ = str(data["link_type"])  # link_type
            l = Link(link_id=len(links),
                     from_node=origin_node, to_node=to_node, flow=float(0.0),
                     free_flow_travel_time=free_flow_travel_time_)
            links.append(l)

    graph = nx.DiGraph()

    for l in links:
        graph.add_edge(l.from_node, l.to_node, object=l, time=l.free_flow_time,link_type=l.link_type)

    return graph


def read_super_network(Network_file):
    with open(Network_file) as f:
        csvreader = csv.DictReader(f)
        nodes = {}
        links = []
        node_list = []

        for data in csvreader:
            origin_node = int(data["from_node"])
            to_node = int(data["to_node"])
            length = float(data["distance"]) #meter
            free_flow_travel_time_ = float(data["travel_time"])  # in second
            link_type_ = int(data["link_type"])  # link_type
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


def read_walking_network(Network_file):
    #     walking_network=os.path.join(network_folder,'network_edges.csv')
    #     with open(edges_dir,  "w+",newline='') as csvfile_edges:
    #     writer_edge = csv.writer(csvfile_edges, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     writer_edge.writerow(edge_fields)
    with open(Network_file) as f:
        csvreader = csv.DictReader(f)
        nodes = {}
        links = []
        node_list = []

        for data in csvreader:
            origin_node = str(int(data["from_node"]))
            to_node = str(int(data["to_node"]))
            length = float(data["distance"])  # meter
            speed = 1.6  # unit: meter/second
            free_flow_travel_time_ = length / speed  # second
            # link_type = str(data["link_type"])  # link_type
            l = Link(link_id=len(links),
                     from_node=origin_node, to_node=to_node, flow=float(0.0),
                     free_flow_travel_time=free_flow_travel_time_)
            links.append(l)
    f.close()
    graph = nx.DiGraph()

    for l in links:
        graph.add_edge(l.from_node, l.to_node, object=l, time=l.free_flow_time)

    return graph


def read_network_dist(Network_file):
    with open(Network_file) as f:
        csvreader = csv.DictReader(f)
        nodes = {}
        links = []
        node_list = []

        for data in csvreader:
            origin_node = str(int(data["from_node"]))
            to_node = str(int(data["to_node"]))
            #                 length = float(data["distance"]) #length (ft)
            free_flow_travel_time_ = float(data["distance"])  # read purely distance
            # link_type = str(data["link_type"])  # link_type
            l = Link(link_id=len(links),
                     from_node=origin_node, to_node=to_node, flow=float(0.0),
                     free_flow_travel_time=free_flow_travel_time_)
            links.append(l)

    graph = nx.DiGraph()

    for l in links:
        graph.add_edge(l.from_node, l.to_node, object=l, time=l.free_flow_time)

    return graph


def distance(lat1, lat2, lon1, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result in meters
    return (c * r) * 1000

def dijsktra_source_to_all(graph, initial,verbose=False):
    visited_temp = {initial: 0}  # dictionary: {node: the weights from source to a visited node}
    path = {}
    try:
        (nodes, edges) = (set(graph.nodes),graph.edges)
        costs = graph.costs
    except: #for NetworkX
        (nodes, edges) = (set(graph.nodes()), graph)  #Siwei: set - sort the graph.nodes
        costs=[]
#     num_nodes=0
    while nodes:
        if verbose == True:
            print("----------------------------------")
        min_node = None
        #find node with minimum distance value, and close this node
        for node in nodes:  #nodes is the list of unexplored nodes
            if node in visited_temp:  #if node is in the list of unexplored nodes and is visited (dist to that "node" is calculated)
                if min_node is None:
                    min_node = node
                    if verbose ==True:
                        print("Selected:", min_node, visited_temp[node])
                elif visited_temp[node] < visited_temp[min_node]:
                    min_node = node
                    if verbose ==True:
                        print("Selected:", min_node, visited_temp[node])
        if min_node is None:
            break


#         if min_node=='289':
#             verbose=False

        nodes.remove(min_node)  # find the min_node to close, remove the recent close node from the open node list
        permanent = visited_temp[min_node]
        if min_node in edges:
            for edge in edges[min_node]:
                # pre_route=..
                link_travel_time = graph.get_edge_data(min_node, edge)["object"].free_flow_time #Siwei: get link travel time
                # current_route=graph.get_edge_data(min_node, edge)["object"].route
                # if current_route!=pre_route:
                #     transfer_penalty=...

                temp = permanent + link_travel_time #Siwei: temp -> the criteria used for closing a node: travel time for UE

                if edge not in visited_temp or temp < visited_temp[edge]:
                    visited_temp[edge] = temp
                    path[edge] = (min_node, link_travel_time)

                if verbose ==True:
                     try:
                         print("Permanent:", permanent, "i:", min_node, "j:", edge, "Link cost:",link_travel_time,"Temp Cost:", visited_temp[edge])
                     except:
                         aaa=0
#                 num_nodes+=1
#         print("number of nodes:",num_nodes)
    return visited_temp,path


def generalized_dijsktra_source_to_all(graph, agent, verbose=False):
    initial = agent.rq_O
    ag_bt_0 = agent.bt_0
    ag_bt_wk = agent.bt_wk  #
    ag_bt_wt = agent.bt_wt  #
    ag_bt_m_ivt = agent.bt_m_ivt  #
    ag_bt_f_ivt = agent.bt_f_ivt  #
    ag_bt_f_trfer = agent.bt_f_trfer  #
    ag_bt_fare = agent.bt_fare

    # agent(rq_id=request_id, rq_O=start, rq_D=end, rq_time=rq_time, bt_0=bt_0,
    # bt_wk=bt_wk,bt_wt=bt_wt,bt_m_ivt=bt_m_ivt, bt_f_ivt=bt_f_ivt, bt_f_trfer=bt_f_trfer,bt_fare=bt_fr)

    visited_temp = {initial: 0}  # dictionary: {node: the weights from source to a visited node}
    path = {}
    try:
        (nodes, edges) = (set(graph.nodes), graph.edges)
        costs = graph.costs
    except:  # for NetworkX
        (nodes, edges) = (set(graph.nodes()), graph)  # Siwei: set - sort the graph.nodes
        costs = []
    #     num_nodes=0
    #     if verbose == True:
    #         print("----------------nodes------------------",nodes)
    while nodes:
        if verbose == True:
            print("----------------------------------")
        min_node = None
        # find node with minimum distance value, and close this node
        for node in nodes:  # nodes is the list of unexplored nodes
            if node in visited_temp:  # if node is in the list of unexplored nodes and is visited (dist to that "node" is calculated)
                if verbose == True:
                    print("---------------minimum-nodes------------------", min_node, node)
                if min_node is None:
                    min_node = node

                    if verbose == True:
                        print("---------------minimum-nodes------------------", min_node)

                    if verbose == True:
                        print("Selected:", min_node, visited_temp[node])
                elif visited_temp[node] < visited_temp[min_node]:
                    min_node = node
                    if verbose == True:
                        print("Selected:", min_node, visited_temp[node])

        if min_node is None:
            break

        #         if min_node=='289':
        #             verbose=False

        nodes.remove(min_node)  # find the min_node to close, remove the recent close node from the open node list
        permanent = visited_temp[min_node]
        if min_node in edges:
            for edge in edges[min_node]:
                # pre_route=..
                link_travel_time = graph.get_edge_data(min_node, edge)[
                    "object"].free_flow_time  # Siwei: get link travel time
                link_type_ = graph.get_edge_data(min_node, edge)["object"].link_type  # Siwei: get link travel time
                if link_type_ == 0:  # walking link
                    generalized_link_travel_time = ag_bt_wk * link_travel_time
                if link_type_ == 1:  # transit link
                    generalized_link_travel_time = ag_bt_f_ivt * link_travel_time
                if link_type_ == 2:  # fixed route transit waiting link
                    generalized_link_travel_time = ag_bt_wt * link_travel_time
                if link_type_ == 3:  # transfer link
                    generalized_link_travel_time = ag_bt_f_trfer * link_travel_time
                if link_type_ == 4:  # microtransit in-vehicle-travel time link
                    generalized_link_travel_time = ag_bt_m_ivt * link_travel_time
                if link_type_ == 5:  # microtransit waiting link
                    generalized_link_travel_time = ag_bt_wt * link_travel_time

                # temp = permanent + link_travel_time #Siwei: temp -> the criteria used for closing a node: travel time for UE

                temp = permanent + generalized_link_travel_time  # Siwei: temp -> the criteria used for closing a node: travel time for UE

                #                 print("temp",temp)
                if edge not in visited_temp or temp < visited_temp[edge]:
                    visited_temp[edge] = temp
                    path[edge] = (min_node, link_travel_time)

                if verbose == True:
                    try:
                        print("Permanent:", permanent, "i:", min_node, "j:", edge, "Link cost:", link_travel_time,
                              "Temp Cost:", visited_temp[edge])
                    except:
                        aaa = 0
    #                 num_nodes+=1
    #         print("number of nodes:",num_nodes)
    return visited_temp, path


def dijsktra_all_to_all(graph, verbose=False):
    visited_temp_all = OrderedDict()  # dictionary: {node: source to all shortest path }
    path_all = OrderedDict()
    i = 0
    try:
        (nodes, edges) = (set(graph.nodes), graph.edges)
        costs = graph.costs
    except:  # for NetworkX
        (nodes, edges) = (set(graph.nodes()), graph)  # Siwei: set - sort the graph.nodes
        costs = []
    if verbose == True:
        print("dijsktra_all_to_all starts here", '\n', ':-------------------')
    #     print("nodes",nodes)
    for origin in nodes:
        #         if origin == '172':
        #             verbose=True
        #         else:
        #             verbose=False
        if verbose == True:
            print("node No.", i, "---------")
        visited_temp, path = dijsktra_source_to_all(graph, origin, verbose=verbose)
        #############################################
        # Get the path sequence of the shortest path
        ############################################
        path_all[origin] = OrderedDict()
        for destination in visited_temp.keys():
            if destination != origin:
                if destination not in path_all[origin]:
                    try:
                        path_all[origin][destination] = getTrajectory_O_to_D(origin, destination, path, visited_temp)

                    except Exception as e:
                        print("Shortest path error related to graph connectivity", origin, destination)
                        raise e

        visited_temp = {int(k): float(v) for k, v in visited_temp.items()}
        visited_temp = collections.OrderedDict(sorted(visited_temp.items()))
        visited_temp_all[int(origin)] = visited_temp

        i += 1

    return visited_temp_all, path_all


def getTrajectory_O_to_D(origin, destination, path, t_visited, currenttime=0, timeinterval=5.0):
    # try:
    #     j=(destination, (t_visited[destination])/timeinterval,t_visited[destination])  # This line goes wrong.
    # except:
    #     pass
    ###############
    ##Danny's version
    #################
    #     j=(destination)
    #     rtrajectory = [j]
    #     prenode = j[0]

    rtrajectory = []
    prenode = destination
    rtrajectory.append(prenode)
    #     if origin=='172' and destination =='45242':
    #         print("path",path,"\n","\n")
    #         print("t_visited",t_visited)

    # 0317 Siwei
    # path[edge] = (min_node,ts_at_node, link_travel_time, link_travel_marginal_time) # (close node, close time, link cost, link marginal cost)
    for k in range(0, len(path)):

        #         if origin=='172' and destination =='289':
        #             print("prenode",prenode,"\n")
        #             print("rtrajectory",rtrajectory)

        if prenode != origin:
            try:
                nextnode = path[prenode][0]
            except Exception as e:
                print("prenode", prenode, "path", path, "origin", origin, "destination", destination, "t_visited",
                      t_visited)
                raise e
            #             nextnode=path[prenode][0]
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
    # rtrajectory[-1]=(destination, rtrajectory[0][1]+visited[destination])
    return rtrajectory_


def get_link_type_from_O_to_D(origin, destination, path):

    rtrajectory = []
    prenode = destination
    rtrajectory.append(prenode)

    IsMicroLink=False
    IsFixedLink=False
    for k in range(0, len(path)):

        if prenode != origin:

            try:
                nextnode = path[prenode][0]
            except Exception as e:
                print("origin",origin,"prenode", prenode, "path", path,"len(path)",len(path), "origin", origin, "destination", destination)
                raise e
            #             nextnode=path[prenode][0]
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
        if link_type==4:
            IsMicroLink=True
        if link_type==1:
            IsFixedLink = True

    rtrajectory_.append(origin)
    rtrajectory_.reverse()
    rtrajectory_.append(destination)

    return IsMicroLink, IsFixedLink, rtrajectory_

#############################################################
#Multi-modal generalized cost shortest path algorithm
############################################################
def generalized_cost_dijsktra_OD_heap(study_area,graph, agent,transit_fare_set,microtransit_start_fare,microtransit_dist_based_rate, PkFareFactor,OffPkFareFactor,Fixed2MicroFactor,Micro2FixedFactor,mode,verbose=False, total_rejection_penalty=0, iteration=0):  # mode="T" or mode="C"

    # Define a class Node to store the values

    ##microtransit_dist_based_rate =0.00123
    class Heap_Node:
        def __init__(self, v, temp):
            self.node_id = v
            self.temp = temp

        # define a comparator method to compare distance of two nodes
        def __lt__(self, other):
            return self.temp < other.temp

    # agent attributes
    initial = agent.rq_O
    dest = agent.rq_D
    #     print("initial",initial,"dest",dest)
    rq_id = agent.rq_id
    rq_time = agent.rq_time
    # agent attributes
    # car mode attributes
    bt_c_0 = agent.bt_c_0
    bt_c_ivt = agent.bt_c_ivt  #
    bt_c_gas = agent.bt_c_gas  #
    # transit mode attributes
    bt_t_0 = agent.bt_t_0  #
    bt_t_wk = agent.bt_t_wk  #
    # bt_t_wt = agent.bt_t_wt  #

    bt_m_wt = agent.bt_m_wt
    bt_f_wt = agent.bt_f_wt

    bt_m_ivt = agent.bt_m_ivt
    bt_f_ivt = agent.bt_f_ivt  #
    bt_f_trfer = agent.bt_f_trfer  #
    bt_t_fr = agent.bt_t_fr

    parking_dur = agent.parking_dur
    # transit_pass = agent.transit_pass

    ########################################
    # Peak and off-peak factor of the microtransit fares. The model has one fare structure, the former fare
    # scenario 10 (docs/progress.md, "Only fare scenario 10").
    #########################################
    if rq_time <= (10 * 3600):
        time_period = "AM"
    elif rq_time <= (15 * 3600):
        time_period = "MD"
    elif rq_time <= (20 * 3600):
        time_period = "PM"
    else:
        time_period = "EV"
    if time_period in ["AM","PM"]:
        peak_factor = PkFareFactor
    else:
        peak_factor = OffPkFareFactor

    # define a priority queue as the heap
    heap_q = []
    if mode == "T":  # transit mode initial travel cost
        visited_temp = {initial: bt_t_0}  # dictionary: {node: the weights from source to a visited node}
        heapq.heappush(heap_q, Heap_Node(initial, bt_t_0))
    #         transit_visited_temp={initial: 0} #document the microtransit travel time
    if mode == "C":  # car mode initial travel cost
        visited_temp = {initial: bt_c_0}  # dictionary: {node: the weights from source to a visited node}
        heapq.heappush(heap_q, Heap_Node(initial, bt_t_0))
    #         auto_visited_temp = {initial: 0} #document the auto vehicle travel time
    time_visited_temp = {initial: 0}  # document the travel time
    dist_visited_temp = {initial: 0}  # document the travel distance
    fare_visited_temp = {initial: 0}  # document the travel fare
    F_fare_visited_temp = {initial: 0}  # document the cumulative fixed route transit fare
    M_fare_visited_temp = {initial: 0}  # document the cumulative microtransit fare
    auto_gas_visited_temp = {initial: 0} # document the cumulative auto gas cost

    path = {}
    time_path = {}
    dist_path = {}
    transit_fare=0
    micro_fare=0
    gas_cost=0
    try:
        (nodes, edges) = (set(graph.nodes), graph.edges)
        costs = graph.costs
    except:  # for NetworkX
        (nodes, edges) = (set(graph.nodes()), graph)  # Siwei: set - sort the graph.nodes
        costs = []

    num_transit_links = 0
    # node_path_link_type_list=OrderedDict()
    # node_path_link_type_list[initial]=[]
    while heap_q:  # while there exist an element in the heap
        # 11/02: Heap
        if verbose == True:
            print("----------------------------------")
        #         min_node = None

        #             break

        #         nodes.remove(min_node)  # find the min_node to close, remove the recent close node from the open node list
        smallest_node = heapq.heappop(heap_q)  # 11/02: Heap: get the smallest value item from the heap
        #         print("smallest_node",smallest_node)
        min_node = smallest_node.node_id
        #         print("HEAP: min_node",min_node)
        # node_path_link_type_list[min_node]=[]
        permanent = visited_temp[min_node] #generalized cost at generalized cost minimum node
        time_permanent = time_visited_temp[min_node] # cumulative travel time at generalized cost minimum node
        dist_permanent = dist_visited_temp[min_node] # cumulative distance at generalized cost minimum node
        fare_permanent = fare_visited_temp[min_node]  # cumulative fare at generalized cost minimum node
        F_fare_permanent=F_fare_visited_temp[min_node]   # document the cumulative fixed route transit fare
        M_fare_permanent=M_fare_visited_temp[min_node]   # document the cumulative microtransit fare
        auto_gas_permanent = auto_gas_visited_temp[min_node]  # document the cumulative car fare

        if min_node == dest:  # OD shortest path
            break

        if min_node in edges:
            if min_node!=initial:
                IsMicroLink, IsFixedLink,rtrajectory_ = get_link_type_from_O_to_D(initial, min_node, path)
            else:
                IsMicroLink, IsFixedLink=False,False
            for edge in edges[min_node]:
                # pre_route=..
                link_travel_time = graph.get_edge_data(min_node, edge)["object"].free_flow_time  # Siwei: get link travel time
                link_type_ = graph.get_edge_data(min_node, edge)["object"].link_type  # Siwei: get link type
                link_length = graph.get_edge_data(min_node, edge)["object"].length  # Siwei: get link length (meters)
                route = graph.get_edge_data(min_node, edge)["object"].route  # Siwei: get link length (meters)

                if min_node!= initial:
                    (min_node_pre, temp_pre, link_type_pre,route_pre)=path[min_node]
                else:
                    link_type_pre=0
                if link_type_ == 0:  # walking link
                    generalized_link_travel_time = bt_t_wk * link_travel_time / 60  # time parameter transfer from sec to min
                if link_type_ == 1:  # transit link
                    # num_transit_links += 1
                    generalized_link_travel_time = bt_f_ivt * link_travel_time / 60
                if link_type_ == 2:  # fixed route transit waiting link
                    if study_area == "lemon_grove":
                        if min_node <= 1098 and 1099 <= edge <= 1170:
                            if link_type_pre != 2:
                                transit_fare = transit_fare_set
                            else:
                                aaa=0
                        else:
                            transit_fare = 0
                    # transit_fare = transit_fare * 1

                    if IsMicroLink==True:  # transfer discount after a microtransit trip leg
                        transit_fare = transit_fare_set* Micro2FixedFactor
                    generalized_link_travel_time = bt_f_wt * link_travel_time / 60 + bt_t_fr * transit_fare
                    # transit_fare=0 ##10/15/2024 Siwei
                if link_type_ == 3:  # transfer link
                    generalized_link_travel_time = bt_f_trfer * link_travel_time / 60
                if link_type_ == 4:  # microtransit in-vehicle-travel time link
                    micro_fare = microtransit_dist_based_rate * link_length * peak_factor  # microtransit fare: 0.00123 dollar per meter, 1.97 dollar per mile
                    if IsFixedLink == True:  # transfer discount after a fixed-route trip leg
                        micro_fare = micro_fare * Fixed2MicroFactor
                    generalized_link_travel_time = bt_m_ivt * link_travel_time / 60 + bt_t_fr * micro_fare
                    # micro_fare=0 ##10/15/2024 Siwei
                else:
                    micro_fare = 0
                if link_type_ == 5:  # microtransit waiting link
                    # microtransit start fare (with the transfer discount and the peak factor) and the rejection penalty
                    if study_area == "lemon_grove":
                        if min_node <= 1098 and 1171 <= edge <= 2269:
                            micro_fare = microtransit_start_fare * Fixed2MicroFactor * peak_factor  # Ritun (docs/open_issues.md, I-19)
                        else:
                            micro_fare = 0

                    if iteration>0:
                        if link_travel_time==180:
                            print(f"WAITING LINK = {link_travel_time}")
                    generalized_link_travel_time = bt_m_wt * link_travel_time / 60 + bt_t_fr * micro_fare + bt_t_fr * total_rejection_penalty
                if link_type_ == 7:  # auto network links
                    gas_cost = 0.00025 * link_length  # gasoline cost: 0.00019 dollar per meter, 0.305 dollar per mile # Ritun: set it to 0.4 ($/mile)
                    generalized_link_travel_time = bt_c_ivt * link_travel_time / 60 + bt_c_gas * gas_cost       # Ritun
                else:
                    gas_cost=0

                temp = permanent + generalized_link_travel_time  # Siwei: temp -> the criteria used for closing a node: travel time for UE
                time_temp = time_permanent + link_travel_time
                dist_temp = dist_permanent + link_length
                if mode == "T":  # transit mode
                    fare_temp = fare_permanent + transit_fare + micro_fare

                    F_fare_temp = F_fare_permanent + transit_fare
                    M_fare_temp = M_fare_permanent + micro_fare

                    # if transit_fare>0:
                    #     print("ageng_rq_id", rq_id,"mode",mode,"min_node",min_node,"edge",edge,"link_type",link_type_,"link_type_pre",link_type_pre, "cumulative", fare_temp,"T_cost",transit_fare,"M_cost",micro_fare)
                    transit_fare = 0
                    auto_gas_temp = 0
                else:
                    fare_temp = fare_permanent + gas_cost
                    auto_gas_temp = auto_gas_permanent + gas_cost

                    F_fare_temp = 0
                    M_fare_temp = 0


                #                 print("temp",temp)
                if edge not in visited_temp or temp < visited_temp[edge]:
                    visited_temp[edge] = temp
                    path[edge] = (min_node, temp, link_type_,route)
                    # node_path_link_type_list[edge]=node_path_link_type_list[min_node]
                    # node_path_link_type_list[edge].append(link_type_)
                    heapq.heappush(heap_q,Heap_Node(edge, temp))  # 11/02: Heap: push the new calculated nodes into heap

                    time_visited_temp[edge] = time_temp
                    dist_visited_temp[edge] = dist_temp
                    fare_visited_temp[edge] = fare_temp
                    F_fare_visited_temp[edge] = F_fare_temp
                    M_fare_visited_temp[edge] = M_fare_temp
                    auto_gas_visited_temp[edge] = auto_gas_temp

                    time_path[edge] = (min_node, time_temp, link_type_,route)
                    dist_path[edge] = (min_node, dist_temp, link_type_,route)

                if verbose == True:
                    try:
                        print("Permanent:", permanent, "i:", min_node, "j:", edge, "Link cost:",
                              generalized_link_travel_time, "Temp Cost:", visited_temp[edge])
                    except:
                        aaa = 0
    if mode =="T":
        aaa=1

    if mode == "C":
        return parking_dur, bt_c_gas, visited_temp, time_visited_temp,dist_visited_temp,fare_visited_temp,F_fare_visited_temp,M_fare_visited_temp, path, time_path, dist_path
    else:
        return visited_temp, time_visited_temp, dist_visited_temp, fare_visited_temp, F_fare_visited_temp, M_fare_visited_temp, path, time_path, dist_path

    # return visited_temp, time_visited_temp, dist_visited_temp, fare_visited_temp, F_fare_visited_temp, M_fare_visited_temp, path, time_path, dist_path

#############################################################
#Multi-modal generalized cost shortest path algorithm
############################################################

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    print("start time:",start_time)
    mtsm.not_self_contained("network_algorithms.py standalone test")
    # STALE: new_network_folder = "D:/Ritun/Siwei_Micro_Transit/Ritun/Latest network 2"
    for headway in [20]:  # [20,30,60]
        for percentage in [50]:  # [50,75,100]
            final_super_network_edges = os.path.join(new_network_folder, "super_network_%s_virstop_%s_hw_edges.csv" % (str(percentage), str(headway)))

    super_network=read_super_network(final_super_network_edges)
    demand_file = os.path.join(demand_folder, "debug_trips_nodes_study_area_with_beta.csv")
    agent_list=read_request(demand_file)
    # agent=agent_list[0]
    mode="T"

    for agent in agent_list:
        visited_temp, time_visited_temp, dist_visited_temp, fare_visited_temp, path, time_path=generalized_cost_dijsktra_OD_heap(super_network, agent, mode, verbose=False)
    # generalized_cost_dijsktra_OD_heap()

    timeatfinished = datetime.datetime.now()
    processingtime = timeatfinished - start_time
    print("integrated system model run finished....... end time is:", timeatfinished, "run time is: ", processingtime)