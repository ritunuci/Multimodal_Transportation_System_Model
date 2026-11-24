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
from mtsm_model import config
import mtsm_paths as mtsm

def get_node_ct(study_area, aggregation):
    """The zone (census tract) of each walk node, for FleetPy's waiting times: ({zone: [nodes]}, {node: zone}).
    With aggregation "whole_region" every walk node is in one zone (0) and the node file is not read: every zone gets
    the same period average there, so the zones do not matter (decision G, docs/study_area_inputs.md, 2026-11-24).
    Only "census_track" reads the zones from the node file (networks/nodes.csv)."""
    if aggregation == "whole_region":
        walk_nodes = list(range(config.NUM_WALK_NODES))
        return OrderedDict([(0, walk_nodes)]), OrderedDict((node, 0) for node in walk_nodes)
    # pre_node_dir
    # census_tract	node_in_fleetpy	is_demand_node
    census_tract_node = OrderedDict()
    node_census_tract = OrderedDict()
    demand_nodes_fleetpy = []
    # networks/nodes.csv (until 2026-11-24 transit/network_folder/pre_nodes.csv, only for "lemon_grove")
    pre_node_dir = mtsm.area_paths(study_area).nodes_file

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