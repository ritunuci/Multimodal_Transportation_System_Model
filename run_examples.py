# -------------------------------------------------------------------------------------------------------------------- #
# external imports
# ----------------
import sys
import traceback
import pandas as pd
import multiprocessing as mp
from collections import OrderedDict
import time
import datetime
import get_microtransit_skims as mt
import csv

# src imports
# -----------
import src.misc.config as config
from src.misc.init_modules import load_simulation_environment
from src.misc.globals import *

import inte_sys_mode_choice
import convergence_test as conv_test
import network_algorithms as n_a
import get_auto_skims as auto
import get_walk_transit_skims as wt
# main functions
# --------------
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
                  keep_old=False, continue_next_after_error=False):
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

# -------------------------------------------------------------------------------------------------------------------- #
# ----> you can replace the following part by your respective if __name__ == '__main__' part for run_private*.py <---- #
# -------------------------------------------------------------------------------------------------------------------- #

# global variables for testing
# ----------------------------
MAIN_DIR = os.path.dirname(__file__)
MOD_STR = "MoD_0"
MM_STR = "Assertion"
LOG_F = "standard_bugfix.log"


# testing results of examples
# ---------------------------
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
        output_dir = os.path.join(MAIN_DIR, "studies", study_name, "results", scenario_name)
        standard_eval_f = os.path.join(output_dir, "standard_eval.csv")
        tmp_df = pd.read_csv(standard_eval_f, index_col=0)
        tmp_df.loc[G_SCENARIO_NAME, MOD_STR] = scenario_name
        return_list.append((tmp_df))
    return return_list


