"""Configuration of a model run.

- read_constant_config() / PARAMETERS: all MTSM parameters (keys and types: mtsm_global_parameters.py), read once at
  import from two files: the model file CONSTANT_CONFIG_FILE (the file named by the environment variable
  MTSM_CONFIG_FILE, set by run_examples_new_parking.py --config <file> and by the optimizer for each candidate's copy;
  else the frozen mtsm_data/input_parameter/mtsm_constant_configurations.csv) and the area file
  mtsm_data/<area>/area_parameters.csv of the model file's study_area (since 2026-11-24). The model's constants
  (upper-case names below) take their values from it.
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
    test_area: List[str]  # study area: the parameter study_area (until 2026-11-24 it had to be lemon_grove)
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


def read_parameter_file(path, keys, other_keys, other_file):
    """Read one parameter file into a dictionary {key: value}, each value converted to its type in
    mtsm_global_parameters.PARAMETER_TYPES; `keys` are the keys this file must have, `other_keys` those of the other
    file (`other_file`, named in the message for a key that belongs there). The description column is not read. Stops
    on a wrong header, a missing, unknown or repeated key, or a value that cannot be converted, listing all of them."""
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
            if name in other_keys:
                problems.append(f"line {line_number}: {name} belongs in {other_file}")
            elif name not in keys:
                problems.append(f"line {line_number}: unknown parameter {name}")
            elif name in params or name in unconverted:
                problems.append(f"line {line_number}: {name} is repeated")
            else:
                try:
                    params[name] = convert_parameter(value, gp.PARAMETER_TYPES[name])
                except ValueError:
                    unconverted.add(name)
                    problems.append(f"line {line_number}: {name} = '{value}' is not a {gp.PARAMETER_TYPES[name]}")
    problems += [f"missing parameter {name}" for name in keys
                 if name not in params and name not in unconverted]
    if problems:
        sys.exit(f"ERROR: {path}:\n  " + "\n  ".join(problems))
    return params


def read_constant_config(path=CONSTANT_CONFIG_FILE):
    """All MTSM parameters, {key: value} in the order of PARAMETER_TYPES: the model file `path` and the area file of
    its study_area (mtsm_data/<area>/area_parameters.csv). A key must be in its own file and only there (until
    2026-11-24 the model file had them all)."""
    model = read_parameter_file(path, gp.MODEL_PARAMETERS, gp.AREA_PARAMETERS, "the area file area_parameters.csv")
    area_file = mtsm.area_paths(model[gp.G_STUDY_AREA]).area_parameter_file
    if not os.path.isfile(area_file):
        sys.exit(f"ERROR: the study area's parameter file is missing: {area_file} (study_area in {path})")
    area = read_parameter_file(area_file, gp.AREA_PARAMETERS, gp.MODEL_PARAMETERS, f"the model file {path}")
    return {key: (area[key] if key in area else model[key]) for key in gp.PARAMETER_TYPES}


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
# (the switch indiv_converg_test, always True, was removed with the aggregate-level test on 2026-11-23; I-16)
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

# ---- parking: the charge per started interval ($); the car's parking cost rate x started intervals is in its
# generalized cost (x bt_c_gas) and its out-of-pocket cost (choice.py). Until 2026-11-19 PARKING_FACTOR_PEAK (1) and
# PARKING_FACTOR_OFFPEAK (0.5), in the generalized cost only ----
PARKING_RATE_PEAK = PARAMETERS[gp.G_PARKING_RATE_PEAK]  # AM and PM, $ per started interval
PARKING_RATE_OFFPEAK = PARAMETERS[gp.G_PARKING_RATE_OFFPEAK]  # MD and EV, $ per started interval

# ---- node numbering of the study area's super-networks (docs/study_area_inputs.md, "Node numbering"): walk node i
# (0..NUM_WALK_NODES-1) is FleetPy node i and microtransit node MICROTRANSIT_NODE_OFFSET + i. Derived from the files
# since 2026-11-24 (decision 3, docs/study_area_plan.md Phase 2 step 2); until then the parameters num_walk_nodes and
# microtransit_node_offset (Lemon Grove: 1099, 1171) ----
def derive_node_numbering(study_area, virstops):
    """(N, M): N = the number of FleetPy road nodes (nodes.csv; node_index must be 0..N-1), M = the smallest node of
    the microtransit in-vehicle links (type 4) of the super-network with microtransit, whose nodes must be exactly
    M..M+N-1, the same in the file of every virtual-stop share; every microtransit boarding / alighting link (type 5)
    must join walk node i and microtransit node M + i. Stops with a message if a file breaks the rule."""
    paths = mtsm.area_paths(study_area)
    nodes_file = os.path.join(paths.fleetpy_inputs_dir, *paths.fleetpy_staged[0].split("/"))  # FleetPy's nodes.csv
    with open(nodes_file, newline="") as f:
        node_index = [int(row["node_index"]) for row in csv.DictReader(f)]
    n = len(node_index)
    if node_index != list(range(n)):
        sys.exit(f"ERROR: {nodes_file}: node_index must be 0, 1, ..., N-1 in this order (docs/study_area_inputs.md)")
    offsets = set()
    for virstop in virstops:
        network_file = paths.super_network_micro_file(virstop)
        micro_nodes = set()
        waiting_links = []
        with open(network_file, newline="") as f:
            for row in csv.DictReader(f):
                link_type = int(row["link_type"])
                if link_type == 4:
                    micro_nodes.update((int(row["from_node"]), int(row["to_node"])))
                elif link_type == 5:
                    waiting_links.append((int(row["from_node"]), int(row["to_node"])))
        m = min(micro_nodes) if micro_nodes else None
        if m is None or micro_nodes != set(range(m, m + n)):
            sys.exit(f"ERROR: {network_file}: the nodes of the microtransit links (type 4) must be M..M+N-1, with "
                     f"N = {n} FleetPy nodes (docs/study_area_inputs.md, node numbering)")
        if m < n:
            sys.exit(f"ERROR: {network_file}: the first microtransit node ({m}) must come after the {n} walk nodes")
        wrong = [(a, b) for a, b in waiting_links if not ((a < n and b == a + m) or (b < n and a == b + m))]
        if wrong:
            sys.exit(f"ERROR: {network_file}: {len(wrong)} microtransit waiting links (type 5) do not join walk node i "
                     f"and microtransit node {m} + i, e.g. {wrong[0]}")
        offsets.add(m)
    if len(offsets) != 1:
        sys.exit(f"ERROR: the super-networks of the virtual-stop shares {virstops} number their microtransit nodes "
                 f"differently: {sorted(offsets)}")
    return n, offsets.pop()


NUM_WALK_NODES, MICROTRANSIT_NODE_OFFSET = derive_node_numbering(PARAMETERS[gp.G_STUDY_AREA],
                                                                 PARAMETERS[gp.G_VIRTUAL_STOP_SCENARIOS])

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
                     test_area=[p[gp.G_STUDY_AREA]],
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
    # The code supports only fare scenario 10; the branches for the other values were removed (docs/progress.md).
    # Until 2026-11-24 it also supported only the study area Lemon Grove (docs/study_area_plan.md, Phase 2 decision 3).
    unsupported = []
    if FARE_SCENARIO != SUPPORTED_FARE_SCENARIO:
        unsupported.append(f"fare_scenario={FARE_SCENARIO} (only {SUPPORTED_FARE_SCENARIO})")
    if unsupported:
        sys.exit("ERROR: configuration in %s is not supported: %s"
                 % (cfg.config_file, ", ".join(unsupported)))
    # the study area's inputs against docs/study_area_inputs.md (since 2026-11-24, Phase 4 of docs/study_area_plan.md;
    # also a standalone tool: python tools/check_study_area.py). Imported here, not at the top: the tool imports this
    # module when it runs on its own.
    from tools.check_study_area import check_study_area
    for area in cfg.test_area:
        result = check_study_area(area, PARAMETERS, NUM_WALK_NODES, MICROTRANSIT_NODE_OFFSET)
        for text in result.warnings:
            print(f"{Fore.YELLOW}WARNING ({area}): {text}{Style.RESET_ALL}")
        if result.errors:
            sys.exit(f"ERROR: the inputs of study area {area} do not fit the model (docs/study_area_inputs.md; "
                     f"python tools/check_study_area.py):\n  " + "\n  ".join(result.errors))
    if os.path.abspath(cfg.config_file) != os.path.abspath(FROZEN_CONSTANT_CONFIG_FILE):
        frozen = read_constant_config(FROZEN_CONSTANT_CONFIG_FILE)
        changed = [f"{key}={PARAMETERS[key]!r} (frozen: {frozen[key]!r})" for key in gp.PARAMETER_TYPES
                   if PARAMETERS[key] != frozen[key] or type(PARAMETERS[key]) is not type(frozen[key])]
        print(f"parameter file: {cfg.config_file}; different from the frozen file: {', '.join(changed) or 'none'}")
    input_problems = check_inputs(cfg.test_area)  # the shared manifest and the run's area manifests (2026-11-24)
    if input_problems:
        print(f"{Fore.RED}WARNING: frozen inputs differ from their manifests -> results are not comparable to "
              f"docs/reference_results: {input_problems}{Style.RESET_ALL}")
    # fleetpy_demand_dir: the run writes FleetPy's demand there; it holds no tracked file since 2026-11-23 (I-11)
    for area in cfg.test_area:
        paths = mtsm.area_paths(area)
        for folder in (paths.initial_network_dir, paths.final_network_dir, paths.indiv_output_dir, paths.output_dir,
                       paths.fleetpy_demand_dir):
            os.makedirs(folder, exist_ok=True)
