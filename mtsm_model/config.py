"""Configuration of a model run.

- read_constant_config() / PARAMETERS: all MTSM parameters (keys and types: mtsm_global_parameters.py), read once at
  import from CONSTANT_CONFIG_FILE: the file named by the environment variable MTSM_CONFIG_FILE (set by
  run_examples_new_parking.py --config <file>; the optimizer passes each candidate's copy), else the frozen
  mtsm_data/input_parameter/mtsm_constant_configurations.csv. The model's constants (upper-case names below) take
  their values from it.
- RunConfig / read_run_config(): the run's parameters (the former input_parameter.csv), from PARAMETERS.
- check_run_config(): the startup check; stops on a configuration the code does not support, and says which values
  differ from the frozen file.

Moved from run_examples_new_parking.py (restructuring step 2, docs/entry_script_refactor_plan.md); the parameters
moved into one file on 2026-11-10 (docs/constant_config_plan.md). The field names of RunConfig and the constant names
keep the old variable names (constants in upper case), so that they can still be found in the old code and in the git
history.
"""
import csv
import os
import sys
from dataclasses import dataclass
from typing import List

from colorama import Fore, Style

import mtsm_paths as mtsm
from mtsm_model import mtsm_global_parameters as gp
from tools.check_inputs import check_inputs

# all MTSM parameters (keys and types: mtsm_global_parameters.py); read by read_constant_config()
FROZEN_CONSTANT_CONFIG_FILE = os.path.join(mtsm.INPUT_PARAMETER_DIR, "mtsm_constant_configurations.csv")
CONFIG_FILE_ENV = "MTSM_CONFIG_FILE"  # a run with another parameter file (a copy of the frozen one)
CONSTANT_CONFIG_FILE = os.environ.get(CONFIG_FILE_ENV) or FROZEN_CONSTANT_CONFIG_FILE
CONSTANT_CONFIG_HEADER = ["parameter_name", "parameter_value", "description"]

@dataclass
class RunConfig:
    """The run's parameters (until 2026-11-10 the columns of input_parameter.csv), from PARAMETERS. The lists hold one
    value (the model loops over them)."""
    config_file: str  # the parameter file of the run
    test_area: List[str]  # study area, must be lemon_grove
    read_fleet_size: List[int]  # microtransit fleet size (vehicles)
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


def convert_parameter(value, value_type):
    """Convert a parameter_value string to value_type (one of the types in mtsm_global_parameters.py)."""
    if value_type == gp.INT:
        return int(value)
    if value_type == gp.FLOAT:
        return float(value)
    if value_type == gp.BOOL:
        return str2bool(value)
    if value_type == gp.STR:
        return value
    if value_type == gp.INT_LIST:
        return [int(v) for v in value.split(";")]
    if value_type == gp.BOOL_LIST:
        return [str2bool(v) for v in value.split(";")]
    if value_type == gp.STR_LIST:
        return value.split(";")
    if value_type == gp.STR_LIST_LIST:
        return [v.split(";") for v in value.split("|")]
    raise ValueError(f"unknown parameter type {value_type}")


def read_constant_config(path=CONSTANT_CONFIG_FILE):
    """Read the MTSM parameters into a dictionary {key: value}, each value converted to its type in
    mtsm_global_parameters.PARAMETER_TYPES. The description column is not read. Stops on a wrong header, a missing,
    unknown or repeated key, or a value that cannot be converted, listing all of them."""
    params = {}
    unconverted = set()
    problems = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != CONSTANT_CONFIG_HEADER:
            sys.exit(f"ERROR: {path}: the header must be {','.join(CONSTANT_CONFIG_HEADER)}, not {header}")
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(CONSTANT_CONFIG_HEADER):
                problems.append(f"line {line_number}: {len(row)} columns instead of {len(CONSTANT_CONFIG_HEADER)}")
                continue
            name, value = row[0], row[1]
            if name not in gp.PARAMETER_TYPES:
                problems.append(f"line {line_number}: unknown parameter {name}")
            elif name in params or name in unconverted:
                problems.append(f"line {line_number}: {name} is repeated")
            else:
                try:
                    params[name] = convert_parameter(value, gp.PARAMETER_TYPES[name])
                except ValueError:
                    unconverted.add(name)
                    problems.append(f"line {line_number}: {name} = '{value}' is not a {gp.PARAMETER_TYPES[name]}")
    problems += [f"missing parameter {name}" for name in gp.PARAMETER_TYPES
                 if name not in params and name not in unconverted]
    if problems:
        sys.exit(f"ERROR: {path}:\n  " + "\n  ".join(problems))
    return params


# ---- all MTSM parameters, read once when this module is imported: PARAMETERS[gp.G_<NAME>] ----
PARAMETERS = read_constant_config()

