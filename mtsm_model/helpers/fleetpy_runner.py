"""The only MTSM module that talks to FleetPy.

FleetPy (fleetpy/) is upstream TUM-VT/FleetPy with the local changes listed in fleetpy/LOCAL_CHANGES.md. It imports
itself as the top-level package `src` and finds its data/ and studies/ folders next to src/, so fleetpy/ is put on
sys.path here. A study area's inputs for FleetPy are kept in mtsm_data/<area>/fleetpy/ (same folder layout as
fleetpy/; fleetpy_inputs/ until 2026-11-24) and copied into fleetpy/ before each run (stage_inputs).

FleetPy runs in the calling process. It re-seeds random/np.random during a simulation, and the mode choice of the
next iteration continues from that state, so running it in a separate process would change the results
(docs/progress.md).
"""
import csv
import multiprocessing as mp
import os
import shutil
import sys
import traceback

from colorama import Fore, Style

import mtsm_paths as mtsm

if mtsm.FLEETPY_DIR not in sys.path:
    sys.path.insert(0, mtsm.FLEETPY_DIR)
import src.misc.config as config
from src.misc.init_modules import load_simulation_environment
from src.misc.globals import G_RANDOM_SEED, G_SCENARIO_NAME, G_STUDY_NAME

# (MOD_STR, MM_STR, read_outputs_for_comparison and check_assertions served only FleetPy's example check of 88
# users, removed on 2026-11-24; docs/study_area_plan.md, Phase 2 decision 2)

def staged_inputs(study_area):
    """FleetPy inputs of a study area besides the two config files; paths relative to both
    mtsm_data/<area>/fleetpy/ and fleetpy/ (until 2026-11-24 the Lemon Grove list LG_STAGED_INPUTS). Since 2026-11-24
    also FleetPy's travel times per period, if the area has them (network_dynamics.csv and its folders)."""
    paths = mtsm.area_paths(study_area)
    return list(paths.fleetpy_staged) + paths.fleetpy_dynamic_inputs()


def clear_staged_dynamics(study_area):
    """Remove network_dynamics.csv and the time folders (integer names) from FleetPy's copy of the area's network
    folder before staging (since 2026-11-24): FleetPy reads every integer-named folder there when the scenario names
    no network_dynamics file, so a folder left from an earlier run would change a whole-day run."""
    network_dir = os.path.join(mtsm.FLEETPY_DIR, *mtsm.area_paths(study_area).fleetpy_network_dir().split("/"))
    if not os.path.isdir(network_dir):
        return
    for name in os.listdir(network_dir):
        p = os.path.join(network_dir, name)
        if name == "network_dynamics.csv" and os.path.isfile(p):
            os.remove(p)
        elif name.isdigit() and os.path.isdir(p):
            shutil.rmtree(p)


def has_network_dynamics(study_area):
    """the area gives FleetPy travel times per period (network_dynamics.csv in its FleetPy network folder)"""
    return bool(mtsm.area_paths(study_area).fleetpy_dynamic_inputs())


def stage_inputs(constant_config_file, scenario_file, study_area):
    """Copy the constant config file (which must be in mtsm_data/<area>/fleetpy/) and staged_inputs(study_area) into
    fleetpy/, at the same relative paths. The scenario file is written into fleetpy/ by scenario_config_file (since
    2026-11-24; until then it was copied from the area's folder too). Returns the paths of the two config files in
    fleetpy/, to run FleetPy with."""
    fleetpy_inputs_dir = mtsm.area_paths(study_area).fleetpy_inputs_dir
    rel_cc = os.path.relpath(constant_config_file, fleetpy_inputs_dir)
    if rel_cc.startswith(".."):
        raise ValueError(f"FleetPy config file {constant_config_file} is not in {fleetpy_inputs_dir}")
    if os.path.relpath(scenario_file, mtsm.FLEETPY_DIR).startswith(".."):
        raise ValueError(f"FleetPy scenario file {scenario_file} is not in {mtsm.FLEETPY_DIR} (scenario_config_file)")
    clear_staged_dynamics(study_area)
    for rel in [rel_cc] + staged_inputs(study_area):
        dst = os.path.join(mtsm.FLEETPY_DIR, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(fleetpy_inputs_dir, rel), dst)
    return os.path.join(mtsm.FLEETPY_DIR, rel_cc), scenario_file


