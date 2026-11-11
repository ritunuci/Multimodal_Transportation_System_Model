"""Study areas and scenarios of a model run (restructuring step 8, docs/entry_script_refactor_plan.md).

- load_study_area(): what a study area needs for all its scenarios (folders, networks, travelers, link dicts).
- scenarios(): the scenario loops (repositioning x FRT headway x virtual stops x fleet size x operating periods x
  microtransit setup); yields one Scenario per model run. Each list has one element in the current runs.

Moved from run_examples_new_parking.py. scenarios() is a generator, so the work done in the outer loops (the FRT
headway in the initial networks, the FRT-only accessibility, FleetPy's scenario config) happens at the same point as
before: just before the first scenario that needs it.
"""
import os
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from mtsm_model.helpers import fleetpy_runner as fleetpy
from mtsm_model.helpers import folder_directory as fld_dir
import mtsm_paths as mtsm
from mtsm_model.helpers import network_algorithms as n_a
from mtsm_model.helpers import output_performance_metrics as output_metrics
from mtsm_model.helpers import testing_scenario_creation as tst_scen_create
from mtsm_model.helpers import update_initial_network as init_net
from mtsm_model import config
from mtsm_model import mtsm_global_parameters as gp


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
    auto_network: Any
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


@dataclass
class Scenario:
    repositioning: bool
    headway: int  # FRT headway (min)
    num_headway_scen: int  # 1-based position in the loop
    tot_weighted_5_min_F: Any  # accessibility of the fixed-route-only network
    tot_weighted_10_min_F: Any
    tot_weighted_15_min_F: Any
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
    new_fleetpy_demand = os.path.join(fleetpy_demand_folder,"%s_debug_False_fleetpy_demand.csv" % str(study_area))
    #############
    ## transit information
    ##########
    transit_line_dist_list = output_metrics.get_transit_line_dist(study_area)
    transit_line_duration=output_metrics.get_transit_line_duration(study_area,transit_line_dist_list)

    print("study_area",study_area,"transit_line_duration (route_id,duration (h))",transit_line_duration)

    evaluation_file = os.path.join(output_folder, "%s_evaluation_zonal_partition_False.csv" % str(study_area))
    demand_file = os.path.join(demand_folder,"%s_trips_nodes_study_area_with_beta.csv" % str(study_area))

    ##############################################
    #1108: read the initial network information
    #############################################
    MicroTransitNodes=OrderedDict()
    for i in range(config.NUM_WALK_NODES):
        MicroTransitNodes[config.MICROTRANSIT_NODE_OFFSET + i] = i #lemon_grove: microtransit node 1171 - corresponding to - walking node 0 (microtransit node 0 in fleetpy)
    ########
    microtransit_setup_scenarios = ["micro", "non_micro","micro_only"]
    time_periods = ["AM", "MD", "PM", "EV"]

    auto_network_dir=os.path.join(initial_network_folder,"auto_edges.csv")
    auto_network = n_a.read_super_network(auto_network_dir)

    #### Create initial and final network scenarios
    initial_super_network_dir, initial_super_network, final_super_network_dir, final_super_network=tst_scen_create.scen_create(microtransit_setup_scenarios,config.VIRTUAL_STOP_SCENARIOS,config.OPERATING_PERIODS_SCENARIOS,time_periods,fleet_size_scenarios,headway_scenarios,initial_network_folder,final_network_folder,config.BASE_FRT_HEADWAY)
    #################################################
    # 1108: prepare for the request files - demand side
    ###################################################
    agent_list_ = n_a.read_request(demand_file)
    tt_num_agents=len(agent_list_)
    print("study_area:", study_area,"total number of agents:",tt_num_agents,"\n")

    transit_link_list=output_metrics.get_transit_link_info(study_area)
    transit_link_vmt,transit_link_pax,off_micro_transit_link_pax,off_micro_transit_link_vmt=output_metrics.vmt_and_link_dict_creation(time_periods,transit_link_list)

    return StudyArea(study_area, headway_scenarios, fleet_size_scenarios, demand_folder, initial_network_folder,
                     final_network_folder, fleetpy_demand_folder, output_folder, new_fleetpy_demand,
                     transit_line_dist_list, transit_line_duration, evaluation_file, demand_file, MicroTransitNodes,
                     microtransit_setup_scenarios, time_periods, auto_network, initial_super_network_dir,
                     initial_super_network, final_super_network_dir, final_super_network, agent_list_, tt_num_agents,
                     transit_link_list, transit_link_vmt, transit_link_pax, off_micro_transit_link_pax,
                     off_micro_transit_link_vmt)


