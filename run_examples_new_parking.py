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
                                                transit_tt_VMT = 0
                                                transit_tt_VMT_base = 0

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
                                                                                F_operating_hrs * 60 / config.BASE_FRT_HEADWAY) * \
                                                                                            transit_line_duration[
                                                                                                route_id] / 60 * 170  # Ritun Jan 7, 2024: add base F operating cost calculation
                                                                        transit_tt_VMT += 2 * (
                                                                                F_operating_hrs * 60 / headway) * dist
                                                                        transit_tt_VMT_base += 2 * (
                                                                                F_operating_hrs * 60 / config.BASE_FRT_HEADWAY) * dist

                                                                F_gas_cost = transit_tt_VMT * config.F_GAS_PER_MILE
                                                                F_gas_cost_base = transit_tt_VMT_base * config.F_GAS_PER_MILE  # Ritun Jan 7, 2024: add base F gas cost calculation
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
                                                                    for rq_id in state.travel_time_delta:
                                                                        T_walking_time = 0 #03/22/26 - Siwei
                                                                        tt_saved_with_micro = 0
                                                                        gen_cost_saved_with_micro = 0
                                                                        c_tt_travel_time = 0
                                                                        c_tt_travel_dist = 0
                                                                        if state.pre_iter_mode[rq_id]=="T": #031726: Siwei add this line
                                                                            mode="T"
                                                                            m_waiting_time = state.agent_M_tot_wait_time[rq_id]
                                                                            if m_waiting_time>0:
                                                                                num_M+=1
                                                                            f_waiting_time = state.agent_F_tot_wait_time[rq_id]
                                                                            if f_waiting_time > 0:
                                                                                num_F += 1
                                                                            T_walking_time=state.agent_tot_walk_time[rq_id]
                                                                            if T_walking_time > 0:
                                                                                num_W += 1

                                                                            total_T_revenue += state.agent_op_cost[rq_id]
                                                                            total_F_revenue += state.agent_op_cost_Fix[rq_id]
                                                                            total_M_revenue += state.agent_op_cost_Micro[rq_id]
                                                                            if m_waiting_time >0:
                                                                                tt_saved_with_micro = state.travel_time_delta[rq_id]
                                                                                gen_cost_saved_with_micro = state.gen_cost_delta[rq_id]
                                                                        else:
                                                                            mode="C"
                                                                            m_waiting_time = 0
                                                                            f_waiting_time = 0
                                                                            T_walking_time = 0
                                                                            c_tt_travel_time = state.agent_travel_time[rq_id]
                                                                            c_tt_travel_dist = state.agent_travel_dist[rq_id]/config.MILE_METER

                                                                        origin=state.agent_O[rq_id]
                                                                        dest=state.agent_D[rq_id]
                                                                        dp_time=state.agent_rq_time[rq_id]

                                                                        total_op_cost+=state.agent_op_cost[rq_id]
                                                                        total_mob_increase+=state.mob_logsum_delta[rq_id]
                                                                        total_switch_mode+=state.agent_switch_mode[rq_id]
                                                                        total_M_wait_time += m_waiting_time
                                                                        total_F_wait_time += f_waiting_time
                                                                        total_walk_time += T_walking_time
                                                                        tt_gen_cost += state.agent_gen_cost[rq_id]

                                                                        # 03/02/2026 Siwei: previously "agent_M_tot_wait_time (s)": m_waiting_time
                                                                        # 03/02/2026 Siwei: now
                                                                        #03/09/2026 Siwei add the following lines of code
                                                                        if (state.agent_M_tot_travel_time[rq_id]==0) and (state.ag_VMT_M[rq_id]!=0):
                                                                            aaa=0
                                                                            print("microtransit distance (%s) not equal to microtransit travel time (%s):",state.ag_VMT_M[rq_id],state.agent_M_tot_travel_time[rq_id])
                                                                        writer_indiv.writerow({"rq_id": rq_id,"origin": origin, "dest": dest,
                                                                             "dp_time": dp_time,"mode": mode, "switch_mode":state.agent_switch_mode[rq_id],
                                                                             "tt (s)": state.agent_travel_time[rq_id],"dist (mi)": state.agent_travel_dist[rq_id] / config.MILE_METER,
                                                                             "tt_C (s)": c_tt_travel_time,"dist_C (mi)": c_tt_travel_dist,"tt_M (s)":state.agent_M_tot_travel_time[rq_id],
                                                                             "dist_M (mi)": state.ag_VMT_M[rq_id],"tt_F (s)":state.agent_F_tot_travel_time[rq_id],"dist_F (mi)": state.ag_VMT_F[rq_id],
                                                                              "agent_M_tot_wait_time (s)": m_waiting_time,"agent_F_tot_wait_time (s)": f_waiting_time,
                                                                             "out_of_pock_cost ($)":state.agent_op_cost[rq_id],"tt_saved_with_micro (s)": tt_saved_with_micro,"gen_cost_saved_with_micro": state.gen_cost_delta[rq_id],
                                                                             "mob_logsum_increased_with_micro":state.mob_logsum_delta[rq_id],"agent_prob (auto,transit)":state.agent_choice_prob[rq_id],
                                                                             "agent_ran_num": state.agent_ran_num[rq_id],
                                                                             "tt_W (s)": T_walking_time,"dist_W (mi)": state.ag_VMT_W[rq_id],"income (USD)":state.agent_income[rq_id],"agent_transit_15min_acc":state.agent_transit_15min_acc[rq_id]})



                                                                csvfile_indiv.close()
                                                                if num_M!=0:
                                                                    avg_M_wait_time = total_M_wait_time /totals.num_M_trips #total microtransit waiting time/microtransit trips
                                                                else:
                                                                    avg_M_wait_time=0
                                                                if num_F!=0:
                                                                    avg_F_wait_time = total_F_wait_time/totals.num_F_trips #total waiting time/ total number of F trips
                                                                else:
                                                                    avg_F_wait_time=0
                                                                if num_W!=0:
                                                                    avg_walk_time = total_walk_time/num_W
                                                                else:
                                                                    avg_walk_time=0
                                                                F_revenue=total_F_revenue
                                                                M_revenue=total_M_revenue
                                                                if totals.num_F_trips==0:
                                                                    if microtransit_run == "micro_only":
                                                                        F_sub_per_ridership = 0
                                                                    else:
                                                                        F_sub_per_ridership=-999
                                                                else:
                                                                    F_sub_per_ridership=(F_oper_cost-F_revenue)/totals.num_F_trips # fixed transit subsidy per fixed transit trip


                                                                #calculate the turn-off micro transit scenario
                                                                #under every different fixed route transit headway, we need to calculate the cost again
                                                                if (num_virstop_scen==1) and (num_fleet_size_scen==1) and (num_operating_periods_scen==1) and (microtransit_run=="micro") and (repositioning==True):
                                                                    #calculate off_micro metrics
                                                                    off_micro_F_revenue=base.off_micro_F_trips*config.BASE_FRT_FARE
                                                                    if base.off_micro_F_trips==0:
                                                                        off_micro_F_sub_per_ridership=-999
                                                                        off_micro_tt_sub = -999
                                                                    else:
                                                                        off_micro_tt_sub =(F_oper_cost - off_micro_F_revenue)
                                                                        off_micro_F_sub_per_ridership = off_micro_tt_sub / base.off_micro_F_trips

                                                                    off_micro_w_trip_legs=0
                                                                    off_micro_tot_walk_time=0
                                                                    off_micro_avg_walk_time=0
                                                                    off_micro_F_trip_legs=0
                                                                    off_micro_tot_F_wait_time=0
                                                                    off_micro_avg_F_wait_time=0
                                                                    off_micro_total_op_cost=0
                                                                    off_micro_tt_gen_cost = 0

                                                                    for rq_id in state.travel_time_delta:
                                                                        off_micro_total_op_cost += base.off_micro_agent_op_cost[rq_id]
                                                                        off_micro_tt_gen_cost += base.off_micro_agent_gen_cost[rq_id]

                                                                    for rq_id in base.off_micro_agent_tot_walk_time:
                                                                        if base.off_micro_agent_tot_walk_time[rq_id]>0:
                                                                            off_micro_w_trip_legs+=1
                                                                            off_micro_tot_walk_time+=base.off_micro_agent_tot_walk_time[rq_id]
                                                                        if base.off_micro_agent_F_tot_wait_time[rq_id]>0:
                                                                            off_micro_F_trip_legs+=1
                                                                            off_micro_tot_F_wait_time+=base.off_micro_agent_F_tot_wait_time[rq_id]



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
                                                                            off_micro_avg_F_wait_time=off_micro_tot_F_wait_time/base.off_micro_F_trips # total waiting time/fixed transit trips
                                                                    off_micro_tt_VMT = base.off_micro_VMT_auto + 0+ transit_tt_VMT

                                                                    microtransit_run_pre=microtransit_run
                                                                    microtransit_run="non_micro"
                                                                    individual_result_dir = os.path.join(output_folder,"individual_results_%s_M_fsize_%s_op_hr_%s_hw_%s_virstop_%s_scen_%s.csv" % (str(microtransit_run), str(fleet_size),str(M_operating_hrs), str(headway),str(virstop),str(test_scenario)))

                                                                    aaa=1
                                                                    if test_scenario==cfg.TRPartA_test_scenario_list[0]:
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
                                                                            for rq_id in state.travel_time_delta:

                                                                                mode = base.off_micro_ag_mode[
                                                                                    rq_id]

                                                                                origin = state.agent_O[rq_id]
                                                                                dest = state.agent_D[rq_id]
                                                                                dp_time = state.agent_rq_time[
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
                                                                                    if base.off_micro_agent_F_tot_wait_time[rq_id] > 0:
                                                                                        tt_F = base.off_micro_ag_tot_tt[rq_id]
                                                                                        dist_F = base.off_micro_ag_tot_dist[rq_id]
                                                                                    else:
                                                                                        tt_F = 0
                                                                                        dist_F = 0
                                                                                else:
                                                                                    tt_C =base.off_micro_ag_tot_tt[rq_id]
                                                                                    dist_C = base.off_micro_ag_tot_dist[rq_id]
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
                                                                                         base.off_micro_ag_tot_tt[
                                                                                             rq_id],
                                                                                     "dist (mi)":
                                                                                         base.off_micro_ag_tot_dist[
                                                                                             rq_id],
                                                                                     "tt_C (s)": tt_C,
                                                                                     "dist_C (mi)": dist_C,
                                                                                     "tt_M (s)": tt_M,
                                                                                     "dist_M (mi)": dist_M,
                                                                                     "tt_F (s)": tt_F,
                                                                                     "dist_F (mi)": dist_F,
                                                                                     "out_of_pock_cost ($)":
                                                                                         base.off_micro_agent_op_cost[
                                                                                             rq_id],
                                                                                     "tt_saved_with_micro (s)": 0,
                                                                                     "gen_cost_saved_with_micro": 0,
                                                                                     "mob_logsum_increased_with_micro": 0,
                                                                                     "agent_prob (auto,transit)":
                                                                                         base.off_micro_agent_choice_prob[
                                                                                             rq_id],
                                                                                     "agent_ran_num":
                                                                                         base.off_micro_agent_ran_num[
                                                                                             rq_id],
                                                                                     "agent_M_tot_wait_time (s)": 0,
                                                                                     "agent_F_tot_wait_time (s)":
                                                                                         base.off_micro_agent_F_tot_wait_time[
                                                                                             rq_id],
                                                                                     "tt_W (s)":
                                                                                         base.off_micro_agent_tot_walk_time[
                                                                                             rq_id],
                                                                                     "dist_W (mi)":
                                                                                         base.off_micro_ag_VMT_W[
                                                                                             rq_id]})

                                                                        microtransit_run = microtransit_run_pre

                                                                        pure_F_users = (
                                                                                    base.off_micro_T_trips - base.off_micro_W_trips)

                                                                        # Write the fixed only scenario
                                                                        if test_scenario == cfg.TRPartA_test_scenario_list[0]:
                                                                            writer.writerow({"test_scen": 0,"dscrptn": "FRT_only_scen", "study_area": study_area,"repositioning": str(False),
                                                                                             "microtrasnit": "non_micro","hdwy (min)": headway,
                                                                                             "vir_stop (%)": 0,"flt_sz": 0, "op_periods": 0,"tt_agents": tt_num_agents,
                                                                                             "car_users": base.off_micro_auto_trips,"car_mode_share (%)": base.off_micro_auto_trips / tt_num_agents,
                                                                                             "trsit_mode_users (W_M_F)": base.off_micro_T_trips,"transit_mode_share (%)": base.off_micro_T_trips / tt_num_agents,
                                                                                             "pure_M_users": 0,"M_trips": 0,"M_mode_share (%)": 0 / tt_num_agents,"pure_F_users": pure_F_users,
                                                                                             "F_trips": base.off_micro_F_trips,"F_mode_share (%)": base.off_micro_F_trips / tt_num_agents,
                                                                                             "pure_walk_users": base.off_micro_W_trips,"W_mode_share (%)": base.off_micro_W_trips / tt_num_agents,
                                                                                             "walk_users": off_micro_w_trip_legs,"M_pls_F_users": 0,
                                                                                             "M_pls_F_mode_share (%)": 0,"F_oper_cost ($)": F_oper_cost_base,
                                                                                             "M_oper_cost ($)": 0,"F_revenue ($)": off_micro_F_revenue,
                                                                                             "M_revenue ($)": 0,"Total_T_revenue ($)": off_micro_F_revenue,
                                                                                             "tot_sub ($)": off_micro_tt_sub,"sub_per_F_trip ($)": off_micro_F_sub_per_ridership,
                                                                                             "sub_per_F_rider ($)": np.nan if pure_F_users==0 else off_micro_tt_sub / (pure_F_users),
                                                                                             "sub_per_M_trip ($)": 0,"sub_per_M_rider ($)": 0,"sub_per_T_trip ($)": off_micro_F_sub_per_ridership,
                                                                                             "sub_per_T_rider ($)": np.nan if pure_F_users==0 else off_micro_tt_sub / (pure_F_users),
                                                                                             "sub_per_M_pax_mile ($/mi)": 0,"sub_per_F_pax_mile ($/mi)": off_micro_tt_sub / base.off_micro_VMT_F,
                                                                                             "sub_per_T_pax_mile ($/mi)": off_micro_tt_sub / base.off_micro_VMT_F,"sub_per_M_VMT ($/mi)": 0,
                                                                                             "sub_per_F_VMT ($/mi)": (off_micro_tt_sub) / (transit_tt_VMT),
                                                                                             "sub_per_T_VMT ($/mi)": (off_micro_tt_sub) / (transit_tt_VMT),
                                                                                             "tt_auto_gas_cost ($)": off_micro_total_op_cost - off_micro_F_revenue,
                                                                                             "auto_gas_cost_per_mile ($/mi)": (off_micro_total_op_cost - off_micro_F_revenue) / base.off_micro_VMT_auto,
                                                                                             "avg_M_fare": 0,"avg_F_fare": np.nan if pure_F_users==0 else off_micro_F_revenue / (pure_F_users),
                                                                                             "avg_T_fare": np.nan if pure_F_users==0 else off_micro_F_revenue / (pure_F_users),
                                                                                             "avg_auto_gas_cost": (off_micro_total_op_cost - off_micro_F_revenue) / base.off_micro_auto_trips,
                                                                                             "tt_o_pckt_cost ($)": off_micro_total_op_cost,"tt_mob_lgsm_inc_with_micro": 0,
                                                                                             "tt_gen_cost": off_micro_tt_gen_cost,"tt_mode_switch": 0,
                                                                                             "M_avg_wait_time (s)": 0,"F_avg_wait_time (s)": off_micro_avg_F_wait_time,
                                                                                             "avg_walk_time (s)": off_micro_avg_walk_time,"tt_walk_time (h)": off_micro_tot_walk_time / 3600,
                                                                                             "car_VMT (mi)": base.off_micro_VMT_auto,"M_VMT (mi)": 0,
                                                                                             "M_PMT (mi)": 0,"M_PMT/M_VMT": 0,"F_VMT (mi)": transit_tt_VMT,"F_PMT (mi)": base.off_micro_VMT_F,"F_PMT/F_VMT": base.off_micro_VMT_F / transit_tt_VMT,
                                                                                             "tt_VMT (mi)": off_micro_tt_VMT,"tt_walk_dist (mi)": base.off_micro_VMT_W,
                                                                                             "wghted_acc_emp_5_min": tot_weighted_5_min_F,"wghted_acc_emp_10_min": tot_weighted_10_min_F,
                                                                                             "wghted_acc_emp_15_min": tot_weighted_15_min_F,"M_util_rate (%)": 0,
                                                                                             "M_veh_occ": 0,"M_avg_speed (mph)": 0,"cnvrg (iter, sm_sq_per_diff)": 0, "fleetpy_wait": 0, "rejection_rate": 0})


                                                                    else:
                                                                        aaa=1

                                                                    microtransit_run=microtransit_run_pre

                                                                    pure_F_users=(base.off_micro_T_trips-base.off_micro_W_trips)

                                                                    # Write the fixed only scenario
                                                                    if test_scenario == cfg.TRPartA_test_scenario_list[0]:

                                                                        writer.writerow({"test_scen":0,"dscrptn":"FRT_only_scen","study_area":study_area,"repositioning":str(False),"microtrasnit":"non_micro","hdwy (min)": headway, "vir_stop (%)": 0, "flt_sz": 0,"op_periods": 0,
                                                                                     "tt_agents": tt_num_agents,"car_users": base.off_micro_auto_trips,"car_mode_share (%)": base.off_micro_auto_trips/tt_num_agents,
                                                                                     "trsit_mode_users (W_M_F)": base.off_micro_T_trips,"transit_mode_share (%)":base.off_micro_T_trips/tt_num_agents,"pure_M_users":0, "M_trips": 0,"M_mode_share (%)":0/tt_num_agents,
                                                                                     "pure_F_users":pure_F_users,"F_trips": base.off_micro_F_trips,"F_mode_share (%)":base.off_micro_F_trips/tt_num_agents,"pure_walk_users": base.off_micro_W_trips,"W_mode_share (%)":base.off_micro_W_trips/tt_num_agents,
                                                                                     "walk_users":off_micro_w_trip_legs, "M_pls_F_users":0,"M_pls_F_mode_share (%)":0,"F_oper_cost ($)": F_oper_cost_base,
                                                                                     "M_oper_cost ($)": 0,"F_revenue ($)": off_micro_F_revenue, "M_revenue ($)": 0,"Total_T_revenue ($)":off_micro_F_revenue, "tot_sub ($)":off_micro_tt_sub,
                                                                                     "sub_per_F_trip ($)": off_micro_F_sub_per_ridership,"sub_per_F_rider ($)":np.nan if pure_F_users==0 else off_micro_tt_sub/(pure_F_users),"sub_per_M_trip ($)": 0,"sub_per_M_rider ($)":0,"sub_per_T_trip ($)":off_micro_F_sub_per_ridership,"sub_per_T_rider ($)":np.nan if pure_F_users==0 else off_micro_tt_sub/(pure_F_users),
                                                                                     "sub_per_M_pax_mile ($/mi)":0,"sub_per_F_pax_mile ($/mi)":off_micro_tt_sub/base.off_micro_VMT_F,"sub_per_T_pax_mile ($/mi)":off_micro_tt_sub/base.off_micro_VMT_F,
                                                                                     "sub_per_M_VMT ($/mi)": 0,"sub_per_F_VMT ($/mi)": (off_micro_tt_sub) / (transit_tt_VMT),"sub_per_T_VMT ($/mi)": (off_micro_tt_sub) / (transit_tt_VMT),
                                                                                     "tt_auto_gas_cost ($)":off_micro_total_op_cost-off_micro_F_revenue,"auto_gas_cost_per_mile ($/mi)":(off_micro_total_op_cost-off_micro_F_revenue)/base.off_micro_VMT_auto,
                                                                                     "avg_M_fare": 0, "avg_F_fare":np.nan if pure_F_users==0 else off_micro_F_revenue/(pure_F_users),"avg_T_fare":np.nan if pure_F_users==0 else off_micro_F_revenue/(pure_F_users), "avg_auto_gas_cost":(off_micro_total_op_cost-off_micro_F_revenue)/base.off_micro_auto_trips,
                                                                                    "tt_o_pckt_cost ($)": off_micro_total_op_cost,
                                                                                     "tt_mob_lgsm_inc_with_micro": 0,"tt_gen_cost":off_micro_tt_gen_cost,
                                                                                     "tt_mode_switch": 0,"M_avg_wait_time (s)": 0,
                                                                                     "F_avg_wait_time (s)": off_micro_avg_F_wait_time,"avg_walk_time (s)": off_micro_avg_walk_time,"tt_walk_time (h)":off_micro_tot_walk_time/3600,
                                                                                     "car_VMT (mi)":base.off_micro_VMT_auto,"M_VMT (mi)":0,"M_PMT (mi)":0,"M_PMT/M_VMT":0,"F_VMT (mi)":transit_tt_VMT,"F_PMT (mi)":base.off_micro_VMT_F,"F_PMT/F_VMT":base.off_micro_VMT_F/transit_tt_VMT,"tt_VMT (mi)":off_micro_tt_VMT,"tt_walk_dist (mi)":base.off_micro_VMT_W,
                                                                                     "wghted_acc_emp_5_min":tot_weighted_5_min_F,
                                                                                     "wghted_acc_emp_10_min":tot_weighted_10_min_F,
                                                                                     "wghted_acc_emp_15_min":tot_weighted_15_min_F,
                                                                                     "M_util_rate (%)": 0, "M_veh_occ": 0,"M_avg_speed (mph)": 0 ,"cnvrg (iter, sm_sq_per_diff)":0, "fleetpy_wait": 0, "rejection_rate": 0})

                                                                #calculate the turn-on micro transit scenario

                                                                util_rate, veh_occ, total_vmt, empty_vkm, avg_speed_mph = output_metrics.get_fleetpy_eval_output_metrics(repositioning)
                                                                tt_VMT = totals.VMT_auto + total_vmt + transit_tt_VMT

                                                                M_gas_cost = total_vmt * config.M_GAS_PER_MILE
                                                                M_mode_operating_cost += M_gas_cost

                                                                M_sub_per_ridership = (M_mode_operating_cost - M_revenue) / totals.num_M_trips # microtransit subsidy per microtransit trips
                                                                tt_sub = (F_oper_cost + M_mode_operating_cost - F_revenue - M_revenue)
                                                                tt_sub_per_ridership = tt_sub / (totals.num_F_trips + totals.num_M_trips)

                                                                if microtransit_run=="micro_only":
                                                                    PMT_VMT_ratio_F = 0
                                                                    headway_pre=headway
                                                                    headway = 0
                                                                    off_micro_tot_walk_time = 0
                                                                else:
                                                                    PMT_VMT_ratio_F = totals.VMT_F / transit_tt_VMT


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

                                                                if (totals.pure_F_user + totals.M_F_user)!=0:
                                                                    sub_per_F_rider = (F_oper_cost-F_revenue)/(totals.pure_F_user+totals.M_F_user)
                                                                else:
                                                                    sub_per_F_rider = 999

                                                                if (totals.pure_M_user+totals.M_F_user) != 0:
                                                                    sub_per_M_rider=(M_mode_operating_cost-M_revenue)/(totals.pure_M_user+totals.M_F_user)
                                                                else:
                                                                    sub_per_M_rider = 999

                                                                if (totals.pure_M_user+totals.M_F_user) != 0:
                                                                    avg_M_fare = M_revenue/(totals.pure_M_user+totals.M_F_user)
                                                                else:
                                                                    avg_M_fare = 0

                                                                if (totals.pure_F_user+totals.M_F_user) != 0:
                                                                    avg_F_fare = F_revenue/(totals.pure_F_user+totals.M_F_user)
                                                                else:
                                                                    avg_F_fare = 0

                                                                if (totals.pure_M_user + totals.pure_F_user + totals.M_F_user) != 0:
                                                                    avg_T_fare = (M_revenue + F_revenue) / (totals.pure_M_user + totals.pure_F_user + totals.M_F_user)
                                                                else:
                                                                    avg_T_fare = 0

                                                                if (totals.VMT_F)!=0:
                                                                    sub_per_F_pax_mile =(F_oper_cost-F_revenue)/(totals.VMT_F)
                                                                else:
                                                                    sub_per_F_pax_mile = 999


                                                                writer.writerow({"test_scen":test_scenario,"dscrptn":dscrptn,"study_area":study_area,"repositioning":repositioning,"microtrasnit":microtransit_run,"hdwy (min)": headway, "vir_stop (%)": virstop, "flt_sz": fleet_size, "op_periods": operating_periods,
                                                                     "tt_agents": tt_num_agents,"car_users": totals.num_car_trips,  "car_mode_share (%)": totals.num_car_trips/tt_num_agents,
                                                                     "trsit_mode_users (W_M_F)": totals.num_transit_users ,"transit_mode_share (%)":totals.num_transit_users/tt_num_agents,"pure_M_users":totals.pure_M_user,"M_trips":totals.num_M_trips,"M_mode_share (%)":totals.pure_M_user/tt_num_agents,
                                                                      "pure_F_users":totals.pure_F_user,"F_trips":totals.num_F_trips,"F_mode_share (%)":totals.pure_F_user/tt_num_agents,"pure_walk_users":totals.num_W_trips,"W_mode_share (%)":totals.num_W_trips/tt_num_agents,
                                                                      "walk_users":num_W,"M_pls_F_users":totals.M_F_user,"M_pls_F_mode_share (%)":totals.M_F_user/tt_num_agents, "F_oper_cost ($)": F_oper_cost,
                                                                     "M_oper_cost ($)": M_mode_operating_cost,"F_revenue ($)":F_revenue,"M_revenue ($)":M_revenue,"Total_T_revenue ($)":F_revenue+M_revenue,"tot_sub ($)":tt_sub,
                                                                      "sub_per_F_trip ($)":F_sub_per_ridership,"sub_per_F_rider ($)":sub_per_F_rider, "sub_per_M_trip ($)":M_sub_per_ridership,"sub_per_M_rider ($)":sub_per_M_rider,"sub_per_T_trip ($)":tt_sub_per_ridership,
                                                                      "sub_per_T_rider ($)":tt_sub/(totals.pure_F_user+totals.pure_M_user+totals.M_F_user),"sub_per_M_pax_mile ($/mi)":(M_mode_operating_cost-M_revenue)/(totals.VMT_M),"sub_per_F_pax_mile ($/mi)":sub_per_F_pax_mile,"sub_per_T_pax_mile ($/mi)":(tt_sub)/(totals.VMT_M+totals.VMT_F),
                                                                      "sub_per_M_VMT ($/mi)": (M_mode_operating_cost - M_revenue) / (total_vmt),"sub_per_F_VMT ($/mi)": (F_oper_cost - F_revenue)/(transit_tt_VMT),"sub_per_T_VMT ($/mi)": (tt_sub) / (total_vmt + transit_tt_VMT),
                                                                      "tt_auto_gas_cost ($)":total_op_cost-(F_revenue+M_revenue),"auto_gas_cost_per_mile ($/mi)":(total_op_cost-(F_revenue+M_revenue))/totals.VMT_auto,
                                                                       "avg_M_fare": avg_M_fare, "avg_F_fare":avg_F_fare,"avg_T_fare":avg_T_fare, "avg_auto_gas_cost":(total_op_cost-(F_revenue+M_revenue))/totals.num_car_trips,
                                                                      "tt_o_pckt_cost ($)": total_op_cost,"tt_mob_lgsm_inc_with_micro": total_mob_increase,"tt_gen_cost":tt_gen_cost,
                                                                      "tt_mode_switch": total_switch_mode, "M_avg_wait_time (s)": avg_M_wait_time,
                                                                      "F_avg_wait_time (s)": avg_F_wait_time, "avg_walk_time (s)":avg_walk_time,"tt_walk_time (h)":total_walk_time/3600,
                                                                      "car_VMT (mi)":totals.VMT_auto,"M_VMT (mi)":total_vmt,"M_PMT (mi)":totals.VMT_M,"M_PMT/M_VMT":totals.VMT_M/total_vmt,"F_VMT (mi)":transit_tt_VMT,"F_PMT (mi)":totals.VMT_F,"F_PMT/F_VMT":PMT_VMT_ratio_F,"tt_VMT (mi)":tt_VMT,"tt_walk_dist (mi)":totals.VMT_W,
                                                                      "wghted_acc_emp_5_min":avg_period_total_weighted_5_min,
                                                                      "wghted_acc_emp_10_min":avg_period_total_weighted_10_min,
                                                                      "wghted_acc_emp_15_min":avg_period_total_weighted_15_min,
                                                                        "M_util_rate (%)":util_rate,"M_veh_occ":veh_occ,"M_avg_speed (mph)":avg_speed_mph,"cnvrg (iter, sm_sq_per_diff)":iter_sum_sq_per_diff, "fleetpy_wait": last_fleetpy_wait_time, "rejection_rate": last_rejection_rate})


                                                                if microtransit_run == "micro_only":
                                                                    headway = headway_pre



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
