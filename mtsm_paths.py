"""Folder locations of the self-contained data tree mtsm_data/ (see docs/progress.md).

Every path is derived from the location of this file, so the codebase keeps working when it is moved or copied.
A study area's folders come from area_paths(area) (since 2026-11-24; docs/study_area_plan.md, Phase 1 step 1);
until then they were the Lemon Grove constants LG_*.
"""
import os
from dataclasses import dataclass

CODE_ROOT = os.path.dirname(os.path.abspath(__file__))
MTSM_DIR = os.path.join(CODE_ROOT, "mtsm_data")

# inputs shared by all study areas
INPUT_PARAMETER_DIR = os.path.join(MTSM_DIR, "input_parameter")             # Bayesian_Optimization/Input_parameter
# (REGION_DIR, region/, and ACTIVITYSIM_DIR, region/activitysim_output/, held the accessibility inputs: removed
# 2026-11-24)

# FleetPy (upstream TUM-VT/FleetPy, see fleetpy/LOCAL_CHANGES.md); it finds data/ and studies/ next to its src/
FLEETPY_DIR = os.path.join(CODE_ROOT, "fleetpy")
FLEETPY_RESULTS_DIR = os.path.join(FLEETPY_DIR, "studies", "example_study", "results")


@dataclass(frozen=True)
class AreaPaths:
    """The folders of one study area. The old Lemon Grove constant (and the folder it replaced, outside the codebase)
    is given in the comment."""
    area: str
    dir: str  # mtsm_data/<area>/ (LG_DIR)
    demand_dir: str  # LG_DEMAND_DIR; Bayesian_Optimization/demand_data/lemon_grove
    initial_network_dir: str  # LG_INITIAL_NETWORK_DIR; Bayesian_Optimization/lemon_grove/initial_network_folder/initial_network
    transit_dir: str  # LG_TRANSIT_DIR; Ritun/Lemon Grove
    transit_network_dir: str  # LG_TRANSIT_NETWORK_DIR; Ritun/Lemon Grove/Network_folder
    final_network_dir: str  # LG_FINAL_NETWORK_DIR; Bayesian_Optimization/lemon_grove/final_network_folder
    indiv_output_dir: str  # LG_INDIV_OUTPUT_DIR; Data/0719_input/indiv_output_folder
    output_dir: str  # LG_OUTPUT_DIR; Bayesian_Optimization/lemon_grove/output_folder
    optimization_output_dir: str  # LG_OPTIMIZATION_OUTPUT_DIR; Bayesian_Optimization/optimization_output (optimizer)
    # the area's inputs for FleetPy, in FleetPy's folder layout (data/..., studies/...); fleetpy_runner copies them
    # into fleetpy/ before each FleetPy run
    fleetpy_inputs_dir: str  # LG_FLEETPY_INPUTS_DIR
    fleetpy_scenarios_dir: str  # LG_FLEETPY_SCENARIOS_DIR
    fleetpy_demand_dir: str  # LG_FLEETPY_DEMAND_DIR: inside fleetpy/; the run writes FleetPy's demand there
    # (LG_INITIAL_NETWORK_0719_DIR and LG_MGRA_NODE_MAPPING_DIR, accessibility only, removed 2026-11-24)


def area_paths(area):
    """The folders of the study area `area` (a folder name in mtsm_data/, e.g. "lemon_grove")."""
    if not area or os.path.basename(area) != area or area in (".", ".."):
        raise ValueError("study area must be a plain folder name in mtsm_data/, got %r" % (area,))
    area_dir = os.path.join(MTSM_DIR, area)
    transit_dir = os.path.join(area_dir, "transit")
    fleetpy_inputs_dir = os.path.join(area_dir, "fleetpy_inputs")
    return AreaPaths(
        area=area,
        dir=area_dir,
        demand_dir=os.path.join(area_dir, "demand_data"),
        initial_network_dir=os.path.join(area_dir, "initial_network"),
        transit_dir=transit_dir,
        transit_network_dir=os.path.join(transit_dir, "network_folder"),
        final_network_dir=os.path.join(area_dir, "final_network"),
        indiv_output_dir=os.path.join(area_dir, "indiv_output"),
        output_dir=os.path.join(area_dir, "output"),
        optimization_output_dir=os.path.join(area_dir, "optimization_output"),
        fleetpy_inputs_dir=fleetpy_inputs_dir,
        fleetpy_scenarios_dir=os.path.join(fleetpy_inputs_dir, "studies", "example_study", "scenarios"),
        fleetpy_demand_dir=os.path.join(FLEETPY_DIR, "data", "demand", "%s_example_demand" % area, "matched",
                                        "%s_example_network" % area),
    )


def not_self_contained(what):
    """Stop on a code branch whose folders are still outside the codebase.

    The old absolute paths of such a branch are kept next to the call as '# STALE:' comments.
    """
    raise NotImplementedError("%s is not self-contained (mtsm_data/) yet; its folders are outside the codebase. "
                              "See docs/progress.md." % what)
