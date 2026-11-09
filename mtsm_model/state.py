"""The model's state during a scenario: what was ~70 loose variables in run_examples_new_parking.py
(restructuring step 3, docs/entry_script_refactor_plan.md).

- TravelerState: per-traveler values (dicts keyed by the request id rq_id), kept across the iterations of a scenario.
- BaseCase: the fixed-route-only base case ("without microtransit", the "off_micro" results), computed in the first
  iteration of a scenario.
- IterationTotals: counts and VMT totals of one iteration, reset at the start of each iteration.

The field names are the old variable names, so that they can still be found in the old code and the git history. The
values are the same objects as before (OrderedDict, or int 0 that the code then adds to), created at the same place.
Distances in miles, times in seconds, costs in $, unless stated otherwise.
"""
from collections import OrderedDict
from dataclasses import dataclass, field


def _od():
    return field(default_factory=OrderedDict)


@dataclass
class BaseCase:
    """The fixed-route-only base case: each traveler chooses between car and walk + FRT."""
    off_micro_T_trips: int = 0  # travelers who choose transit (incl. walk-only)
    off_micro_W_trips: int = 0  # transit travelers whose path is walk only
    off_micro_F_trips: int = 0  # FRT trip legs
    off_micro_auto_trips: int = 0  # travelers who choose car
    off_micro_agent_tot_walk_time: OrderedDict = _od()
    off_micro_agent_F_tot_wait_time: OrderedDict = _od()
    off_micro_agent_op_cost: OrderedDict = _od()  # out-of-pocket cost
    off_micro_VMT_F: float = 0  # FRT passenger miles
    off_micro_VMT_W: float = 0  # walk miles
    off_micro_VMT_auto: float = 0
    off_micro_agent_gen_cost: OrderedDict = _od()  # generalized cost of the chosen mode
    off_micro_ag_tot_tt: OrderedDict = _od()  # travel time of the chosen mode
    off_micro_ag_mode: OrderedDict = _od()  # "T" (transit) or "C" (car)
    off_micro_ag_tot_dist: OrderedDict = _od()  # distance of the chosen mode (mi)
    off_micro_agent_ran_num: OrderedDict = _od()  # the random draw of the mode choice
    off_micro_agent_choice_prob: OrderedDict = _od()  # [prob_Auto, prob_T]
    off_micro_c_tt_travel_time: OrderedDict = _od()  # not filled
    off_micro_f_tt_travel_time: OrderedDict = _od()  # not filled
    off_micro_ag_VMT_W: OrderedDict = _od()  # walk miles


@dataclass
class TravelerState:
    """Per-traveler values with microtransit, carried from one iteration to the next."""
    # the previous iteration, used when a traveler keeps the mode (change_mode=False)
    pre_iter_prob_T: OrderedDict = _od()  # transit probability
    pre_iter_mode: OrderedDict = _od()  # "T" or "C"
    pre_iter_M_info: OrderedDict = _od()  # the FleetPy request (rq_time, start, end, request_id)
    pre_iter_F_info: OrderedDict = _od()  # the FRT trip (depart_time, start, end, request_id)

    ag_VMT_F: OrderedDict = _od()  # FRT miles
    ag_VMT_M: OrderedDict = _od()  # microtransit miles
    ag_VMT_W: OrderedDict = _od()  # walk miles

    ag_num_W_trips: OrderedDict = _od()
    ag_num_M_trips: OrderedDict = _od()
    ag_num_F_trips: OrderedDict = _od()

    # agent level attributes
    travel_time_delta: OrderedDict = _od()  # travel time without minus with microtransit
    gen_cost_delta: OrderedDict = _od()  # generalized cost without minus with microtransit
    mob_logsum_delta: OrderedDict = _od()  # mobility logsum increase with microtransit, in $
    agent_beta_fare: OrderedDict = _od()

    agent_O: OrderedDict = _od()
    agent_D: OrderedDict = _od()
    agent_rq_time: OrderedDict = _od()
    agent_choice_prob: OrderedDict = _od()  # [prob_Auto, prob_T]
    agent_switch_mode: OrderedDict = _od()  # 1: transit with microtransit, car without it
    agent_ran_num: OrderedDict = _od()  # the random draw of the mode choice
    agent_M_tot_wait_time: OrderedDict = _od()
    agent_F_tot_wait_time: OrderedDict = _od()
    agent_M_tot_travel_time: OrderedDict = _od()
    agent_F_tot_travel_time: OrderedDict = _od()

    agent_M_tot_travel_dist: OrderedDict = _od()
    agent_F_tot_travel_dist: OrderedDict = _od()

    agent_tot_walk_time: OrderedDict = _od()
    agent_travel_time: OrderedDict = _od()
    agent_travel_dist: OrderedDict = _od()  # in meters
    agent_op_cost: OrderedDict = _od()  # agent_out-of-pocket cost
    agent_op_cost_Fix: OrderedDict = _od()  # FRT fare
    agent_op_cost_Micro: OrderedDict = _od()  # microtransit fare

    agent_gen_cost: OrderedDict = _od()  # generalized cost of the chosen mode

    agent_income: OrderedDict = _od()
    agent_transit_15min_acc: OrderedDict = _od()


@dataclass
class IterationTotals:
    """Totals of one iteration, with microtransit."""
    num_car_trips: int = 0
    num_transit_users: int = 0
    num_M_trips: int = 0  # microtransit trip legs
    num_F_trips: int = 0  # FRT trip legs
    num_W_trips: int = 0  # walk-only transit trips

    pure_M_user: int = 0  # transit travelers with microtransit legs only
    pure_F_user: int = 0  # transit travelers with FRT legs only
    M_F_user: int = 0  # transit travelers with both

    # VMT when micro transit is turned on (M and F: passenger miles on the legs)
    VMT_M: float = 0
    VMT_F: float = 0
    VMT_auto: float = 0
    VMT_W: float = 0
