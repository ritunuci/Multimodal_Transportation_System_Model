"""Folder locations of the self-contained data tree mtsm/ (see docs/progress.md).

Every path is derived from the location of this file, so the codebase keeps working when it is moved or copied.
Each constant replaces one folder that used to live outside the codebase (old location in the comment).
"""
import os

CODE_ROOT = os.path.dirname(os.path.abspath(__file__))
MTSM_DIR = os.path.join(CODE_ROOT, "mtsm")

# inputs shared by all study areas
INPUT_PARAMETER_DIR = os.path.join(MTSM_DIR, "input_parameter")             # Bayesian_Optimization/Input_parameter
REGION_DIR = os.path.join(MTSM_DIR, "region")                               # Data/0719_input
ACTIVITYSIM_DIR = os.path.join(REGION_DIR, "activitysim_output")            # Data/0719_input/ActivitySim_output

# lemon_grove
LG_DIR = os.path.join(MTSM_DIR, "lemon_grove")
LG_DEMAND_DIR = os.path.join(LG_DIR, "demand_data")                         # Bayesian_Optimization/demand_data/lemon_grove
LG_INITIAL_NETWORK_DIR = os.path.join(LG_DIR, "initial_network")            # Bayesian_Optimization/lemon_grove/initial_network_folder/initial_network
LG_INITIAL_NETWORK_0719_DIR = os.path.join(LG_DIR, "initial_network_0719")  # Data/0719_input/lemon_grove/initial_network
LG_TRANSIT_DIR = os.path.join(LG_DIR, "transit")                            # Ritun/Lemon Grove
LG_TRANSIT_NETWORK_DIR = os.path.join(LG_TRANSIT_DIR, "network_folder")     # Ritun/Lemon Grove/Network_folder
LG_MGRA_NODE_MAPPING_DIR = os.path.join(LG_TRANSIT_DIR, "mgra_node_mapping")  # Ritun/Lemon Grove/MGRA_Node_Mapping
LG_FINAL_NETWORK_DIR = os.path.join(LG_DIR, "final_network")                # Bayesian_Optimization/lemon_grove/final_network_folder
LG_INDIV_OUTPUT_DIR = os.path.join(LG_DIR, "indiv_output")                  # Data/0719_input/indiv_output_folder
LG_OUTPUT_DIR = os.path.join(LG_DIR, "output")                              # Bayesian_Optimization/lemon_grove/output_folder
LG_OPTIMIZATION_OUTPUT_DIR = os.path.join(LG_DIR, "optimization_output")    # Bayesian_Optimization/optimization_output (optimizer)

# Lemon Grove inputs for FleetPy, in FleetPy's folder layout (data/..., studies/...); fleetpy_runner copies them
# into fleetpy/ before each FleetPy run
LG_FLEETPY_INPUTS_DIR = os.path.join(LG_DIR, "fleetpy_inputs")
LG_FLEETPY_SCENARIOS_DIR = os.path.join(LG_FLEETPY_INPUTS_DIR, "studies", "example_study", "scenarios")

# FleetPy (upstream TUM-VT/FleetPy, see fleetpy/LOCAL_CHANGES.md); it finds data/ and studies/ next to its src/
FLEETPY_DIR = os.path.join(CODE_ROOT, "fleetpy")
LG_FLEETPY_DEMAND_DIR = os.path.join(FLEETPY_DIR, "data", "demand", "lemon_grove_example_demand", "matched",
                                     "lemon_grove_example_network")
FLEETPY_RESULTS_DIR = os.path.join(FLEETPY_DIR, "studies", "example_study", "results")


def not_self_contained(what):
    """Stop on a code branch whose folders are still outside the codebase.

    The old absolute paths of such a branch are kept next to the call as '# STALE:' comments.
    """
    raise NotImplementedError("%s is not self-contained (mtsm/) yet; its folders are outside the codebase. "
                              "See docs/progress.md." % what)
