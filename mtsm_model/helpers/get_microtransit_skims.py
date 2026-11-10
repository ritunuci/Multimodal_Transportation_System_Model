import random
import os

import pandas as pd
import numpy as np
import os
import networkx as nx

import networkx as nx
import csv
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


from mtsm_model.helpers import network_algorithms as n_a
import mtsm_paths as mtsm

def get_node_ct(study_area):
    # pre_node_dir
    # census_tract	node_in_fleetpy	is_demand_node
    census_tract_node = OrderedDict()
    node_census_tract = OrderedDict()
    demand_nodes_fleetpy = []
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