def scenario_config_file(study_area, repositioning, fleet_size):
    """Write FleetPy's scenario file for the run (create_config_files) into FleetPy's scenarios folder, where FleetPy
    reads it, and return its path: <area>_example_ir_heuristics_repositioning_<fleet>_veh.csv (with repositioning) or
    <area>_example_ir_only_<fleet>_veh.csv. Written for every scenario, since 2026-11-24 (docs/study_area_plan.md,
    Phase 3 decision 2); until then one tracked file per fleet size was kept in the area's folder."""
    scenarios_dir = os.path.join(mtsm.FLEETPY_DIR, "studies", "example_study", "scenarios")
    os.makedirs(scenarios_dir, exist_ok=True)
    if repositioning == True:
        name = "%s_example_ir_heuristics_repositioning_%s_veh.csv" % (str(study_area), str(fleet_size))
    else:
        name = "%s_example_ir_only_%s_veh.csv" % (str(study_area), str(fleet_size))
    sc = os.path.join(scenarios_dir, name)
    create_config_files(sc, study_area, repositioning, fleet_size)
    return sc


def run_single_simulation(scenario_parameters):
    SF = load_simulation_environment(scenario_parameters)
    if scenario_parameters.get("bugfix", False):
        try:
            SF.run()
        except:
            traceback.print_exc()
    else:
        SF.run()


def run_scenarios(constant_config_file, scenario_file, n_parallel_sim=1, n_cpu_per_sim=1, evaluate=1, log_level="info",
                  keep_old=False, continue_next_after_error=False, random_seed=None):
    """
    This function combines constant study parameters and scenario parameters.
    Then it sets up a pool of workers and starts a simulation for each scenario.
    The required parameters are stated in the documentation.

    :param constant_config_file: this file contains all input parameters that remain constant for a study
    :type constant_config_file: str
    :param scenario_file: this file contain all input parameters that are varied for a study
    :type scenario_file: str
    :param n_parallel_sim: number of parallel simulation processes
    :type n_parallel_sim: int
    :param n_cpu_per_sim: number of cpus for a single simulation
    :type n_cpu_per_sim: int
    :param evaluate: 0: no automatic evaluation / != 0 automatic simulation after each simulation
    :type evaluate: int
    :param log_level: hierarchical output to the logging file. Possible inputs with hierarchy from low to high:
            - "verbose": lowest level -> logs everything; even code which could scale exponentially
            - "debug": standard debugging logger. code which scales exponentially should not be logged here
            - "info": basic information during simulations (default)
            - "warning": only logs warnings
    :type log_level: str
    :param keep_old: does not start new simulation if result files are already available in scenario output directory
    :type keep_old: bool
    :param continue_next_after_error: continue with next simulation if one the simulations threw an error (only SP)
    :type continue_next_after_error: bool
    :param random_seed: overrides random_seed of the constant config if given
    :type random_seed: int
    """
    assert type(n_parallel_sim) == int, "n_parallel_sim must be of type int"
    # read constant and scenario config files
    constant_cfg = config.ConstantConfig(constant_config_file)
    scenario_cfgs = config.ScenarioConfig(scenario_file)

    # set constant parameters from function arguments
    # TODO # get study name and check if its a studyname
    const_abs = os.path.abspath(constant_config_file)
    study_name = os.path.basename(os.path.dirname(os.path.dirname(const_abs)))

    if study_name == "scenarios":
        print("ERROR! The path of the config files is not longer up to date!")
        print("See documentation/Data_Directory_Structure.md for the updated directory structure needed as input!")
        exit()
    if constant_cfg.get(G_STUDY_NAME) is not None and study_name != constant_cfg.get(G_STUDY_NAME):
        print("ERROR! {} from constant config is not consistent with study directory: {}".format(constant_cfg[G_STUDY_NAME], study_name))
        print("{} is now given directly by the folder name !".format(G_STUDY_NAME))
        exit()
    constant_cfg[G_STUDY_NAME] = study_name

    constant_cfg["n_cpu_per_sim"] = n_cpu_per_sim
    constant_cfg["evaluate"] = evaluate
    constant_cfg["log_level"] = log_level
    constant_cfg["keep_old"] = keep_old
    if random_seed is not None:
        constant_cfg[G_RANDOM_SEED] = random_seed

    # combine constant and scenario parameters into verbose scenario parameters
    for i, scenario_cfg in enumerate(scenario_cfgs):
        scenario_cfgs[i] = constant_cfg + scenario_cfg

    # perform simulation(s)
    print(f"Simulation of {len(scenario_cfgs)} scenarios on {n_parallel_sim} processes with {n_cpu_per_sim} cpus per simulation ...")
    if n_parallel_sim == 1:
        for scenario_cfg in scenario_cfgs:
            if continue_next_after_error:
                try:
                    run_single_simulation(scenario_cfg)
                except:
                    traceback.print_exc()
            else:
                run_single_simulation(scenario_cfg)
    else:
        if n_cpu_per_sim == 1:
            mp_pool = mp.Pool(n_parallel_sim)
            mp_pool.map(run_single_simulation, scenario_cfgs)
        else:
            n_scenarios = len(scenario_cfgs)
            rest_scenarios = n_scenarios
            current_scenario = 0
            while rest_scenarios != 0:
                if rest_scenarios >= n_parallel_sim:
                    par_processes = [None for i in range(n_parallel_sim)]
                    for i in range(n_parallel_sim):
                        par_processes[i] = mp.Process(target=run_single_simulation, args=(scenario_cfgs[current_scenario],))
                        current_scenario += 1
                        par_processes[i].start()
                    for i in range(n_parallel_sim):
                        par_processes[i].join()
                        rest_scenarios -= 1
                else:
                    par_processes = [None for i in range(rest_scenarios)]
                    for i in range(rest_scenarios):
                        par_processes[i] = mp.Process(target=run_single_simulation, args=(scenario_cfgs[current_scenario],))
                        current_scenario += 1
                        par_processes[i].start()
                    for i in range(rest_scenarios):
                        par_processes[i].join()
                        rest_scenarios -= 1


