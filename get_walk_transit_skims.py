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
from mtsm_model.helpers import network_algorithms as n_a

def get_walk_transit_skims(walk_transit_network):

    walk_transit_graph=n_a.read_network(walk_transit_network)
    walk_transit_visited_temp_all,walk_transit_path_all=n_a.dijsktra_all_to_all(walk_transit_graph,verbose=False)

    return walk_transit_visited_temp_all

def get_walk_skims(edges_dir):

    walking_network_graph = n_a.read_walking_network(edges_dir)
    walking_visited_temp_all, walk_path_all = n_a.dijsktra_all_to_all(walking_network_graph)

    return walking_visited_temp_all