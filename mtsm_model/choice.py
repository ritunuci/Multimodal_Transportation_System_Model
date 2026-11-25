"""A traveler's trip costs and mode choice (restructuring step 5, docs/entry_script_refactor_plan.md).

Car versus transit (walk + microtransit + FRT, or walk + FRT in the base case without microtransit), binary logit
(binary_choice.py). Moved from run_examples_new_parking.py without changes to the arithmetic; the random draw of the
choice stays in the iteration loop, so that the travelers draw in the same order.
"""
import math
from dataclasses import dataclass

from mtsm_model.helpers import binary_choice as b_c
from mtsm_model import config
from mtsm_model import mtsm_global_parameters as gp


@dataclass
class TripCosts:
    """Generalized cost, travel time (s), distance (m) and out-of-pocket cost ($) of the three options.
    _T: transit with microtransit, _F: transit without microtransit (base case)."""
    gen_cost_auto: float
    travel_time_auto: float
    travel_dist_auto: float
    agent_op_cost_auto: float  # gas + parking (until 2026-11-19 gas only)
    parking_cost_auto: float  # $, part of agent_op_cost_auto
    gen_cost_T: float
    gen_cost_F: float
    travel_time_T: float
    travel_time_F: float
    travel_dist_T: float
    travel_dist_F: float
    agent_op_cost_T: float
    agent_op_cost_F: float
    agent_F_fare: float  # FRT fare of the path with microtransit
    agent_M_fare: float  # microtransit fare of the path with microtransit


def time_period_of(t):
    """The time period of a time of day t (s): the study area's periods (config.period_of; Lemon Grove AM until 10 h,
    MD until 15 h, PM until 20 h, then EV, written in the code until 2026-11-24)."""
    return config.period_of(t)


def trip_costs(microtransit_run, in_operating_period, auto, parking_dur, bt_c_gas, frt, micro, dest, time_period):
    """The costs of a traveler's three options at the destination node dest. For "micro_only" there is no FRT, and
    outside the operating periods no transit at all (costs 0)."""
    if microtransit_run == "micro_only":
        gen_cost_F = 0
        travel_time_F = 0
        travel_dist_F = 0
        agent_op_cost_F = 0
        if not in_operating_period:
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
            gen_cost_T = micro.visited_temp[dest]
            travel_time_T = micro.time_visited_temp[dest]
            travel_dist_T = micro.dist_visited_temp[dest]
            agent_op_cost_T = micro.fare_visited_temp[dest]

            agent_F_fare = 0
            agent_M_fare = micro.M_fare_visited_temp[dest]
    else:
        # calculate generalized cost
        gen_cost_T = micro.visited_temp[dest]
        gen_cost_F = frt.visited_temp[dest]  # 1107 Siwei: add the generalized cost for without microtransit scenario
        # calculate travel time and distance
        travel_time_T = micro.time_visited_temp[dest]
        travel_time_F = frt.time_visited_temp[dest]
        travel_dist_T = micro.dist_visited_temp[dest]
        travel_dist_F = frt.dist_visited_temp[dest]

        # calculate out of pocket cost
        agent_op_cost_T = micro.fare_visited_temp[dest]
        agent_op_cost_F = frt.fare_visited_temp[dest]

        agent_F_fare = micro.F_fare_visited_temp[dest]
        agent_M_fare = micro.M_fare_visited_temp[dest]

    if auto is None:
        # no car (auto_available False, 2026-11-24): no car values; choice_probabilities gives transit with
        # probability 1, and the car values are never read
        return TripCosts(None, None, None, None, None, gen_cost_T, gen_cost_F, travel_time_T, travel_time_F,
                         travel_dist_T, travel_dist_F, agent_op_cost_T, agent_op_cost_F, agent_F_fare, agent_M_fare)

    # parking charge per started interval (30 min) of half the parking duration, at the rate of the period ($1 peak,
    # $0.5 off-peak). Until 2026-11-19 the factors PARKING_FACTOR_PEAK (1) / _OFFPEAK (0.5) stood where the rates are,
    # in the generalized cost only; the values are the same to the last digit.
    parking_dur_trip = parking_dur / 2
    parking_dur_30_min_count = math.ceil(parking_dur_trip / config.PARAMETERS[gp.G_PARKING_CHARGE_INTERVAL_MIN])
    if time_period in config.PEAK_PERIODS:  # Ritun added for parking fee (peak periods: ["AM","PM"] until 2026-11-24)
        gen_cost_auto = auto.visited_temp[dest] + bt_c_gas * parking_dur_30_min_count * config.PARKING_RATE_PEAK
        parking_cost_auto = parking_dur_30_min_count * config.PARKING_RATE_PEAK
    else:
        gen_cost_auto = auto.visited_temp[dest] + bt_c_gas * parking_dur_30_min_count * config.PARKING_RATE_OFFPEAK
        parking_cost_auto = parking_dur_30_min_count * config.PARKING_RATE_OFFPEAK

    # the car's out-of-pocket cost: gas (from the path search) + parking (until 2026-11-19 gas only)
    return TripCosts(gen_cost_auto, auto.time_visited_temp[dest], auto.dist_visited_temp[dest],
                     auto.fare_visited_temp[dest] + parking_cost_auto, parking_cost_auto, gen_cost_T, gen_cost_F,
                     travel_time_T, travel_time_F, travel_dist_T, travel_dist_F, agent_op_cost_T, agent_op_cost_F,
                     agent_F_fare, agent_M_fare)


