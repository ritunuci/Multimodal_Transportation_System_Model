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


def binary_logit_model(gen_cost_auto, gen_cost_T):
    exp_T = math.exp(-gen_cost_T)
    exp_auto = math.exp(-gen_cost_auto)

    # calculate the probability of choosing each mode
    prob_T = exp_T / (exp_T + exp_auto)
    prob_Auto = exp_auto / (exp_T + exp_auto)

    return prob_Auto, prob_T


def mobility_logsum(gen_cost_auto, gen_cost_T,microtransit="micro"):
    exp_T = math.exp(-gen_cost_T)
    exp_auto = math.exp(-gen_cost_auto)

    # calculate the probability of choosing each mode
    if gen_cost_T == 0: # turn off microtransit service and turn off fixed route transit service
        mob_logsum = math.log(exp_auto)
    else:
        mob_logsum = math.log(exp_auto + exp_T)

    return mob_logsum

