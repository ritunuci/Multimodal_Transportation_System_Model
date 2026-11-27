"""Study areas and scenarios of a model run (restructuring step 8, docs/entry_script_refactor_plan.md).

- load_study_area(): what a study area needs for all its scenarios (folders, networks, travelers, link dicts).
- scenarios(): the scenario loops (repositioning x FRT headway x virtual stops x fleet size x operating periods x
  microtransit setup); yields one Scenario per model run. Each list has one element in the current runs.

Moved from run_examples_new_parking.py. scenarios() is a generator, so the work done in the outer loops (the FRT
headway in the initial networks, FleetPy's scenario config) happens at the same point as before: just before the first
scenario that needs it. (Until 2026-11-24 the outer loop also computed the FRT-only accessibility; removed.)
"""
import os
import sys
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from mtsm_model.helpers import fleetpy_runner as fleetpy
from mtsm_model.helpers import folder_directory as fld_dir
import mtsm_paths as mtsm
from mtsm_model.helpers import network_algorithms as n_a
from mtsm_model.helpers import output_performance_metrics as output_metrics
from mtsm_model.helpers import synthetic_demand
from mtsm_model.helpers import testing_scenario_creation as tst_scen_create
from mtsm_model.helpers import update_initial_network as init_net
from mtsm_model import config
from mtsm_model import mtsm_global_parameters as gp
from mtsm_model.networks import read_period_networks


@dataclass
class StudyArea:
    study_area: str
    headway_scenarios: Any
    fleet_size_scenarios: Any
    demand_folder: str
    initial_network_folder: str
    final_network_folder: str
    fleetpy_demand_folder: str
    output_folder: str
    new_fleetpy_demand: str  # FleetPy's demand file, written in each iteration
    transit_line_dist_list: Any
    transit_line_duration: Any
    evaluation_file: str
    demand_file: str  # the travelers
    MicroTransitNodes: Any  # super-network node -> FleetPy node
    microtransit_setup_scenarios: Any
    time_periods: Any
    auto_network: Any  # {time period: car network} (since 2026-11-24; the same network for all in whole-day mode)
    initial_super_network_dir: Any
    initial_super_network: Any
    final_super_network_dir: Any
    final_super_network: Any
    agent_list_: Any  # the travelers (requests)
    tt_num_agents: int
    transit_link_list: Any
    transit_link_vmt: Any  # FRT link VMT / passengers with microtransit, summed over the scenarios' iterations
    transit_link_pax: Any
    off_micro_transit_link_pax: Any  # the same for the fixed-route-only base case
    off_micro_transit_link_vmt: Any
    # the demand file has the column auto_available (2026-11-24; docs/period_networks_and_car_availability_plan.md,
    # step 2): the individual results then report it
    has_auto_available: bool = False
    # demand_upscaling (I-32, 2026-11-25): the first request id of the synthetic FleetPy requests; None when off
    synthetic_id_start: Any = None


@dataclass
class Scenario:
    repositioning: bool
    headway: int  # FRT headway (min)
    num_headway_scen: int  # 1-based position in the loop
    virstop: int  # virtual stops (%)
    num_virstop_scen: int
    fleet_size: int
    num_fleet_size_scen: int
    scs_path: str  # FleetPy's scenario folder
    sc: str  # FleetPy's scenario config
    operating_periods: Any  # microtransit operating periods
    num_operating_periods_scen: int
    M_operating_hrs: int
    F_operating_hrs: int
    F_transit_trips: str  # the FRT demand file, written in each iteration
    microtransit_run: str  # "micro" or "micro_only"


