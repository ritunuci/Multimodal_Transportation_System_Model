"""Check that mtsm_data/input_parameter/mtsm_constant_configurations.csv holds today's values, with today's types.

    python tools/check_constant_config.py      exit code 1 on any difference

Compares the dictionary from config.read_constant_config() with the values before the move (literals below, copied
from commit 027630a: input_parameter.csv, the constants of config.py, the values written into the code, with where
they were). A check for the move of the parameters into one file
(docs/constant_config_plan.md); it is removed in step 5, once the code reads everything from the new file.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mtsm_model import config
from mtsm_model import mtsm_global_parameters as gp


def expected_values():
    return {
        # input_parameter.csv at commit 027630a (one row; deleted in step 4)
        gp.G_TEST_AREA: "lemon_grove",  # test_area
        gp.G_TRANSIT_FARE: 3.615388,  # transit_fare ($)
        gp.G_MICROTRANSIT_DIST_BASED_RATE: 5.0,  # microtransit_dist_based_rate ($/mile)
        gp.G_MICROTRANSIT_START_FARE: 2.3811314,  # microtransit_start_fare ($)
        gp.G_FLEET_SIZE: 2,  # Fleet_size
        gp.G_PK_FARE_FACTOR: 2.3703918,  # PkFareFactor
        gp.G_OFF_PK_FARE_FACTOR: 1.0,  # OffPkFareFactor
        gp.G_FIXED2MICRO_FACTOR: 1.0,  # Fixed2MicroFactor
        gp.G_MICRO2FIXED_FACTOR: 0.0,  # Micro2FixedFactor
        gp.G_FRT_HEADWAY: 10,  # FRT_headway
        gp.G_INITIAL_REJECTION_RATE: 20.0,  # initial_rejection_rate
        gp.G_MICRO_REJECTION_PENALTY: 3.0,  # micro_rejection_penalty ($)
        gp.G_RANDOM_SEED: 0,  # random_seed
        # the constants of config.py at commit 027630a
        gp.G_FARE_SCENARIO: 10,  # FARE_SCENARIO
        gp.G_BASE_FRT_HEADWAY: 20,  # BASE_FRT_HEADWAY
        gp.G_BASE_FRT_FARE: 2.5,  # BASE_FRT_FARE
        gp.G_INDIV_CONVERG_TEST: True,  # INDIV_CONVERG_TEST
        gp.G_MAXIMUM_ITERATION: 15,  # MAXIMUM_ITERATION
        gp.G_CONVERGENCE_GAP: 0.01,  # CONVERGENCE_GAP
        gp.G_MODE_CHANGE_THRESHOLD: 0.05,  # MODE_CHANGE_THRESHOLD
        gp.G_AGGREGATION: "whole_region",  # AGGREGATION
        gp.G_AM_END_H: 10,  # AM_END = 10 * 3600
        gp.G_MD_END_H: 15,  # MD_END = 15 * 3600
        gp.G_PM_END_H: 20,  # PM_END = 20 * 3600
        gp.G_PARKING_FACTOR_PEAK: 1,  # PARKING_FACTOR_PEAK
        gp.G_PARKING_FACTOR_OFFPEAK: 0.5,  # PARKING_FACTOR_OFFPEAK
        gp.G_NUM_WALK_NODES: 1099,  # NUM_WALK_NODES
        gp.G_MICROTRANSIT_NODE_OFFSET: 1171,  # MICROTRANSIT_NODE_OFFSET
        gp.G_F_GAS_PER_MILE: 0.350,  # F_GAS_PER_MILE
        gp.G_M_GAS_PER_MILE: 0.550,  # M_GAS_PER_MILE
        gp.G_METERS_PER_MILE: 1609.34,  # MILE_METER
        gp.G_OPERATING_PERIODS_SCENARIOS: [["AM", "MD", "PM"]],  # OPERATING_PERIODS_SCENARIOS = [OPERATING_PERIOD_2]
        gp.G_VIRTUAL_STOP_SCENARIOS: [75],  # VIRTUAL_STOP_SCENARIOS
        gp.G_MICROTRANSIT_RUNNING_SCENARIOS: ["micro"],  # MICROTRANSIT_RUNNING_SCENARIOS
        gp.G_REPOSITIONING_LIST: [True],  # REPOSITIONING_LIST
        # values written into the code (line numbers at commit 027630a)
        gp.G_REJECTION_RATE_WINDOW: 3,  # mtsm_model/model.py:91-95
        gp.G_DAY_START_H: 5,  # config.py comment: AM = 5-10 h
        gp.G_DAY_END_H: 24,  # config.py comment: EV = 20-24 h
        gp.G_FRT_OPERATING_HOURS: 19,  # mtsm_model/scenarios.py:174
        gp.G_PARKING_CHARGE_INTERVAL_MIN: 30,  # mtsm_model/choice.py:93
        gp.G_MICRO_ONLY_MAX_WALK_NODE: 731,  # helpers/update_network_files.py:378
        gp.G_CAR_GAS_COST_PER_METER: 0.00025,  # helpers/network_algorithms.py:524
        gp.G_FRT_OPERATING_COST_PER_VEH_HOUR: 170,  # mtsm_model/results.py:58, 62
        gp.G_MICRO_OPERATING_COST_PER_VEH_HOUR: 130,  # mtsm_model/results.py:73
        gp.G_FRT_SPEED_MPH: 30,  # helpers/output_performance_metrics.py:771
        gp.G_FRT_DWELL_TIME_MIN: 3,  # helpers/output_performance_metrics.py:768
        gp.G_FRT_DEAD_END_TIME_MIN: 20,  # helpers/output_performance_metrics.py:769
        gp.G_DEFAULT_MICRO_WAIT_TIME: 180,  # helpers/update_network_files.py:217, 260
        gp.G_METERS_PER_MILE_FRT_LINES: 1609,  # helpers/output_performance_metrics.py:758
        gp.G_KM_PER_MILE_FLEETPY: 1.609,  # helpers/output_performance_metrics.py:704, 707
        gp.G_ACCESSIBILITY_THRESHOLDS_MIN: [5, 10, 15],  # helpers/output_performance_metrics.py:372, 553
        gp.G_FALLBACK_EMPLOYMENT_MICRO: [431, 5074, 6341],  # helpers/output_performance_metrics.py:474-484
        gp.G_FALLBACK_EMPLOYMENT_FRT: [156, 486, 1020],  # helpers/output_performance_metrics.py:650-660
    }


def same(a, b):
    """equal value and equal type, also for each element of a list"""
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def derived_problems(p, cfg):
    """values the code computed from literals or converted, now computed from the parameters"""
    problems = []
    if cfg.microtransit_dist_based_rate != 5.0 / 1609.34:  # read_run_config() at commit 027630a: $/mile -> $/m
        problems.append("microtransit_dist_based_rate in $/m")
    hours = {"AM": p[gp.G_AM_END_H] - p[gp.G_DAY_START_H], "MD": p[gp.G_MD_END_H] - p[gp.G_AM_END_H],
             "PM": p[gp.G_PM_END_H] - p[gp.G_MD_END_H], "EV": p[gp.G_DAY_END_H] - p[gp.G_PM_END_H]}
    # mtsm_model/scenarios.py:168-173, helpers/testing_scenario_creation.py: microtransit operating hours
    for periods, hrs in ((["AM", "PM"], 10), (["AM", "MD", "PM"], 15), (["AM", "MD", "PM", "EV"], 19)):
        if sum(hours[period] for period in periods) != hrs:
            problems.append(f"operating hours of {periods}: {sum(hours[period] for period in periods)} != {hrs}")
    # helpers/network_algorithms.py:493, 514: walk nodes <= 1098, FRT stops 1099-1170, microtransit nodes 1171-2269
    walk, offset = p[gp.G_NUM_WALK_NODES], p[gp.G_MICROTRANSIT_NODE_OFFSET]
    if (walk - 1, walk, offset - 1, offset, offset + walk - 1) != (1098, 1099, 1170, 1171, 2269):
        problems.append("node ranges")
    return problems


def main():
    params = config.read_constant_config()
    cfg = config.read_run_config()
    expected = expected_values()
    problems = []
    if set(expected) != set(gp.PARAMETER_TYPES):
        problems.append(f"keys not checked: {sorted(set(gp.PARAMETER_TYPES) - set(expected))}")
    for key, value in expected.items():
        if not same(params[key], value):
            problems.append(f"{key}: file {params[key]!r} ({type(params[key]).__name__}), "
                            f"today {value!r} ({type(value).__name__})")
    problems += derived_problems(params, cfg)
    for problem in problems:
        print("DIFFERENT:", problem)
    print("SAME: %d parameters" % len(params) if not problems else "%d problems" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
