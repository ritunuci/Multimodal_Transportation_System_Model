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

def get_auto_time_skims(edges_dir):
    auto_network_graph = n_a.read_network(edges_dir)
    auto_visited_temp_all, auto_path_all = n_a.dijsktra_all_to_all(auto_network_graph)

    return auto_visited_temp_all


def get_auto_dist_skims(edges_dir):
    auto_network_dist_graph = n_a.read_network_dist(edges_dir)
    auto_dist_visited_temp_all, auto_dist_path_all = n_a.dijsktra_all_to_all(auto_network_dist_graph)

    return auto_dist_visited_temp_all