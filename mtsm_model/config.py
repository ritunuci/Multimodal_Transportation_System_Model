"""Configuration of a model run.

- RunConfig / read_run_config(): the run's parameters, read from mtsm_data/input_parameter/input_parameter.csv
  (written by Bayesian_optimization_script.py for each candidate).
- check_run_config(): the startup check; stops on a configuration the code does not support.
- The model's fixed settings and constants, which are not in the input file (upper-case names below).

Moved from run_examples_new_parking.py without changes to the values or the reading (restructuring step 2,
docs/entry_script_refactor_plan.md). The field names of RunConfig and the constant names keep the old variable names
(constants in upper case), so that they can still be found in the old code and in the git history.
"""
import csv
import os
import sys
from dataclasses import dataclass
from typing import List

from colorama import Fore, Style

import mtsm_paths as mtsm
from tools.check_inputs import check_inputs

# ---- units ----
MILE_METER = 1609.34  # meters per mile

# ---- fixed-route transit (FRT) base case: the "without microtransit" network and fare ----
BASE_FRT_HEADWAY = 20  # min
BASE_FRT_FARE = 2.5  # $, Ritun: base fare for fixed route transit

# ---- iterations and convergence ----
# True: individual-level convergence test (used). False: aggregate-level test, kept for later but unfinished;
# see the convergence test in the iteration loop of run_examples_new_parking.py and docs/open_issues.md, I-16.
INDIV_CONVERG_TEST = True
MAXIMUM_ITERATION = 15  # the iterations stop here even if the convergence test has not passed
CONVERGENCE_GAP = 0.01  # Ritun changed it from 0.01
# A traveler keeps the mode of the previous iteration if the transit probability changed by at most this.
MODE_CHANGE_THRESHOLD = 0.05
# How FleetPy's waiting times update the microtransit waiting links (update_network_files.py):
# "whole_region" = one average per time period; "census_track" = per census tract, with a rejection penalty.
AGGREGATION = "whole_region"

# ---- time periods: a trip departing at t (s) is AM if t <= AM_END, MD if t <= MD_END, PM if t <= PM_END, else EV ----
AM_END = 10 * 3600
MD_END = 15 * 3600
PM_END = 20 * 3600

# ---- parking: share of the parking charge in the generalized cost of a car trip ----
PARKING_FACTOR_PEAK = 1  # AM and PM
PARKING_FACTOR_OFFPEAK = 0.5  # MD and EV

# ---- Lemon Grove super-network: walk node i (0..NUM_WALK_NODES-1) is microtransit node MICROTRANSIT_NODE_OFFSET + i,
# and FleetPy node i ----
NUM_WALK_NODES = 1099
MICROTRANSIT_NODE_OFFSET = 1171

# ---- gas cost ----
F_GAS_PER_MILE = 0.350  # The fuel cost for the CNG buses averaged $0.35 per mile
M_GAS_PER_MILE = 0.550  # gasoline cost: 0.00019 dollar per meter, 0.305 dollar per mile # Ritun: set it to 0.55 $/mile

# ---- scenarios (each list has one element in the run) ----
# Microtransit operating periods: AM = 5-10 h, MD = 10-15 h, PM = 15-20 h, EV = 20-24 h.
OPERATING_PERIOD_1 = ["AM", "PM"]  # 10 hr
OPERATING_PERIOD_2 = ["AM", "MD", "PM"]  # 15hr
OPERATING_PERIOD_3 = ["AM", "MD", "PM", "EV"]  # 19hr
OPERATING_PERIODS_SCENARIOS = [OPERATING_PERIOD_2]
VIRTUAL_STOP_SCENARIOS = [75]  # % of the nodes that are virtual microtransit stops
MICROTRANSIT_RUNNING_SCENARIOS = ["micro"]  # "micro" (microtransit + FRT) or "micro_only" (no FRT)
REPOSITIONING_LIST = [True]  # FleetPy vehicle repositioning


@dataclass
class RunConfig:
    """The parameters in input_parameter.csv. The lists hold one value per row of the file; the other fields hold
    the value of the last row (the file has one row)."""
    input_para_dir: str
    TRPartA_test_scenario_list: List[int]  # fare scenario (test_scenario), 0-10
    debug_mode_list: List[bool]  # must be FALSE (I-15)
    test_area: List[str]  # study area, must be lemon_grove
    read_fleet_size: List[int]  # microtransit fleet size (vehicles)
    TRPartA: bool  # must be TRUE (I-15)
    BayesianOptimization: bool  # must be TRUE (I-15)
    transit_fare: float  # $
    microtransit_dist_based_rate: float  # $ per meter (the file gives $ per mile)
    microtransit_start_fare: float  # $
    fleet_size: int
    PkFareFactor: float
    OffPkFareFactor: float
    Fixed2MicroFactor: float
    Micro2FixedFactor: float
    headway: int  # FRT headway (min)
    initial_rejection_rate: float  # % of microtransit requests rejected, assumed for the first iteration
    micro_rejection_penalty: float  # $
    random_seed: int  # one seed drives both the mode-choice draws and FleetPy's random_seed


