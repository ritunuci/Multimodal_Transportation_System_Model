# -------------------------------------------------------------------------------------------------------------------- #
# external imports
# ----------------
import os
import sys
import multiprocessing as mp
from collections import OrderedDict
import time
import datetime
import csv
import numpy as np
# FleetPy (fleetpy/) is reached only through fleetpy_runner
# ---------------------------------------------------------
import fleetpy_runner as fleetpy

import convergence_test as conv_test
import network_algorithms as n_a
import random
import output_performance_metrics as output_metrics
import folder_directory as fld_dir
import testing_scenario_creation as tst_scen_create
import update_initial_network as init_net
import mtsm_paths as mtsm
from mtsm_model import config
from mtsm_model.state import BaseCase, TravelerState
from mtsm_model.paths import PathCache
from mtsm_model.networks import read_iteration_networks
from mtsm_model.iteration import run_iteration
from mtsm_model.microtransit import run_fleetpy_and_update_networks
from mtsm_model.results import write_converged_results

# global variables
# ----------------
LOG_F = os.path.join(mtsm.CODE_ROOT, "standard_bugfix.log")


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
    # the run's parameters (input_parameter.csv) are cfg.<name>; the model's constants are config.<NAME>
    cfg = config.read_run_config()
    config.check_run_config(cfg)

    random.seed(cfg.random_seed)
    np.random.seed(cfg.random_seed)
    print("random_seed:", cfg.random_seed, "PYTHONHASHSEED:", os.environ.get("PYTHONHASHSEED"))

    headway_scenarios = [cfg.headway]  # [30,60]  #Ritun
    fleet_size_scenarios = cfg.read_fleet_size

    for study_area in cfg.test_area:
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

        initial_super_network_dir, initial_super_network, final_super_network_dir, final_super_network=tst_scen_create.scen_create(microtransit_setup_scenarios,config.VIRTUAL_STOP_SCENARIOS,config.OPERATING_PERIODS_SCENARIOS,time_periods,fleet_size_scenarios,headway_scenarios,initial_network_folder,final_network_folder,config.BASE_FRT_HEADWAY)
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

            for repositioning in config.REPOSITIONING_LIST:

                # the car and FRT-only paths of each traveler, computed in the first fare scenario (paths.py)
                path_cache = PathCache()

                for test_scenario in cfg.TRPartA_test_scenario_list:
                    print("aggregation:",config.AGGREGATION,"; mode_change_threshold:",config.MODE_CHANGE_THRESHOLD,"; convergence_gap:",config.CONVERGENCE_GAP,"; maximum_iteration:",config.MAXIMUM_ITERATION,  "; F_gas_per_mile ($/mi):",config.F_GAS_PER_MILE,
                    "; M_gas_per_mile ($/mi):", config.M_GAS_PER_MILE,"; repositioning",repositioning,"; Testing Scenario:",test_scenario,"; transit_fare ($):", cfg.transit_fare,"; microtransit_start_fare ($):",cfg.microtransit_start_fare,"; microtransit_dist_based_rate ($/mi):",cfg.microtransit_dist_based_rate*config.MILE_METER,
                          "; Peak fare factor (0~1):",cfg.PkFareFactor,"; Off-peak fare factor (0~1):",cfg.OffPkFareFactor,"; Fixed to Micro discount factor (0~1):",cfg.Fixed2MicroFactor,"; Micro to Fixed discount factor (0~1):",cfg.Micro2FixedFactor)



                    num_headway_scen = 0
                    for headway in headway_scenarios: #put bus design parameter in the most outer loop
                        init_net.update_initial_net_with_bayesian_headway(headway,study_area)  #Ritun
                        tot_weighted_5_min_F,tot_weighted_10_min_F,tot_weighted_15_min_F=output_metrics.all_scenario_fixed_acc_calculation(headway,study_area,test_scenario)
                        num_headway_scen+=1
                        num_virstop_scen = 0
                        for virstop in config.VIRTUAL_STOP_SCENARIOS: #virtual stops - not necessarily influence the cost, but will influence the mobility
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

                                for operating_periods in config.OPERATING_PERIODS_SCENARIOS: #fleetsize - influence the cost & mobility
                                    num_operating_periods_scen+=1
                                    if operating_periods==["AM", "MD", "PM", "EV"]:
                                        M_operating_hrs=19
                                    elif operating_periods==["AM", "MD", "PM"]:
                                        M_operating_hrs = 15
                                    else:
                                        M_operating_hrs = 10
                                    F_operating_hrs = 19 # fixed route transit 19 hrs


                                    F_transit_trips = os.path.join(fleetpy_demand_folder, "debug_False_F_transit_demand_%s_op_hr_%s_hw_%s_virstop_%s.csv" % (str(fleet_size),str(M_operating_hrs), str(headway), str(virstop)))

                                    for microtransit_run in config.MICROTRANSIT_RUNNING_SCENARIOS:
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
                                                rejection_rate = cfg.initial_rejection_rate / 100  # Ritun added: Feb 14
                                                last_rejection_rate = 0
                                                iter_agent_choice_prob=OrderedDict()
                                                iter_agent_selected_mode=OrderedDict()
                                                converged=False

                                                # Metrics of turn-off microtransit (the fixed-route-only base case)
                                                base = BaseCase()

                                                num_converged=0

                                                # per-traveler values with microtransit, kept across the iterations
                                                state = TravelerState()

                                                iter_sum_sq_per_diff=[]

                                                rejection_rate_dict = {}  # Ritun added Feb 14

                                                running_avg_rejection_rate = []  # Ritun added Feb 14

                                                last_fleetpy_wait_time = 0
                                                wait_times = None  # FleetPy's waiting times per period, from the previous iteration


                                                while converged==False:
                                                    # Ritun added Feb 14
                                                    rejection_rate_dict[iteration] = rejection_rate
                                                    if iteration >= 3:
                                                        rejection_rate = (rejection_rate_dict[iteration - 1] +
                                                                          rejection_rate_dict[iteration - 2] +
                                                                          rejection_rate_dict[
                                                                              iteration - 3]) / 3
                                                    total_rejection_penalty = rejection_rate * cfg.micro_rejection_penalty
                                                    print(f"TOATL REJECTION PENALTY IS: {total_rejection_penalty}")

                                                    print("iteration:",iteration)
                                                    iter_agent_choice_prob[iteration]=OrderedDict()
                                                    log_level = "info"

                                                    if repositioning == True:
                                                        cc = os.path.join(scs_path, "%s_constant_config_ir_repo.csv"% str(study_area))
                                                    else:
                                                        cc = os.path.join(scs_path, "%s_constant_config_ir.csv" % str(study_area))


                                                    print("Demand Component (choice model).....")
                                                    # Read the updated super-network file
                                                    read_iteration_networks(microtransit_run, iteration, converged, time_periods, initial_super_network,
                                                                            initial_super_network_dir, final_super_network, final_super_network_dir, headway, virstop,
                                                                            M_operating_hrs, fleet_size, operating_periods)

                                                    # Demand component: calculate how many travelers will choose transit, how many will choose auto;
                                                    # write into FleetPy's demand input directly
                                                    totals = run_iteration(
                                                        iteration=iteration, cfg=cfg, test_scenario=test_scenario, study_area=study_area,
                                                        microtransit_run=microtransit_run, headway=headway, virstop=virstop, fleet_size=fleet_size,
                                                        M_operating_hrs=M_operating_hrs, operating_periods=operating_periods, num_virstop_scen=num_virstop_scen,
                                                        num_fleet_size_scen=num_fleet_size_scen, num_operating_periods_scen=num_operating_periods_scen,
                                                        agent_list_=agent_list_, tt_num_agents=tt_num_agents, auto_network=auto_network,
                                                        initial_super_network=initial_super_network, final_super_network=final_super_network,
                                                        MicroTransitNodes=MicroTransitNodes, path_cache=path_cache, state=state, base=base,
                                                        iter_choice_prob=iter_agent_choice_prob[iteration], total_rejection_penalty=total_rejection_penalty,
                                                        wait_times=wait_times, transit_link_vmt=transit_link_vmt, transit_link_pax=transit_link_pax,
                                                        off_micro_transit_link_vmt=off_micro_transit_link_vmt, off_micro_transit_link_pax=off_micro_transit_link_pax,
                                                        F_transit_trips=F_transit_trips, new_fleetpy_demand=new_fleetpy_demand)


                                                    ####################
                                                    #Convergence test right after the Binary Choice Model
                                                    ##########################################
                                                    # config.INDIV_CONVERG_TEST (mtsm_model/config.py) chooses between two convergence tests:
                                                    # - True (used): individual-level test, conv_test.indiv_convergence_test(). For every traveler it compares the
                                                    #   choice probabilities [prob_Auto, prob_T] with the previous iteration and sums (p_now - p_before)^2 / p_before
                                                    #   over all travelers and both modes. An iteration passes if the sum is <= CONVERGENCE_GAP. The model has
                                                    #   converged after two passing iterations (num_converged == 2), or at MAXIMUM_ITERATION.
                                                    # - False (not used, kept for later): aggregate-level test, conv_test.convergence_test(M_share, M_share_pre). It
                                                    #   compares only the overall microtransit mode share with the previous iteration: converged if the share changed
                                                    #   by at most 1% (relative). It is unfinished and does not work if switched on as it is (docs/open_issues.md, I-16):
                                                    #     * its call below is commented out, and nothing computes M_share / M_share_pre, so `converged` never
                                                    #       becomes True;
                                                    #     * the stop at MAXIMUM_ITERATION is only in the individual-level branch, so the loop would never end;
                                                    #     * convergence_test() raises UnboundLocalError when the share changed by more than 1%.
                                                    # aggregated level convergence test
                                                    if config.INDIV_CONVERG_TEST == False:
                                                        if iteration >= 1:
                                                            print("convergence check.....")
                                                            # converged,per_diff=conv_test.convergence_test(M_share,M_share_pre)
                                                            # print("Aggregated Level Convergence Test","M_share",M_share,"M_share_pre",M_share_pre,"per_diff",per_diff,"converged",converged)
                                                    else:
                                                        if iteration >= 1:
                                                            print("convergence check.....")
                                                            converged_, sum_sq_per_diff = conv_test.indiv_convergence_test(iter_agent_choice_prob[iteration], iter_agent_choice_prob[iteration - 1],config.CONVERGENCE_GAP)

                                                            iter_sum_sq_per_diff.append((iteration,sum_sq_per_diff))

                                                            if converged_ == True:
                                                                num_converged += 1
                                                                if num_converged == 2:
                                                                    converged = True


                                                            if iteration == config.MAXIMUM_ITERATION:
                                                                # stop after MAXIMUM_ITERATION iterations even if the test has not passed twice
                                                                converged = True

                                                            print("Individual Level Convergence Test:","sum of square percentage difference ", sum_sq_per_diff, "converged",converged)
                                                            if converged == True:
                                                                write_converged_results(
                                                                    writer=writer, cfg=cfg, test_scenario=test_scenario, study_area=study_area, repositioning=repositioning,
                                                                    microtransit_run=microtransit_run, headway=headway, virstop=virstop, fleet_size=fleet_size,
                                                                    M_operating_hrs=M_operating_hrs, F_operating_hrs=F_operating_hrs, operating_periods=operating_periods,
                                                                    num_virstop_scen=num_virstop_scen, num_fleet_size_scen=num_fleet_size_scen,
                                                                    num_operating_periods_scen=num_operating_periods_scen, tt_num_agents=tt_num_agents,
                                                                    output_folder=output_folder, transit_line_dist_list=transit_line_dist_list,
                                                                    transit_line_duration=transit_line_duration, transit_link_vmt=transit_link_vmt,
                                                                    transit_link_pax=transit_link_pax, off_micro_transit_link_vmt=off_micro_transit_link_vmt,
                                                                    off_micro_transit_link_pax=off_micro_transit_link_pax, tot_weighted_5_min_F=tot_weighted_5_min_F,
                                                                    tot_weighted_10_min_F=tot_weighted_10_min_F, tot_weighted_15_min_F=tot_weighted_15_min_F, state=state,
                                                                    base=base, totals=totals, iter_sum_sq_per_diff=iter_sum_sq_per_diff,
                                                                    last_fleetpy_wait_time=last_fleetpy_wait_time, last_rejection_rate=last_rejection_rate)
                                                                scenario_count += 1
                                                    if converged == False:
                                                        wait_times, rejection_rate, last_rejection_rate, last_fleetpy_wait_time = run_fleetpy_and_update_networks(
                                                            cc=cc, sc=sc, log_level=log_level, log_f=LOG_F, cfg=cfg, repositioning=repositioning,
                                                            microtransit_run=microtransit_run, headway=headway, virstop=virstop, M_operating_hrs=M_operating_hrs,
                                                            fleet_size=fleet_size, study_area=study_area, iteration=iteration, demand_file=demand_file,
                                                            new_fleetpy_demand=new_fleetpy_demand)


                                                    iteration+=1



                                                timeatfinished = datetime.datetime.now()
                                                processingtime = timeatfinished - pre_timeatfinished
                                                pre_timeatfinished = timeatfinished
                                                print(scenario_count, "th scenario finished","...virtual_stop:", virstop, "(%)","headway", headway, "(mins)", "fleet_size", fleet_size, "(veh)", "operating_periods",operating_periods,"....... end time is:",timeatfinished,"run time is: ",processingtime)



        csvfile.close()

        timeatfinished = datetime.datetime.now()
        processingtime = timeatfinished - start_time
        print("Study_area",study_area,"integrated system model run finished....... end time is:", timeatfinished, "total run time is: ", processingtime)