def check_assertions(list_eval_df, all_scenario_assertion_dict):
    """This function checks assertions of scenarios to give a quick impression if results are fitting.

    :param list_eval_df: list of evaluation data frames
    :param all_scenario_assertion_dict: dictionary of scenario id to assertion dictionaries
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
        with open(LOG_F, "a") as fh:
            fh.write(prt_str)
        list_result_tuples.append((scenario_name, mismatch, tmp_df))
    return list_result_tuples


# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == "__main__":
    mp.freeze_support()

    start_time = datetime.datetime.now()
    indiv_converg_test=True
    debug_mode=True
    ###############
    #
    #################
    ##########
    # Different operating hours testing scenarios
    operating_period_1 = ["AM", "PM"] #10 hr
    operating_period_2 = ["AM", "MD", "PM"] #15hr
    operating_period_3 = ["AM", "MD", "PM", "EV"] #19hr
    # operating_periods_scenarios=[operating_period_1,operating_period_2,operating_period_3]
    operating_periods_scenarios = [operating_period_3] #just for testing
    #####################
    # Different virtual stops testing scenarios
    # virtual_stop_scenarios=[50,75,100]
    # virtual_stop_scenarios = [75,100] #just for testing
    virtual_stop_scenarios = [75]  # just for testing
    ###############################
    # Different headway testing scenarios
    # headway_scenarios=[20,30,60]
    headway_scenarios = [30]  #just for testing
    #######################################
    # Different Fleet size scenarios
    if debug_mode==True:
        # fleet_size_scenarios = [3,4,5,6]
        fleet_size_scenarios = [4]
    else:
        fleet_size_scenarios=[20,30,40]
        # fleet_size_scenarios = [40]
    #######################################
    #Create performance metrics dictonaries
    ###***Cost****###############################
    # operating_cost_bf_M_dict=OrderedDict()
    # operating_cost_af_M_dict = OrderedDict()
    # revenue_bf_M_dict=OrderedDict()
    # revenue_af_M_dict = OrderedDict()
    # net_profit_bf_M_dict=OrderedDict()
    # net_profit_af_M_dict = OrderedDict()
    # net_profit_diff_dict = OrderedDict()
    # ###***Mobility******##################################
    # mobility_sum_before_M_dict=OrderedDict()
    # mobility_sum_after_M_dict = OrderedDict()
    # mobility_sum_diff_dict = OrderedDict()
    # ###***selected mode experience******##################################
    # selected_mode_user_exper_dict=OrderedDict()
    # selected_mode_user_exper_bf_dict = OrderedDict()
    # selected_mode_user_exper_diff_dict = OrderedDict()

    ##########################################
    # #Initialization of dictionaries
    # for headway in headway_scenarios:
    #     operating_cost_bf_M_dict[headway] = OrderedDict()
    #     operating_cost_af_M_dict[headway] = OrderedDict()
    #     revenue_bf_M_dict[headway] = OrderedDict()
    #     revenue_af_M_dict[headway] = OrderedDict()
    #     net_profit_bf_M_dict[headway] = OrderedDict()
    #     net_profit_af_M_dict[headway] = OrderedDict()
    #     net_profit_diff_dict[headway] = OrderedDict()
    #
    #     mobility_sum_before_M_dict[headway] = OrderedDict()
    #     mobility_sum_after_M_dict[headway] = OrderedDict()
    #     mobility_sum_diff_dict[headway] = OrderedDict()
    #
    #     selected_mode_user_exper_dict[headway] = OrderedDict()
    #     selected_mode_user_exper_bf_dict[headway] = OrderedDict()
    #     selected_mode_user_exper_diff_dict[headway] = OrderedDict()
    #     for virtual_stop in virtual_stop_scenarios:
    #         operating_cost_bf_M_dict[headway][virtual_stop] = OrderedDict()
    #         operating_cost_af_M_dict[headway][virtual_stop] = OrderedDict()
    #         revenue_bf_M_dict[headway][virtual_stop] = OrderedDict()
    #         revenue_af_M_dict[headway][virtual_stop] = OrderedDict()
    #         net_profit_bf_M_dict[headway][virtual_stop] = OrderedDict()
    #         net_profit_af_M_dict[headway][virtual_stop] = OrderedDict()
    #         net_profit_diff_dict[headway][virtual_stop] = OrderedDict()
    #
    #         mobility_sum_before_M_dict[headway][virtual_stop] = OrderedDict()
    #         mobility_sum_after_M_dict[headway][virtual_stop] = OrderedDict()
    #         mobility_sum_diff_dict[headway][virtual_stop] = OrderedDict()
    #
    #         selected_mode_user_exper_dict[headway][virtual_stop] = OrderedDict()
    #         selected_mode_user_exper_bf_dict[headway][virtual_stop] = OrderedDict()
    #         selected_mode_user_exper_diff_dict[headway][virtual_stop] = OrderedDict()
    #         for fleet_size in fleet_size_scenarios:
    #             operating_cost_bf_M_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             operating_cost_af_M_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             revenue_bf_M_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             revenue_af_M_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             net_profit_bf_M_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             net_profit_af_M_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             net_profit_diff_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #
    #             mobility_sum_before_M_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             mobility_sum_after_M_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             mobility_sum_diff_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #
    #             selected_mode_user_exper_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             selected_mode_user_exper_bf_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             selected_mode_user_exper_diff_dict[headway][virtual_stop][fleet_size] = OrderedDict()
    #             for operating_periods in operating_periods_scenarios:
    #                 if operating_periods==["AM", "MD", "PM", "EV"]:
    #                     M_operating_hrs=19
    #                 elif operating_periods==["AM", "MD", "PM"]:
    #                     M_operating_hrs = 15
    #                 else:
    #                     M_operating_hrs = 10
    #                 F_operating_hrs=19
    #                 route_duration=60 #60minutes
    #                 F_mode_operating_cost=(F_operating_hrs*60/headway*route_duration)/60*100 #$fixed route transit operating cost 100/veh-hour
    #                 M_mode_operating_cost=(M_operating_hrs*fleet_size)*60 #microtransit operating cost $60/veh-hour
    #
    #                 operating_cost_bf_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = F_mode_operating_cost
    #                 operating_cost_af_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = F_mode_operating_cost+M_mode_operating_cost
    #                 revenue_bf_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #                 revenue_af_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #                 net_profit_bf_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #                 net_profit_af_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #                 net_profit_diff_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #
    #                 mobility_sum_before_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #                 mobility_sum_after_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #                 mobility_sum_diff_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #
    #                 selected_mode_user_exper_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #                 selected_mode_user_exper_bf_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0
    #                 selected_mode_user_exper_diff_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = 0

    scenario_count=0

    network_folder="D:/Ritun/Siwei_Micro_Transit/Data/0719_input"
    if debug_mode==True:
        evaluation_file=os.path.join(network_folder,"debug_evaluation.csv")
    else:
        evaluation_file = os.path.join(network_folder, "evaluation.csv")
    with open(evaluation_file, 'w+', newline='') as csvfile:
        fieldnames = ['headway', 'virtual_stop','fleet_size','operating_periods',"total_trips","mode_split","F_oper_cost","M_oper_cost","revenue_bf_M","revenue_af_M","net_prft_bf_M","net_prft_af_M","net_prfit_diff","mob_bf_M","mob_af_M","mob_diff","select_mode_exper_bf_M","select_mode_exper_af_M","select_mode_exper_diff"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        print("program starts here......start time is:",start_time)
        print("Debug mode:",debug_mode)

        # read the request profile
        # request_file = os.path.join(network_folder, "trips_nodes_study_area_with_beta.csv")
        # agent_list = n_a.read_request(request_file)
        # print("Read the request. Number of agents:", len(agent_list))
        for headway in headway_scenarios: #put bus design parameter in the most outer loop
            walk_transit_network = os.path.join(network_folder, 'hw_%s_walk_transit_edges.csv' % str(int(headway/2)))
            for virtual_stop in virtual_stop_scenarios: #virtual stops - not necessarily influence the cost, but will influence the mobility
                virtual_stop_dir = os.path.join(network_folder, 'virtual_stops_%s.csv' % str(virtual_stop))
                virtual_stop_list = mt.read_virtual_stop(virtual_stop_dir)
                for fleet_size in fleet_size_scenarios: #fleetsize - influence the cost & mobility
                    scs_path = os.path.join(os.path.dirname(__file__), "studies", "example_study", "scenarios")

                    if debug_mode == True:
                        sc = os.path.join(scs_path, "debug_example_ir_only_%s_veh.csv" % str(fleet_size))
                    else:
                        sc = os.path.join(scs_path, "example_ir_only_%s_veh.csv" % str(fleet_size))

                    for operating_periods in operating_periods_scenarios: #fleetsize - influence the cost & mobility
                        if operating_periods==["AM", "MD", "PM", "EV"]:
                            M_operating_hrs=19
                        elif operating_periods==["AM", "MD", "PM"]:
                            M_operating_hrs = 15
                        else:
                            M_operating_hrs = 10
                        F_operating_hrs = 19 # fixed route transit 19 hrs
                        route_duration = 60  # 60minutes
                        print("Current Scenario:",scenario_count,"th senario","...virtual_stop:",virtual_stop,"(%)","headway",headway,"(mins)","fleet_size",fleet_size,"(veh)","operating_periods",operating_periods)

                        if len(sys.argv) > 1:
                            run_scenarios(*sys.argv)
                        else:
                            import time
                            # touch log file
                            with open(LOG_F, "w") as _:
                                pass


                            # eval_output_dir='D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/eval_output_dir'
                            # eval_output_file=os.path.join(eval_output_dir, "0510_evaluation.csv")

                            # Base Examples IRS only
                            # ----------------------
                            # a) Pooling in ImmediateOfferEnvironment
                            iteration=0
                            iter_agent_choice_prob=OrderedDict()
                            iter_agent_selected_mode=OrderedDict()
                            # req=1000
                            # veh=5
                            # vir_stop=0.1
                            converged=False
                            # iter_mode_share=OrderedDict()
                            print("Preparing fixed route transit and auto matrices...")
                            print("walk_tansit_network:",walk_transit_network)
                            # network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'
                            edges_dir = os.path.join(network_folder, 'edges.csv')
                            # walking_network_graph = n_a.read_walking_network(edges_dir)
                            walking_visited_temp_all = wt.get_walk_transit_skims(edges_dir)
                            auto_visited_temp_all = auto.get_auto_time_skims(edges_dir)
                            auto_dist_visited_temp_all = auto.get_auto_dist_skims(edges_dir)

                            F_path_mat, F_fare_mat = inte_sys_mode_choice.prepare_F_matrices(walk_transit_network)

                            D_ivt_mat, D_gas_mat = inte_sys_mode_choice.prepare_D_matrices(auto_visited_temp_all,auto_dist_visited_temp_all)

                            num_converged=0
                            while converged==False:
                                print("iteration:",iteration)
                                iter_agent_choice_prob[iteration]=OrderedDict()
                                iter_agent_selected_mode[iteration] = OrderedDict()
                                log_level = "info"
                                cc = os.path.join(scs_path, "constant_config_ir.csv")

                                print("running FleetPy....")
                                run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
                                list_results = read_outputs_for_comparison(cc, sc)
                                all_scenario_assert_dict = {0: {"number users": 88}}
                                check_assertions(list_results, all_scenario_assert_dict)
                                print("running the choice model.....")
                                ##comment it for now
                                if iteration>=1:
                                    iter_agent_choice_prob[iteration],iter_agent_selected_mode[iteration],total_trips,mode_split,revenue_total_af,revenue_total_bf,mobility_sum_after_M,mobility_sum_before_M,mobility_diff_sum,selected_mode_user_exper,selected_mode_user_exper_bf,selected_mode_user_exper_diff = inte_sys_mode_choice.MNL_choice(F_path_mat,F_fare_mat,D_ivt_mat,D_gas_mat,walking_visited_temp_all,auto_visited_temp_all,auto_dist_visited_temp_all,
                                                                                                                                                                                                                                                                                                                              debug_mode,operating_periods,virtual_stop_list,iteration,iter_agent_choice_prob[iteration-1],iter_agent_selected_mode[iteration-1])
                                else:
                                    iter_agent_choice_prob[iteration], iter_agent_selected_mode[iteration],total_trips,mode_split, revenue_total_af, revenue_total_bf, mobility_sum_after_M, mobility_sum_before_M, mobility_diff_sum, selected_mode_user_exper, selected_mode_user_exper_bf, selected_mode_user_exper_diff = inte_sys_mode_choice.MNL_choice(
                                    F_path_mat, F_fare_mat, D_ivt_mat, D_gas_mat,walking_visited_temp_all,auto_visited_temp_all,auto_dist_visited_temp_all, debug_mode, operating_periods,
                                    virtual_stop_list, iteration)

                                #aggregated level convergence test
                                if indiv_converg_test==False:
                                    if iteration>=1:
                                        print("convergence check.....")
                                        # converged,per_diff=conv_test.convergence_test(M_share,M_share_pre)
                                        # print("Aggregated Level Convergence Test","M_share",M_share,"M_share_pre",M_share_pre,"per_diff",per_diff,"converged",converged)
                                    # M_share_pre=M_share
                                    #individual level convergence test
                                else:
                                    if iteration>=1:
                                        print("convergence check.....")
                                        converged_,sum_sq_per_diff=conv_test.indiv_convergence_test(iter_agent_choice_prob[iteration],iter_agent_choice_prob[iteration-1])

                                        if converged_==True:
                                            num_converged+=1
                                            if num_converged==2:
                                                converged=True

                                        if iteration==10:
                                            converged = True
                                        print("Individual Level Convergence Test:", "sum of square percentage difference ",sum_sq_per_diff, "converged", converged)
                                        if converged==True:
                                            F_oper_cost= (F_operating_hrs * 60 / headway) * route_duration / 60 * 100  # $fixed route transit operating cost 100/veh-hour
                                            M_mode_operating_cost = M_operating_hrs * fleet_size * 60  # microtransit operating cost $60/veh-hour
                                            #revenue_total_af, revenue_total_bf, mobility_sum_after_M, mobility_sum_before_M, mobility_diff_sum, selected_mode_user_exper, selected_mode_user_exper_bf, selected_mode_user_exper_diff
                                            revenue_bf_M=revenue_total_bf
                                            revenue_af_M=revenue_total_af
                                            net_prft_bf_M=revenue_total_bf-F_oper_cost
                                            net_prft_af_M=revenue_total_af-F_oper_cost-M_mode_operating_cost
                                            net_prfit_diff=net_prft_af_M-net_prft_bf_M
                                            mob_bf_M=mobility_sum_before_M
                                            mob_af_M=mobility_sum_after_M
                                            mob_diff=mobility_diff_sum
                                            select_mode_exper_bf_M=selected_mode_user_exper_bf
                                            select_mode_exper_af_M=selected_mode_user_exper
                                            select_mode_exper_diff=selected_mode_user_exper_diff

                                            writer.writerow(
                                                {'headway': headway, 'virtual_stop': virtual_stop, 'fleet_size': fleet_size,
                                                 'operating_periods': operating_periods,"total_trips":total_trips,"mode_split":mode_split,"F_oper_cost":F_oper_cost,"M_oper_cost":M_mode_operating_cost,
                                                 "revenue_bf_M":revenue_bf_M, "revenue_af_M":revenue_af_M, "net_prft_bf_M":net_prft_bf_M, "net_prft_af_M":net_prft_af_M,
                                                "net_prfit_diff":net_prfit_diff, "mob_bf_M":mob_bf_M, "mob_af_M":mob_af_M, "mob_diff":mob_diff,
                                                "select_mode_exper_bf_M":select_mode_exper_bf_M, "select_mode_exper_af_M":select_mode_exper_af_M,
                                                "select_mode_exper_diff": select_mode_exper_diff })
                                            scenario_count+=1
                                            #['headway', 'virtual_stop','fleet_size','operating_periods',"F_oper_cost","M_oper_cost","revenue_bf_M","revenue_af_M","net_prft_bf_M","net_prft_af_M","net_prfit_diff","mob_bf_M","mob_af_M","mob_diff","select_mode_exper_bf_M","select_mode_exper_af_M","select_mode_exper_diff"]

                                            # revenue_bf_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = revenue_total_bf
                                            # revenue_af_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = revenue_total_af
                                            # net_profit_bf_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = revenue_total_bf-operating_cost_bf_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs]
                                            # net_profit_af_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = revenue_total_af-operating_cost_af_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs]
                                            # net_profit_diff_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = net_profit_af_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs]-net_profit_bf_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs]
                                            #
                                            # mobility_sum_before_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = mobility_sum_before_M
                                            # mobility_sum_after_M_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = mobility_sum_after_M
                                            # mobility_sum_diff_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = mobility_diff_sum
                                            #
                                            # selected_mode_user_exper_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = selected_mode_user_exper
                                            # selected_mode_user_exper_bf_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = selected_mode_user_exper_bf
                                            # selected_mode_user_exper_diff_dict[headway][virtual_stop][fleet_size][M_operating_hrs] = selected_mode_user_exper_diff

                                    # M_share_pre=M_share
                                # converged=True #####just for testing purpose
                                iteration+=1

                            timeatfinished = datetime.datetime.now()
                            processingtime = timeatfinished - start_time
                            print("integrated system model run finished....... end time is:",timeatfinished,"run time is: ",processingtime)
    csvfile.close()




        # df_final.to_csv(eval_output_file)
        # # Base Examples with Optimization (requires gurobi license!)
        # # ----------------------------------------------------------
        # b) Pooling in BatchOffer environment
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_pool.csv")
        # # sc = os.path.join(scs_path, "example_pool.csv")
        # # sc = os.path.join(scs_path, "example_pool_1000_rq_5_veh.csv")
        # # sc = os.path.join(scs_path, "example_pool_1000_rq_10_veh.csv")
        # sc = os.path.join(scs_path, "example_pool_1000_rq_20_veh.csv")
        # # sc = os.path.join(scs_path, "example_pool_1000_rq_30_veh.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        # list_results = read_outputs_for_comparison(cc, sc)
        # all_scenario_assert_dict = {0: {"number users": 91}}
        # check_assertions(list_results, all_scenario_assert_dict)

        # # c) Pooling in ImmediateOfferEnvironment
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_ir.csv")
        # sc = os.path.join(scs_path, "example_ir_batch.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        # list_results = read_outputs_for_comparison(cc, sc)
        # all_scenario_assert_dict = {0: {"number users": 90}}
        # check_assertions(list_results, all_scenario_assert_dict)
        #
        # # d) Pooling with RV heuristics in ImmediateOfferEnvironment (with doubled demand)
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_ir.csv")
        # t0 = time.perf_counter()
        # # no heuristic scenario
        # sc = os.path.join(scs_path, "example_pool_noheuristics.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        # list_results = read_outputs_for_comparison(cc, sc)
        # all_scenario_assert_dict = {0: {"number users": 199}}
        # check_assertions(list_results, all_scenario_assert_dict)
        # # with heuristic scenarios
        # t1 = time.perf_counter()
        # sc = os.path.join(scs_path, "example_pool_heuristics.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        # list_results = read_outputs_for_comparison(cc, sc)
        # t2 = time.perf_counter()
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=2)
        # t3 = time.perf_counter()
        # print(f"Computation time without heuristics: {round(t1-t0, 1)} | with heuristics 1 CPU: {round(t2-t1,1)}"
        #       f"| with heuristics 2 CPU: {round(t3-t2,1)}")
        # all_scenario_assert_dict = {0: {"number users": 191}}
        # check_assertions(list_results, all_scenario_assert_dict)
        #
        # # g) Pooling with RV heuristic and Repositioning in ImmediateOfferEnvironment (with doubled demand and
        # #       bad initial vehicle distribution)
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_ir_repo.csv")
        # sc = os.path.join(scs_path, "example_ir_heuristics_repositioning.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        # list_results = read_outputs_for_comparison(cc, sc)
        # all_scenario_assert_dict = {0: {"number users": 198}}
        # check_assertions(list_results, all_scenario_assert_dict)
        #
        # # h) Pooling with public charging infrastructure (low range vehicles)
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_charge.csv")
        # sc = os.path.join(scs_path, "example_charge.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        #
        # # i) Pooling and active vehicle fleet size is controlled externally (time and utilization based)
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_depot.csv")
        # sc = os.path.join(scs_path, "example_depot.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        #
        # # j) Pooling with public charging and fleet size control (low range vehicles)
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_depot_charge.csv")
        # sc = os.path.join(scs_path, "example_depot_charge.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        #
        # # h) Pooling with multiprocessing
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_depot_charge.csv")
        # # no heuristic scenario single core
        # t0 = time.perf_counter()
        # sc = os.path.join(scs_path, "example_depot_charge.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        # list_results = read_outputs_for_comparison(cc, sc)
        # all_scenario_assert_dict = {0: {"number users": 199}}
        # check_assertions(list_results, all_scenario_assert_dict)
        # print("Computation without multiprocessing took {}s".format(time.perf_counter() - t0))
        # # no heuristic scenario multiple cores
        # cores = 2
        # t0 = time.perf_counter()
        # sc = os.path.join(scs_path, "example_depot_charge.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=cores, n_parallel_sim=1)
        # list_results = read_outputs_for_comparison(cc, sc)
        # all_scenario_assert_dict = {0: {"number users": 199}}
        # check_assertions(list_results, all_scenario_assert_dict)
        # print("Computation with multiprocessing took {}s".format(time.perf_counter() - t0))
        # print(" -> multiprocessing only usefull for large vehicle fleets")
        #
        # # j) Pooling - multiple operators and broker
        # log_level = "info"
        # cc = os.path.join(scs_path, "constant_config_broker.csv")
        # sc = os.path.join(scs_path, "example_broker.csv")
        # run_scenarios(cc, sc, log_level=log_level, n_cpu_per_sim=1, n_parallel_sim=1)
        #
