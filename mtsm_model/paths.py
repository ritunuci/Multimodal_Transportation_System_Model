"""A traveler's networks and least generalized cost paths (restructuring step 5, docs/entry_script_refactor_plan.md).

Three paths per traveler and iteration: by car (auto network), by walk + fixed-route transit (FRT-only network, the
"without microtransit" base case) and by walk + microtransit + FRT (the super-network with microtransit). Moved from
run_examples_new_parking.py; the calls of network_algorithms are unchanged.

The car and FRT paths are computed in the first fare scenario (test_scenario == cfg.TRPartA_test_scenario_list[0]) and
reused from PathCache in the other fare scenarios of the same repositioning setting.
"""
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

import network_algorithms as n_a
from mtsm_model import config


@dataclass
class AutoPath:
    visited_temp: Any  # generalized cost to each node
    time_visited_temp: Any
    dist_visited_temp: Any
    fare_visited_temp: Any
    path: Any
    time_path: Any
    time_path_all_: Any  # (node, time, link_type, route) from origin to destination


@dataclass
class FrtPath:
    visited_temp: Any
    time_visited_temp: Any
    dist_visited_temp: Any
    fare_visited_temp: Any
    path: Any
    time_path: Any
    time_path_all_: Any  # (node, time, link_type, route) from origin to destination
    dist_path_all_: Any  # (node, dist, link_type, route) from origin to destination


@dataclass
class MicroPath:
    visited_temp: Any
    time_visited_temp: Any
    dist_visited_temp: Any
    fare_visited_temp: Any
    F_fare_visited_temp: Any
    M_fare_visited_temp: Any
    time_path_all_: Any
    dist_path_all_: Any


@dataclass
class PathCache:
    """The car and FRT paths of each traveler (keyed by rq_id), from the first fare scenario."""
    auto: OrderedDict = field(default_factory=OrderedDict)
    frt: OrderedDict = field(default_factory=OrderedDict)


def networks_for_traveler(microtransit_run, iteration, time_period, operating_periods, initial_super_network,
                          final_super_network, auto_network, headway, virstop, M_operating_hrs, fleet_size):
    """The FRT-only network (T_F_network) and the network with microtransit (T_micro_network) for a traveler who
    departs in time_period. Iteration 0 uses the initial super-network, later iterations the one updated with
    FleetPy's results. Outside the microtransit operating periods: the FRT-only network ("micro") or the auto
    network ("micro_only")."""
    # 1108 Siwei: read the initial super-network according to "microtransit", "fixed route trasnit headway","virstop", and "time_period"
    T_F_network = \
        initial_super_network["non_micro"][
            config.BASE_FRT_HEADWAY]
    if iteration == 0:
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
    return T_F_network, T_micro_network


def auto_path(path_cache, study_area, auto_network, agent, cfg, iteration):
    """Compute the car path (and cache it). Returns parking_dur, bt_c_gas and the AutoPath."""
    parking_dur, bt_c_gas, auto_visited_temp, auto_time_visited_temp, auto_dist_visited_temp, auto_fare_visited_temp,F_fare_visited_temp,M_fare_visited_temp, auto_path, auto_time_path,auto_dist_path = n_a.generalized_cost_dijsktra_OD_heap(study_area,auto_network, agent,cfg.transit_fare,cfg.microtransit_start_fare,cfg.microtransit_dist_based_rate,cfg.PkFareFactor,cfg.OffPkFareFactor,cfg.Fixed2MicroFactor,cfg.Micro2FixedFactor,test_scenario=0, mode="C", verbose=False, iteration=iteration)
    auto_time_path_all_ = n_a.getTrajectory_O_to_D(agent.rq_O, agent.rq_D, auto_time_path, auto_visited_temp)
    auto = AutoPath(auto_visited_temp, auto_time_visited_temp, auto_dist_visited_temp, auto_fare_visited_temp,
                    auto_path, auto_time_path, auto_time_path_all_)
    path_cache.auto[agent.rq_id] = auto
    return parking_dur, bt_c_gas, auto


def frt_path(path_cache, study_area, T_F_network, agent, cfg, test_scenario, total_rejection_penalty, iteration):
    """Compute the walk + FRT path of the base case (and cache it), with the base FRT fare."""
    visited_temp_F, time_visited_temp_F, dist_visited_temp_F, fare_visited_temp_F,F_fare_visited_temp_F,M_fare_visited_temp_F, path_F, time_path_F,dist_path_F = n_a.generalized_cost_dijsktra_OD_heap(study_area,T_F_network, agent,config.BASE_FRT_FARE, cfg.microtransit_start_fare,cfg.microtransit_dist_based_rate,cfg.PkFareFactor,cfg.OffPkFareFactor,cfg.Fixed2MicroFactor,cfg.Micro2FixedFactor,test_scenario,mode="T",verbose=False, total_rejection_penalty=total_rejection_penalty, iteration=iteration)
    transit_time_path_all_F = n_a.getTrajectory_O_to_D(agent.rq_O, agent.rq_D, time_path_F, visited_temp_F)
    transit_dist_path_all_F = n_a.getTrajectory_O_to_D(agent.rq_O, agent.rq_D, dist_path_F, dist_visited_temp_F)  # calculate fixed transit VMT
    frt = FrtPath(visited_temp_F, time_visited_temp_F, dist_visited_temp_F, fare_visited_temp_F, path_F, time_path_F,
                  transit_time_path_all_F, transit_dist_path_all_F)
    path_cache.frt[agent.rq_id] = frt
    return frt


def micro_path(study_area, T_micro_network, agent, cfg, test_scenario, total_rejection_penalty, iteration):
    """Compute the walk + microtransit + FRT path, with the scenario's fares."""
    visited_temp, time_visited_temp,dist_visited_temp,fare_visited_temp,F_fare_visited_temp,M_fare_visited_temp, path, time_path,dist_path = n_a.generalized_cost_dijsktra_OD_heap(study_area,T_micro_network,agent,cfg.transit_fare,cfg.microtransit_start_fare,cfg.microtransit_dist_based_rate,cfg.PkFareFactor,cfg.OffPkFareFactor,cfg.Fixed2MicroFactor,cfg.Micro2FixedFactor,test_scenario,mode="T",verbose=False, total_rejection_penalty=total_rejection_penalty, iteration=iteration)
    transit_time_path_all_ = n_a.getTrajectory_O_to_D(agent.rq_O, agent.rq_D, time_path, visited_temp)
    transit_dist_path_all_ = n_a.getTrajectory_O_to_D(agent.rq_O, agent.rq_D, dist_path, dist_visited_temp)  # calculate microtransit and fixed transit VMT
    return MicroPath(visited_temp, time_visited_temp, dist_visited_temp, fare_visited_temp, F_fare_visited_temp,
                     M_fare_visited_temp, transit_time_path_all_, transit_dist_path_all_)