def choice_probabilities(microtransit_run, in_operating_period, costs):
    """(prob_Auto, prob_T): car versus transit with microtransit; (prob_Auto_no_micro, prob_T_no_micro): car versus
    transit in the base case. Without transit ("micro_only" outside the operating periods, and the base case of
    "micro_only"): car with probability 1. Without a car (costs.gen_cost_auto None; auto_available False, since
    2026-11-24): transit with probability 1, with and without microtransit ("micro_only" then stops the run at
    startup, scenarios.load_study_area)."""
    if costs.gen_cost_auto is None:
        return 0, 1, 0, 1
    if microtransit_run == "micro_only" and not in_operating_period:
        prob_Auto, prob_T = 1,0
    else:
        prob_Auto, prob_T = b_c.binary_logit_model(costs.gen_cost_auto, costs.gen_cost_T)
    if microtransit_run == "micro_only":
        prob_Auto_no_micro, prob_T_no_micro = 1,0
    else:
        prob_Auto_no_micro, prob_T_no_micro = b_c.binary_logit_model(costs.gen_cost_auto, costs.gen_cost_F)
    return prob_Auto, prob_T, prob_Auto_no_micro, prob_T_no_micro


def keeps_previous_mode(pre_iter_prob_T, prob_T):
    """True if the transit probability changed by at most MODE_CHANGE_THRESHOLD since the previous iteration: the
    traveler then keeps the previous iteration's mode."""
    diff_prob_T = abs(pre_iter_prob_T - prob_T)
    return diff_prob_T <= config.MODE_CHANGE_THRESHOLD


def mobility_logsum_delta(costs, beta_fare):
    """The increase in the mobility logsum with microtransit, divided by the traveler's fare coefficient. Without a car
    (costs.gen_cost_auto None, 2026-11-24) the logsum has the transit term only: log(exp(-gen_cost)) = -gen_cost."""
    if costs.gen_cost_auto is None:
        return (costs.gen_cost_F - costs.gen_cost_T) / beta_fare
    # calculate the mobility logsum change (logsum delta)
    mob_logsum_micro = b_c.mobility_logsum(costs.gen_cost_auto, costs.gen_cost_T)
    mob_logsum_fixed = b_c.mobility_logsum(costs.gen_cost_auto, costs.gen_cost_F)
    return (mob_logsum_micro - mob_logsum_fixed)/beta_fare
