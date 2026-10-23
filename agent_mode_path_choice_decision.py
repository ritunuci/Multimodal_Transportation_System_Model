#







# def agent_mode_path_choice():
#
#     with open(F_transit_trips, 'w+', newline='') as csvfile_F:
#         fieldnames_F = ["depart_time", "start", "end", "request_id"]
#         writer_F = csv.DictWriter(csvfile_F, fieldnames=fieldnames_F)
#         writer_F.writeheader()
#
#         with open(new_fleetpy_demand, 'w+', newline='') as csvfile_M:
#             fieldnames_M = ["rq_time", "start", "end", "request_id"]
#             writer_M = csv.DictWriter(csvfile_M, fieldnames=fieldnames_M)
#             writer_M.writeheader()
#
#             M_rq_id_list = []
#             for agent in agent_list_:
#                 change_mod e =True  # change_mode is True, unless the probability difference is smaller than the mode_change_threshold
#
#                 origin = agent.rq_O
#                 dest = agent.rq_D
#                 rq_time = agent.rq_time
#                 rq_id = agent.rq_id
#
#                 agent_O[rq_id] = origin
#                 agent_D[rq_id] = dest
#                 agent_rq_time[rq_id] = rq_time
#                 if rq_time <= (10 * 3600):
#                     time_period = "AM"
#                 elif rq_time <= (15 * 3600):
#                     time_period = "MD"
#                 elif rq_time <= (20 * 3600):
#                     time_period = "PM"
#                 else:
#                     time_period = "EV"
#
#                 # agent_M_tot_travel_time[rq_id] = 0
#                 # agent_F_tot_travel_time[rq_id] = 0
#
#                 agent_M_tot_travel_dist[rq_id] = 0
#                 agent_F_tot_travel_dist[rq_id] = 0
#                 # 1108 Siwei: read the initial super-network according to "microtransit", "fixed route trasnit headway","virstop", and "time_period"
#                 T_F_network = initial_super_network["non_micro"]
#                     [headway]  # the fixed route transit network remain constant - won't feedback to it
#                 # microtransit_run = "micro" ###**********************
#                 if iteratio n= =0:
#                     if microtransit_run == "micro":
#                         if time_period in operating_periods:
#                             T_micro_network = initial_super_network["micro"][headway][virstop][M_operating_hrs]
#                         else:
#                             T_micro_network = T_F_network
#                     if microtransit_run == "micro_only":
#                         if time_period in operating_periods:
#                             T_micro_network = initial_super_network["micro_only"][virstop][M_operating_hrs]
#                         else:
#                             T_micro_network = auto_network
#
#                 else:
#                     if microtransit_run == "micro":
#                         if time_period in operating_periods:
#                             T_micro_network = final_super_network["micro"][headway][virstop][M_operating_hrs][time_period]
#                                 [fleet_size]
#                         else:
#                             T_micro_network = T_F_network
#                     if microtransit_run == "micro_only":
#                         if time_period in operating_periods:
#                             T_micro_network = final_super_network["micro_only"][virstop][M_operating_hrs][time_period]
#                                 [fleet_size]
#                         else:
#                             T_micro_network = auto_network
#                         # T_micro_network = initial_super_network["non_micro"][headway] #the fixed route transit network remain constant - won't feedback to it
#
#                 # *****don't calculate it along the way - only*********
#                 # calculate generalized cost shortest path for agent on Auto network
#                 if (num_headway_scen == 1) and (num_virstop_scen == 1) and (num_fleet_size_scen == 1) and \
#                         (num_operating_periods_scen == 1) and (iteration == 0):
#                     auto_visited_temp, auto_time_visited_temp, auto_dist_visited_temp, auto_fare_visited_temp, auto_path, auto_time_path, auto_dist_path = n_a.generalized_cost_dijsktra_OD_heap(
#                         study_area, auto_network, agent, transit_fare, dt_sd_full_trnst_ntwk, mode="C", verbose=False)
#                     auto_time_path_all_ = n_a.getTrajectory_O_to_D(origin, dest, auto_time_path, auto_visited_temp)
#                     agent_auto_visited_temp[rq_id] = auto_visited_temp
#                     agent_auto_time_visited_temp[rq_id] = auto_time_visited_temp
#                     agent_auto_dist_visited_temp[rq_id] = auto_dist_visited_temp
#                     agent_auto_fare_visited_temp[rq_id] = auto_fare_visited_temp
#                     agent_auto_path[rq_id] = auto_path
#                     agent_auto_time_path[rq_id] = auto_time_path
#                     agent_auto_time_path_all_[rq_id] = auto_time_path_all_
#                 else:
#                     auto_visited_temp = agent_auto_visited_temp[rq_id]
#                     auto_time_visited_temp = agent_auto_time_visited_temp[rq_id]
#                     auto_dist_visited_temp = agent_auto_dist_visited_temp[rq_id]
#                     auto_fare_visited_temp = agent_auto_fare_visited_temp[rq_id]
#                     auto_path = agent_auto_path[rq_id]
#                     auto_time_path = agent_auto_time_path[rq_id]
#                     auto_time_path_all_ = agent_auto_time_path_all_[rq_id]
#
#                 # if :
#                 # calculate generalized cost shortest path for agent on W_F network
#                 if (num_virstop_scen == 1) and (num_fleet_size_scen == 1) and (num_operating_periods_scen == 1) and (
#                         iteration == 0):
#                     visited_temp_F, time_visited_temp_F, dist_visited_temp_F, fare_visited_temp_F, path_F, time_path_F, dist_path_F = n_a.generalized_cost_dijsktra_OD_heap(
#                         study_area, T_F_network, agent, transit_fare, dt_sd_full_trnst_ntwk, mode="T", verbose=False)
#                     transit_time_path_all_F = n_a.getTrajectory_O_to_D(origin, dest, time_path_F, visited_temp_F)
#                     transit_dist_path_all_F = n_a.getTrajectory_O_to_D(origin, dest, dist_path_F,
#                                                                        dist_visited_temp_F)  # calculate fixed transit VMT
#
#                     agent_visited_temp_F[rq_id] = visited_temp_F
#                     agent_time_visited_temp_F[rq_id] = time_visited_temp_F
#                     agent_dist_visited_temp_F[rq_id] = dist_visited_temp_F
#                     agent_fare_visited_temp_F[rq_id] = fare_visited_temp_F
#                     agent_path_F[rq_id] = path_F
#                     agent_time_path_F[rq_id] = time_path_F
#                     agent_transit_time_path_all_F[rq_id] = transit_time_path_all_F
#                     agent_transit_dist_path_all_F[rq_id] = transit_dist_path_all_F
#
#                 else:
#                     visited_temp_F = agent_visited_temp_F[rq_id]
#                     time_visited_temp_F = agent_time_visited_temp_F[rq_id]
#                     dist_visited_temp_F = agent_dist_visited_temp_F[rq_id]
#                     fare_visited_temp_F = agent_fare_visited_temp_F[rq_id]
#                     path_F = agent_path_F[rq_id]
#                     time_path_F = agent_time_path_F[rq_id]
#                     transit_time_path_all_F = agent_transit_time_path_all_F[rq_id]
#                     transit_dist_path_all_F = agent_transit_dist_path_all_F[rq_id]
#
#                 # calculate generalized cost shortest path for agent on W_M_F network
#                 if microtransit_run == "micro_only" and (time_period not in operating_periods):
#                     aaa = 0
#                 else:
#                     visited_temp, time_visited_temp, dist_visited_temp, fare_visited_temp, path, time_path, dist_path = n_a.generalized_cost_dijsktra_OD_heap(
#                         study_area, T_micro_network, agent, transit_fare, dt_sd_full_trnst_ntwk, mode="T", verbose=False)
#                     transit_time_path_all_ = n_a.getTrajectory_O_to_D(origin, dest, time_path, visited_temp)
#                     transit_dist_path_all_ = n_a.getTrajectory_O_to_D(origin, dest, dist_path,
#                                                                       dist_visited_temp)  # calculate microtransit and fixed transit VMT
#
#                 if microtransit_run == "micro_only":
#                     aaa = 0
#                     gen_cost_F = 0
#                     travel_time_F = 0
#                     travel_dist_F = 0
#                     agent_op_cost_F = 0
#                     if (time_period not in operating_periods):
#                         # calculate generalized cost
#                         gen_cost_T = 0
#                         # calculate travel time and distance
#                         travel_time_T = 0
#                         travel_dist_T = 0
#                         # calculate oout of pocket cost
#                         agent_op_cost_T = 0
#                     else:
#                         gen_cost_T = visited_temp[dest]
#                         travel_time_T = time_visited_temp[dest]
#                         travel_dist_T = dist_visited_temp[dest]
#                         agent_op_cost_T = fare_visited_temp[dest]
#                 else:
#                     # calculate generalized cost
#                     gen_cost_T = visited_temp[dest]
#                     gen_cost_F = visited_temp_F[
#                         dest]  # 1107 Siwei: add the generalized cost for without microtransit scenario
#                     # calculate travel time and distance
#                     travel_time_T = time_visited_temp[dest]
#                     travel_time_F = time_visited_temp_F[dest]
#                     travel_dist_T = dist_visited_temp[dest]
#                     travel_dist_F = dist_visited_temp_F[dest]
#
#                     # calculate out of pocket cost
#                     agent_op_cost_T = fare_visited_temp[dest]
#                     agent_op_cost_F = fare_visited_temp_F[dest]
#                 gen_cost_auto = auto_visited_temp[dest]
#
#                 # calculate travel time savings by allowing microtransit
#                 travel_time_auto = auto_time_visited_temp[dest]
#                 travel_time_delta[rq_id] = travel_time_F - travel_time_T
#
#                 travel_dist_auto = auto_dist_visited_temp[dest]
#                 agent_op_cost_auto = auto_fare_visited_temp[dest]
#                 gen_cost_delta[rq_id] = gen_cost_F - gen_cost_T
#                 if (gen_cost_F - gen_cost_T) < 0 and (gen_cost_F != 0):
#                     print("gen_cost_F", gen_cost_F, "gen_cost_T", gen_cost_T)
#                 #                 print("transit_time_path_all_",transit_time_path_all_,"\n","transit_time_path_all_F",transit_time_path_all_F,"\n")
#                 if microtransit_run == "micro_only" and (time_period not in operating_periods):
#                     prob_Auto, prob_T = 1, 0
#                 else:
#                     prob_Auto, prob_T = b_c.binary_logit_model(gen_cost_auto, gen_cost_T)
#
#                 if iteration > 0:
#                     diff_prob_T = abs(pre_iter_prob_T[rq_id] - prob_T)
#                     if diff_prob_T <= mode_change_threshold:  # if probability does not change a lot, then we don't change agents' modes.
#                         change_mode = False
#                     else:
#                         change_mode_ag_list.append(rq_id)
#                         # print("change_mode agent", rq_id, "change modes", "previous_prob_T",pre_iter_prob_T[rq_id], "current_prob_T", prob_T)
#
#                 pre_iter_prob_T[rq_id] = prob_T
#                 if microtransit_run == "micro_only":
#                     prob_Auto_no_micro, prob_T_no_micro = 1, 0
#                 else:
#                     prob_Auto_no_micro, prob_T_no_micro = b_c.binary_logit_model(gen_cost_auto, gen_cost_F)
#
#                 # calculate the mobility logsum change (logsum delta)
#                 mob_logsum_micro = b_c.mobility_logsum(gen_cost_auto, gen_cost_T)
#                 mob_logsum_fixed = b_c.mobility_logsum(gen_cost_auto, gen_cost_F)
#                 mob_logsum_delta[rq_id] = mob_logsum_micro - mob_logsum_fixed
#
#                 agent_choice_prob[rq_id] = [prob_Auto, prob_T]
#                 off_micro_agent_choice_prob[rq_id] = prob_Auto_no_micro, prob_T_no_micro
#                 iter_agent_choice_prob[iteration][rq_id] = [prob_Auto, prob_T]
#
#                 ran_num = random.random()
#                 # ran_num = np.random.gumbel()
#                 agent_ran_num[rq_id] = ran_num
#                 #             print("random number:",ran_num)
#                 # calculate the output metrics of turn-off microtransit
#                 if (num_virstop_scen == 1) and (num_fleet_size_scen == 1) and (num_operating_periods_scen == 1) and (
#                         iteration == 0):
#                     off_micro_ag_tot_dist[rq_id] = 0
#                     off_micro_ag_tot_tt[rq_id] = 0
#                     off_micro_agent_gen_cost[rq_id] = 0
#                     off_micro_ag_VMT_W[rq_id] = 0
#                     off_micro_agent_F_tot_wait_time[rq_id] = 0
#                     off_micro_agent_tot_walk_time[rq_id] = 0
#                     if ran_num < prob_T_no_micro:
#
#                         off_micro_ag_mode[rq_id] = "T"
#                         # off_micro_c_tt_travel_time[rq_id] = 0
#                         off_micro_T_trips += 1
#                         off_micro_ag_tot_tt[rq_id] = travel_time_F
#                         # off_micro_f_tt_travel_time[rq_id] = travel_time_F
#                         off_micro_ag_tot_dist[rq_id] = travel_dist_F / mile_meter
#                         # off_micro_ag_VMT_F[rq_id] = off_micro_ag_dist_F
#
#                         off_micro_agent_gen_cost[rq_id] = gen_cost_F
#                         trimmed_transit_time_path_F = transit_time_path_all_F[1:-1]
#                         pre_link_type = None
#                         # request_time=test_agent.rq_time
#                         sum_link_type_F = 0  # recorde the pure walking trips
#                         # 11/07 Siwei: record the time of reaching the previous link
#                         pre_time = 0
#
#                         # 1107 Siwei
#                         # agent_M_tot_wait_time[rq_id] = 0
#                         agent_F_tot_wait_time[rq_id] = 0
#
#                         # agent_travel_time[rq_id] = travel_time_T
#                         # agent_travel_dist[rq_id] = travel_dist_T
#                         # agent_op_cost[rq_id] = agent_op_cost_T  # agent_out-of-pocket cost
#                         off_micro_agent_op_cost[rq_id] = agent_op_cost_F
#                         for (node, time, link_type, route) in trimmed_transit_time_path_F:
#                             # calculate the number of fixed route transit trip legs
#                             if (pre_link_type != 1 and pre_link_type != 3) and (link_type == 1):
#                                 F_origin_node = node
#                                 request_time = rq_time + int(time)
#                             if (pre_link_type == 1) and (link_type != 1 and link_type != 3):
#                                 F_dest_node = pre_node
#                                 off_micro_F_trips += 1
#
#                             # 11/07 Siwei: calculate the fixed route transit waiting time
#                             if (pre_link_type != 2) and (link_type == 2):
#                                 F_wait_time = (time - pre_time)
#                                 off_micro_agent_F_tot_wait_time[rq_id] += F_wait_time
#                             # 11/07 Siwei: calculate the walking time
#                             if link_type == 0:
#                                 walk_time = (time - pre_time)
#                                 off_micro_agent_tot_walk_time[rq_id] += walk_time
#
#                             pre_time = time
#                             sum_link_type_F += link_type
#                             pre_node = node
#                             pre_link_type = link_type
#                         if sum_link_type_F == 0:
#                             off_micro_W_trips += 1
#
#                         # calculate VMT for fixed transit and walking when microtransit turned off
#                         trimmed_transit_dist_path_F = transit_dist_path_all_F[1:-1]
#                         pre_dist = 0
#                         pre_node = transit_dist_path_all_[0]
#                         for (node, dist, link_type, route) in trimmed_transit_dist_path_F:
#                             # calculate the number of fixed route transit trip legs
#                             if link_type == 1:
#                                 distance_F = dist - pre_dist
#                                 off_micro_VMT_F += (distance_F / mile_meter)
#                                 off_micro_transit_link_vmt[time_period][(pre_node, node)] += (distance_F / mile_meter)
#                                 off_micro_transit_link_pax[time_period][(pre_node, node)] += 1
#                             if link_type == 0:
#                                 distance_W = dist - pre_dist
#                                 off_micro_VMT_W += (distance_W / mile_meter)
#                                 off_micro_ag_VMT_W[rq_id] += (distance_W / mile_meter)
#                             pre_dist = dist
#                             pre_node = node
#
#
#                     else:  # agent choose the car mode
#                         off_micro_ag_mode[rq_id] = "C"
#                         off_micro_ag_tot_tt[rq_id] = travel_time_auto
#                         # off_micro_c_tt_travel_time[rq_id]= travel_time_auto
#                         # off_micro_f_tt_travel_time[rq_id]= 0
#                         off_micro_ag_tot_dist[rq_id] = travel_dist_auto / mile_meter
#                         off_micro_auto_trips += 1
#                         # agent_travel_time[rq_id] = travel_time_auto
#                         # agent_travel_dist[rq_id] = travel_dist_auto
#                         off_micro_agent_op_cost[rq_id] = agent_op_cost_auto  # agent_out-of-pocket
#                         off_micro_VMT_auto += (travel_dist_auto / mile_meter)
#                         off_micro_agent_gen_cost[rq_id] = gen_cost_auto
#
#                         # off_micro_auto_trips+=1
#                 # turn on microtransit
#                 if change_mode == True:
#
#                     if iteration == 0:  # when it is in iteration 0, all travelers get M and F travel time initialized
#                         agent_switch_mode[rq_id] = 0
#                         agent_M_tot_travel_time[rq_id] = 0
#                         agent_F_tot_travel_time[rq_id] = 0
#                         ag_VMT_F[rq_id] = 0
#                         ag_VMT_W[rq_id] = 0
#                         ag_VMT_M[rq_id] = 0
#                         ag_num_W_trips[rq_id] = 0
#                         ag_num_M_trips[rq_id] = 0
#                         ag_num_F_trips[rq_id] = 0
#
#                     if ran_num < prob_T:  # agent choose the transit mode
#                         ##when mode change=true, and transit mode is chosen, all travelers get M and F travel time initialized
#                         agent_switch_mode[rq_id] = 0
#                         agent_M_tot_travel_time[rq_id] = 0
#                         agent_F_tot_travel_time[rq_id] = 0
#                         ag_VMT_F[rq_id] = 0
#                         ag_VMT_W[rq_id] = 0
#                         ag_VMT_M[rq_id] = 0
#                         ag_num_W_trips[rq_id] = 0
#                         ag_num_M_trips[rq_id] = 0
#                         ag_num_F_trips[rq_id] = 0
#
#                         current_mode = "T"
#                         pre_iter_mode[rq_id] = current_mode
#
#                         agent_gen_cost[rq_id] = gen_cost_T
#                         if ran_num >= prob_T_no_micro:
#                             agent_switch_mode[
#                                 rq_id] = 1  # this means: if no microtransit, this agent will choose car, but with microtransit, this agent will choose transit mode
#                         trimmed_transit_time_path = transit_time_path_all_[1:-1]
#                         pre_link_type = None
#                         # request_time=test_agent.rq_time
#                         sum_link_type = 0  # recorde the pure walking trips
#                         # 11/07 Siwei: record the time of reaching the previous link
#                         pre_time = 0
#                         M_tot_wait_time = 0
#
#                         # 1107 Siwei
#                         agent_M_tot_wait_time[rq_id] = 0
#                         agent_F_tot_wait_time[rq_id] = 0
#
#                         agent_tot_walk_time[rq_id] = 0
#                         agent_travel_time[rq_id] = travel_time_T
#                         agent_travel_dist[rq_id] = travel_dist_T
#                         agent_op_cost[rq_id] = agent_op_cost_T  # agent_out-of-pocket cost
#
#                         for (node, time, link_type, route) in trimmed_transit_time_path:
#                             # calculate the number of microtransit trip legs
#                             if (pre_link_type != 4) and (link_type == 4):  ##1228 testing!
#                                 # if (pre_link_type == 5) and (link_type == 4):  ##1228 testing!
#                                 M_origin_node = node
#                                 request_time = rq_time + round(time, 0)
#                             if (pre_link_type == 4) and (link_type != 4):  ##1228 testing!
#                                 # if (pre_link_type == 4) and (link_type == 5):  ##1228 testing!
#                                 M_dest_node = pre_node
#                                 # MicroTransitNodes
#                                 rq_id_fleetpy = rq_id
#                                 while (
#                                         rq_id_fleetpy in M_rq_id_list):  # this condition is to deal with the situation where 1 person has more than 1 microtransit trips
#                                     rq_id_fleetpy += 1
#
#                                 try:
#                                     writer_M.writerow({'rq_time': request_time, 'start': MicroTransitNodes[M_origin_node],
#                                                        'end': MicroTransitNodes[M_dest_node], 'request_id': rq_id_fleetpy})
#                                 except:
#                                     raise Exception("M_origin_node", M_origin_node, "M_dest_node", M_dest_node,
#                                                     "pre_link_type", pre_link_type, "link_type", link_type, "node", node,
#                                                     "pre_node", pre_node, "trimmed_transit_time_path",
#                                                     trimmed_transit_time_path)
#                                 M_rq_id_list.append(rq_id_fleetpy)
#                                 # document the previous iteration microtransit information
#                                 # rq_time, start, end, request_id
#                                 pre_iter_M_info[rq_id] = (
#                                 request_time, MicroTransitNodes[M_origin_node], MicroTransitNodes[M_dest_node],
#                                 rq_id_fleetpy)
#
#                                 num_M_trips += 1
#                                 ag_num_M_trips[rq_id] += 1
#                             #                         print("depart",rq_time,"O",M_origin_node,"D",M_dest_node,"request_time",request_time,"walking_time",request_time-rq_time)
#                             # calculate the number of fixed route transit trip legs
#                             if (pre_link_type != 1 and pre_link_type != 3) and (link_type == 1):
#                                 F_origin_node = node
#                                 request_time = rq_time + int(time)
#                             if (pre_link_type == 1) and (link_type != 1 and link_type != 3):
#                                 F_dest_node = pre_node
#                                 num_F_trips += 1
#                                 ag_num_F_trips[rq_id] += 1
#                                 writer_F.writerow({'depart_time': request_time, 'start': F_origin_node, 'end': F_dest_node,
#                                                    'request_id': rq_id})
#                                 # document the previous iteration fixed route transit information
#                                 # rq_time, start, end, request_id
#                                 pre_iter_F_info[rq_id] = (request_time, F_origin_node, F_dest_node, rq_id)
#                             # 11/07 Siwei: calculate the microtransit waiting time
#                             if (pre_link_type != 5) and (link_type == 5):
#                                 M_wait_time = (time - pre_time)
#                                 agent_M_tot_wait_time[rq_id] += M_wait_time
#
#                             # 11/07 Siwei: calculate the fixed route transit waiting time
#                             if (pre_link_type != 2) and (link_type == 2):
#                                 F_wait_time = (time - pre_time)
#                                 agent_F_tot_wait_time[rq_id] += F_wait_time
#
#                             # 11/07 Siwei: calculate the walking time
#                             if link_type == 0:
#                                 walk_time = (time - pre_time)
#                                 agent_tot_walk_time[rq_id] += walk_time
#                             # 12/22 Siwei: calculate the microtransit travel time
#                             if link_type == 4:
#                                 M_travel_time = (time - pre_time)
#                                 agent_M_tot_travel_time[rq_id] += M_travel_time
#
#                             # 12/22 Siwei: calculate the fixed route transit travel time
#                             if link_type == 1 or link_type == 3:
#                                 F_travel_time = (time - pre_time)
#                                 agent_F_tot_travel_time[rq_id] += F_travel_time
#
#                             pre_time = time
#                             sum_link_type += link_type
#                             pre_node = node
#                             pre_link_type = link_type
#                         if sum_link_type == 0:
#                             num_W_trips += 1
#                             ag_num_W_trips[rq_id] += 1
#                         # calculate pure microtransit users:
#                         if ag_num_M_trips[rq_id] != 0 and ag_num_F_trips[rq_id] == 0:
#                             pure_M_user += 1
#                         # calculate pure fixed route transit users:
#                         if ag_num_M_trips[rq_id] == 0 and ag_num_F_trips[rq_id] != 0:
#                             pure_F_user += 1
#                         if ag_num_M_trips[rq_id] != 0 and ag_num_F_trips[rq_id] != 0:
#                             M_F_user += 1
#                         # calculate VMT for fixed transit and walking when microtransit turned on
#
#                         trimmed_transit_dist_path = transit_dist_path_all_[1:-1]
#                         pre_dist = 0
#                         pre_node = transit_dist_path_all_[0]
#                         for (node, dist, link_type, route) in trimmed_transit_dist_path:
#                             # calculate the number of fixed route transit trip legs
#                             if link_type == 1:
#                                 distance_F = dist - pre_dist
#                                 VMT_F += (distance_F / mile_meter)
#                                 ag_VMT_F[rq_id] += (distance_F / mile_meter)
#                                 transit_link_vmt[time_period][(pre_node, node)] += (distance_F / mile_meter)
#                                 transit_link_pax[time_period][(pre_node, node)] += 1
#
#                             if link_type == 0:
#                                 distance_W = dist - pre_dist
#                                 VMT_W += (distance_W / mile_meter)
#                                 ag_VMT_W[rq_id] += (distance_W / mile_meter)
#
#                             if link_type == 4:
#                                 distance_M = dist - pre_dist
#                                 VMT_M += (distance_M / mile_meter)
#                                 ag_VMT_M[rq_id] += (distance_M / mile_meter)
#                             pre_dist = dist
#                             pre_node = node
#
#                     else:  # agent choose the car mode
#                         current_mode = "C"
#                         pre_iter_mode[rq_id] = current_mode
#                         num_car_trips += 1
#                         agent_travel_time[rq_id] = travel_time_auto
#                         agent_travel_dist[rq_id] = travel_dist_auto
#                         agent_op_cost[rq_id] = agent_op_cost_auto  # agent_out-of-pocket cost
#                         VMT_auto += (travel_dist_auto / mile_meter)
#                         agent_gen_cost[rq_id] = gen_cost_auto
#                 else:
#                     ag_prev_iter_mode = pre_iter_mode[rq_id]
#                     if ag_prev_iter_mode == "T":
#
#                         VMT_F += ag_VMT_F[rq_id]
#                         VMT_W += ag_VMT_W[rq_id]
#                         VMT_M += ag_VMT_M[rq_id]
#
#                         num_W_trips += ag_num_W_trips[rq_id]
#                         num_F_trips += ag_num_F_trips[rq_id]
#                         num_M_trips += ag_num_M_trips[rq_id]
#
#                         if ag_num_M_trips[rq_id] != 0 and ag_num_F_trips[rq_id] == 0:
#                             pure_M_user += 1
#                         # calculate pure fixed route transit users:
#                         if ag_num_M_trips[rq_id] == 0 and ag_num_F_trips[rq_id] != 0:
#                             pure_F_user += 1
#                         if ag_num_M_trips[rq_id] != 0 and ag_num_F_trips[rq_id] != 0:
#                             M_F_user += 1
#
#                         if rq_id in pre_iter_M_info:
#                             # rq_time, start, end, request_id
#                             (pre_ier_rq_time, pre_iter_start, pre_iter_end, pre_iter_request_id) = pre_iter_M_info[rq_id]
#                             rq_id_fleetpy = pre_iter_request_id
#                             while (
#                                     rq_id_fleetpy in M_rq_id_list):  # this condition is to deal with the situation where 1 person has more than 1 microtransit trips
#                                 rq_id_fleetpy += 1
#                             writer_M.writerow({'rq_time': pre_ier_rq_time, 'start': pre_iter_start, 'end': pre_iter_end,
#                                                'request_id': rq_id_fleetpy})
#                             M_rq_id_list.append(rq_id_fleetpy)
#                         if rq_id in pre_iter_F_info:
#                             # (request_time,F_origin_node,F_dest_node,rq_id)
#                             (pre_ier_rq_time_F, pre_iter_start_F, pre_iter_end_F, pre_iter_request_id_F) = pre_iter_F_info[
#                                 rq_id]
#                             writer_F.writerow(
#                                 {'depart_time': pre_ier_rq_time_F, 'start': pre_iter_start_F, 'end': pre_iter_end_F,
#                                  'request_id': pre_iter_request_id_F})
#                             # writer_F.writerow({'rq_time': pre_ier_rq_time_F,'start': pre_iter_start_F,'end': pre_iter_end_F,'request_id': pre_iter_request_id_F})
#
#
#                     else:
#                         num_car_trips += 1
#                         VMT_auto += (travel_dist_auto / mile_meter)
#
#                 #         print("prob_Auto",prob_Auto,"prob_T",prob_T)
#
#             num_transit_users = tt_num_agents - num_car_trips
#
#             print("number of agents prob_T changed greater than threshold", mode_change_threshold, ":",
#                   len(change_mode_ag_list))
#
#             # print("assign pro iteration",iteration)
#             # iter_agent_choice_prob[iteration] = agent_choice_prob
#             # print("assign pro iteration", iteration,"iter_agent_choice_prob[iteration]",iter_agent_choice_prob[iteration])
#
#         csvfile_M.close()
#
#     csvfile_F.close()
#
#     return