def load_study_area(cfg, study_area):
    headway_scenarios = [cfg.headway]  # [30,60]  #Ritun
    fleet_size_scenarios = cfg.read_fleet_size

    demand_folder,initial_network_folder,final_network_folder,fleetpy_demand_folder,output_folder=fld_dir.determine_folders(study_area)
    # (until 2026-11-25 "<area>_debug_False_fleetpy_demand.csv", I-40)
    new_fleetpy_demand = os.path.join(fleetpy_demand_folder, mtsm.fleetpy_demand_name(study_area))
    #############
    ## transit information
    ##########
    transit_line_dist_list = output_metrics.get_transit_line_dist(study_area)
    transit_line_duration=output_metrics.get_transit_line_duration(study_area,transit_line_dist_list)

    print("study_area",study_area,"transit_line_duration ((route_id,direction),duration (h))",transit_line_duration)

    evaluation_file = mtsm.evaluation_file(study_area)  # (until 2026-11-25 "<area>_evaluation_zonal_partition_False.csv", I-40)
    paths = mtsm.area_paths(study_area)
    # demand/demand.csv (until 2026-11-24 demand_data/<area>_trips_nodes_study_area_with_beta.csv), or the sample file
    # when demand_upscaling is on (since 2026-11-25, I-32)
    try:
        demand_file = mtsm.run_demand_file(study_area, config.PARAMETERS)
    except ValueError as e:
        sys.exit(f"ERROR: {e}")

    ##############################################
    #1108: read the initial network information
    #############################################
    MicroTransitNodes=OrderedDict()
    for i in range(config.NUM_WALK_NODES):
        MicroTransitNodes[config.MICROTRANSIT_NODE_OFFSET + i] = i #lemon_grove: microtransit node 1171 - corresponding to - walking node 0 (microtransit node 0 in fleetpy)
    ########
    microtransit_setup_scenarios = ["micro", "non_micro","micro_only"]
    time_periods = config.TIME_PERIODS  # the study area's periods (["AM", "MD", "PM", "EV"] until 2026-11-24)

    # networks/car_network.csv (until 2026-11-24 initial_network/auto_edges.csv), or one file per time period
    # (car_network_<P>.csv, since 2026-11-24): {period: network}, each distinct file read once
    auto_network = read_period_networks(paths.car_network_files(time_periods))

    #### Create initial and final network scenarios
    initial_super_network_dir, initial_super_network, final_super_network_dir, final_super_network = tst_scen_create.scen_create(
        microtransit_setup_scenarios, config.VIRTUAL_STOP_SCENARIOS, config.OPERATING_PERIODS_SCENARIOS, time_periods,
        fleet_size_scenarios, headway_scenarios, initial_network_folder, final_network_folder, config.BASE_FRT_HEADWAY,
        base_frt_headway_file=paths.super_network_frt_base_headway_file, study_area=study_area)
    #################################################
    # 1108: prepare for the request files - demand side
    ###################################################
    agent_list_all = n_a.read_request(demand_file)
    # only the trips departing within the model's day are modelled (since 2026-11-26, config.in_model_day); the
    # demand file is not changed
    agent_list_ = [agent for agent in agent_list_all if config.in_model_day(agent.rq_time)]
    if len(agent_list_) < len(agent_list_all):
        before = sum(1 for agent in agent_list_all if agent.rq_time < config.MODEL_DAY_START)
        after = len(agent_list_all) - len(agent_list_) - before
        print(f"study_area: {study_area} trips outside the model's day ({config.MODEL_DAY_START:g}-"
              f"{config.MODEL_DAY_END:g} s) not modelled: {before} before, {after} after; {len(agent_list_)} of "
              f"{len(agent_list_all)} kept")
    tt_num_agents=len(agent_list_)
    has_auto_available = "auto_available" in n_a.demand_columns(demand_file)
    no_car = sum(1 for agent in agent_list_ if not agent.auto_available)
    if has_auto_available:
        print("study_area:", study_area, "travelers without a car (auto_available False):", no_car)
    if no_car and "micro_only" in config.MICROTRANSIT_RUNNING_SCENARIOS:
        # micro_only offers no transit outside the microtransit operating periods: such a traveler has no option
        sys.exit(f"ERROR: {demand_file}: {no_car} travelers have no car (auto_available False); the scenario "
                 f"micro_only offers them no mode outside the microtransit operating periods "
                 f"(docs/period_networks_and_car_availability_plan.md, decision 6)")
    print("study_area:", study_area,"total number of agents:",tt_num_agents,"\n")
    synthetic_id_start = None
    if config.DEMAND_UPSCALING:
        # (the ids of all trips of the file, also those outside the model's day, so no synthetic id repeats one)
        synthetic_id_start = synthetic_demand.synthetic_id_start([agent.rq_id for agent in agent_list_all],
                                                                 config.DEMAND_SAMPLE_SHARE)
        print(f"demand_upscaling: {demand_file} holds a share {config.DEMAND_SAMPLE_SHARE} of the travelers; the "
              f"results are scaled by {config.DEMAND_SCALE}; synthetic FleetPy request ids from {synthetic_id_start}\n")

    transit_link_list=output_metrics.get_transit_link_info(study_area)
    transit_link_vmt,transit_link_pax,off_micro_transit_link_pax,off_micro_transit_link_vmt=output_metrics.vmt_and_link_dict_creation(time_periods,transit_link_list)

    return StudyArea(study_area, headway_scenarios, fleet_size_scenarios, demand_folder, initial_network_folder,
                     final_network_folder, fleetpy_demand_folder, output_folder, new_fleetpy_demand,
                     transit_line_dist_list, transit_line_duration, evaluation_file, demand_file, MicroTransitNodes,
                     microtransit_setup_scenarios, time_periods, auto_network, initial_super_network_dir,
                     initial_super_network, final_super_network_dir, final_super_network, agent_list_, tt_num_agents,
                     transit_link_list, transit_link_vmt, transit_link_pax, off_micro_transit_link_pax,
                     off_micro_transit_link_vmt, has_auto_available, synthetic_id_start=synthetic_id_start)