def scenarios(cfg, area, log_f):
    """Yield the scenarios of the study area, in the order of the old nested loops. log_f: FleetPy's log file, emptied
    before each scenario."""
    study_area = area.study_area
    for repositioning in config.REPOSITIONING_LIST:

        # the fare structure: the former fare scenario 10, the only one (docs/progress.md, "Only fare scenario 10")
        test_scenario = config.FARE_SCENARIO
        print("aggregation:",config.AGGREGATION,"; mode_change_threshold:",config.MODE_CHANGE_THRESHOLD,"; convergence_gap:",config.CONVERGENCE_GAP,"; maximum_iteration:",config.MAXIMUM_ITERATION,  "; F_gas_per_mile ($/mi):",config.F_GAS_PER_MILE,
        "; M_gas_per_mile ($/mi):", config.M_GAS_PER_MILE,"; repositioning",repositioning,"; Testing Scenario:",test_scenario,"; transit_fare ($):", cfg.transit_fare,"; microtransit_start_fare ($):",cfg.microtransit_start_fare,"; microtransit_dist_based_rate ($/mi):",cfg.microtransit_dist_based_rate*config.MILE_METER,
              "; Peak fare factor (0~1):",cfg.PkFareFactor,"; Off-peak fare factor (0~1):",cfg.OffPkFareFactor,"; Fixed to Micro discount factor (0~1):",cfg.Fixed2MicroFactor,"; Micro to Fixed discount factor (0~1):",cfg.Micro2FixedFactor)

        num_headway_scen = 0
        for headway in area.headway_scenarios: #put bus design parameter in the most outer loop
            init_net.update_initial_net_with_bayesian_headway(headway,study_area)  #Ritun
            tot_weighted_5_min_F,tot_weighted_10_min_F,tot_weighted_15_min_F=output_metrics.all_scenario_fixed_acc_calculation(headway,study_area,test_scenario)
            num_headway_scen+=1
            num_virstop_scen = 0
            for virstop in config.VIRTUAL_STOP_SCENARIOS: #virtual stops - not necessarily influence the cost, but will influence the mobility
                num_virstop_scen+=1
                num_fleet_size_scen = 0
                for fleet_size in area.fleet_size_scenarios: #fleetsize - influence the cost & mobility
                    num_fleet_size_scen+=1
                    scs_path = mtsm.LG_FLEETPY_SCENARIOS_DIR
                    num_operating_periods_scen = 0

                    if repositioning ==True:
                        sc = os.path.join(scs_path, "%s_example_ir_heuristics_repositioning_%s_veh.csv" % (str(study_area), str(fleet_size)))
                    else:
                        sc = os.path.join(scs_path, "%s_example_ir_only_%s_veh.csv" % (str(study_area), str(fleet_size)))
                    isExist = os.path.exists(sc)
                    if isExist==False:
                        fleetpy.create_config_files(sc, study_area, repositioning, fleet_size)

                    for operating_periods in config.OPERATING_PERIODS_SCENARIOS: #fleetsize - influence the cost & mobility
                        num_operating_periods_scen+=1
                        M_operating_hrs = config.microtransit_operating_hours(operating_periods)
                        F_operating_hrs = config.PARAMETERS[gp.G_FRT_OPERATING_HOURS]  # fixed route transit 19 hrs


                        F_transit_trips = os.path.join(area.fleetpy_demand_folder, "debug_False_F_transit_demand_%s_op_hr_%s_hw_%s_virstop_%s.csv" % (str(fleet_size),str(M_operating_hrs), str(headway), str(virstop)))

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
                                               num_headway_scen, tot_weighted_5_min_F, tot_weighted_10_min_F,
                                               tot_weighted_15_min_F, virstop, num_virstop_scen, fleet_size,
                                               num_fleet_size_scen, scs_path, sc, operating_periods,
                                               num_operating_periods_scen, M_operating_hrs, F_operating_hrs,
                                               F_transit_trips, microtransit_run)
