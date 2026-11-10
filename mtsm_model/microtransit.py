"""Run FleetPy on the microtransit demand of an iteration and feed its results back into the super-network
(restructuring step 6, docs/entry_script_refactor_plan.md).

Moved unchanged from run_examples_new_parking.py, including the commented-out "Ritun added" block, which adds
synthetic microtransit demand (syn_rq) before FleetPy runs; it is kept on purpose, with its import.

"""
import os

import pandas as pd
from colorama import Fore, Style

from mtsm_model.helpers import fleetpy_runner as fleetpy
import mtsm_paths as mtsm
from mtsm_model.helpers import update_network_files as update
from mtsm_model import config
from pre_process.generate_demand_files import synthesize_requests_with_trend_time as syn_rq


def run_fleetpy_and_update_networks(cfg, area, scen, *, cc, log_level, log_f, iteration):
    """Run FleetPy (cc, sc: its constant and scenario configs), write the final super-networks with its waiting and
    travel times (update_network_files), and read its rejection rate and waiting time.
    Returns wait_times (per period), rejection_rate, last_rejection_rate, last_fleetpy_wait_time.
    area: scenarios.StudyArea, scen: scenarios.Scenario; demand_file and new_fleetpy_demand are used only by the
    commented-out "Ritun added" block."""
    sc, repositioning, microtransit_run, headway = scen.sc, scen.repositioning, scen.microtransit_run, scen.headway
    virstop, M_operating_hrs, fleet_size = scen.virstop, scen.M_operating_hrs, scen.fleet_size
    study_area, demand_file, new_fleetpy_demand = area.study_area, area.demand_file, area.new_fleetpy_demand
    LOG_F = log_f
    print("running FleetPy....according to demand component result")
    print(f"{Fore.RED}Running Fleetpy from position 2 {Style.RESET_ALL}")
    ############################################# Ritun added #############################################
    # full_demand_df = pd.read_csv(demand_file)
    # micro_demand_df = pd.read_csv(new_fleetpy_demand)
    # num_M_travelers = len(micro_demand_df)
    # extra_demand = num_M_travelers * 3
    # new_rq_id_start = 60000
    # new_rows = syn_rq(
    #     new_fleetpy_demand,
    #     new_fleetpy_demand,
    #     extra_demand,
    #     new_rq_id_start,
    #     42,
    #     True,
    #     "ordered",
    #     # "undirected" (pair strength, random direction) or "ordered"
    #     0.5,
    #     # chance to flip direction when preserve_od=True
    #     18000,  # 5:00 AM
    #     72000,  # 8:00 PM
    #     300,  # 5-minute bins for trend
    #     0.5  # Laplace smoothing per time bin
    # )
    # print(f"{Fore.RED}New Fleetpy demand file created. New rq from {new_rq_id_start + 5}{Style.RESET_ALL}")
    # print(f"{Fore.RED}Total global agents entering FleetPy: {num_M_travelers}{Style.RESET_ALL}")
    # print(f"{Fore.RED}Local agents added to FleetPy: {extra_demand}{Style.RESET_ALL}")
    # print(f"{Fore.RED}Total demand in FleetPy: {num_M_travelers+extra_demand}{Style.RESET_ALL}")
    #######################################################################################################
    # FleetPy runs on copies of the inputs in mtsm_data/lemon_grove/fleetpy_inputs/ placed inside fleetpy/
    cc_fleetpy, sc_fleetpy = fleetpy.stage_inputs(cc, sc)
    fleetpy.run_scenarios(cc_fleetpy, sc_fleetpy, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1, random_seed=cfg.random_seed)
    fleetpy.warn_non_optimal_repositioning(cc_fleetpy, sc_fleetpy)
    list_results = fleetpy.read_outputs_for_comparison(cc_fleetpy, sc_fleetpy)
    all_scenario_assert_dict = {0: {"number users": 88}}
    fleetpy.check_assertions(list_results, all_scenario_assert_dict, LOG_F)
    print("FleetPy finishes. Now update the microtransit part in super-network.....","iteration:",iteration)
    wait_times = update.update_network_files(repositioning,microtransit_run,headway,virstop,M_operating_hrs,fleet_size,study_area,iteration,
                                config.AGGREGATION)

    # Ritun added: Feb 14
    if repositioning == True:
        Fleetpy_output_folder = os.path.join(mtsm.FLEETPY_RESULTS_DIR, "example_pool_repo_AM_sc_1")
    else:
        Fleetpy_output_folder = os.path.join(mtsm.FLEETPY_RESULTS_DIR, "example_pool_irsonly_sc_1")
    Fleetpy_eval_file = os.path.join(Fleetpy_output_folder,
                                     "standard_eval.csv")
    df_fleetpy = pd.read_csv(Fleetpy_eval_file, index_col=0,
                             header=0)
    frac_booking_served = df_fleetpy.loc["modal split rq"][
        "MoD_0"]
    per_created_offers = df_fleetpy.loc["% created offers"][
        "MoD_0"]
    rejection_rate = (100 - per_created_offers) / 100
    last_rejection_rate = rejection_rate
    print(
        f"PER CREATED OFFERS:{per_created_offers}, AND REJECTION RATE:{rejection_rate}")
    last_fleetpy_wait_time = float(df_fleetpy.loc["waiting time"][
        "MoD_0"])

    return wait_times, rejection_rate, last_rejection_rate, last_fleetpy_wait_time