# ---- the model's constants, from PARAMETERS (written here until 2026-11-10; docs/constant_config_plan.md, step 2).
# The names stay, so that they can still be found in the old code and in the git history. ----

# ---- units ----
MILE_METER = PARAMETERS[gp.G_METERS_PER_MILE]  # meters per mile

# ---- fixed-route transit (FRT) base case: the "without microtransit" network and fare ----
BASE_FRT_HEADWAY = PARAMETERS[gp.G_BASE_FRT_HEADWAY]  # min
BASE_FRT_FARE = PARAMETERS[gp.G_BASE_FRT_FARE]  # $, Ritun: base fare for fixed route transit

# ---- iterations and convergence ----
# True: individual-level convergence test (used). False: aggregate-level test, kept for later but unfinished;
# see the convergence test in the iteration loop of run_examples_new_parking.py and docs/open_issues.md, I-16.
INDIV_CONVERG_TEST = PARAMETERS[gp.G_INDIV_CONVERG_TEST]
# the iterations stop here even if the convergence test has not passed
MAXIMUM_ITERATION = PARAMETERS[gp.G_MAXIMUM_ITERATION]
CONVERGENCE_GAP = PARAMETERS[gp.G_CONVERGENCE_GAP]  # Ritun changed it from 0.01
# A traveler keeps the mode of the previous iteration if the transit probability changed by at most this.
MODE_CHANGE_THRESHOLD = PARAMETERS[gp.G_MODE_CHANGE_THRESHOLD]
# How FleetPy's waiting times update the microtransit waiting links (update_network_files.py):
# "whole_region" = one average per time period; "census_track" = per census tract, with a rejection penalty.
AGGREGATION = PARAMETERS[gp.G_AGGREGATION]

# ---- time periods: a trip departing at t (s) is AM if t <= AM_END, MD if t <= MD_END, PM if t <= PM_END, else EV ----
AM_END = PARAMETERS[gp.G_AM_END_H] * 3600
MD_END = PARAMETERS[gp.G_MD_END_H] * 3600
PM_END = PARAMETERS[gp.G_PM_END_H] * 3600

# ---- parking: share of the parking charge in the generalized cost of a car trip ----
PARKING_FACTOR_PEAK = PARAMETERS[gp.G_PARKING_FACTOR_PEAK]  # AM and PM
PARKING_FACTOR_OFFPEAK = PARAMETERS[gp.G_PARKING_FACTOR_OFFPEAK]  # MD and EV

# ---- Lemon Grove super-network: walk node i (0..NUM_WALK_NODES-1) is microtransit node MICROTRANSIT_NODE_OFFSET + i,
# and FleetPy node i ----
NUM_WALK_NODES = PARAMETERS[gp.G_NUM_WALK_NODES]
MICROTRANSIT_NODE_OFFSET = PARAMETERS[gp.G_MICROTRANSIT_NODE_OFFSET]

# ---- gas cost ----
F_GAS_PER_MILE = PARAMETERS[gp.G_F_GAS_PER_MILE]  # The fuel cost for the CNG buses averaged $0.35 per mile
# gasoline cost: 0.00019 dollar per meter, 0.305 dollar per mile # Ritun: set it to 0.55 $/mile
M_GAS_PER_MILE = PARAMETERS[gp.G_M_GAS_PER_MILE]

# ---- fare structure: the former fare scenario 10, the only one left (docs/progress.md, "Only fare scenario 10").
# The number stays in the output file names (..._scen_10) and the evaluation rows. ----
FARE_SCENARIO = PARAMETERS[gp.G_FARE_SCENARIO]
SUPPORTED_FARE_SCENARIO = 10  # the fare structure the code implements (check_run_config)

# ---- scenarios (each list has one element in the run) ----
# Microtransit operating periods: AM = 5-10 h, MD = 10-15 h, PM = 15-20 h, EV = 20-24 h. Used so far:
# AM;PM (10 hr), AM;MD;PM (15 hr, the run), AM;MD;PM;EV (19 hr).
OPERATING_PERIODS_SCENARIOS = PARAMETERS[gp.G_OPERATING_PERIODS_SCENARIOS]
VIRTUAL_STOP_SCENARIOS = PARAMETERS[gp.G_VIRTUAL_STOP_SCENARIOS]  # % of the nodes that are virtual microtransit stops
# "micro" (microtransit + FRT) or "micro_only" (no FRT)
MICROTRANSIT_RUNNING_SCENARIOS = PARAMETERS[gp.G_MICROTRANSIT_RUNNING_SCENARIOS]
REPOSITIONING_LIST = PARAMETERS[gp.G_REPOSITIONING_LIST]  # FleetPy vehicle repositioning

