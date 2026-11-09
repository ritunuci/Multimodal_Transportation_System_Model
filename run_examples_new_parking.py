# -------------------------------------------------------------------------------------------------------------------- #
# external imports
# ----------------
from colorama import Fore, Style
import os
import sys
import pandas as pd
import multiprocessing as mp
from collections import OrderedDict
import time
import datetime
import csv
import numpy as np
import math
# FleetPy (fleetpy/) is reached only through fleetpy_runner
# ---------------------------------------------------------
import fleetpy_runner as fleetpy

import convergence_test as conv_test
import network_algorithms as n_a
import binary_choice as b_c
import random
import update_network_files as update
import output_performance_metrics as output_metrics
import folder_directory as fld_dir
import testing_scenario_creation as tst_scen_create
import pre_process.dictionary_initialization as dict_init
import update_initial_network as init_net
from pre_process.generate_demand_files import synthesize_requests_with_trend_time as syn_rq
import mtsm_paths as mtsm
from tools.check_inputs import check_inputs

# global variables
# ----------------
LOG_F = os.path.join(mtsm.CODE_ROOT, "standard_bugfix.log")


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

# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == "__main__":
    mp.freeze_support()

    # Reproducibility (docs/progress.md, Phase 1): str hashing (set/dict order) is randomized per process unless
    # PYTHONHASHSEED is fixed before the interpreter starts -> re-launch once with a fixed hash seed and no
    # inherited PYTHONPATH (stale entries could shadow modules).
    if os.environ.get("PYTHONHASHSEED") != "0":
        import subprocess
        child_env = dict(os.environ, PYTHONHASHSEED="0")
        child_env.pop("PYTHONPATH", None)
        sys.exit(subprocess.call([sys.executable] + sys.argv, env=child_env))

    start_time = datetime.datetime.now()
    pre_timeatfinished=start_time
    print("program starts here......start time is:", start_time)
    input_para_folder = mtsm.INPUT_PARAMETER_DIR
    input_para_dir=os.path.join(input_para_folder,"input_parameter.csv")
    TRPartA_test_scenario_list=[]
    debug_mode_list=[]
    test_area=[]
    read_fleet_size=[]
    mile_meter = 1609.34

    ##
    with open(input_para_dir) as f:

        csvreader = csv.DictReader(f)
        for data in csvreader:
            TRPartA = str2bool(str(data["TRPartA"]))
            TRPartA_test_scenario_list.append(int(data["TRPartA_test_scenario_list"]))
            debug_mode_list.append(str2bool(str(data["debug_mode_list"])))
            transit_fare = float(data["transit_fare ($)"])
            microtransit_dist_based_rate = float(data["microtransit_dist_based_rate ($/mile)"])/mile_meter
            microtransit_start_fare = float(data["microtransit_start_fare ($)"])
            test_area.append(str(data["test_area"]))
            BayesianOptimization = str2bool(str(data["BayesianOptimization"]))
            fleet_size = int(data["Fleet_size"])
            PkFareFactor = float(data["PkFareFactor"])
            OffPkFareFactor=float(data["OffPkFareFactor"])
            Fixed2MicroFactor=float(data["Fixed2MicroFactor"])
            Micro2FixedFactor=float(data["Micro2FixedFactor"])
            headway = int(data["FRT_headway"]) #Ritun
            base_FRT_headway = 20
            base_FRT_fare = 2.5  # Ritun: base fare for fixed route transit
            initial_rejection_rate = float(data["initial_rejection_rate"])
            micro_rejection_penalty = float(data["micro_rejection_penalty ($)"])
            # one seed drives both the mode-choice draws here and FleetPy's random_seed; 0 if the column is absent
            random_seed = int(data.get("random_seed") or 0)

            read_fleet_size.append(fleet_size)

    f.close()

    # The code supports only Lemon Grove with TRPartA=TRUE, BayesianOptimization=TRUE and debug_mode_list=FALSE; the
    # branches for the other values were removed (docs/progress.md). The three columns stay in input_parameter.csv
    # because the optimizer writes its parameters by column position (docs/open_issues.md, I-15).
    unsupported = []
    if any(area != "lemon_grove" for area in test_area):
        unsupported.append(f"test_area={test_area} (only lemon_grove)")
    if not TRPartA:
        unsupported.append("TRPartA=False")
    if not BayesianOptimization:
        unsupported.append("BayesianOptimization=False")
    if any(debug_mode_list):
        unsupported.append("debug_mode_list=True")
    if unsupported:
        sys.exit("ERROR: configuration in %s is not supported: %s"
                 % (input_para_dir, ", ".join(unsupported)))
    input_problems = check_inputs()
    if input_problems:
        print(f"{Fore.RED}WARNING: frozen inputs differ from mtsm_data/MANIFEST.csv -> results are not comparable to "
              f"docs/reference_results: {input_problems}{Style.RESET_ALL}")
    for folder in (mtsm.LG_FINAL_NETWORK_DIR, mtsm.LG_INDIV_OUTPUT_DIR, mtsm.LG_OUTPUT_DIR):
        os.makedirs(folder, exist_ok=True)

    random.seed(random_seed)
    np.random.seed(random_seed)
    print("random_seed:", random_seed, "PYTHONHASHSEED:", os.environ.get("PYTHONHASHSEED"))

    # True: individual-level convergence test (used). False: aggregate-level test, kept for later but unfinished;
    # see the convergence test in the iteration loop below and docs/open_issues.md, I-16.
    indiv_converg_test=True

    maximum_iteration = 15
    ###############
    #
    aggregation = "whole_region" #["census_track","whole_region"]
    convergence_gap = 0.01       # Ritun changed it from 0.01
    #####################
    #Gas cost
    #####
    F_gas_per_mile = 0.350  #The fuel cost for the CNG buses averaged $0.35 per mile
    M_gas_per_mile = 0.550  # gasoline cost: 0.00019 dollar per meter, 0.305 dollar per mile # Ritun: set it to 0.55 $/mile



    #################
    ##########
    # Different operating hours testing scenarios
    operating_period_1 = ["AM", "PM"] #10 hr
    operating_period_2 = ["AM", "MD", "PM"] #15hr
    operating_period_3 = ["AM", "MD", "PM", "EV"] #19hr

    #####################
    # output_metrics
    mode_change_threshold=0.05



    microtransit_running_scenarios = ["micro"]
    repositioning_list=[True]
    operating_periods_scenarios = [operating_period_2]  # just for testing [operating_period_1,operating_period_2]
    virtual_stop_scenarios = [75]  # [75,100]
    headway_scenarios = [headway]  # [30,60]  #Ritun
    fleet_size_scenarios = read_fleet_size

    for study_area in test_area:
        demand_folder,initial_network_folder,final_network_folder,fleetpy_demand_folder,output_folder=fld_dir.determine_dolders(study_area)
        new_fleetpy_demand = os.path.join(fleetpy_demand_folder,"%s_debug_False_fleetpy_demand.csv" % str(study_area))
        #############
        ## transit information
        ##########
        transit_line_dist_list = output_metrics.get_transit_line_dist(study_area)
        transit_line_duration=output_metrics.get_transit_line_duration(study_area,transit_line_dist_list)

        print("study_area",study_area,"transit_line_duration (route_id,duration (h))",transit_line_duration)
        scenario_count = 0


        evaluation_file = os.path.join(output_folder, "%s_evaluation_zonal_partition_False.csv" % str(study_area))
        demand_file = os.path.join(demand_folder,"%s_trips_nodes_study_area_with_beta.csv" % str(study_area))



    ##############################################
    #1108: read the initial network information
    #############################################
        MicroTransitNodes=OrderedDict()
        for i in range(1099):
            MicroTransitNodes[1171 + i] = i #lemon_grove: microtransit node 1171 - corresponding to - walking node 0 (microtransit node 0 in fleetpy)
        ########
        microtransit_setup_scenarios = ["micro", "non_micro","micro_only"]
        time_periods = ["AM", "MD", "PM", "EV"]

        auto_network_dir=os.path.join(initial_network_folder,"auto_edges.csv")
        auto_network = n_a.read_super_network(auto_network_dir)

        ##############################
        #### Create initial and final network scenarios
        ###################
        ######################################################

        initial_super_network_dir, initial_super_network, final_super_network_dir, final_super_network=tst_scen_create.scen_create(microtransit_setup_scenarios,virtual_stop_scenarios,operating_periods_scenarios,time_periods,fleet_size_scenarios,headway_scenarios,initial_network_folder,final_network_folder,base_FRT_headway)
        #################################################
        # 1108: prepare for the request files - demand side
        ###################################################
        agent_list_ = n_a.read_request(demand_file)
        tt_num_agents=len(agent_list_)
        print("study_area:", study_area,"total number of agents:",tt_num_agents,"\n")

        transit_link_list=output_metrics.get_transit_link_info(study_area)
        transit_link_vmt,transit_link_pax,off_micro_transit_link_pax,off_micro_transit_link_vmt=output_metrics.vmt_and_link_dict_creation(time_periods,transit_link_list)


        with open(evaluation_file, 'w+', newline='') as csvfile:

            fieldnames = ["test_scen","dscrptn","study_area","repositioning","microtrasnit",'hdwy (min)', 'vir_stop (%)', 'flt_sz', 'op_periods',"tt_agents", "car_users", "car_mode_share (%)",
                          "trsit_mode_users (W_M_F)","transit_mode_share (%)","pure_M_users","M_mode_share (%)","M_trips","pure_F_users","F_mode_share (%)","F_trips","pure_walk_users",
                          "W_mode_share (%)","walk_users","M_pls_F_users","M_pls_F_mode_share (%)","F_oper_cost ($)", "M_oper_cost ($)", "F_revenue ($)","M_revenue ($)","Total_T_revenue ($)","tot_sub ($)",
                          "sub_per_F_trip ($)","sub_per_F_rider ($)","sub_per_M_trip ($)","sub_per_M_rider ($)","sub_per_T_trip ($)","sub_per_T_rider ($)","sub_per_M_pax_mile ($/mi)","sub_per_F_pax_mile ($/mi)","sub_per_T_pax_mile ($/mi)",
                          "sub_per_M_VMT ($/mi)","sub_per_F_VMT ($/mi)","sub_per_T_VMT ($/mi)",
                          "tt_auto_gas_cost ($)","auto_gas_cost_per_mile ($/mi)",
                          "avg_M_fare", "avg_F_fare", "avg_T_fare", "avg_auto_gas_cost",
                          "tt_o_pckt_cost ($)","tt_mob_lgsm_inc_with_micro", "tt_gen_cost",
                          "tt_mode_switch", "M_avg_wait_time (s)", "F_avg_wait_time (s)","avg_walk_time (s)","tt_walk_time (h)",
                          "car_VMT (mi)","M_VMT (mi)","M_PMT (mi)","M_PMT/M_VMT","F_VMT (mi)","F_PMT (mi)","F_PMT/F_VMT","tt_VMT (mi)",
                          "tt_walk_dist (mi)", "wghted_acc_emp_5_min","wghted_acc_emp_10_min","wghted_acc_emp_15_min", "M_util_rate (%)","M_veh_occ","M_avg_speed (mph)","cnvrg (iter, sm_sq_per_diff)", "fleetpy_wait", "rejection_rate"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for repositioning in repositioning_list:

                ##########################
                # store the auto shortest path result
                ########################
                agent_auto_visited_temp, agent_auto_time_visited_temp, agent_auto_dist_visited_temp, agent_auto_fare_visited_temp, agent_auto_path, agent_auto_time_path, agent_auto_time_path_all_ = dict_init.auto_sp_dict_init()

                ##########################
                # store the transit shortest path result
                ########################
                agent_visited_temp_F, agent_time_visited_temp_F, agent_dist_visited_temp_F, agent_fare_visited_temp_F, agent_path_F, agent_time_path_F, agent_transit_time_path_all_F, agent_transit_dist_path_all_F = dict_init.F_transit_sp_dict_init()

                for test_scenario in TRPartA_test_scenario_list:
                    print("aggregation:",aggregation,"; mode_change_threshold:",mode_change_threshold,"; convergence_gap:",convergence_gap,"; maximum_iteration:",maximum_iteration,  "; F_gas_per_mile ($/mi):",F_gas_per_mile,
                    "; M_gas_per_mile ($/mi):", M_gas_per_mile,"; repositioning",repositioning,"; Testing Scenario:",test_scenario,"; transit_fare ($):", transit_fare,"; microtransit_start_fare ($):",microtransit_start_fare,"; microtransit_dist_based_rate ($/mi):",microtransit_dist_based_rate*mile_meter,
                          "; Peak fare factor (0~1):",PkFareFactor,"; Off-peak fare factor (0~1):",OffPkFareFactor,"; Fixed to Micro discount factor (0~1):",Fixed2MicroFactor,"; Micro to Fixed discount factor (0~1):",Micro2FixedFactor)



                    num_headway_scen = 0
                    for headway in headway_scenarios: #put bus design parameter in the most outer loop
                        init_net.update_initial_net_with_bayesian_headway(headway,study_area)  #Ritun
                        tot_weighted_5_min_F,tot_weighted_10_min_F,tot_weighted_15_min_F=output_metrics.all_scenario_fixed_acc_calculation(headway,study_area,test_scenario)
                        num_headway_scen+=1
                        num_virstop_scen = 0
                        for virstop in virtual_stop_scenarios: #virtual stops - not necessarily influence the cost, but will influence the mobility
                            num_virstop_scen+=1
                            num_fleet_size_scen = 0
                            for fleet_size in fleet_size_scenarios: #fleetsize - influence the cost & mobility
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

                                for operating_periods in operating_periods_scenarios: #fleetsize - influence the cost & mobility
                                    num_operating_periods_scen+=1
                                    if operating_periods==["AM", "MD", "PM", "EV"]:
                                        M_operating_hrs=19
                                    elif operating_periods==["AM", "MD", "PM"]:
                                        M_operating_hrs = 15
                                    else:
                                        M_operating_hrs = 10
                                    F_operating_hrs = 19 # fixed route transit 19 hrs


                                    F_transit_trips = os.path.join(fleetpy_demand_folder, "debug_False_F_transit_demand_%s_op_hr_%s_hw_%s_virstop_%s.csv" % (str(fleet_size),str(M_operating_hrs), str(headway), str(virstop)))

                                    for microtransit_run in microtransit_running_scenarios:
                                        if microtransit_run == "micro_only" and num_headway_scen>1:
                                            continue
                                        else:
                                            if len(sys.argv) > 1:
                                                fleetpy.run_scenarios(*sys.argv)
                                            else:
                                                import time
                                                # touch log file
                                                with open(LOG_F, "w") as _:
                                                    pass



                                                ################################################
                                                #1108: prepare the network files - supply side
                                                ###################################################
                                                print("Current Scenario:", scenario_count, "th senario", "....headway",headway, "(mins),", "scen", num_headway_scen,
                                                      "; virtual_stop:", virstop, "(%),", "scen", num_virstop_scen,"; fleet_size:", fleet_size, "(veh),", "scen", num_fleet_size_scen,
                                                      "; operating_periods:", operating_periods, "scen,",num_operating_periods_scen,"microtransit_scen:",microtransit_run,";")

                                                iteration=0
                                                rejection_rate = initial_rejection_rate / 100  # Ritun added: Feb 14
                                                last_rejection_rate = 0
                                                iter_agent_choice_prob=OrderedDict()
                                                iter_agent_selected_mode=OrderedDict()
                                                converged=False

                                                # Metrics of turn-off microtransit
                                                off_micro_T_trips = 0
                                                off_micro_W_trips = 0
                                                off_micro_F_trips = 0
                                                off_micro_auto_trips = 0
                                                off_micro_agent_tot_walk_time = OrderedDict()
                                                off_micro_agent_F_tot_wait_time = OrderedDict()
                                                off_micro_agent_op_cost = OrderedDict()
                                                off_micro_VMT_F = 0
                                                off_micro_VMT_W = 0
                                                off_micro_VMT_auto = 0
                                                off_micro_agent_gen_cost = OrderedDict()
                                                off_micro_ag_tot_tt = OrderedDict()
                                                off_micro_ag_mode = OrderedDict()
                                                off_micro_ag_tot_dist = OrderedDict()
                                                off_micro_agent_ran_num = OrderedDict()
                                                off_micro_agent_choice_prob = OrderedDict()
                                                off_micro_c_tt_travel_time = OrderedDict()
                                                off_micro_f_tt_travel_time = OrderedDict()
                                                off_micro_ag_VMT_W = OrderedDict()
                                                transit_tt_VMT = 0
                                                transit_tt_VMT_base = 0




                                                num_converged=0

                                                pre_iter_prob_T = OrderedDict()
                                                pre_iter_mode = OrderedDict()
                                                pre_iter_M_info = OrderedDict()
                                                pre_iter_F_info = OrderedDict()

                                                ag_VMT_F = OrderedDict()
                                                ag_VMT_M = OrderedDict()
                                                ag_VMT_W = OrderedDict()

                                                ag_num_W_trips = OrderedDict()
                                                ag_num_M_trips = OrderedDict()
                                                ag_num_F_trips = OrderedDict()

                                                #agent level attributes
                                                travel_time_delta = OrderedDict()
                                                gen_cost_delta = OrderedDict()
                                                mob_logsum_delta = OrderedDict()
                                                agent_beta_fare = OrderedDict()

                                                agent_O = OrderedDict()
                                                agent_D = OrderedDict()
                                                agent_rq_time = OrderedDict()
                                                agent_choice_prob = OrderedDict()
                                                agent_switch_mode = OrderedDict()
                                                agent_ran_num = OrderedDict()
                                                agent_M_tot_wait_time = OrderedDict()
                                                agent_F_tot_wait_time = OrderedDict()
                                                agent_M_tot_travel_time = OrderedDict()
                                                agent_F_tot_travel_time = OrderedDict()

                                                agent_M_tot_travel_dist = OrderedDict()
                                                agent_F_tot_travel_dist = OrderedDict()

                                                agent_tot_walk_time = OrderedDict()
                                                agent_travel_time = OrderedDict()
                                                agent_travel_dist = OrderedDict()
                                                agent_op_cost = OrderedDict()  # agent_out-of-pocket cost
                                                agent_op_cost_Fix  = OrderedDict()
                                                agent_op_cost_Micro = OrderedDict()

                                                agent_gen_cost = OrderedDict()

                                                iter_sum_sq_per_diff=[]

                                                agent_income = OrderedDict()
                                                agent_transit_15min_acc = OrderedDict()

                                                rejection_rate_dict = {}  # Ritun added Feb 14

                                                running_avg_rejection_rate = []  # Ritun added Feb 14

                                                last_fleetpy_wait_time = 0


                                                while converged==False:
                                                    # Ritun added Feb 14
                                                    rejection_rate_dict[iteration] = rejection_rate
                                                    if iteration >= 3:
                                                        rejection_rate = (rejection_rate_dict[iteration - 1] +
                                                                          rejection_rate_dict[iteration - 2] +
                                                                          rejection_rate_dict[
                                                                              iteration - 3]) / 3
                                                    total_rejection_penalty = rejection_rate * micro_rejection_penalty
                                                    print(f"TOATL REJECTION PENALTY IS: {total_rejection_penalty}")

                                                    print("iteration:",iteration)
                                                    iter_agent_choice_prob[iteration]=OrderedDict()
                                                    log_level = "info"

                                                    if repositioning == True:
                                                        cc = os.path.join(scs_path, "%s_constant_config_ir_repo.csv"% str(study_area))
                                                    else:
                                                        cc = os.path.join(scs_path, "%s_constant_config_ir.csv" % str(study_area))


                                                    print("Demand Component (choice model).....")
                                                    ###########################################
                                                    # Initial dictionaries to store performance metrics

                                                    num_car_trips = 0
                                                    num_transit_users = 0
                                                    num_M_trips = 0
                                                    num_F_trips = 0
                                                    num_W_trips = 0

                                                    pure_M_user = 0
                                                    pure_F_user = 0
                                                    M_F_user = 0

                                                    #calculate VMT when micro transit is turned on
                                                    VMT_M = 0
                                                    VMT_F = 0
                                                    VMT_auto = 0
                                                    VMT_W = 0




                                                    #################################################
                                                    #Demand component: calculate how many travelers will choose transit, how many will choose auto
                                                    # Write into FleetPy's demand input directly
                                                    #######################################################
                                                    # Read the updated super-network file
                                                    ###############

                                                    if microtransit_run == "micro_only":
                                                        for time_period in time_periods:
                                                            if iteration == 0:
                                                                initial_super_network[microtransit_run][virstop][M_operating_hrs] = n_a.read_super_network(initial_super_network_dir[microtransit_run][virstop][M_operating_hrs])
                                                            else:
                                                                final_super_network[microtransit_run][virstop][M_operating_hrs][time_period][fleet_size]=n_a.read_super_network(final_super_network_dir[microtransit_run][virstop][M_operating_hrs][time_period][fleet_size])
                                                    elif microtransit_run=="micro":
                                                        for time_period in time_periods:
                                                            if iteration == 0:
                                                                #[microtransit][headway][virstop][M_operating_hrs][time_period]
                                                                initial_super_network[microtransit_run][headway][virstop][M_operating_hrs] = n_a.read_super_network(initial_super_network_dir[microtransit_run][headway][virstop][M_operating_hrs])
                                                            else:
                                                                try:
                                                                    final_super_network[microtransit_run][headway][virstop][M_operating_hrs][time_period][fleet_size]=n_a.read_super_network(final_super_network_dir[microtransit_run][headway][virstop][M_operating_hrs][time_period][fleet_size])
                                                                except:
                                                                    raise Exception("iteration",iteration,"converged",converged,"....headway",headway, "(mins),", "microtransit", microtransit_run,"; virtual_stop:", virstop, "(%),", "time_period", time_period,"; fleet_size:", fleet_size, "(veh)," ,"; operating_periods:", operating_periods,";")
                                                    initial_super_network["non_micro"][
                                                        base_FRT_headway] = n_a.read_super_network(
                                                        initial_super_network_dir["non_micro"][
                                                            base_FRT_headway])

                                                    change_mode_ag_list=[]
                                                    print("Demand Component.....assigning travelers to different modes...")
                                                    with open(F_transit_trips, 'w+', newline='') as csvfile_F:
                                                        fieldnames_F = ["depart_time", "start", "end", "request_id"]
                                                        writer_F = csv.DictWriter(csvfile_F, fieldnames=fieldnames_F)
                                                        writer_F.writeheader()

                                                        with open(new_fleetpy_demand, 'w+', newline='') as csvfile_M:
                                                            fieldnames_M = ["rq_time", "start", "end", "request_id"]
                                                            writer_M = csv.DictWriter(csvfile_M, fieldnames=fieldnames_M)
                                                            writer_M.writeheader()

                                                            M_rq_id_list = []
                                                            for agent in agent_list_:
                                                                change_mode=True  #change_mode is True, unless the probability difference is smaller than the mode_change_threshold

                                                                origin = agent.rq_O
                                                                dest = agent.rq_D
                                                                rq_time = agent.rq_time
                                                                rq_id = agent.rq_id

                                                                agent_O[rq_id] = origin
                                                                agent_D[rq_id] = dest
                                                                agent_rq_time[rq_id] = rq_time
                                                                agent_income[rq_id]= agent.income
                                                                agent_transit_15min_acc[rq_id] = agent.transit_15min_acc
                                                                agent_beta_fare[rq_id] = agent.bt_t_fr

                                                                if rq_time <= (10 * 3600):
                                                                    time_period = "AM"
                                                                elif rq_time <= (15 * 3600):
                                                                    time_period = "MD"
                                                                elif rq_time <= (20 * 3600):
                                                                    time_period = "PM"
                                                                else:
                                                                    time_period = "EV"



                                                                agent_M_tot_travel_dist[rq_id] = 0
                                                                agent_F_tot_travel_dist[rq_id] = 0
                                                                #1108 Siwei: read the initial super-network according to "microtransit", "fixed route trasnit headway","virstop", and "time_period"
                                                                T_F_network = \
                                                                    initial_super_network["non_micro"][
                                                                        base_FRT_headway]
                                                                if iteration==0:
                                                                    if microtransit_run == "micro":
                                                                        if time_period in operating_periods:
                                                                            T_micro_network = initial_super_network["micro"][headway][virstop][M_operating_hrs]
                                                                        else:
                                                                            T_micro_network = T_F_network
                                                                    if microtransit_run == "micro_only":
                                                                        if time_period in operating_periods:
                                                                            T_micro_network = initial_super_network["micro_only"][virstop][M_operating_hrs]
                                                                        else:
                                                                            T_micro_network = auto_network

                                                                else:
                                                                    if microtransit_run == "micro":
                                                                        if time_period in operating_periods:
                                                                            T_micro_network = final_super_network["micro"][headway][virstop][M_operating_hrs][time_period][fleet_size]
                                                                        else:
                                                                            T_micro_network = T_F_network
                                                                    if microtransit_run == "micro_only":
                                                                        if time_period in operating_periods:
                                                                            T_micro_network = final_super_network["micro_only"][virstop][M_operating_hrs][time_period][fleet_size]
                                                                        else:
                                                                            T_micro_network = auto_network

                                                                # *****don't calculate it along the way - only*********
                                                                # calculate generalized cost shortest path for agent on Auto network
                                                                if test_scenario == TRPartA_test_scenario_list[0]:
                                                                    parking_dur, bt_c_gas, auto_visited_temp, auto_time_visited_temp, auto_dist_visited_temp, auto_fare_visited_temp,F_fare_visited_temp,M_fare_visited_temp, auto_path, auto_time_path,auto_dist_path = n_a.generalized_cost_dijsktra_OD_heap(study_area,auto_network, agent,transit_fare,microtransit_start_fare,microtransit_dist_based_rate,PkFareFactor,OffPkFareFactor,Fixed2MicroFactor,Micro2FixedFactor,test_scenario=0, mode="C", verbose=False, iteration=iteration)
                                                                    auto_time_path_all_ = n_a.getTrajectory_O_to_D(origin, dest,auto_time_path,auto_visited_temp)
                                                                    agent_auto_visited_temp[rq_id] = auto_visited_temp
                                                                    agent_auto_time_visited_temp[rq_id] = auto_time_visited_temp
                                                                    agent_auto_dist_visited_temp[rq_id] = auto_dist_visited_temp
                                                                    agent_auto_fare_visited_temp[rq_id] = auto_fare_visited_temp
                                                                    agent_auto_path[rq_id] = auto_path
                                                                    agent_auto_time_path[rq_id] = auto_time_path
                                                                    agent_auto_time_path_all_[rq_id] = auto_time_path_all_
                                                                else:
                                                                    auto_visited_temp = agent_auto_visited_temp[rq_id]
                                                                    auto_time_visited_temp = agent_auto_time_visited_temp[rq_id]
                                                                    auto_dist_visited_temp = agent_auto_dist_visited_temp[rq_id]
                                                                    auto_fare_visited_temp = agent_auto_fare_visited_temp[rq_id]
                                                                    auto_path = agent_auto_path[rq_id]
                                                                    auto_time_path = agent_auto_time_path[rq_id]
                                                                    auto_time_path_all_ = agent_auto_time_path_all_[rq_id]

                                                                # calculate generalized cost shortest path for agent on W_F network
                                                                if test_scenario == TRPartA_test_scenario_list[0]:
                                                                        visited_temp_F, time_visited_temp_F, dist_visited_temp_F, fare_visited_temp_F,F_fare_visited_temp_F,M_fare_visited_temp_F, path_F, time_path_F,dist_path_F = n_a.generalized_cost_dijsktra_OD_heap(study_area,T_F_network, agent,base_FRT_fare, microtransit_start_fare,microtransit_dist_based_rate,PkFareFactor,OffPkFareFactor,Fixed2MicroFactor,Micro2FixedFactor,test_scenario,mode="T",verbose=False, total_rejection_penalty=total_rejection_penalty, iteration=iteration)
                                                                        transit_time_path_all_F = n_a.getTrajectory_O_to_D(origin, dest,time_path_F,visited_temp_F)
                                                                        transit_dist_path_all_F = n_a.getTrajectory_O_to_D(origin, dest,dist_path_F,dist_visited_temp_F)  # calculate fixed transit VMT

                                                                        agent_visited_temp_F[rq_id] = visited_temp_F
                                                                        agent_time_visited_temp_F[rq_id] = time_visited_temp_F
                                                                        agent_dist_visited_temp_F[rq_id] = dist_visited_temp_F
                                                                        agent_fare_visited_temp_F[rq_id] = fare_visited_temp_F
                                                                        agent_path_F[rq_id] = path_F
                                                                        agent_time_path_F[rq_id] = time_path_F
                                                                        agent_transit_time_path_all_F[rq_id] = transit_time_path_all_F
                                                                        agent_transit_dist_path_all_F[rq_id] = transit_dist_path_all_F

                                                                else:
                                                                    visited_temp_F = agent_visited_temp_F[rq_id]
                                                                    time_visited_temp_F = agent_time_visited_temp_F[rq_id]
                                                                    dist_visited_temp_F = agent_dist_visited_temp_F[rq_id]
                                                                    fare_visited_temp_F = agent_fare_visited_temp_F[rq_id]
                                                                    path_F = agent_path_F[rq_id]
                                                                    time_path_F = agent_time_path_F[rq_id]
                                                                    transit_time_path_all_F = agent_transit_time_path_all_F[rq_id]
                                                                    transit_dist_path_all_F = agent_transit_dist_path_all_F[rq_id]

                                                                #calculate generalized cost shortest path for agent on W_M_F network
                                                                if microtransit_run == "micro_only" and (time_period not in operating_periods):
                                                                    aaa=0
                                                                else:
                                                                    visited_temp, time_visited_temp,dist_visited_temp,fare_visited_temp,F_fare_visited_temp,M_fare_visited_temp, path, time_path,dist_path = n_a.generalized_cost_dijsktra_OD_heap(study_area,T_micro_network,agent,transit_fare,microtransit_start_fare,microtransit_dist_based_rate,PkFareFactor,OffPkFareFactor,Fixed2MicroFactor,Micro2FixedFactor,test_scenario,mode="T",verbose=False, total_rejection_penalty=total_rejection_penalty, iteration=iteration)
                                                                    transit_time_path_all_ = n_a.getTrajectory_O_to_D(origin, dest, time_path, visited_temp)
                                                                    transit_dist_path_all_ = n_a.getTrajectory_O_to_D(origin, dest, dist_path,dist_visited_temp) #calculate microtransit and fixed transit VMT

                                                                if microtransit_run == "micro_only":
                                                                    aaa=0
                                                                    gen_cost_F = 0
                                                                    travel_time_F = 0
                                                                    travel_dist_F = 0
                                                                    agent_op_cost_F = 0
                                                                    if (time_period not in operating_periods):
                                                                        # calculate generalized cost
                                                                        gen_cost_T = 0
                                                                        # calculate travel time and distance
                                                                        travel_time_T = 0
                                                                        travel_dist_T = 0
                                                                        # calculate oout of pocket cost
                                                                        agent_op_cost_T = 0

                                                                        agent_F_fare = 0
                                                                        agent_M_fare = 0

                                                                    else:
                                                                        gen_cost_T = visited_temp[dest]
                                                                        travel_time_T = time_visited_temp[dest]
                                                                        travel_dist_T = dist_visited_temp[dest]
                                                                        agent_op_cost_T = fare_visited_temp[dest]

                                                                        agent_F_fare = 0
                                                                        agent_M_fare = M_fare_visited_temp[dest]
                                                                else:
                                                                    # calculate generalized cost
                                                                    gen_cost_T = visited_temp[dest]
                                                                    gen_cost_F = visited_temp_F[dest]  # 1107 Siwei: add the generalized cost for without microtransit scenario
                                                                    # calculate travel time and distance
                                                                    travel_time_T = time_visited_temp[dest]
                                                                    travel_time_F = time_visited_temp_F[dest]
                                                                    travel_dist_T = dist_visited_temp[dest]
                                                                    travel_dist_F = dist_visited_temp_F[dest]

                                                                    # calculate out of pocket cost
                                                                    agent_op_cost_T = fare_visited_temp[dest]
                                                                    agent_op_cost_F = fare_visited_temp_F[dest]

                                                                    agent_F_fare = F_fare_visited_temp[dest]
                                                                    agent_M_fare = M_fare_visited_temp[dest]
                                                                parking_dur_trip = parking_dur / 2
                                                                parking_dur_30_min_count = math.ceil(parking_dur_trip / 30)
                                                                if time_period in ["AM","PM"]:  # Ritun added for parking fee
                                                                    gen_cost_auto = auto_visited_temp[dest] + bt_c_gas * parking_dur_30_min_count * 1
                                                                else:
                                                                    gen_cost_auto = auto_visited_temp[dest] + bt_c_gas * parking_dur_30_min_count * 0.5

                                                                # calculate travel time savings by allowing microtransit
                                                                travel_time_auto=auto_time_visited_temp[dest]
                                                                travel_time_delta[rq_id] = travel_time_F - travel_time_T

                                                                travel_dist_auto = auto_dist_visited_temp[dest]
                                                                agent_op_cost_auto=auto_fare_visited_temp[dest]
                                                                gen_cost_delta[rq_id] = gen_cost_F - gen_cost_T
                                                                if microtransit_run == "micro_only" and (time_period not in operating_periods):
                                                                    prob_Auto, prob_T = 1,0
                                                                else:
                                                                    prob_Auto, prob_T = b_c.binary_logit_model(gen_cost_auto, gen_cost_T)

                                                                if iteration>0:
                                                                    diff_prob_T=abs(pre_iter_prob_T[rq_id]-prob_T)

                                                                    if diff_prob_T <= mode_change_threshold: # if probability does not change a lot, then we don't change agents' modes.
                                                                        change_mode=False
                                                                    else:
                                                                        change_mode = True #03/02/2026: Siwei added this line
                                                                        change_mode_ag_list.append(rq_id)


                                                                pre_iter_prob_T[rq_id]=prob_T
                                                                if microtransit_run == "micro_only":
                                                                    prob_Auto_no_micro, prob_T_no_micro = 1,0
                                                                else:
                                                                    prob_Auto_no_micro, prob_T_no_micro = b_c.binary_logit_model(gen_cost_auto, gen_cost_F)

                                                                # calculate the mobility logsum change (logsum delta)
                                                                mob_logsum_micro = b_c.mobility_logsum(gen_cost_auto, gen_cost_T)
                                                                mob_logsum_fixed = b_c.mobility_logsum(gen_cost_auto, gen_cost_F)
                                                                mob_logsum_delta[rq_id] = (mob_logsum_micro - mob_logsum_fixed)/agent_beta_fare[rq_id]

                                                                off_micro_agent_choice_prob[rq_id]= [prob_Auto_no_micro, prob_T_no_micro]
                                                                iter_agent_choice_prob[iteration][rq_id] = [prob_Auto, prob_T]


                                                                ran_num = random.random()
                                                                #calculate the output metrics of turn-off microtransit
                                                                if (num_virstop_scen == 1) and (num_fleet_size_scen == 1) and (num_operating_periods_scen == 1) and (iteration==0):
                                                                    off_micro_ag_tot_dist[rq_id] = 0
                                                                    off_micro_ag_tot_tt[rq_id] = 0
                                                                    off_micro_agent_gen_cost[rq_id] = 0
                                                                    off_micro_ag_VMT_W[rq_id] = 0
                                                                    off_micro_agent_F_tot_wait_time[rq_id] = 0
                                                                    off_micro_agent_tot_walk_time[rq_id] = 0

                                                                    off_micro_agent_ran_num[rq_id]=ran_num
                                                                    if ran_num < prob_T_no_micro:

                                                                        off_micro_ag_mode[rq_id] = "T"
                                                                        off_micro_T_trips += 1
                                                                        off_micro_ag_tot_tt[rq_id] = travel_time_F
                                                                        off_micro_ag_tot_dist[rq_id] = travel_dist_F/mile_meter

                                                                        off_micro_agent_gen_cost[rq_id]=gen_cost_F
                                                                        trimmed_transit_time_path_F = transit_time_path_all_F[1:-1]
                                                                        pre_link_type = None
                                                                        sum_link_type_F = 0  # recorde the pure walking trips
                                                                        # 11/07 Siwei: record the time of reaching the previous link
                                                                        pre_time = 0



                                                                        off_micro_agent_op_cost[rq_id] = agent_op_cost_F
                                                                        for (node, time, link_type,route) in trimmed_transit_time_path_F:
                                                                            # calculate the number of fixed route transit trip legs
                                                                            if (pre_link_type != 1 and pre_link_type != 3) and (link_type == 1):
                                                                                F_origin_node = node
                                                                                request_time = rq_time + int(time)
                                                                            if (pre_link_type == 1) and (link_type != 1 and link_type != 3):
                                                                                F_dest_node = pre_node
                                                                                off_micro_F_trips += 1

                                                                            # 11/07 Siwei: calculate the fixed route transit waiting time
                                                                            if (pre_link_type != 2) and (link_type == 2):
                                                                                F_wait_time = (time - pre_time)
                                                                                off_micro_agent_F_tot_wait_time[rq_id] += F_wait_time
                                                                            # 11/07 Siwei: calculate the walking time
                                                                            if link_type == 0:
                                                                                walk_time = (time - pre_time)
                                                                                off_micro_agent_tot_walk_time[rq_id] += walk_time


                                                                            pre_time = time
                                                                            sum_link_type_F += link_type
                                                                            pre_node = node
                                                                            pre_link_type = link_type
                                                                        if sum_link_type_F == 0:
                                                                            off_micro_W_trips += 1

                                                                        #calculate VMT for fixed transit and walking when microtransit turned off
                                                                        trimmed_transit_dist_path_F=transit_dist_path_all_F[1:-1]
                                                                        pre_dist = 0
                                                                        pre_node = transit_dist_path_all_[0]
                                                                        for (node, dist, link_type,route) in trimmed_transit_dist_path_F:
                                                                            # calculate the number of fixed route transit trip legs
                                                                            if link_type == 1:
                                                                                distance_F = dist - pre_dist
                                                                                off_micro_VMT_F+=(distance_F/mile_meter)
                                                                                off_micro_transit_link_vmt[time_period][(pre_node, node)] += (distance_F / mile_meter)
                                                                                off_micro_transit_link_pax[time_period][(pre_node, node)]+=1
                                                                            if link_type==0:
                                                                                distance_W = dist - pre_dist
                                                                                off_micro_VMT_W += (distance_W / mile_meter)
                                                                                off_micro_ag_VMT_W[rq_id]+=(distance_W / mile_meter)
                                                                            pre_dist = dist
                                                                            pre_node = node


                                                                    else:  # agent choose the car mode
                                                                        off_micro_ag_mode[rq_id] = "C"
                                                                        off_micro_ag_tot_tt[rq_id]= travel_time_auto
                                                                        off_micro_ag_tot_dist[rq_id] = travel_dist_auto/mile_meter
                                                                        off_micro_auto_trips+=1
                                                                        off_micro_agent_op_cost[rq_id] = agent_op_cost_auto  # agent_out-of-pocket
                                                                        off_micro_VMT_auto += (travel_dist_auto/mile_meter)
                                                                        off_micro_agent_gen_cost[rq_id]=gen_cost_auto



                                                                #turn on microtransit
                                                                if change_mode==True:

                                                                    if iteration ==0: #when it is in iteration 0, all travelers get M and F travel time initialized
                                                                        agent_switch_mode[rq_id] = 0
                                                                        agent_M_tot_travel_time[rq_id] = 0
                                                                        agent_F_tot_travel_time[rq_id] = 0
                                                                        ag_VMT_F[rq_id] = 0
                                                                        ag_VMT_W[rq_id] = 0
                                                                        ag_VMT_M[rq_id] = 0
                                                                        ag_num_W_trips[rq_id] = 0
                                                                        ag_num_M_trips[rq_id] = 0
                                                                        ag_num_F_trips[rq_id] = 0

                                                                    agent_ran_num[rq_id] = ran_num
                                                                    agent_choice_prob[rq_id] = [prob_Auto,prob_T]

                                                                    if ran_num < prob_T:  # agent choose the transit mode
                                                                        ##when mode change=true, and transit mode is chosen, all travelers get M and F travel time initialized
                                                                        current_mode = "T"
                                                                        pre_iter_mode[rq_id] = current_mode

                                                                        agent_switch_mode[rq_id] = 0
                                                                        agent_M_tot_travel_time[rq_id] = 0
                                                                        agent_F_tot_travel_time[rq_id] = 0
                                                                        ag_num_W_trips[rq_id] = 0
                                                                        ag_num_M_trips[rq_id] = 0
                                                                        ag_num_F_trips[rq_id] = 0



                                                                        agent_gen_cost[rq_id] = gen_cost_T
                                                                        if ran_num>=prob_T_no_micro:
                                                                            agent_switch_mode[rq_id]=1 #this means: if no microtransit, this agent will choose car, but with microtransit, this agent will choose transit mode
                                                                        trimmed_transit_time_path = transit_time_path_all_[1:-1]
                                                                        pre_link_type = None
                                                                        sum_link_type = 0  # recorde the pure walking trips
                                                                        # 11/07 Siwei: record the time of reaching the previous link
                                                                        pre_time = 0
                                                                        M_tot_wait_time = 0

                                                                        # 1107 Siwei
                                                                        agent_M_tot_wait_time[rq_id] = 0
                                                                        agent_F_tot_wait_time[rq_id] = 0



                                                                        agent_tot_walk_time[rq_id] = 0
                                                                        agent_travel_time[rq_id]=travel_time_T
                                                                        agent_travel_dist[rq_id] =travel_dist_T
                                                                        agent_op_cost[rq_id] = agent_op_cost_T  # agent_out-of-pocket cost

                                                                        agent_op_cost_Fix[rq_id] = agent_F_fare
                                                                        agent_op_cost_Micro[rq_id] = agent_M_fare

                                                                        for (node, time, link_type,route) in trimmed_transit_time_path:
                                                                            # calculate the number of microtransit trip legs
                                                                            if (pre_link_type != 4) and (link_type == 4): ##1228 testing!
                                                                                M_origin_node = node
                                                                                request_time = rq_time + round(time,0)
                                                                            if (pre_link_type == 4) and (link_type != 4): ##1228 testing!
                                                                                M_dest_node = pre_node
                                                                                # MicroTransitNodes
                                                                                rq_id_fleetpy = rq_id
                                                                                while (rq_id_fleetpy in M_rq_id_list): #this condition is to deal with the situation where 1 person has more than 1 microtransit trips
                                                                                    rq_id_fleetpy += 1

                                                                                try:
                                                                                    writer_M.writerow({'rq_time': request_time, 'start': MicroTransitNodes[M_origin_node],'end': MicroTransitNodes[M_dest_node], 'request_id': rq_id_fleetpy})
                                                                                except:
                                                                                    raise Exception("M_origin_node",M_origin_node,"M_dest_node",M_dest_node,"pre_link_type",pre_link_type,"link_type",link_type,"node",node,"pre_node",pre_node,"trimmed_transit_time_path",trimmed_transit_time_path)
                                                                                M_rq_id_list.append(rq_id_fleetpy)
                                                                                #document the previous iteration microtransit information
                                                                                #rq_time, start, end, request_id
                                                                                pre_iter_M_info[rq_id]=(request_time,MicroTransitNodes[M_origin_node],MicroTransitNodes[M_dest_node],rq_id_fleetpy)

                                                                                num_M_trips += 1
                                                                                ag_num_M_trips[rq_id] +=1
                                                                            # calculate the number of fixed route transit trip legs
                                                                            if (pre_link_type != 1 and pre_link_type != 3) and (link_type == 1):
                                                                                F_origin_node = node
                                                                                request_time = rq_time + int(time)
                                                                            if (pre_link_type == 1) and (link_type != 1 and link_type != 3):
                                                                                F_dest_node = pre_node
                                                                                num_F_trips += 1
                                                                                ag_num_F_trips[rq_id] +=1
                                                                                writer_F.writerow({'depart_time':request_time , 'start': F_origin_node,'end': F_dest_node,'request_id': rq_id})
                                                                                # document the previous iteration fixed route transit information
                                                                                # rq_time, start, end, request_id
                                                                                pre_iter_F_info[rq_id]=(request_time,F_origin_node,F_dest_node,rq_id)
                                                                            # 11/07 Siwei: calculate the microtransit waiting time
                                                                            if (pre_link_type != 5) and (link_type == 5):
                                                                                M_wait_time = (time - pre_time)
                                                                                if iteration>0 and M_wait_time == 180:
                                                                                    print(f"MICRO WAIT TIME = {M_wait_time}")
                                                                                agent_M_tot_wait_time[rq_id] += M_wait_time

                                                                            # 11/07 Siwei: calculate the fixed route transit waiting time
                                                                            if (pre_link_type != 2) and (link_type == 2):
                                                                                F_wait_time = (time - pre_time)
                                                                                agent_F_tot_wait_time[rq_id] += F_wait_time

                                                                            # 11/07 Siwei: calculate the walking time
                                                                            if link_type == 0:
                                                                                walk_time = (time - pre_time)
                                                                                agent_tot_walk_time[rq_id] += walk_time
                                                                            # 12/22 Siwei: calculate the microtransit travel time
                                                                            if link_type ==4:
                                                                                M_travel_time = (time - pre_time)
                                                                                #03/09/2026: Siwei add the following code for debug purpose
                                                                                if iteration>0 and M_travel_time == 0:
                                                                                    print(f"MICRO Link Travel Time = {M_travel_time}")

                                                                                agent_M_tot_travel_time[rq_id] += M_travel_time

                                                                            # 12/22 Siwei: calculate the fixed route transit travel time
                                                                            if link_type == 1 or link_type ==3:
                                                                                F_travel_time = (time - pre_time)
                                                                                agent_F_tot_travel_time[rq_id] += F_travel_time

                                                                            pre_time = time
                                                                            sum_link_type += link_type
                                                                            pre_node = node
                                                                            pre_link_type = link_type
                                                                        if sum_link_type == 0:
                                                                            num_W_trips += 1
                                                                            ag_num_W_trips[rq_id]+=1
                                                                        #calculate pure microtransit users:
                                                                        if ag_num_M_trips[rq_id] != 0 and ag_num_F_trips[rq_id] == 0:
                                                                            pure_M_user += 1
                                                                        # calculate pure fixed route transit users:
                                                                        if ag_num_M_trips[rq_id] == 0 and ag_num_F_trips[rq_id] != 0:
                                                                            pure_F_user += 1
                                                                        if ag_num_M_trips[rq_id] != 0 and ag_num_F_trips[rq_id] != 0:
                                                                            M_F_user += 1
                                                                        # calculate VMT for fixed transit and walking when microtransit turned on


                                                                        trimmed_transit_dist_path = transit_dist_path_all_[1:-1]
                                                                        pre_dist = 0
                                                                        pre_node = transit_dist_path_all_[0]
                                                                        ag_VMT_W_intermediate=0
                                                                        ag_VMT_M_intermediate=0
                                                                        ag_VMT_F_intermediate = 0
                                                                        for (node, dist, link_type,route) in trimmed_transit_dist_path:
                                                                            # calculate the number of fixed route transit trip legs
                                                                            if link_type == 1:
                                                                                distance_F = dist - pre_dist
                                                                                VMT_F += (distance_F / mile_meter)
                                                                                ag_VMT_F_intermediate += (distance_F / mile_meter)
                                                                                transit_link_vmt[time_period][(pre_node, node)]+=(distance_F / mile_meter)
                                                                                transit_link_pax[time_period][(pre_node, node)]+=1



                                                                            if link_type == 0:
                                                                                distance_W = dist - pre_dist
                                                                                VMT_W += (distance_W / mile_meter)
                                                                                ag_VMT_W_intermediate += (distance_W / mile_meter)

                                                                            if link_type == 4:
                                                                                distance_M = dist - pre_dist
                                                                                VMT_M += (distance_M / mile_meter)
                                                                                ag_VMT_M_intermediate += (distance_M / mile_meter)
                                                                            pre_dist = dist
                                                                            pre_node=node

                                                                        ag_VMT_W[rq_id]=ag_VMT_W_intermediate
                                                                        ag_VMT_M[rq_id]=ag_VMT_M_intermediate
                                                                        ag_VMT_F[rq_id]=ag_VMT_F_intermediate

                                                                    else:  # agent choose the car mode

                                                                        current_mode = "C"
                                                                        agent_M_tot_travel_time[rq_id] = 0
                                                                        agent_F_tot_travel_time[rq_id] = 0
                                                                        # 03/09/2026 Siwei add the following lines of code
                                                                        ag_VMT_M[rq_id] = 0
                                                                        agent_M_tot_wait_time[rq_id]=0

                                                                        pre_iter_mode[rq_id] = current_mode
                                                                        num_car_trips += 1
                                                                        agent_travel_time[rq_id] = travel_time_auto
                                                                        agent_travel_dist[rq_id] = travel_dist_auto
                                                                        agent_op_cost[rq_id] = agent_op_cost_auto  # agent_out-of-pocket cost
                                                                        agent_op_cost_Fix[rq_id] = 0
                                                                        agent_op_cost_Micro[rq_id] = 0
                                                                        VMT_auto+=(travel_dist_auto/mile_meter)
                                                                        agent_gen_cost[rq_id]=gen_cost_auto

                                                                        ag_VMT_W[rq_id] = 0
                                                                        agent_F_tot_wait_time[rq_id] = 0
                                                                        agent_tot_walk_time[rq_id] = 0
                                                                else:
                                                                    ag_prev_iter_mode=pre_iter_mode[rq_id]
                                                                    if ag_prev_iter_mode =="T":

                                                                        VMT_F += ag_VMT_F[rq_id]
                                                                        VMT_W += ag_VMT_W[rq_id]
                                                                        VMT_M += ag_VMT_M[rq_id]

                                                                        num_W_trips += ag_num_W_trips[rq_id]
                                                                        num_F_trips += ag_num_F_trips[rq_id]
                                                                        num_M_trips += ag_num_M_trips[rq_id]



                                                                        if ag_num_M_trips[rq_id] != 0 and ag_num_F_trips[rq_id] == 0:
                                                                            pure_M_user += 1
                                                                        # calculate pure fixed route transit users:
                                                                        if ag_num_M_trips[rq_id] == 0 and ag_num_F_trips[rq_id] != 0:
                                                                            pure_F_user += 1
                                                                        if ag_num_M_trips[rq_id] != 0 and ag_num_F_trips[rq_id] != 0:
                                                                            M_F_user += 1

                                                                        if rq_id in pre_iter_M_info:
                                                                            # rq_time, start, end, request_id
                                                                            (pre_ier_rq_time, pre_iter_start,pre_iter_end, pre_iter_request_id) = pre_iter_M_info[rq_id]
                                                                            rq_id_fleetpy = pre_iter_request_id
                                                                            while (rq_id_fleetpy in M_rq_id_list):  # this condition is to deal with the situation where 1 person has more than 1 microtransit trips
                                                                                rq_id_fleetpy += 1
                                                                            writer_M.writerow({'rq_time': pre_ier_rq_time,'start': pre_iter_start,'end': pre_iter_end,'request_id':rq_id_fleetpy})
                                                                            M_rq_id_list.append(rq_id_fleetpy)


                                                                            if pre_ier_rq_time <= (10 * 3600):                  # Ritun added: March 2nd, 2026
                                                                                agent_M_tot_wait_time[rq_id] = wait_times["AM"] * ag_num_M_trips[rq_id]
                                                                            elif pre_ier_rq_time <= (15 * 3600):
                                                                                agent_M_tot_wait_time[rq_id] = wait_times["MD"] * ag_num_M_trips[rq_id]
                                                                            elif pre_ier_rq_time <= (20 * 3600):
                                                                                agent_M_tot_wait_time[rq_id] = wait_times["PM"] * ag_num_M_trips[rq_id]
                                                                            else:
                                                                                print("!!!! EVENING MICRO USER DETECTED !!!!")
                                                                                agent_M_tot_wait_time[rq_id] = wait_times["EV"] * ag_num_M_trips[rq_id]

                                                                        if rq_id in pre_iter_F_info:
                                                                            #(request_time,F_origin_node,F_dest_node,rq_id)
                                                                            (pre_ier_rq_time_F, pre_iter_start_F,pre_iter_end_F, pre_iter_request_id_F) = pre_iter_F_info[rq_id]
                                                                            writer_F.writerow({'depart_time': pre_ier_rq_time_F, 'start': pre_iter_start_F,'end': pre_iter_end_F, 'request_id': pre_iter_request_id_F})
                                                                        agent_travel_time[rq_id]=agent_M_tot_wait_time[rq_id]+agent_M_tot_travel_time[rq_id]+agent_F_tot_travel_time[rq_id]+agent_F_tot_wait_time[rq_id]+agent_tot_walk_time[rq_id]

                                                                    else:
                                                                        num_car_trips += 1
                                                                        VMT_auto += (travel_dist_auto / mile_meter)



                                                            #03/02/2026: Siwei comment it
                                                            num_transit_users = tt_num_agents - num_car_trips

                                                            print("number of agents prob_T changed greater than threshold",mode_change_threshold,":", len(change_mode_ag_list))


                                                        csvfile_M.close()

                                                    csvfile_F.close()


                                                    ####################
                                                    #Convergence test right after the Binary Choice Model
                                                    ##########################################
                                                    # indiv_converg_test (set at the top) chooses between two convergence tests:
                                                    # - True (used): individual-level test, conv_test.indiv_convergence_test(). For every traveler it compares the
                                                    #   choice probabilities [prob_Auto, prob_T] with the previous iteration and sums (p_now - p_before)^2 / p_before
                                                    #   over all travelers and both modes. An iteration passes if the sum is <= convergence_gap. The model has
                                                    #   converged after two passing iterations (num_converged == 2), or at maximum_iteration.
                                                    # - False (not used, kept for later): aggregate-level test, conv_test.convergence_test(M_share, M_share_pre). It
                                                    #   compares only the overall microtransit mode share with the previous iteration: converged if the share changed
                                                    #   by at most 1% (relative). It is unfinished and does not work if switched on as it is (docs/open_issues.md, I-16):
                                                    #     * its call below is commented out, and nothing computes M_share / M_share_pre, so `converged` never
                                                    #       becomes True;
                                                    #     * the stop at maximum_iteration is only in the individual-level branch, so the loop would never end;
                                                    #     * convergence_test() raises UnboundLocalError when the share changed by more than 1%.
                                                    # aggregated level convergence test
                                                    if indiv_converg_test == False:
                                                        if iteration >= 1:
                                                            print("convergence check.....")
                                                            # converged,per_diff=conv_test.convergence_test(M_share,M_share_pre)
                                                            # print("Aggregated Level Convergence Test","M_share",M_share,"M_share_pre",M_share_pre,"per_diff",per_diff,"converged",converged)
                                                    else:
                                                        if iteration >= 1:
                                                            print("convergence check.....")
                                                            converged_, sum_sq_per_diff = conv_test.indiv_convergence_test(iter_agent_choice_prob[iteration], iter_agent_choice_prob[iteration - 1],convergence_gap)

                                                            iter_sum_sq_per_diff.append((iteration,sum_sq_per_diff))

                                                            if converged_ == True:
                                                                num_converged += 1
                                                                if num_converged == 2:
                                                                    converged = True


                                                            if iteration == maximum_iteration:
                                                                # stop after maximum_iteration iterations even if the test has not passed twice
                                                                converged = True

                                                            print("Individual Level Convergence Test:","sum of square percentage difference ", sum_sq_per_diff, "converged",converged)
                                                            if converged == True:
                                                                F_oper_cost = 0
                                                                F_oper_cost_base = 0
                                                                if microtransit_run == "micro_only":
                                                                    transit_tt_VMT=0
                                                                    transit_tt_VMT_base = 0
                                                                else:
                                                                    for (route_id,dist,num_stops) in transit_line_dist_list:
                                                                        F_oper_cost += 2 * (
                                                                                F_operating_hrs * 60 / headway) * \
                                                                                       transit_line_duration[
                                                                                           route_id] / 60 * 170  # 5 lines and $fixed route transit operating cost 170/veh-hour
                                                                        F_oper_cost_base += 2 * (
                                                                                F_operating_hrs * 60 / base_FRT_headway) * \
                                                                                            transit_line_duration[
                                                                                                route_id] / 60 * 170  # Ritun Jan 7, 2024: add base F operating cost calculation
                                                                        transit_tt_VMT += 2 * (
                                                                                F_operating_hrs * 60 / headway) * dist
                                                                        transit_tt_VMT_base += 2 * (
                                                                                F_operating_hrs * 60 / base_FRT_headway) * dist

                                                                F_gas_cost = transit_tt_VMT * F_gas_per_mile
                                                                F_gas_cost_base = transit_tt_VMT_base * F_gas_per_mile  # Ritun Jan 7, 2024: add base F gas cost calculation
                                                                F_oper_cost += F_gas_cost
                                                                F_oper_cost_base += F_gas_cost_base  # Ritun Jan 7, 2024: add base F gas cost calculation

                                                                M_mode_operating_cost = M_operating_hrs * fleet_size * 130  # microtransit operating cost $130/veh-hour
                                                                output_metrics.write_fixed_transit_link_vmt(study_area,fleet_size,M_operating_hrs,headway,virstop,transit_link_vmt,transit_link_pax,test_scenario,microtransit="micro")
                                                                output_metrics.write_fixed_transit_link_vmt(study_area,fleet_size,M_operating_hrs,headway,virstop,off_micro_transit_link_vmt,off_micro_transit_link_pax,test_scenario,microtransit="non_micro")

                                                                avg_period_total_weighted_5_min,avg_period_total_weighted_10_min,avg_period_total_weighted_15_min = output_metrics.all_scenario_micro_acc_calculation(microtransit_run,headway, virstop,M_operating_hrs,fleet_size,study_area,test_scenario) #1112 Siwei: comment to make the program run faster.


                                                                print("The program is converged.")


                                                                individual_result_dir=os.path.join(output_folder,"individual_results_%s_M_fsize_%s_op_hr_%s_hw_%s_virstop_%s_scen_%s.csv" % (str(microtransit_run),str(fleet_size),str(M_operating_hrs), str(headway),str(virstop),str(test_scenario)))



                                                                with open(individual_result_dir, 'w+', newline='', encoding='utf-8') as csvfile_indiv:
                                                                    fieldnames = ["rq_id", "origin", "dest","dp_time", "mode","switch_mode", "tt (s)","dist (mi)", "tt_C (s)",
                                                                                  "dist_C (mi)", "tt_M (s)","dist_M (mi)", "tt_F (s)","dist_F (mi)", "tt_W (s)",
                                                                                  "dist_W (mi)","agent_M_tot_wait_time (s)","agent_F_tot_wait_time (s)","out_of_pock_cost ($)","tt_saved_with_micro (s)",
                                                                                  "gen_cost_saved_with_micro","mob_logsum_increased_with_micro",
                                                                                  "agent_prob (auto,transit)","agent_ran_num","income (USD)","agent_transit_15min_acc"]

                                                                    writer_indiv = csv.DictWriter(csvfile_indiv, fieldnames=fieldnames)
                                                                    writer_indiv.writeheader()

                                                                    total_op_cost=0
                                                                    total_T_revenue = 0
                                                                    total_F_revenue = 0
                                                                    total_M_revenue = 0
                                                                    F_sub_per_ridership=0
                                                                    M_sub_per_ridership=0
                                                                    tt_sub_per_ridership=0
                                                                    M_revenue = 0
                                                                    F_revenue =0
                                                                    total_mob_increase=0
                                                                    total_switch_mode=0
                                                                    total_M_wait_time=0
                                                                    total_F_wait_time = 0
                                                                    total_walk_time = 0
                                                                    tt_gen_cost = 0 #total generalized cost for the selected mode
                                                                    num_M=0
                                                                    num_F=0
                                                                    num_W=0
                                                                    T_walking_time=0
                                                                    for rq_id in travel_time_delta:
                                                                        T_walking_time = 0 #03/22/26 - Siwei
                                                                        tt_saved_with_micro = 0
                                                                        gen_cost_saved_with_micro = 0
                                                                        c_tt_travel_time = 0
                                                                        c_tt_travel_dist = 0
                                                                        if pre_iter_mode[rq_id]=="T": #031726: Siwei add this line
                                                                            mode="T"
                                                                            m_waiting_time = agent_M_tot_wait_time[rq_id]
                                                                            if m_waiting_time>0:
                                                                                num_M+=1
                                                                            f_waiting_time = agent_F_tot_wait_time[rq_id]
                                                                            if f_waiting_time > 0:
                                                                                num_F += 1
                                                                            T_walking_time=agent_tot_walk_time[rq_id]
                                                                            if T_walking_time > 0:
                                                                                num_W += 1

                                                                            total_T_revenue += agent_op_cost[rq_id]
                                                                            total_F_revenue += agent_op_cost_Fix[rq_id]
                                                                            total_M_revenue += agent_op_cost_Micro[rq_id]
                                                                            if m_waiting_time >0:
                                                                                tt_saved_with_micro = travel_time_delta[rq_id]
                                                                                gen_cost_saved_with_micro = gen_cost_delta[rq_id]
                                                                        else:
                                                                            mode="C"
                                                                            m_waiting_time = 0
                                                                            f_waiting_time = 0
                                                                            T_walking_time = 0
                                                                            c_tt_travel_time = agent_travel_time[rq_id]
                                                                            c_tt_travel_dist = agent_travel_dist[rq_id]/mile_meter

                                                                        origin=agent_O[rq_id]
                                                                        dest=agent_D[rq_id]
                                                                        dp_time=agent_rq_time[rq_id]

                                                                        total_op_cost+=agent_op_cost[rq_id]
                                                                        total_mob_increase+=mob_logsum_delta[rq_id]
                                                                        total_switch_mode+=agent_switch_mode[rq_id]
                                                                        total_M_wait_time += m_waiting_time
                                                                        total_F_wait_time += f_waiting_time
                                                                        total_walk_time += T_walking_time
                                                                        tt_gen_cost += agent_gen_cost[rq_id]

                                                                        # 03/02/2026 Siwei: previously "agent_M_tot_wait_time (s)": m_waiting_time
                                                                        # 03/02/2026 Siwei: now
                                                                        #03/09/2026 Siwei add the following lines of code
                                                                        if (agent_M_tot_travel_time[rq_id]==0) and (ag_VMT_M[rq_id]!=0):
                                                                            aaa=0
                                                                            print("microtransit distance (%s) not equal to microtransit travel time (%s):",ag_VMT_M[rq_id],agent_M_tot_travel_time[rq_id])
                                                                        writer_indiv.writerow({"rq_id": rq_id,"origin": origin, "dest": dest,
                                                                             "dp_time": dp_time,"mode": mode, "switch_mode":agent_switch_mode[rq_id],
                                                                             "tt (s)": agent_travel_time[rq_id],"dist (mi)": agent_travel_dist[rq_id] / mile_meter,
                                                                             "tt_C (s)": c_tt_travel_time,"dist_C (mi)": c_tt_travel_dist,"tt_M (s)":agent_M_tot_travel_time[rq_id],
                                                                             "dist_M (mi)": ag_VMT_M[rq_id],"tt_F (s)":agent_F_tot_travel_time[rq_id],"dist_F (mi)": ag_VMT_F[rq_id],
                                                                              "agent_M_tot_wait_time (s)": m_waiting_time,"agent_F_tot_wait_time (s)": f_waiting_time,
                                                                             "out_of_pock_cost ($)":agent_op_cost[rq_id],"tt_saved_with_micro (s)": tt_saved_with_micro,"gen_cost_saved_with_micro": gen_cost_delta[rq_id],
                                                                             "mob_logsum_increased_with_micro":mob_logsum_delta[rq_id],"agent_prob (auto,transit)":agent_choice_prob[rq_id],
                                                                             "agent_ran_num": agent_ran_num[rq_id],
                                                                             "tt_W (s)": T_walking_time,"dist_W (mi)": ag_VMT_W[rq_id],"income (USD)":agent_income[rq_id],"agent_transit_15min_acc":agent_transit_15min_acc[rq_id]})



                                                                csvfile_indiv.close()
                                                                if num_M!=0:
                                                                    avg_M_wait_time = total_M_wait_time /num_M_trips #total microtransit waiting time/microtransit trips
                                                                else:
                                                                    avg_M_wait_time=0
                                                                if num_F!=0:
                                                                    avg_F_wait_time = total_F_wait_time/num_F_trips #total waiting time/ total number of F trips
                                                                else:
                                                                    avg_F_wait_time=0
                                                                if num_W!=0:
                                                                    avg_walk_time = total_walk_time/num_W
                                                                else:
                                                                    avg_walk_time=0
                                                                F_revenue=total_F_revenue
                                                                M_revenue=total_M_revenue
                                                                if num_F_trips==0:
                                                                    if microtransit_run == "micro_only":
                                                                        F_sub_per_ridership = 0
                                                                    else:
                                                                        F_sub_per_ridership=-999
                                                                else:
                                                                    F_sub_per_ridership=(F_oper_cost-F_revenue)/num_F_trips # fixed transit subsidy per fixed transit trip


                                                                #calculate the turn-off micro transit scenario
                                                                #under every different fixed route transit headway, we need to calculate the cost again
                                                                if (num_virstop_scen==1) and (num_fleet_size_scen==1) and (num_operating_periods_scen==1) and (microtransit_run=="micro") and (repositioning==True):
                                                                    #calculate off_micro metrics
                                                                    off_micro_F_revenue=off_micro_F_trips*base_FRT_fare
                                                                    if off_micro_F_trips==0:
                                                                        off_micro_F_sub_per_ridership=-999
                                                                        off_micro_tt_sub = -999
                                                                    else:
                                                                        off_micro_tt_sub =(F_oper_cost - off_micro_F_revenue)
                                                                        off_micro_F_sub_per_ridership = off_micro_tt_sub / off_micro_F_trips

                                                                    off_micro_w_trip_legs=0
                                                                    off_micro_tot_walk_time=0
                                                                    off_micro_avg_walk_time=0
                                                                    off_micro_F_trip_legs=0
                                                                    off_micro_tot_F_wait_time=0
                                                                    off_micro_avg_F_wait_time=0
                                                                    off_micro_total_op_cost=0
                                                                    off_micro_tt_gen_cost = 0

                                                                    for rq_id in travel_time_delta:
                                                                        off_micro_total_op_cost += off_micro_agent_op_cost[rq_id]
                                                                        off_micro_tt_gen_cost += off_micro_agent_gen_cost[rq_id]

                                                                    for rq_id in off_micro_agent_tot_walk_time:
                                                                        if off_micro_agent_tot_walk_time[rq_id]>0:
                                                                            off_micro_w_trip_legs+=1
                                                                            off_micro_tot_walk_time+=off_micro_agent_tot_walk_time[rq_id]
                                                                        if off_micro_agent_F_tot_wait_time[rq_id]>0:
                                                                            off_micro_F_trip_legs+=1
                                                                            off_micro_tot_F_wait_time+=off_micro_agent_F_tot_wait_time[rq_id]



                                                                    if microtransit_run =="micro_only":
                                                                        off_micro_avg_walk_time = 0
                                                                    else:
                                                                        off_micro_avg_walk_time = off_micro_tot_walk_time/off_micro_w_trip_legs

                                                                    if microtransit_run == "micro_only":
                                                                        off_micro_avg_F_wait_time = 0
                                                                    else:
                                                                        if off_micro_F_trip_legs==0:
                                                                            off_micro_avg_F_wait_time = headway*60/2
                                                                        else:
                                                                            off_micro_avg_F_wait_time=off_micro_tot_F_wait_time/off_micro_F_trips # total waiting time/fixed transit trips
                                                                    off_micro_tt_VMT = off_micro_VMT_auto + 0+ transit_tt_VMT

                                                                    microtransit_run_pre=microtransit_run
                                                                    microtransit_run="non_micro"
                                                                    individual_result_dir = os.path.join(output_folder,"individual_results_%s_M_fsize_%s_op_hr_%s_hw_%s_virstop_%s_scen_%s.csv" % (str(microtransit_run), str(fleet_size),str(M_operating_hrs), str(headway),str(virstop),str(test_scenario)))

                                                                    aaa=1
                                                                    if test_scenario==TRPartA_test_scenario_list[0]:
                                                                        with open(individual_result_dir,'w+',newline='', encoding='utf-8') as csvfile_indiv_fixed_only:
                                                                            fieldnames = ["rq_id", "origin","dest", "dp_time","mode","switch_mode","tt (s)","dist (mi)",
                                                                                          "tt_C (s)","dist_C (mi)","tt_M (s)","dist_M (mi)",
                                                                                          "tt_F (s)","dist_F (mi)","tt_W (s)","dist_W (mi)","agent_M_tot_wait_time (s)",
                                                                                          "agent_F_tot_wait_time (s)","out_of_pock_cost ($)",
                                                                                          "tt_saved_with_micro (s)","gen_cost_saved_with_micro","mob_logsum_increased_with_micro",
                                                                                          "agent_prob (auto,transit)","agent_ran_num"]
                                                                            writer_indiv_fixed_only = csv.DictWriter(
                                                                                csvfile_indiv_fixed_only,
                                                                                fieldnames=fieldnames)
                                                                            writer_indiv_fixed_only.writeheader()
                                                                            for rq_id in travel_time_delta:

                                                                                mode = off_micro_ag_mode[
                                                                                    rq_id]

                                                                                origin = agent_O[rq_id]
                                                                                dest = agent_D[rq_id]
                                                                                dp_time = agent_rq_time[
                                                                                    rq_id]

                                                                                tt_M = 0
                                                                                dist_M = 0
                                                                                tt_F = 0
                                                                                dist_F = 0
                                                                                tt_C = 0
                                                                                dist_C = 0
                                                                                if mode == "T":
                                                                                    tt_C = 0
                                                                                    dist_C = 0
                                                                                    if off_micro_agent_F_tot_wait_time[rq_id] > 0:
                                                                                        tt_F = off_micro_ag_tot_tt[rq_id]
                                                                                        dist_F = off_micro_ag_tot_dist[rq_id]
                                                                                    else:
                                                                                        tt_F = 0
                                                                                        dist_F = 0
                                                                                else:
                                                                                    tt_C =off_micro_ag_tot_tt[rq_id]
                                                                                    dist_C = off_micro_ag_tot_dist[rq_id]
                                                                                    tt_F = 0
                                                                                    dist_F = 0

                                                                                writer_indiv_fixed_only.writerow(
                                                                                    {"rq_id": rq_id,
                                                                                     "origin": origin,
                                                                                     "dest": dest,
                                                                                     "dp_time": dp_time,
                                                                                     "mode": mode,
                                                                                     "switch_mode": 0,
                                                                                     "tt (s)":
                                                                                         off_micro_ag_tot_tt[
                                                                                             rq_id],
                                                                                     "dist (mi)":
                                                                                         off_micro_ag_tot_dist[
                                                                                             rq_id],
                                                                                     "tt_C (s)": tt_C,
                                                                                     "dist_C (mi)": dist_C,
                                                                                     "tt_M (s)": tt_M,
                                                                                     "dist_M (mi)": dist_M,
                                                                                     "tt_F (s)": tt_F,
                                                                                     "dist_F (mi)": dist_F,
                                                                                     "out_of_pock_cost ($)":
                                                                                         off_micro_agent_op_cost[
                                                                                             rq_id],
                                                                                     "tt_saved_with_micro (s)": 0,
                                                                                     "gen_cost_saved_with_micro": 0,
                                                                                     "mob_logsum_increased_with_micro": 0,
                                                                                     "agent_prob (auto,transit)":
                                                                                         off_micro_agent_choice_prob[
                                                                                             rq_id],
                                                                                     "agent_ran_num":
                                                                                         off_micro_agent_ran_num[
                                                                                             rq_id],
                                                                                     "agent_M_tot_wait_time (s)": 0,
                                                                                     "agent_F_tot_wait_time (s)":
                                                                                         off_micro_agent_F_tot_wait_time[
                                                                                             rq_id],
                                                                                     "tt_W (s)":
                                                                                         off_micro_agent_tot_walk_time[
                                                                                             rq_id],
                                                                                     "dist_W (mi)":
                                                                                         off_micro_ag_VMT_W[
                                                                                             rq_id]})

                                                                        microtransit_run = microtransit_run_pre

                                                                        pure_F_users = (
                                                                                    off_micro_T_trips - off_micro_W_trips)

                                                                        # Write the fixed only scenario
                                                                        if test_scenario == TRPartA_test_scenario_list[0]:
                                                                            writer.writerow({"test_scen": 0,"dscrptn": "FRT_only_scen", "study_area": study_area,"repositioning": str(False),
                                                                                             "microtrasnit": "non_micro","hdwy (min)": headway,
                                                                                             "vir_stop (%)": 0,"flt_sz": 0, "op_periods": 0,"tt_agents": tt_num_agents,
                                                                                             "car_users": off_micro_auto_trips,"car_mode_share (%)": off_micro_auto_trips / tt_num_agents,
                                                                                             "trsit_mode_users (W_M_F)": off_micro_T_trips,"transit_mode_share (%)": off_micro_T_trips / tt_num_agents,
                                                                                             "pure_M_users": 0,"M_trips": 0,"M_mode_share (%)": 0 / tt_num_agents,"pure_F_users": pure_F_users,
                                                                                             "F_trips": off_micro_F_trips,"F_mode_share (%)": off_micro_F_trips / tt_num_agents,
                                                                                             "pure_walk_users": off_micro_W_trips,"W_mode_share (%)": off_micro_W_trips / tt_num_agents,
                                                                                             "walk_users": off_micro_w_trip_legs,"M_pls_F_users": 0,
                                                                                             "M_pls_F_mode_share (%)": 0,"F_oper_cost ($)": F_oper_cost_base,
                                                                                             "M_oper_cost ($)": 0,"F_revenue ($)": off_micro_F_revenue,
                                                                                             "M_revenue ($)": 0,"Total_T_revenue ($)": off_micro_F_revenue,
                                                                                             "tot_sub ($)": off_micro_tt_sub,"sub_per_F_trip ($)": off_micro_F_sub_per_ridership,
                                                                                             "sub_per_F_rider ($)": np.nan if pure_F_users==0 else off_micro_tt_sub / (pure_F_users),
                                                                                             "sub_per_M_trip ($)": 0,"sub_per_M_rider ($)": 0,"sub_per_T_trip ($)": off_micro_F_sub_per_ridership,
                                                                                             "sub_per_T_rider ($)": np.nan if pure_F_users==0 else off_micro_tt_sub / (pure_F_users),
                                                                                             "sub_per_M_pax_mile ($/mi)": 0,"sub_per_F_pax_mile ($/mi)": off_micro_tt_sub / off_micro_VMT_F,
                                                                                             "sub_per_T_pax_mile ($/mi)": off_micro_tt_sub / off_micro_VMT_F,"sub_per_M_VMT ($/mi)": 0,
                                                                                             "sub_per_F_VMT ($/mi)": (off_micro_tt_sub) / (transit_tt_VMT),
                                                                                             "sub_per_T_VMT ($/mi)": (off_micro_tt_sub) / (transit_tt_VMT),
                                                                                             "tt_auto_gas_cost ($)": off_micro_total_op_cost - off_micro_F_revenue,
                                                                                             "auto_gas_cost_per_mile ($/mi)": (off_micro_total_op_cost - off_micro_F_revenue) / off_micro_VMT_auto,
                                                                                             "avg_M_fare": 0,"avg_F_fare": np.nan if pure_F_users==0 else off_micro_F_revenue / (pure_F_users),
                                                                                             "avg_T_fare": np.nan if pure_F_users==0 else off_micro_F_revenue / (pure_F_users),
                                                                                             "avg_auto_gas_cost": (off_micro_total_op_cost - off_micro_F_revenue) / off_micro_auto_trips,
                                                                                             "tt_o_pckt_cost ($)": off_micro_total_op_cost,"tt_mob_lgsm_inc_with_micro": 0,
                                                                                             "tt_gen_cost": off_micro_tt_gen_cost,"tt_mode_switch": 0,
                                                                                             "M_avg_wait_time (s)": 0,"F_avg_wait_time (s)": off_micro_avg_F_wait_time,
                                                                                             "avg_walk_time (s)": off_micro_avg_walk_time,"tt_walk_time (h)": off_micro_tot_walk_time / 3600,
                                                                                             "car_VMT (mi)": off_micro_VMT_auto,"M_VMT (mi)": 0,
                                                                                             "M_PMT (mi)": 0,"M_PMT/M_VMT": 0,"F_VMT (mi)": transit_tt_VMT,"F_PMT (mi)": off_micro_VMT_F,"F_PMT/F_VMT": off_micro_VMT_F / transit_tt_VMT,
                                                                                             "tt_VMT (mi)": off_micro_tt_VMT,"tt_walk_dist (mi)": off_micro_VMT_W,
                                                                                             "wghted_acc_emp_5_min": tot_weighted_5_min_F,"wghted_acc_emp_10_min": tot_weighted_10_min_F,
                                                                                             "wghted_acc_emp_15_min": tot_weighted_15_min_F,"M_util_rate (%)": 0,
                                                                                             "M_veh_occ": 0,"M_avg_speed (mph)": 0,"cnvrg (iter, sm_sq_per_diff)": 0, "fleetpy_wait": 0, "rejection_rate": 0})


                                                                    else:
                                                                        aaa=1

                                                                    microtransit_run=microtransit_run_pre

                                                                    pure_F_users=(off_micro_T_trips-off_micro_W_trips)

                                                                    # Write the fixed only scenario
                                                                    if test_scenario == TRPartA_test_scenario_list[0]:

                                                                        writer.writerow({"test_scen":0,"dscrptn":"FRT_only_scen","study_area":study_area,"repositioning":str(False),"microtrasnit":"non_micro","hdwy (min)": headway, "vir_stop (%)": 0, "flt_sz": 0,"op_periods": 0,
                                                                                     "tt_agents": tt_num_agents,"car_users": off_micro_auto_trips,"car_mode_share (%)": off_micro_auto_trips/tt_num_agents,
                                                                                     "trsit_mode_users (W_M_F)": off_micro_T_trips,"transit_mode_share (%)":off_micro_T_trips/tt_num_agents,"pure_M_users":0, "M_trips": 0,"M_mode_share (%)":0/tt_num_agents,
                                                                                     "pure_F_users":pure_F_users,"F_trips": off_micro_F_trips,"F_mode_share (%)":off_micro_F_trips/tt_num_agents,"pure_walk_users": off_micro_W_trips,"W_mode_share (%)":off_micro_W_trips/tt_num_agents,
                                                                                     "walk_users":off_micro_w_trip_legs, "M_pls_F_users":0,"M_pls_F_mode_share (%)":0,"F_oper_cost ($)": F_oper_cost_base,
                                                                                     "M_oper_cost ($)": 0,"F_revenue ($)": off_micro_F_revenue, "M_revenue ($)": 0,"Total_T_revenue ($)":off_micro_F_revenue, "tot_sub ($)":off_micro_tt_sub,
                                                                                     "sub_per_F_trip ($)": off_micro_F_sub_per_ridership,"sub_per_F_rider ($)":np.nan if pure_F_users==0 else off_micro_tt_sub/(pure_F_users),"sub_per_M_trip ($)": 0,"sub_per_M_rider ($)":0,"sub_per_T_trip ($)":off_micro_F_sub_per_ridership,"sub_per_T_rider ($)":np.nan if pure_F_users==0 else off_micro_tt_sub/(pure_F_users),
                                                                                     "sub_per_M_pax_mile ($/mi)":0,"sub_per_F_pax_mile ($/mi)":off_micro_tt_sub/off_micro_VMT_F,"sub_per_T_pax_mile ($/mi)":off_micro_tt_sub/off_micro_VMT_F,
                                                                                     "sub_per_M_VMT ($/mi)": 0,"sub_per_F_VMT ($/mi)": (off_micro_tt_sub) / (transit_tt_VMT),"sub_per_T_VMT ($/mi)": (off_micro_tt_sub) / (transit_tt_VMT),
                                                                                     "tt_auto_gas_cost ($)":off_micro_total_op_cost-off_micro_F_revenue,"auto_gas_cost_per_mile ($/mi)":(off_micro_total_op_cost-off_micro_F_revenue)/off_micro_VMT_auto,
                                                                                     "avg_M_fare": 0, "avg_F_fare":np.nan if pure_F_users==0 else off_micro_F_revenue/(pure_F_users),"avg_T_fare":np.nan if pure_F_users==0 else off_micro_F_revenue/(pure_F_users), "avg_auto_gas_cost":(off_micro_total_op_cost-off_micro_F_revenue)/off_micro_auto_trips,
                                                                                    "tt_o_pckt_cost ($)": off_micro_total_op_cost,
                                                                                     "tt_mob_lgsm_inc_with_micro": 0,"tt_gen_cost":off_micro_tt_gen_cost,
                                                                                     "tt_mode_switch": 0,"M_avg_wait_time (s)": 0,
                                                                                     "F_avg_wait_time (s)": off_micro_avg_F_wait_time,"avg_walk_time (s)": off_micro_avg_walk_time,"tt_walk_time (h)":off_micro_tot_walk_time/3600,
                                                                                     "car_VMT (mi)":off_micro_VMT_auto,"M_VMT (mi)":0,"M_PMT (mi)":0,"M_PMT/M_VMT":0,"F_VMT (mi)":transit_tt_VMT,"F_PMT (mi)":off_micro_VMT_F,"F_PMT/F_VMT":off_micro_VMT_F/transit_tt_VMT,"tt_VMT (mi)":off_micro_tt_VMT,"tt_walk_dist (mi)":off_micro_VMT_W,
                                                                                     "wghted_acc_emp_5_min":tot_weighted_5_min_F,
                                                                                     "wghted_acc_emp_10_min":tot_weighted_10_min_F,
                                                                                     "wghted_acc_emp_15_min":tot_weighted_15_min_F,
                                                                                     "M_util_rate (%)": 0, "M_veh_occ": 0,"M_avg_speed (mph)": 0 ,"cnvrg (iter, sm_sq_per_diff)":0, "fleetpy_wait": 0, "rejection_rate": 0})

                                                                #calculate the turn-on micro transit scenario

                                                                util_rate, veh_occ, total_vmt, empty_vkm, avg_speed_mph = output_metrics.get_fleetpy_eval_output_metrics(repositioning)
                                                                tt_VMT = VMT_auto + total_vmt + transit_tt_VMT

                                                                M_gas_cost = total_vmt * M_gas_per_mile
                                                                M_mode_operating_cost += M_gas_cost

                                                                M_sub_per_ridership = (M_mode_operating_cost - M_revenue) / num_M_trips # microtransit subsidy per microtransit trips
                                                                tt_sub = (F_oper_cost + M_mode_operating_cost - F_revenue - M_revenue)
                                                                tt_sub_per_ridership = tt_sub / (num_F_trips + num_M_trips)

                                                                if microtransit_run=="micro_only":
                                                                    PMT_VMT_ratio_F = 0
                                                                    headway_pre=headway
                                                                    headway = 0
                                                                    off_micro_tot_walk_time = 0
                                                                else:
                                                                    PMT_VMT_ratio_F = VMT_F / transit_tt_VMT


                                                                if test_scenario==0:
                                                                    dscrptn="Base_scen (M+F)"
                                                                if test_scenario==1:
                                                                    dscrptn="Low-income discount"
                                                                if test_scenario == 2:
                                                                    dscrptn = "Time-based fare"
                                                                if test_scenario == 3:
                                                                    dscrptn = "FRT accessibility-based fare"
                                                                if test_scenario == 4:
                                                                    dscrptn = "Intermodal transfer discount"
                                                                if test_scenario == 5:
                                                                    dscrptn = "Micro_flat_fare"
                                                                if test_scenario == 6:
                                                                    dscrptn = "Micro_start+dist_based_fr"
                                                                if test_scenario == 7:
                                                                    dscrptn = "Intermodal trfr disct+Micro_start+dist_based_fr"
                                                                if test_scenario == 8:
                                                                    dscrptn = "Time-based fare+no_peak_surchge"
                                                                if test_scenario == 9:
                                                                    dscrptn = "FRT accessibility-based fare+no_high_FRT_acc_surchge"
                                                                if test_scenario == 10:
                                                                    dscrptn = "Ritun BO (time-based+intrmdl_trfr+Micro_start+dist_based_fr)"

                                                                if (pure_F_user + M_F_user)!=0:
                                                                    sub_per_F_rider = (F_oper_cost-F_revenue)/(pure_F_user+M_F_user)
                                                                else:
                                                                    sub_per_F_rider = 999

                                                                if (pure_M_user+M_F_user) != 0:
                                                                    sub_per_M_rider=(M_mode_operating_cost-M_revenue)/(pure_M_user+M_F_user)
                                                                else:
                                                                    sub_per_M_rider = 999

                                                                if (pure_M_user+M_F_user) != 0:
                                                                    avg_M_fare = M_revenue/(pure_M_user+M_F_user)
                                                                else:
                                                                    avg_M_fare = 0

                                                                if (pure_F_user+M_F_user) != 0:
                                                                    avg_F_fare = F_revenue/(pure_F_user+M_F_user)
                                                                else:
                                                                    avg_F_fare = 0

                                                                if (pure_M_user + pure_F_user + M_F_user) != 0:
                                                                    avg_T_fare = (M_revenue + F_revenue) / (pure_M_user + pure_F_user + M_F_user)
                                                                else:
                                                                    avg_T_fare = 0

                                                                if (VMT_F)!=0:
                                                                    sub_per_F_pax_mile =(F_oper_cost-F_revenue)/(VMT_F)
                                                                else:
                                                                    sub_per_F_pax_mile = 999


                                                                writer.writerow({"test_scen":test_scenario,"dscrptn":dscrptn,"study_area":study_area,"repositioning":repositioning,"microtrasnit":microtransit_run,"hdwy (min)": headway, "vir_stop (%)": virstop, "flt_sz": fleet_size, "op_periods": operating_periods,
                                                                     "tt_agents": tt_num_agents,"car_users": num_car_trips,  "car_mode_share (%)": num_car_trips/tt_num_agents,
                                                                     "trsit_mode_users (W_M_F)": num_transit_users ,"transit_mode_share (%)":num_transit_users/tt_num_agents,"pure_M_users":pure_M_user,"M_trips":num_M_trips,"M_mode_share (%)":pure_M_user/tt_num_agents,
                                                                      "pure_F_users":pure_F_user,"F_trips":num_F_trips,"F_mode_share (%)":pure_F_user/tt_num_agents,"pure_walk_users":num_W_trips,"W_mode_share (%)":num_W_trips/tt_num_agents,
                                                                      "walk_users":num_W,"M_pls_F_users":M_F_user,"M_pls_F_mode_share (%)":M_F_user/tt_num_agents, "F_oper_cost ($)": F_oper_cost,
                                                                     "M_oper_cost ($)": M_mode_operating_cost,"F_revenue ($)":F_revenue,"M_revenue ($)":M_revenue,"Total_T_revenue ($)":F_revenue+M_revenue,"tot_sub ($)":tt_sub,
                                                                      "sub_per_F_trip ($)":F_sub_per_ridership,"sub_per_F_rider ($)":sub_per_F_rider, "sub_per_M_trip ($)":M_sub_per_ridership,"sub_per_M_rider ($)":sub_per_M_rider,"sub_per_T_trip ($)":tt_sub_per_ridership,
                                                                      "sub_per_T_rider ($)":tt_sub/(pure_F_user+pure_M_user+M_F_user),"sub_per_M_pax_mile ($/mi)":(M_mode_operating_cost-M_revenue)/(VMT_M),"sub_per_F_pax_mile ($/mi)":sub_per_F_pax_mile,"sub_per_T_pax_mile ($/mi)":(tt_sub)/(VMT_M+VMT_F),
                                                                      "sub_per_M_VMT ($/mi)": (M_mode_operating_cost - M_revenue) / (total_vmt),"sub_per_F_VMT ($/mi)": (F_oper_cost - F_revenue)/(transit_tt_VMT),"sub_per_T_VMT ($/mi)": (tt_sub) / (total_vmt + transit_tt_VMT),
                                                                      "tt_auto_gas_cost ($)":total_op_cost-(F_revenue+M_revenue),"auto_gas_cost_per_mile ($/mi)":(total_op_cost-(F_revenue+M_revenue))/VMT_auto,
                                                                       "avg_M_fare": avg_M_fare, "avg_F_fare":avg_F_fare,"avg_T_fare":avg_T_fare, "avg_auto_gas_cost":(total_op_cost-(F_revenue+M_revenue))/num_car_trips,
                                                                      "tt_o_pckt_cost ($)": total_op_cost,"tt_mob_lgsm_inc_with_micro": total_mob_increase,"tt_gen_cost":tt_gen_cost,
                                                                      "tt_mode_switch": total_switch_mode, "M_avg_wait_time (s)": avg_M_wait_time,
                                                                      "F_avg_wait_time (s)": avg_F_wait_time, "avg_walk_time (s)":avg_walk_time,"tt_walk_time (h)":total_walk_time/3600,
                                                                      "car_VMT (mi)":VMT_auto,"M_VMT (mi)":total_vmt,"M_PMT (mi)":VMT_M,"M_PMT/M_VMT":VMT_M/total_vmt,"F_VMT (mi)":transit_tt_VMT,"F_PMT (mi)":VMT_F,"F_PMT/F_VMT":PMT_VMT_ratio_F,"tt_VMT (mi)":tt_VMT,"tt_walk_dist (mi)":VMT_W,
                                                                      "wghted_acc_emp_5_min":avg_period_total_weighted_5_min,
                                                                      "wghted_acc_emp_10_min":avg_period_total_weighted_10_min,
                                                                      "wghted_acc_emp_15_min":avg_period_total_weighted_15_min,
                                                                        "M_util_rate (%)":util_rate,"M_veh_occ":veh_occ,"M_avg_speed (mph)":avg_speed_mph,"cnvrg (iter, sm_sq_per_diff)":iter_sum_sq_per_diff, "fleetpy_wait": last_fleetpy_wait_time, "rejection_rate": last_rejection_rate})


                                                                if microtransit_run == "micro_only":
                                                                    headway = headway_pre



                                                                scenario_count += 1
                                                    if converged == False:
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
                                                        fleetpy.run_scenarios(cc_fleetpy, sc_fleetpy, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1, random_seed=random_seed)
                                                        fleetpy.warn_non_optimal_repositioning(cc_fleetpy, sc_fleetpy)
                                                        list_results = fleetpy.read_outputs_for_comparison(cc_fleetpy, sc_fleetpy)
                                                        all_scenario_assert_dict = {0: {"number users": 88}}
                                                        fleetpy.check_assertions(list_results, all_scenario_assert_dict, LOG_F)
                                                        print("FleetPy finishes. Now update the microtransit part in super-network.....","iteration:",iteration)
                                                        wait_times = update.update_network_files(repositioning,microtransit_run,headway,virstop,M_operating_hrs,fleet_size,study_area,iteration,
                                                                                    aggregation)

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


                                                    iteration+=1



                                                timeatfinished = datetime.datetime.now()
                                                processingtime = timeatfinished - pre_timeatfinished
                                                pre_timeatfinished = timeatfinished
                                                print(scenario_count, "th scenario finished","...virtual_stop:", virstop, "(%)","headway", headway, "(mins)", "fleet_size", fleet_size, "(veh)", "operating_periods",operating_periods,"....... end time is:",timeatfinished,"run time is: ",processingtime)



        csvfile.close()

        timeatfinished = datetime.datetime.now()
        processingtime = timeatfinished - start_time
        print("Study_area",study_area,"integrated system model run finished....... end time is:", timeatfinished, "total run time is: ", processingtime)
