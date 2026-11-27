"""Run FleetPy on the microtransit demand of an iteration and feed its results back into the super-network
(restructuring step 6, docs/entry_script_refactor_plan.md).

Moved unchanged from run_examples_new_parking.py. With demand_upscaling on (since 2026-11-25, docs/open_issues.md
I-32, I-45), synthetic microtransit requests are added to FleetPy's demand file before FleetPy runs
(synthetic_demand.add_synthetic_requests). Until then this was a commented-out "Ritun added" block (3 synthetic
requests per request, for a 25 % sample of the travelers).

"""
import os

import pandas as pd
from colorama import Fore, Style

from mtsm_model.helpers import fleetpy_runner as fleetpy
import mtsm_paths as mtsm
from mtsm_model.helpers import update_network_files as update
from mtsm_model import config
from mtsm_model import mtsm_global_parameters as gp
from mtsm_model.helpers import synthetic_demand


def run_fleetpy_and_update_networks(cfg, area, scen, *, cc, log_level, log_f, iteration):
    """Run FleetPy (cc, sc: its constant and scenario configs), write the final super-networks with its waiting and
    travel times (update_network_files), and read its rejection rate and waiting time.
    Returns wait_times (per period), rejection_rate, last_rejection_rate, last_fleetpy_wait_time.
    area: scenarios.StudyArea, scen: scenarios.Scenario."""
    sc, repositioning, microtransit_run, headway = scen.sc, scen.repositioning, scen.microtransit_run, scen.headway
    virstop, M_operating_hrs, fleet_size = scen.virstop, scen.M_operating_hrs, scen.fleet_size
    study_area, new_fleetpy_demand = area.study_area, area.new_fleetpy_demand
    print("running FleetPy....according to demand component result")
    print(f"{Fore.RED}Running Fleetpy from position 2 {Style.RESET_ALL}")
    if config.DEMAND_UPSCALING:
        # The demand file is a sample of the travelers: FleetPy also serves 1 / share - 1 copies of each request of the
        # sample, so the fleet is as busy as with all travelers (docs/open_issues.md I-32, I-45). A copy is shifted in
        # time by up to +- synthetic_time_shift_min within the request's time period, and has a virtual stop within
        # synthetic_stop_radius_m walking distance of the request's as origin and as destination. The copies are not
        # MTSM travelers: the trips, fares and logsums come from the sample alone, while FleetPy's waiting times,
        # rejection rate and fleet results include them. (Until 2026-11-25 a commented-out "Ritun added" block: 3 per
        # request drawn from the time-of-day profile, ids from 60005, times 5:00-20:00, seed 42, not sorted.)
        network_files = mtsm.area_paths(study_area).micro_network_files(scen.virstop, config.TIME_PERIODS)
        radius = config.PARAMETERS[gp.G_SYNTHETIC_STOP_RADIUS_M]
        nearby = {p: synthetic_demand.nearby_stops(f, config.NUM_WALK_NODES, radius) for p, f in network_files.items()}
        n_real, n_new = synthetic_demand.add_synthetic_requests(
            new_fleetpy_demand, config.DEMAND_SAMPLE_SHARE, area.synthetic_id_start,
            [config.PERIOD_BOUNDS[p] for p in config.TIME_PERIODS], nearby, config.TIME_PERIODS,
            config.PARAMETERS[gp.G_SYNTHETIC_TIME_SHIFT_MIN] * 60, cfg.random_seed)
        print(f"{Fore.RED}FleetPy demand: {n_real} requests of the sample + {n_new} synthetic (ids from "
              f"{area.synthetic_id_start}) = {n_real + n_new}{Style.RESET_ALL}")
    # FleetPy's simulation window for this run (since 2026-11-26, branch TRA_resubmission; user's decisions): from the
    # start of the first microtransit operating period to one time step after the latest request of FleetPy's demand
    # file (at least the end of the last operating period); the scenario file is written again with it
    # (fleetpy_runner.simulation_window). Until then the constant config's start_time 0 and end_time 86400
    time_step = int(float(fleetpy.constant_config_value(cc, "time_step")))
    start_time, end_time, before_start = fleetpy.simulation_window(
        new_fleetpy_demand, [config.PERIOD_BOUNDS[p] for p in scen.operating_periods], time_step)
    sc = fleetpy.scenario_config_file(study_area, repositioning, fleet_size, window=(start_time, end_time))
    print(f"FleetPy simulation window: start_time {start_time} s, end_time {end_time} s")
    if before_start:
        print(f"{Fore.RED}WARNING: {before_start} FleetPy requests before start_time {start_time} s are not "
              f"simulated (FleetPy reads only start_time <= rq_time < end_time){Style.RESET_ALL}")
    # FleetPy runs on copies of the inputs in mtsm_data/<area>/fleetpy/ placed inside fleetpy/
    cc_fleetpy, sc_fleetpy = fleetpy.stage_inputs(cc, sc, study_area)
    fleetpy.run_scenarios(cc_fleetpy, sc_fleetpy, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1, random_seed=cfg.random_seed)
    fleetpy.warn_non_optimal_repositioning(cc_fleetpy, sc_fleetpy)
    # (FleetPy's example check of 88 users, which mismatched in every iteration, removed on 2026-11-24)
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