# ---- derived from the parameters ----
# Lemon Grove node ranges: walk nodes 0..LAST_WALK_NODE, FRT stops FIRST_FRT_STOP..LAST_FRT_STOP (1099-1170),
# microtransit nodes MICROTRANSIT_NODE_OFFSET..LAST_MICROTRANSIT_NODE (1171-2269)
LAST_WALK_NODE = NUM_WALK_NODES - 1
FIRST_FRT_STOP = NUM_WALK_NODES
LAST_FRT_STOP = MICROTRANSIT_NODE_OFFSET - 1
LAST_MICROTRANSIT_NODE = MICROTRANSIT_NODE_OFFSET + NUM_WALK_NODES - 1
# length of each time period (h)
PERIOD_HOURS = {"AM": PARAMETERS[gp.G_AM_END_H] - PARAMETERS[gp.G_DAY_START_H],
                "MD": PARAMETERS[gp.G_MD_END_H] - PARAMETERS[gp.G_AM_END_H],
                "PM": PARAMETERS[gp.G_PM_END_H] - PARAMETERS[gp.G_MD_END_H],
                "EV": PARAMETERS[gp.G_DAY_END_H] - PARAMETERS[gp.G_PM_END_H]}


def microtransit_operating_hours(operating_periods):
    """hours of microtransit service in the operating periods: ["AM", "PM"] -> 10, ["AM", "MD", "PM"] -> 15,
    ["AM", "MD", "PM", "EV"] -> 19 (until 2026-11-10 these three values were written into the code)"""
    return sum(PERIOD_HOURS[period] for period in operating_periods)


def read_run_config():
    p = PARAMETERS
    return RunConfig(config_file=CONSTANT_CONFIG_FILE,
                     test_area=[p[gp.G_TEST_AREA]],
                     read_fleet_size=[p[gp.G_FLEET_SIZE]],
                     transit_fare=p[gp.G_TRANSIT_FARE],
                     microtransit_dist_based_rate=p[gp.G_MICROTRANSIT_DIST_BASED_RATE] / MILE_METER,  # $/mile -> $/m
                     microtransit_start_fare=p[gp.G_MICROTRANSIT_START_FARE],
                     fleet_size=p[gp.G_FLEET_SIZE],
                     PkFareFactor=p[gp.G_PK_FARE_FACTOR],
                     OffPkFareFactor=p[gp.G_OFF_PK_FARE_FACTOR],
                     Fixed2MicroFactor=p[gp.G_FIXED2MICRO_FACTOR],
                     Micro2FixedFactor=p[gp.G_MICRO2FIXED_FACTOR],
                     headway=p[gp.G_FRT_HEADWAY],
                     initial_rejection_rate=p[gp.G_INITIAL_REJECTION_RATE],
                     micro_rejection_penalty=p[gp.G_MICRO_REJECTION_PENALTY],
                     random_seed=p[gp.G_RANDOM_SEED])


def check_run_config(cfg):
    """Stop on a configuration the code does not support; warn if the frozen inputs changed; create the output
    folders."""
    # The code supports only Lemon Grove and fare scenario 10; the branches for the other values were removed
    # (docs/progress.md).
    unsupported = []
    if any(area != "lemon_grove" for area in cfg.test_area):
        unsupported.append(f"test_area={cfg.test_area} (only lemon_grove)")
    if FARE_SCENARIO != SUPPORTED_FARE_SCENARIO:
        unsupported.append(f"fare_scenario={FARE_SCENARIO} (only {SUPPORTED_FARE_SCENARIO})")
    if unsupported:
        sys.exit("ERROR: configuration in %s is not supported: %s"
                 % (cfg.config_file, ", ".join(unsupported)))
    if os.path.abspath(cfg.config_file) != os.path.abspath(FROZEN_CONSTANT_CONFIG_FILE):
        frozen = read_constant_config(FROZEN_CONSTANT_CONFIG_FILE)
        changed = [f"{key}={PARAMETERS[key]!r} (frozen: {frozen[key]!r})" for key in gp.PARAMETER_TYPES
                   if PARAMETERS[key] != frozen[key] or type(PARAMETERS[key]) is not type(frozen[key])]
        print(f"parameter file: {cfg.config_file}; different from the frozen file: {', '.join(changed) or 'none'}")
    input_problems = check_inputs()
    if input_problems:
        print(f"{Fore.RED}WARNING: frozen inputs differ from mtsm_data/MANIFEST.csv -> results are not comparable to "
              f"docs/reference_results: {input_problems}{Style.RESET_ALL}")
    for folder in (mtsm.LG_FINAL_NETWORK_DIR, mtsm.LG_INDIV_OUTPUT_DIR, mtsm.LG_OUTPUT_DIR):
        os.makedirs(folder, exist_ok=True)
