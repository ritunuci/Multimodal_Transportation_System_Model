"""One iteration of the choice model (restructuring step 6, docs/entry_script_refactor_plan.md).

For every traveler: networks, least-cost paths, costs, logit probabilities, one random draw, and the trip legs
of the chosen mode, which go into FleetPy's demand file (microtransit legs) and the FRT demand file. Moved
unchanged from run_examples_new_parking.py (the random draws happen in the same order); the arguments are the
values the code read from the surrounding scenario loop, now taken from the StudyArea and Scenario objects.

"""
import csv
import random

from mtsm_model import config, paths, choice, trip_legs
from mtsm_model.state import IterationTotals


def run_iteration(cfg, area, scen, *, iteration, state, base, iter_choice_prob, total_rejection_penalty, wait_times):
    """Run the choice model for all travelers; write the FRT demand file (F_transit_trips) and FleetPy's demand
    file (new_fleetpy_demand). Updates state, base (iteration 0 of the first virtual-stop / fleet / period
    scenario), path_cache, the link VMT dicts and iter_choice_prob (iter_agent_choice_prob[iteration]). wait_times:
    FleetPy's average waiting time per period from the previous iteration (None in iteration 0, where it is not
    read). area: scenarios.StudyArea, scen: scenarios.Scenario. Returns the IterationTotals."""
    test_scenario, microtransit_run, headway, virstop = scen.test_scenario, scen.microtransit_run, scen.headway, scen.virstop
    fleet_size, M_operating_hrs, operating_periods = scen.fleet_size, scen.M_operating_hrs, scen.operating_periods
    num_virstop_scen, num_fleet_size_scen, num_operating_periods_scen = scen.num_virstop_scen, scen.num_fleet_size_scen, scen.num_operating_periods_scen
    path_cache, F_transit_trips = scen.path_cache, scen.F_transit_trips
    study_area, agent_list_, tt_num_agents, auto_network = area.study_area, area.agent_list_, area.tt_num_agents, area.auto_network
    initial_super_network, final_super_network = area.initial_super_network, area.final_super_network
    MicroTransitNodes, new_fleetpy_demand = area.MicroTransitNodes, area.new_fleetpy_demand
    transit_link_vmt, transit_link_pax = area.transit_link_vmt, area.transit_link_pax
    off_micro_transit_link_vmt, off_micro_transit_link_pax = area.off_micro_transit_link_vmt, area.off_micro_transit_link_pax

    totals = IterationTotals()

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
                change_mode=True  #change_mode is True, unless the probability difference is smaller than MODE_CHANGE_THRESHOLD

                origin = agent.rq_O
                dest = agent.rq_D
                rq_time = agent.rq_time
                rq_id = agent.rq_id

                state.agent_O[rq_id] = origin
                state.agent_D[rq_id] = dest
                state.agent_rq_time[rq_id] = rq_time
                state.agent_income[rq_id]= agent.income
                state.agent_transit_15min_acc[rq_id] = agent.transit_15min_acc
                state.agent_beta_fare[rq_id] = agent.bt_t_fr

                time_period = choice.time_period_of(rq_time)
                in_operating_period = time_period in operating_periods

                state.agent_M_tot_travel_dist[rq_id] = 0
                state.agent_F_tot_travel_dist[rq_id] = 0
                T_F_network, T_micro_network = paths.networks_for_traveler(microtransit_run, iteration, time_period, operating_periods,
                                                                           initial_super_network, final_super_network, auto_network,
                                                                           headway, virstop, M_operating_hrs, fleet_size)

                # least generalized cost paths: car and walk + FRT computed in the first fare scenario and reused in the others
                if test_scenario == cfg.TRPartA_test_scenario_list[0]:
                    parking_dur, bt_c_gas, auto = paths.auto_path(path_cache, study_area, auto_network, agent, cfg, iteration)
                else:
                    # parking_dur and bt_c_gas are not cached: they are the values of the last car path computed, i.e. of the
                    # last traveler of the first fare scenario (docs/open_issues.md, I-18)
                    auto = path_cache.auto[rq_id]
                    parking_dur, bt_c_gas = path_cache.last_parking_dur, path_cache.last_bt_c_gas
                if test_scenario == cfg.TRPartA_test_scenario_list[0]:
                    frt = paths.frt_path(path_cache, study_area, T_F_network, agent, cfg, test_scenario, total_rejection_penalty,
                                         iteration)
                else:
                    frt = path_cache.frt[rq_id]
                # walk + microtransit + FRT; no path for "micro_only" outside the operating periods (only transit costs 0 are
                # read then)
                if microtransit_run == "micro_only" and not in_operating_period:
                    micro = None
                else:
                    micro = paths.micro_path(study_area, T_micro_network, agent, cfg, test_scenario, total_rejection_penalty,
                                             iteration)

                costs = choice.trip_costs(microtransit_run, in_operating_period, auto, parking_dur, bt_c_gas, frt, micro, dest,
                                          time_period)
                # calculate travel time savings by allowing microtransit
                state.travel_time_delta[rq_id] = costs.travel_time_F - costs.travel_time_T
                state.gen_cost_delta[rq_id] = costs.gen_cost_F - costs.gen_cost_T
                prob_Auto, prob_T, prob_Auto_no_micro, prob_T_no_micro = choice.choice_probabilities(microtransit_run,
                                                                                                     in_operating_period, costs)

                if iteration>0:
                    if choice.keeps_previous_mode(state.pre_iter_prob_T[rq_id], prob_T): # if probability does not change a lot, then we don't change agents' modes.
                        change_mode=False
                    else:
                        change_mode = True #03/02/2026: Siwei added this line
                        change_mode_ag_list.append(rq_id)

                state.pre_iter_prob_T[rq_id]=prob_T
                state.mob_logsum_delta[rq_id] = choice.mobility_logsum_delta(costs, state.agent_beta_fare[rq_id])

                base.off_micro_agent_choice_prob[rq_id]= [prob_Auto_no_micro, prob_T_no_micro]
                iter_choice_prob[rq_id] = [prob_Auto, prob_T]


                ran_num = random.random()
                #calculate the output metrics of turn-off microtransit
                if (num_virstop_scen == 1) and (num_fleet_size_scen == 1) and (num_operating_periods_scen == 1) and (iteration==0):
                    base.off_micro_ag_tot_dist[rq_id] = 0
                    base.off_micro_ag_tot_tt[rq_id] = 0
                    base.off_micro_agent_gen_cost[rq_id] = 0
                    base.off_micro_ag_VMT_W[rq_id] = 0
                    base.off_micro_agent_F_tot_wait_time[rq_id] = 0
                    base.off_micro_agent_tot_walk_time[rq_id] = 0

                    base.off_micro_agent_ran_num[rq_id]=ran_num
                    if ran_num < prob_T_no_micro:

                        base.off_micro_ag_mode[rq_id] = "T"
                        base.off_micro_T_trips += 1
                        base.off_micro_ag_tot_tt[rq_id] = costs.travel_time_F
                        base.off_micro_ag_tot_dist[rq_id] = costs.travel_dist_F/config.MILE_METER

                        base.off_micro_agent_gen_cost[rq_id]=costs.gen_cost_F
                        base.off_micro_agent_op_cost[rq_id] = costs.agent_op_cost_F
                        legs_F = trip_legs.split_time_path(frt.time_path_all_[1:-1], rq_time, iteration)
                        base.off_micro_F_trips += len(legs_F.F_legs)
                        for F_wait_time in legs_F.F_wait:
                            base.off_micro_agent_F_tot_wait_time[rq_id] += F_wait_time
                        for walk_time in legs_F.walk:
                            base.off_micro_agent_tot_walk_time[rq_id] += walk_time
                        if legs_F.walk_only:
                            base.off_micro_W_trips += 1

                        #calculate VMT for fixed transit and walking when microtransit turned off
                        dist_legs_F = trip_legs.split_dist_path(frt.dist_path_all_[1:-1], micro.dist_path_all_[0])
                        for (pre_node, node, miles) in dist_legs_F.F_links:
                            base.off_micro_VMT_F += miles
                            off_micro_transit_link_vmt[time_period][(pre_node, node)] += miles
                            off_micro_transit_link_pax[time_period][(pre_node, node)] += 1
                        for miles in dist_legs_F.W_links:
                            base.off_micro_VMT_W += miles
                            base.off_micro_ag_VMT_W[rq_id] += miles


                    else:  # agent choose the car mode
                        base.off_micro_ag_mode[rq_id] = "C"
                        base.off_micro_ag_tot_tt[rq_id]= costs.travel_time_auto
                        base.off_micro_ag_tot_dist[rq_id] = costs.travel_dist_auto/config.MILE_METER
                        base.off_micro_auto_trips+=1
                        base.off_micro_agent_op_cost[rq_id] = costs.agent_op_cost_auto  # agent_out-of-pocket
                        base.off_micro_VMT_auto += (costs.travel_dist_auto/config.MILE_METER)
                        base.off_micro_agent_gen_cost[rq_id]=costs.gen_cost_auto



                #turn on microtransit
                if change_mode==True:

                    if iteration ==0: #when it is in iteration 0, all travelers get M and F travel time initialized
                        state.agent_switch_mode[rq_id] = 0
                        state.agent_M_tot_travel_time[rq_id] = 0
                        state.agent_F_tot_travel_time[rq_id] = 0
                        state.ag_VMT_F[rq_id] = 0
                        state.ag_VMT_W[rq_id] = 0
                        state.ag_VMT_M[rq_id] = 0
                        state.ag_num_W_trips[rq_id] = 0
                        state.ag_num_M_trips[rq_id] = 0
                        state.ag_num_F_trips[rq_id] = 0

                    state.agent_ran_num[rq_id] = ran_num
                    state.agent_choice_prob[rq_id] = [prob_Auto,prob_T]

                    if ran_num < prob_T:  # agent choose the transit mode
                        ##when mode change=true, and transit mode is chosen, all travelers get M and F travel time initialized
                        current_mode = "T"
                        state.pre_iter_mode[rq_id] = current_mode

                        state.agent_switch_mode[rq_id] = 0
                        state.agent_M_tot_travel_time[rq_id] = 0
                        state.agent_F_tot_travel_time[rq_id] = 0
                        state.ag_num_W_trips[rq_id] = 0
                        state.ag_num_M_trips[rq_id] = 0
                        state.ag_num_F_trips[rq_id] = 0



                        state.agent_gen_cost[rq_id] = costs.gen_cost_T
                        if ran_num>=prob_T_no_micro:
                            state.agent_switch_mode[rq_id]=1 #this means: if no microtransit, this agent will choose car, but with microtransit, this agent will choose transit mode
                        # 1107 Siwei
                        state.agent_M_tot_wait_time[rq_id] = 0
                        state.agent_F_tot_wait_time[rq_id] = 0
                        state.agent_tot_walk_time[rq_id] = 0
                        state.agent_travel_time[rq_id]=costs.travel_time_T
                        state.agent_travel_dist[rq_id] =costs.travel_dist_T
                        state.agent_op_cost[rq_id] = costs.agent_op_cost_T  # agent_out-of-pocket cost

                        state.agent_op_cost_Fix[rq_id] = costs.agent_F_fare
                        state.agent_op_cost_Micro[rq_id] = costs.agent_M_fare

                        legs = trip_legs.split_time_path(micro.time_path_all_[1:-1], rq_time, iteration)
                        # microtransit legs: FleetPy requests
                        for (request_time, M_origin_node, M_dest_node) in legs.M_legs:
                            rq_id_fleetpy = trip_legs.free_request_id(rq_id, M_rq_id_list)
                            try:
                                writer_M.writerow({'rq_time': request_time, 'start': MicroTransitNodes[M_origin_node],'end': MicroTransitNodes[M_dest_node], 'request_id': rq_id_fleetpy})
                            except:
                                raise Exception("M_origin_node",M_origin_node,"M_dest_node",M_dest_node,"trimmed_transit_time_path",micro.time_path_all_[1:-1])
                            M_rq_id_list.append(rq_id_fleetpy)
                            #document the previous iteration microtransit information
                            #rq_time, start, end, request_id
                            state.pre_iter_M_info[rq_id]=(request_time,MicroTransitNodes[M_origin_node],MicroTransitNodes[M_dest_node],rq_id_fleetpy)

                            totals.num_M_trips += 1
                            state.ag_num_M_trips[rq_id] +=1
                        # fixed route transit legs
                        for (request_time, F_origin_node, F_dest_node) in legs.F_legs:
                            totals.num_F_trips += 1
                            state.ag_num_F_trips[rq_id] +=1
                            writer_F.writerow({'depart_time':request_time , 'start': F_origin_node,'end': F_dest_node,'request_id': rq_id})
                            # document the previous iteration fixed route transit information
                            # rq_time, start, end, request_id
                            state.pre_iter_F_info[rq_id]=(request_time,F_origin_node,F_dest_node,rq_id)
                        for M_wait_time in legs.M_wait:
                            state.agent_M_tot_wait_time[rq_id] += M_wait_time
                        for F_wait_time in legs.F_wait:
                            state.agent_F_tot_wait_time[rq_id] += F_wait_time
                        for walk_time in legs.walk:
                            state.agent_tot_walk_time[rq_id] += walk_time
                        for M_travel_time in legs.M_travel:
                            state.agent_M_tot_travel_time[rq_id] += M_travel_time
                        for F_travel_time in legs.F_travel:
                            state.agent_F_tot_travel_time[rq_id] += F_travel_time
                        if legs.walk_only:
                            totals.num_W_trips += 1
                            state.ag_num_W_trips[rq_id]+=1
                        trip_legs.count_transit_user(totals, state.ag_num_M_trips[rq_id], state.ag_num_F_trips[rq_id])
                        # calculate VMT for fixed transit and walking when microtransit turned on
                        dist_legs = trip_legs.split_dist_path(micro.dist_path_all_[1:-1], micro.dist_path_all_[0])
                        ag_VMT_W_intermediate=0
                        ag_VMT_M_intermediate=0
                        ag_VMT_F_intermediate = 0
                        for (pre_node, node, miles) in dist_legs.F_links:
                            totals.VMT_F += miles
                            ag_VMT_F_intermediate += miles
                            transit_link_vmt[time_period][(pre_node, node)]+=miles
                            transit_link_pax[time_period][(pre_node, node)]+=1
                        for miles in dist_legs.W_links:
                            totals.VMT_W += miles
                            ag_VMT_W_intermediate += miles
                        for miles in dist_legs.M_links:
                            totals.VMT_M += miles
                            ag_VMT_M_intermediate += miles

                        state.ag_VMT_W[rq_id]=ag_VMT_W_intermediate
                        state.ag_VMT_M[rq_id]=ag_VMT_M_intermediate
                        state.ag_VMT_F[rq_id]=ag_VMT_F_intermediate

                    else:  # agent choose the car mode

                        current_mode = "C"
                        state.agent_M_tot_travel_time[rq_id] = 0
                        state.agent_F_tot_travel_time[rq_id] = 0
                        # 03/09/2026 Siwei add the following lines of code
                        state.ag_VMT_M[rq_id] = 0
                        state.agent_M_tot_wait_time[rq_id]=0

                        state.pre_iter_mode[rq_id] = current_mode
                        totals.num_car_trips += 1
                        state.agent_travel_time[rq_id] = costs.travel_time_auto
                        state.agent_travel_dist[rq_id] = costs.travel_dist_auto
                        state.agent_op_cost[rq_id] = costs.agent_op_cost_auto  # agent_out-of-pocket cost
                        state.agent_op_cost_Fix[rq_id] = 0
                        state.agent_op_cost_Micro[rq_id] = 0
                        totals.VMT_auto+=(costs.travel_dist_auto/config.MILE_METER)
                        state.agent_gen_cost[rq_id]=costs.gen_cost_auto

                        state.ag_VMT_W[rq_id] = 0
                        state.agent_F_tot_wait_time[rq_id] = 0
                        state.agent_tot_walk_time[rq_id] = 0
                else:
                    ag_prev_iter_mode=state.pre_iter_mode[rq_id]
                    if ag_prev_iter_mode =="T":

                        totals.VMT_F += state.ag_VMT_F[rq_id]
                        totals.VMT_W += state.ag_VMT_W[rq_id]
                        totals.VMT_M += state.ag_VMT_M[rq_id]

                        totals.num_W_trips += state.ag_num_W_trips[rq_id]
                        totals.num_F_trips += state.ag_num_F_trips[rq_id]
                        totals.num_M_trips += state.ag_num_M_trips[rq_id]



                        trip_legs.count_transit_user(totals, state.ag_num_M_trips[rq_id], state.ag_num_F_trips[rq_id])

                        if rq_id in state.pre_iter_M_info:
                            # rq_time, start, end, request_id
                            (pre_ier_rq_time, pre_iter_start,pre_iter_end, pre_iter_request_id) = state.pre_iter_M_info[rq_id]
                            rq_id_fleetpy = trip_legs.free_request_id(pre_iter_request_id, M_rq_id_list)
                            writer_M.writerow({'rq_time': pre_ier_rq_time,'start': pre_iter_start,'end': pre_iter_end,'request_id':rq_id_fleetpy})
                            M_rq_id_list.append(rq_id_fleetpy)


                            # Ritun added: March 2nd, 2026
                            pre_iter_period = choice.time_period_of(pre_ier_rq_time)
                            if pre_iter_period == "EV":
                                print("!!!! EVENING MICRO USER DETECTED !!!!")
                            state.agent_M_tot_wait_time[rq_id] = wait_times[pre_iter_period] * state.ag_num_M_trips[rq_id]

                        if rq_id in state.pre_iter_F_info:
                            #(request_time,F_origin_node,F_dest_node,rq_id)
                            (pre_ier_rq_time_F, pre_iter_start_F,pre_iter_end_F, pre_iter_request_id_F) = state.pre_iter_F_info[rq_id]
                            writer_F.writerow({'depart_time': pre_ier_rq_time_F, 'start': pre_iter_start_F,'end': pre_iter_end_F, 'request_id': pre_iter_request_id_F})
                        state.agent_travel_time[rq_id]=state.agent_M_tot_wait_time[rq_id]+state.agent_M_tot_travel_time[rq_id]+state.agent_F_tot_travel_time[rq_id]+state.agent_F_tot_wait_time[rq_id]+state.agent_tot_walk_time[rq_id]

                    else:
                        totals.num_car_trips += 1
                        totals.VMT_auto += (costs.travel_dist_auto / config.MILE_METER)



            #03/02/2026: Siwei comment it
            totals.num_transit_users = tt_num_agents - totals.num_car_trips

            print("number of agents prob_T changed greater than threshold",config.MODE_CHANGE_THRESHOLD,":", len(change_mode_ag_list))


        csvfile_M.close()

    csvfile_F.close()

    return totals