def warn_non_optimal_repositioning(constant_csv, scenario_csv):
    """AlonsoMoraRepositioning writes 70_repo_am_opt_model_infeasible_*.lp whenever Gurobi ends without an optimal
    solution (e.g. TimeLimit hit) and then skips repositioning -> results may depend on machine speed."""
    constant_cfg = config.ConstantConfig(constant_csv)
    study_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(constant_csv))))
    for scenario_cfg in config.ScenarioConfig(scenario_csv):
        output_dir = os.path.join(mtsm.FLEETPY_DIR, "studies", study_name, "results", (constant_cfg + scenario_cfg)[G_SCENARIO_NAME])
        lp_files = [f for f in os.listdir(output_dir) if f.startswith("70_repo_am_opt_model_infeasible_")]
        if lp_files:
            print(f"{Fore.RED}WARNING: {len(lp_files)} repositioning solves were not optimal (Gurobi status != OPTIMAL),"
                  f" results may not be reproducible: {output_dir}{Style.RESET_ALL}")


# FleetPy's operator settings are fixed here (op_module, op_max_VR_con, repositioning method, horizons, timestep, the
# scenario names): docs/open_issues.md I-41
def create_config_files(sc,study_area,repositioning,fleet_size):
    # FleetPy's travel times per period (since 2026-11-24): the column nw_dynamic_f only when the area has
    # network_dynamics.csv, so that the scenario file (and FleetPy's 00_config.json) stays as before without it
    dynamics = {"nw_dynamic_f": "network_dynamics.csv"} if has_network_dynamics(study_area) else {}

    with open(sc, 'w+', newline='') as csvfile_config:
        if repositioning == True:
            fieldnames_config = ["op_module", "scenario_name", "rq_file", "op_fleet_composition","op_max_VR_con","forecast_f","op_repo_method","op_repo_horizons","op_repo_timestep"]
        else:
            fieldnames_config = ["op_module", "scenario_name", "rq_file", "op_fleet_composition"]
        fieldnames_config += list(dynamics)
        writer_config = csv.DictWriter(csvfile_config, fieldnames=fieldnames_config)
        writer_config.writeheader()
        if repositioning == True:
            op_module="PoolingIRSOnly"
            scenario_name="example_pool_repo_AM_sc_1"
            rq_file=mtsm.fleetpy_demand_name(study_area)  # "<area>_debug_False_fleetpy_demand.csv" until 2026-11-25 (I-40)
            op_fleet_composition="%s_vehtype:" % str(study_area) + str(fleet_size)  # lemon_grove_vehtype until 2026-11-24
            op_max_VR_con=int(3)
            forecast_f=""  # empty, as in the tracked files (until 2026-11-24 a space; FleetPy reads both as None)
            op_repo_method="AlonsoMoraRepositioning"
            op_repo_horizons=int(60)
            op_repo_timestep=int(300)
            writer_config.writerow({"op_module": op_module, "scenario_name": scenario_name, "rq_file": rq_file,
                                    "op_fleet_composition": op_fleet_composition,"op_max_VR_con": op_max_VR_con, "forecast_f": forecast_f,
                                    "op_repo_method": op_repo_method, "op_repo_horizons": op_repo_horizons,"op_repo_timestep": op_repo_timestep,
                                    **dynamics})
        else:
            op_module = "PoolingIRSOnly"
            scenario_name = "example_pool_irsonly_sc_1"
            rq_file = mtsm.fleetpy_demand_name(study_area)  # as above
            op_fleet_composition = "%s_vehtype:" % str(study_area) + str(fleet_size)  # lemon_grove_vehtype until 2026-11-24
            writer_config.writerow({"op_module": op_module, "scenario_name": scenario_name, "rq_file": rq_file,
                                    "op_fleet_composition": op_fleet_composition, **dynamics})
    csvfile_config.close()
