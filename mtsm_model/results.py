"""The results of a scenario after convergence (restructuring step 7, docs/entry_script_refactor_plan.md).

Operating costs, revenues and subsidies; fixed-route link VMT files; accessibility; the individual-results files
(with microtransit, and for the fixed-route-only base case); and the rows of the evaluation file (the
fixed-route-only base case, written twice: docs/open_issues.md, I-04; and the scenario). Moved unchanged from
run_examples_new_parking.py; the arguments are the values the code read from the surrounding loops.
"""
import csv
import os

import numpy as np

import output_performance_metrics as output_metrics
from mtsm_model import config


def write_converged_results(*, writer, cfg, test_scenario, study_area, repositioning, microtransit_run, headway,
                            virstop, fleet_size, M_operating_hrs, F_operating_hrs, operating_periods,
                            num_virstop_scen, num_fleet_size_scen, num_operating_periods_scen, tt_num_agents,
                            output_folder, transit_line_dist_list, transit_line_duration, transit_link_vmt,
                            transit_link_pax, off_micro_transit_link_vmt, off_micro_transit_link_pax,
                            tot_weighted_5_min_F, tot_weighted_10_min_F, tot_weighted_15_min_F, state, base, totals,
                            iter_sum_sq_per_diff, last_fleetpy_wait_time, last_rejection_rate):
    """Compute and write the results of the converged scenario. writer: the DictWriter of the evaluation file.
    headway and microtransit_run are changed only inside this function (for the base case and "micro_only").
    The fare scenario's description is known for test_scenario 0-10."""
    transit_tt_VMT = 0
    transit_tt_VMT_base = 0
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