def scenarios(cfg, area, log_f):
    """Yield the scenarios of the study area, in the order of the old nested loops. log_f: FleetPy's log file, emptied
    before each scenario."""
    study_area = area.study_area
    for repositioning in config.REPOSITIONING_LIST:

        # the fare structure: the former fare scenario 10, the only one (docs/progress.md, "Only fare scenario 10"); its
        # number, the parameter fare_scenario, was printed here as "Testing Scenario" until 2026-11-25 (I-40)
        print("aggregation:",config.AGGREGATION,"; mode_change_threshold:",config.MODE_CHANGE_THRESHOLD,"; convergence_gap:",config.CONVERGENCE_GAP,"; maximum_iteration:",config.MAXIMUM_ITERATION,  "; F_gas_per_mile ($/mi):",config.F_GAS_PER_MILE,
        "; M_gas_per_mile ($/mi):", config.M_GAS_PER_MILE,"; repositioning",repositioning,"; transit_fare ($):", cfg.transit_fare,"; microtransit_start_fare ($):",cfg.microtransit_start_fare,"; microtransit_dist_based_rate ($/mi):",cfg.microtransit_dist_based_rate*config.MILE_METER,
              "; Peak fare factor (0~1):",cfg.PkFareFactor,"; Off-peak fare factor (0~1):",cfg.OffPkFareFactor,"; Fixed to Micro discount factor (0~1):",cfg.Fixed2MicroFactor,"; Micro to Fixed discount factor (0~1):",cfg.Micro2FixedFactor)

        num_headway_scen = 0
        for headway in area.headway_scenarios: #put bus design parameter in the most outer loop
            init_net.update_initial_net_with_bayesian_headway(headway,study_area,config.VIRTUAL_STOP_SCENARIOS)  #Ritun
            num_headway_scen+=1
            num_virstop_scen = 0
            for virstop in config.VIRTUAL_STOP_SCENARIOS: #virtual stops - not necessarily influence the cost, but will influence the mobility
                num_virstop_scen+=1
                num_fleet_size_scen = 0
                for fleet_size in area.fleet_size_scenarios: #fleetsize - influence the cost & mobility
                    num_fleet_size_scen+=1
                    scs_path = mtsm.area_paths(study_area).fleetpy_scenarios_dir  # the area's FleetPy constant configs
                    num_operating_periods_scen = 0

                    # FleetPy's scenario file for this fleet size, written into FleetPy's staging folder (since
                    # 2026-11-24; until then a tracked file per fleet size in the area's folder, written there if missing)
                    sc = fleetpy.scenario_config_file(study_area, repositioning, fleet_size)

                    for operating_periods in config.OPERATING_PERIODS_SCENARIOS: #fleetsize - influence the cost & mobility
                        num_operating_periods_scen+=1
                        M_operating_hrs = config.microtransit_operating_hours(operating_periods)
                        F_operating_hrs = config.PARAMETERS[gp.G_FRT_OPERATING_HOURS]  # fixed route transit 19 hrs


                        # (until 2026-11-25 "debug_False_F_transit_demand_...", I-40)
                        F_transit_trips = mtsm.frt_demand_file(study_area, fleet_size, M_operating_hrs, headway, virstop)

                        for microtransit_run in config.MICROTRANSIT_RUNNING_SCENARIOS:
                            if microtransit_run == "micro_only" and num_headway_scen>1:
                                continue
                            else:
                                # (a branch "if len(sys.argv) > 1: fleetpy.run_scenarios(*sys.argv)" from FleetPy's
                                # example script was removed on 2026-11-11: it handed --config to FleetPy)
                                # touch log file
                                with open(log_f, "w") as _:
                                    pass

                                yield Scenario(repositioning, headway,
                                               num_headway_scen, virstop, num_virstop_scen, fleet_size,
                                               num_fleet_size_scen, scs_path, sc, operating_periods,
                                               num_operating_periods_scen, M_operating_hrs, F_operating_hrs,
                                               F_transit_trips, microtransit_run)
