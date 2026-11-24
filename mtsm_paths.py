"""Folder locations of the self-contained data tree mtsm_data/ (see docs/progress.md).

Every path is derived from the location of this file, so the codebase keeps working when it is moved or copied.
A study area's folders and input files come from area_paths(area) (since 2026-11-24; docs/study_area_plan.md,
Phase 1 steps 1-2); until then they were the Lemon Grove constants LG_*.
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
    """The folders and input files of one study area (docs/study_area_inputs.md; layout since 2026-11-24, Phase 1
    step 2 of docs/study_area_plan.md). The comment names the old Lemon Grove constant or file."""
    area: str
    dir: str  # mtsm_data/<area>/ (LG_DIR)
    # ---- inputs ----
    area_parameter_file: str  # area_parameters.csv, file 1 (since 2026-11-24; the values were in the model file)
    demand_dir: str  # demand/ (until 2026-11-24 demand_data/; LG_DEMAND_DIR)
    networks_dir: str  # networks/ (until 2026-11-24 the inputs were in initial_network/ and transit/)
    demand_file: str  # demand/demand.csv (demand_data/lemon_grove_trips_nodes_study_area_with_beta.csv)
    super_network_frt_file: str  # file 4 (initial_network/base_super_network_lemon_grove_non_micro_hw_10.csv)
    super_network_frt_base_headway_file: str  # file 9 (initial_network/initial_super_network_non_micro_hw_20.csv)
    car_network_file: str  # file 5 (initial_network/auto_edges.csv)
    frt_links_file: str  # file 6 (transit/super_network_transit_edges.csv)
    frt_routes_file: str  # file 10, the FRT route table (since 2026-11-24; TRA_input_data_prep's frt_routes.csv)
    nodes_file: str  # file 7, optional (transit/network_folder/pre_nodes.csv)
    manifest_file: str  # checksums of the area's frozen inputs, optional (tools/check_inputs.py)
    # the area's inputs for FleetPy, in FleetPy's folder layout (data/..., studies/...); fleetpy_runner copies them
    # into fleetpy/ before each FleetPy run
    fleetpy_inputs_dir: str  # fleetpy/ (until 2026-11-24 fleetpy_inputs/; LG_FLEETPY_INPUTS_DIR)
    fleetpy_scenarios_dir: str  # LG_FLEETPY_SCENARIOS_DIR
    fleetpy_staged: tuple  # FleetPy inputs besides the two config files, relative to fleetpy_inputs_dir and fleetpy/
    # ---- written by the run ----
    initial_network_dir: str  # the networks per scenario headway (LG_INITIAL_NETWORK_DIR; inputs too until 2026-11-24)
    final_network_dir: str  # LG_FINAL_NETWORK_DIR; Bayesian_Optimization/lemon_grove/final_network_folder
    indiv_output_dir: str  # LG_INDIV_OUTPUT_DIR; Data/0719_input/indiv_output_folder
    output_dir: str  # LG_OUTPUT_DIR; Bayesian_Optimization/lemon_grove/output_folder
    optimization_output_dir: str  # LG_OPTIMIZATION_OUTPUT_DIR; Bayesian_Optimization/optimization_output (optimizer)
    fleetpy_demand_dir: str  # LG_FLEETPY_DEMAND_DIR: inside fleetpy/; the run writes FleetPy's demand there
    # (LG_TRANSIT_DIR and LG_TRANSIT_NETWORK_DIR: their files are in networks/ since 2026-11-24;
    # LG_INITIAL_NETWORK_0719_DIR and LG_MGRA_NODE_MAPPING_DIR, accessibility only, removed 2026-11-24)

    def super_network_micro_file(self, virstop):
        """file 3: the super-network with microtransit and `virstop` % virtual stops
        (initial_network/base_super_network_lemon_grove_micro_hw_10_virstop_75.csv)"""
        return os.path.join(self.networks_dir, "super_network_micro_virstop_%s.csv" % virstop)


def area_paths(area):
    """The folders and input files of the study area `area` (a folder name in mtsm_data/, e.g. "lemon_grove")."""
    if not area or os.path.basename(area) != area or area in (".", ".."):
        raise ValueError("study area must be a plain folder name in mtsm_data/, got %r" % (area,))
    area_dir = os.path.join(MTSM_DIR, area)
    networks_dir = os.path.join(area_dir, "networks")
    fleetpy_inputs_dir = os.path.join(area_dir, "fleetpy")
    return AreaPaths(
        area=area,
        dir=area_dir,
        area_parameter_file=os.path.join(area_dir, "area_parameters.csv"),
        demand_dir=os.path.join(area_dir, "demand"),
        networks_dir=networks_dir,
        demand_file=os.path.join(area_dir, "demand", "demand.csv"),
        super_network_frt_file=os.path.join(networks_dir, "super_network_frt.csv"),
        super_network_frt_base_headway_file=os.path.join(networks_dir, "super_network_frt_base_headway.csv"),
        car_network_file=os.path.join(networks_dir, "car_network.csv"),
        frt_links_file=os.path.join(networks_dir, "frt_links.csv"),
        frt_routes_file=os.path.join(networks_dir, "frt_routes.csv"),
        nodes_file=os.path.join(networks_dir, "nodes.csv"),
        manifest_file=os.path.join(area_dir, "MANIFEST.csv"),
        fleetpy_inputs_dir=fleetpy_inputs_dir,
        fleetpy_scenarios_dir=os.path.join(fleetpy_inputs_dir, "studies", "example_study", "scenarios"),
        fleetpy_staged=(
            "data/networks/%s_example_network/base/nodes.csv" % area,
            "data/networks/%s_example_network/base/edges.csv" % area,
            "data/networks/%s_example_network/base/crs.info" % area,
            "data/fleetctrl/initial_vehicle_distribution/%s_example_network/imbalanced.csv" % area,
            "data/vehicles/%s_vehtype.csv" % area,
        ),
        initial_network_dir=os.path.join(area_dir, "initial_network"),
        final_network_dir=os.path.join(area_dir, "final_network"),
        indiv_output_dir=os.path.join(area_dir, "indiv_output"),
        output_dir=os.path.join(area_dir, "output"),
        optimization_output_dir=os.path.join(area_dir, "optimization_output"),
        fleetpy_demand_dir=os.path.join(FLEETPY_DIR, "data", "demand", "%s_example_demand" % area, "matched",
                                        "%s_example_network" % area),
    )


def not_self_contained(what):
    """Stop on a code branch whose folders are still outside the codebase.

    The old absolute paths of such a branch are kept next to the call as '# STALE:' comments.
    """
    raise NotImplementedError("%s is not self-contained (mtsm_data/) yet; its folders are outside the codebase. "
                              "See docs/progress.md." % what)
