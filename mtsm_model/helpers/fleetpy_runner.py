"""The only MTSM module that talks to FleetPy.

FleetPy (fleetpy/) is upstream TUM-VT/FleetPy with the local changes listed in fleetpy/LOCAL_CHANGES.md. It imports
itself as the top-level package `src` and finds its data/ and studies/ folders next to src/, so fleetpy/ is put on
sys.path here. The Lemon Grove inputs for FleetPy are kept in mtsm_data/lemon_grove/fleetpy_inputs/ (same folder layout
as fleetpy/) and copied into fleetpy/ before each run (stage_inputs).

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

import pandas as pd
from colorama import Fore, Style

import mtsm_paths as mtsm

if mtsm.FLEETPY_DIR not in sys.path:
    sys.path.insert(0, mtsm.FLEETPY_DIR)
import src.misc.config as config
from src.misc.init_modules import load_simulation_environment
from src.misc.globals import G_RANDOM_SEED, G_SCENARIO_NAME, G_STUDY_NAME

MOD_STR = "MoD_0"
MM_STR = "Assertion"

# FleetPy inputs of the Lemon Grove run besides the two config files; paths relative to both
# mtsm_data/lemon_grove/fleetpy_inputs/ and fleetpy/
LG_STAGED_INPUTS = [
    "data/networks/lemon_grove_example_network/base/nodes.csv",
    "data/networks/lemon_grove_example_network/base/edges.csv",
    "data/networks/lemon_grove_example_network/base/crs.info",
    "data/fleetctrl/initial_vehicle_distribution/lemon_grove_example_network/imbalanced.csv",
    "data/vehicles/lemon_grove_vehtype.csv",
]


def stage_inputs(constant_config_file, scenario_file):
    """Copy the two config files (which must be in mtsm_data/lemon_grove/fleetpy_inputs/) and LG_STAGED_INPUTS into
    fleetpy/, at the same relative paths. Returns the paths of the copied config files, to run FleetPy with."""
    rel_cfgs = []
    for f in (constant_config_file, scenario_file):
        rel = os.path.relpath(f, mtsm.LG_FLEETPY_INPUTS_DIR)
        if rel.startswith(".."):
            raise ValueError(f"FleetPy config file {f} is not in {mtsm.LG_FLEETPY_INPUTS_DIR}")
        rel_cfgs.append(rel)
    for rel in rel_cfgs + LG_STAGED_INPUTS:
        dst = os.path.join(mtsm.FLEETPY_DIR, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(mtsm.LG_FLEETPY_INPUTS_DIR, rel), dst)
    return tuple(os.path.join(mtsm.FLEETPY_DIR, rel) for rel in rel_cfgs)


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


def read_outputs_for_comparison(constant_csv, scenario_csv):
    """This function reads some output parameters for a test of meaningful results of the test cases.

    :param constant_csv: constant parameter definition
    :param scenario_csv: scenario definition
    :return: list of standard_eval data frames
    :rtype: list[DataFrame]
    """
    constant_cfg = config.ConstantConfig(constant_csv)
    scenario_cfgs = config.ScenarioConfig(scenario_csv)
    const_abs = os.path.abspath(constant_csv)
    study_name = os.path.basename(os.path.dirname(os.path.dirname(const_abs)))
    return_list = []
    for scenario_cfg in scenario_cfgs:
        complete_scenario_cfg = constant_cfg + scenario_cfg
        scenario_name = complete_scenario_cfg[G_SCENARIO_NAME]
        output_dir = os.path.join(mtsm.FLEETPY_DIR, "studies", study_name, "results", scenario_name)
        standard_eval_f = os.path.join(output_dir, "standard_eval.csv")
        tmp_df = pd.read_csv(standard_eval_f, index_col=0)
        tmp_df.loc[G_SCENARIO_NAME, MOD_STR] = scenario_name
        return_list.append((tmp_df))
    return return_list


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


def check_assertions(list_eval_df, all_scenario_assertion_dict, log_file):
    """This function checks assertions of scenarios to give a quick impression if results are fitting.

    :param list_eval_df: list of evaluation data frames
    :param all_scenario_assertion_dict: dictionary of scenario id to assertion dictionaries
    :param log_file: the result of each check is appended to this file
    :return: list of (scenario_name, mismatch_flag, tmp_df) tuples
    """
    list_result_tuples = []
    for sc_id, assertion_dict in all_scenario_assertion_dict.items():
        tmp_df = list_eval_df[sc_id]
        scenario_name = tmp_df.loc[G_SCENARIO_NAME, MOD_STR]
        print("-"*80)
        mismatch = False
        for k, v in assertion_dict.items():
            if tmp_df.loc[k, MOD_STR] != v:
                tmp_df.loc[k, MM_STR] = v
                mismatch = True
        if mismatch:
            prt_str = f"Scenario {scenario_name} has mismatch with assertions:/n{tmp_df}/n" + "-"*80 + "/n"
        else:
            prt_str = f"Scenario {scenario_name} results match assertions/n" + "-"*80 + "/n"
        print(prt_str)
        with open(log_file, "a") as fh:
            fh.write(prt_str)
        list_result_tuples.append((scenario_name, mismatch, tmp_df))
    return list_result_tuples


def create_config_files(sc,study_area,repositioning,fleet_size):

    with open(sc, 'w+', newline='') as csvfile_config:
        if repositioning == True:
            fieldnames_config = ["op_module", "scenario_name", "rq_file", "op_fleet_composition","op_max_VR_con","forecast_f","op_repo_method","op_repo_horizons","op_repo_timestep"]
        else:
            fieldnames_config = ["op_module", "scenario_name", "rq_file", "op_fleet_composition"]
        writer_config = csv.DictWriter(csvfile_config, fieldnames=fieldnames_config)
        writer_config.writeheader()
        if repositioning == True:
            op_module="PoolingIRSOnly"
            scenario_name="example_pool_repo_AM_sc_1"
            rq_file="%s_debug_False_fleetpy_demand.csv" % str(study_area)
            op_fleet_composition="lemon_grove_vehtype:"+str(fleet_size)
            op_max_VR_con=int(3)
            forecast_f=" "
            op_repo_method="AlonsoMoraRepositioning"
            op_repo_horizons=int(60)
            op_repo_timestep=int(300)
            writer_config.writerow({"op_module": op_module, "scenario_name": scenario_name, "rq_file": rq_file,
                                    "op_fleet_composition": op_fleet_composition,"op_max_VR_con": op_max_VR_con, "forecast_f": forecast_f,
                                    "op_repo_method": op_repo_method, "op_repo_horizons": op_repo_horizons,"op_repo_timestep": op_repo_timestep})
        else:
            op_module = "PoolingIRSOnly"
            scenario_name = "example_pool_irsonly_sc_1"
            rq_file = "%s_debug_False_fleetpy_demand.csv" % str(study_area)
            op_fleet_composition = "lemon_grove_vehtype:" + str(fleet_size)
            writer_config.writerow({"op_module": op_module, "scenario_name": scenario_name, "rq_file": rq_file,
                                    "op_fleet_composition": op_fleet_composition})
    csvfile_config.close()