def str2bool(string_, default='raise'):
    """
    Convert a string to a bool.

    Parameters
    ----------
    string_ : str
    default : {'raise', False}
        Default behaviour if none of the "true" strings is detected.

    Returns
    -------
    boolean : bool

    Examples
    --------
    # >>> str2bool('True')
    # True
    # >>> str2bool('1')
    # True
    # >>> str2bool('0')
    False
    """
    true = ['true', 't', '1', 'y', 'yes', 'enabled', 'enable', 'on']
    false = ['false', 'f', '0', 'n', 'no', 'disabled', 'disable', 'off']
    if string_.lower() in true:
        return True
    elif string_.lower() in false or (not default):
        return False
    else:
        raise ValueError('The value \'{}\' cannot be mapped to boolean.'
                         .format(string_))


def read_run_config(input_para_dir=os.path.join(mtsm.INPUT_PARAMETER_DIR, "input_parameter.csv")):
    TRPartA_test_scenario_list = []
    debug_mode_list = []
    test_area = []
    read_fleet_size = []
    with open(input_para_dir) as f:

        csvreader = csv.DictReader(f)
        for data in csvreader:
            TRPartA = str2bool(str(data["TRPartA"]))
            TRPartA_test_scenario_list.append(int(data["TRPartA_test_scenario_list"]))
            debug_mode_list.append(str2bool(str(data["debug_mode_list"])))
            transit_fare = float(data["transit_fare ($)"])
            microtransit_dist_based_rate = float(data["microtransit_dist_based_rate ($/mile)"]) / MILE_METER
            microtransit_start_fare = float(data["microtransit_start_fare ($)"])
            test_area.append(str(data["test_area"]))
            BayesianOptimization = str2bool(str(data["BayesianOptimization"]))
            fleet_size = int(data["Fleet_size"])
            PkFareFactor = float(data["PkFareFactor"])
            OffPkFareFactor = float(data["OffPkFareFactor"])
            Fixed2MicroFactor = float(data["Fixed2MicroFactor"])
            Micro2FixedFactor = float(data["Micro2FixedFactor"])
            headway = int(data["FRT_headway"])  # Ritun
            initial_rejection_rate = float(data["initial_rejection_rate"])
            micro_rejection_penalty = float(data["micro_rejection_penalty ($)"])
            # 0 if the column is absent
            random_seed = int(data.get("random_seed") or 0)

            read_fleet_size.append(fleet_size)

    return RunConfig(input_para_dir, TRPartA_test_scenario_list, debug_mode_list, test_area, read_fleet_size, TRPartA,
                     BayesianOptimization, transit_fare, microtransit_dist_based_rate, microtransit_start_fare,
                     fleet_size, PkFareFactor, OffPkFareFactor, Fixed2MicroFactor, Micro2FixedFactor, headway,
                     initial_rejection_rate, micro_rejection_penalty, random_seed)


def check_run_config(cfg):
    """Stop on a configuration the code does not support; warn if the frozen inputs changed; create the output
    folders."""
    # The code supports only Lemon Grove with TRPartA=TRUE, BayesianOptimization=TRUE and debug_mode_list=FALSE; the
    # branches for the other values were removed (docs/progress.md). The three columns stay in input_parameter.csv
    # because the optimizer writes its parameters by column position (docs/open_issues.md, I-15).
    unsupported = []
    if any(area != "lemon_grove" for area in cfg.test_area):
        unsupported.append(f"test_area={cfg.test_area} (only lemon_grove)")
    if not cfg.TRPartA:
        unsupported.append("TRPartA=False")
    if not cfg.BayesianOptimization:
        unsupported.append("BayesianOptimization=False")
    if any(cfg.debug_mode_list):
        unsupported.append("debug_mode_list=True")
    if unsupported:
        sys.exit("ERROR: configuration in %s is not supported: %s"
                 % (cfg.input_para_dir, ", ".join(unsupported)))
    input_problems = check_inputs()
    if input_problems:
        print(f"{Fore.RED}WARNING: frozen inputs differ from mtsm_data/MANIFEST.csv -> results are not comparable to "
              f"docs/reference_results: {input_problems}{Style.RESET_ALL}")
    for folder in (mtsm.LG_FINAL_NETWORK_DIR, mtsm.LG_INDIV_OUTPUT_DIR, mtsm.LG_OUTPUT_DIR):
        os.makedirs(folder, exist_ok=True)
