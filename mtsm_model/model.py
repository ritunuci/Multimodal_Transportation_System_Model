"""Run the model: all study areas and scenarios (restructuring step 8, docs/entry_script_refactor_plan.md).

run_model() follows the framework diagram (docs/mtsm_framework.png): for each scenario, iterate the choice model
(iteration.run_iteration) and FleetPy (microtransit.run_fleetpy_and_update_networks) until the travelers' choices
converge, then write the results (results.write_converged_results). Moved from run_examples_new_parking.py.
"""
import csv
import datetime
import os
from collections import OrderedDict

from mtsm_model.helpers import convergence_test as conv_test
from mtsm_model import config
from mtsm_model.state import BaseCase, TravelerState
from mtsm_model.scenarios import load_study_area, scenarios
from mtsm_model.networks import read_iteration_networks
from mtsm_model.iteration import run_iteration
from mtsm_model.microtransit import run_fleetpy_and_update_networks
from mtsm_model.results import EVALUATION_FIELDNAMES, write_converged_results


def run_model(cfg, start_time, log_f):
    """Run every scenario of every study area; write one evaluation file per study area. start_time: for the
    run-time messages; log_f: FleetPy's log file."""
    pre_timeatfinished = start_time
    for study_area in cfg.test_area:
        area = load_study_area(cfg, study_area)
        scenario_count = 0

        with open(area.evaluation_file, 'w+', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=EVALUATION_FIELDNAMES)
            writer.writeheader()

            for scen in scenarios(cfg, area, log_f):
                virstop, headway, fleet_size = scen.virstop, scen.headway, scen.fleet_size
                operating_periods, microtransit_run = scen.operating_periods, scen.microtransit_run
                num_headway_scen, num_virstop_scen = scen.num_headway_scen, scen.num_virstop_scen
                num_fleet_size_scen, num_operating_periods_scen = scen.num_fleet_size_scen, scen.num_operating_periods_scen
                print("Current Scenario:", scenario_count, "th senario", "....headway",headway, "(mins),", "scen", num_headway_scen,
                      "; virtual_stop:", virstop, "(%),", "scen", num_virstop_scen,"; fleet_size:", fleet_size, "(veh),", "scen", num_fleet_size_scen,
                      "; operating_periods:", operating_periods, "scen,",num_operating_periods_scen,"microtransit_scen:",microtransit_run,";")

                run_scenario(cfg, area, scen, writer, log_f)
                scenario_count += 1

                timeatfinished = datetime.datetime.now()
                processingtime = timeatfinished - pre_timeatfinished
                pre_timeatfinished = timeatfinished
                print(scenario_count, "th scenario finished","...virtual_stop:", virstop, "(%)","headway", headway, "(mins)", "fleet_size", fleet_size, "(veh)", "operating_periods",operating_periods,"....... end time is:",timeatfinished,"run time is: ",processingtime)

            csvfile.close()

        timeatfinished = datetime.datetime.now()
        processingtime = timeatfinished - start_time
        print("Study_area",study_area,"integrated system model run finished....... end time is:", timeatfinished, "total run time is: ", processingtime)


def run_scenario(cfg, area, scen, writer, log_f):
    """Iterate the choice model and FleetPy until the travelers' choices converge (or MAXIMUM_ITERATION), then write
    the scenario's results."""
    repositioning, scs_path, study_area = scen.repositioning, scen.scs_path, area.study_area

    iteration=0
    rejection_rate = cfg.initial_rejection_rate / 100  # Ritun added: Feb 14
    last_rejection_rate = 0
    iter_agent_choice_prob=OrderedDict()
    converged=False

    # Metrics of turn-off microtransit (the fixed-route-only base case)
    base = BaseCase()

    num_converged=0

    # per-traveler values with microtransit, kept across the iterations
    state = TravelerState()

    # the car and FRT paths of each traveler, searched in the first iteration and reused (iteration.run_iteration)
    fixed_paths = {}

    iter_sum_sq_per_diff=[]

    rejection_rate_dict = {}  # Ritun added Feb 14

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
        read_iteration_networks(area, scen, iteration, converged)

        # Demand component: calculate how many travelers will choose transit, how many will choose auto;
        # write into FleetPy's demand input directly
        totals = run_iteration(cfg, area, scen, iteration=iteration, state=state, base=base,
                               iter_choice_prob=iter_agent_choice_prob[iteration],
                               total_rejection_penalty=total_rejection_penalty, wait_times=wait_times,
                               fixed_paths=fixed_paths)


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
                    write_converged_results(cfg, area, scen, writer, state=state, base=base, totals=totals,
                                            iter_sum_sq_per_diff=iter_sum_sq_per_diff, last_fleetpy_wait_time=last_fleetpy_wait_time,
                                            last_rejection_rate=last_rejection_rate)
        if converged == False:
            wait_times, rejection_rate, last_rejection_rate, last_fleetpy_wait_time = run_fleetpy_and_update_networks(
                cfg, area, scen, cc=cc, log_level=log_level, log_f=log_f, iteration=iteration)


        iteration+=1
