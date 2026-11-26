"""Names (keys) and types of the MTSM parameters.

Since 2026-11-24 (docs/study_area_plan.md, Phase 1 step 3) they are in two files: the model file
mtsm_data/input_parameter/mtsm_constant_configurations.csv (the keys not in AREA_PARAMETERS; the optimizer writes
copies of it) and the study area's file mtsm_data/<area>/area_parameters.csv (AREA_PARAMETERS); the model file's
study_area names the area. Until then the model file had them all.

Both files have three columns: parameter_name (one of the keys below), parameter_value, and description (for people;
no code reads it). config.read_constant_config() reads both into one dictionary {key: value}, converting each value to
the type given in PARAMETER_TYPES. Lists are written with ";" (75;100), lists of lists with "|" between the lists
(AM;PM|AM;MD;PM). Each type matches today's value exactly (for example FRT_HEADWAY int, PK_FARE_FACTOR float): values
appear in output file names (hw_10) and output CSVs, where 10 and 10.0 differ.

The keys are named like FleetPy's (fleetpy/src/misc/globals.py): G_<NAME> = "<name>". Where a value was a constant in
config.py or a column of input_parameter.csv, the old name is given in the comment.
"""

# ---- value types ----
INT = "int"
FLOAT = "float"
BOOL = "bool"
STR = "str"
INT_LIST = "int_list"
BOOL_LIST = "bool_list"
STR_LIST = "str_list"
STR_LIST_LIST = "str_list_list"
# a number written as an int when it is whole (15 -> 15, 15.5 -> 15.5): hours appear in file names (op_hr_15)
NUMBER = "number"
NUMBER_LIST = "number_list"

# ---- run parameters (until 2026-11-10 the columns of input_parameter.csv; the optimizer sets seven of them) ----
G_STUDY_AREA = "study_area"  # test_area (key "test_area" and constant G_TEST_AREA until 2026-11-24): the folder mtsm_data/<area>/
G_TRANSIT_FARE = "transit_fare"  # transit_fare ($)
G_MICROTRANSIT_DIST_BASED_RATE = "microtransit_dist_based_rate"  # microtransit_dist_based_rate ($/mile)
G_MICROTRANSIT_START_FARE = "microtransit_start_fare"  # microtransit_start_fare ($)
G_FLEET_SIZE = "fleet_size"  # Fleet_size
G_PK_FARE_FACTOR = "pk_fare_factor"  # PkFareFactor
G_OFF_PK_FARE_FACTOR = "off_pk_fare_factor"  # OffPkFareFactor
G_FIXED2MICRO_FACTOR = "fixed2micro_factor"  # Fixed2MicroFactor
G_MICRO2FIXED_FACTOR = "micro2fixed_factor"  # Micro2FixedFactor
G_FRT_HEADWAY = "frt_headway"  # FRT_headway
G_INITIAL_REJECTION_RATE = "initial_rejection_rate"  # initial_rejection_rate
G_MICRO_REJECTION_PENALTY = "micro_rejection_penalty"  # micro_rejection_penalty ($)
G_RANDOM_SEED = "random_seed"  # random_seed

# ---- fare structure and the base case without microtransit ----
G_FARE_SCENARIO = "fare_scenario"  # FARE_SCENARIO
G_BASE_FRT_HEADWAY = "base_frt_headway"  # BASE_FRT_HEADWAY
G_BASE_FRT_FARE = "base_frt_fare"  # BASE_FRT_FARE

# ---- iterations and convergence ----
G_MAXIMUM_ITERATION = "maximum_iteration"  # MAXIMUM_ITERATION
G_CONVERGENCE_GAP = "convergence_gap"  # CONVERGENCE_GAP
G_MODE_CHANGE_THRESHOLD = "mode_change_threshold"  # MODE_CHANGE_THRESHOLD
G_AGGREGATION = "aggregation"  # AGGREGATION
G_REJECTION_RATE_WINDOW = "rejection_rate_window"  # model.py: average of the last 3 iterations from iteration 3

# ---- time periods of the study area (area file, since 2026-11-24; docs/period_networks_and_car_availability_plan.md,
# step 3): the names in order, the start of the first (h) and the end of each (h), and the peak periods (peak fare
# factor and peak parking rate). Lemon Grove: AM;MD;PM;EV, 5, 10;15;20;24, AM;PM. Until 2026-11-24 the model file had
# day_start_h (5), am_end_h (10), md_end_h (15), pm_end_h (20), day_end_h (24), and the four names and the peak
# periods were written in the code ----
G_TIME_PERIODS = "time_periods"
G_PERIOD_START_H = "period_start_h"
G_PERIOD_END_H = "period_end_h"
G_PEAK_PERIODS = "peak_periods"
G_FRT_OPERATING_HOURS = "frt_operating_hours"  # F_operating_hrs = 19

# ---- parking ----
G_PARKING_CHARGE_INTERVAL_MIN = "parking_charge_interval_min"  # choice.py: per started 30 min
# $ per started interval; new 2026-11-19, replacing parking_factor_peak (1) and parking_factor_offpeak (0.5), which
# were the charge per interval in $ (rate 1 implied)
G_PARKING_RATE_PEAK = "parking_rate_peak"  # PARKING_RATE_PEAK
G_PARKING_RATE_OFFPEAK = "parking_rate_offpeak"  # PARKING_RATE_OFFPEAK

# ---- path search ----
G_ENABLE_NUM_TRANSFER_PENALTY = "enable_num_transfer_penalty"  # new 2026-11-11; to be turned on with a new reference (I-25)

# ---- demand sample and upscaling (new 2026-11-25, docs/open_issues.md I-32): with demand_upscaling True the run reads
# the sample file sample_demand_file (a path relative to mtsm_data/<area>/) holding a share demand_sample_share of all
# travelers; FleetPy gets synthetic requests for the others, and the evaluation file reports all travelers. With False
# the run reads demand/demand.csv as all travelers, and the other two are not used ----
G_DEMAND_UPSCALING = "demand_upscaling"
G_DEMAND_SAMPLE_SHARE = "demand_sample_share"
G_SAMPLE_DEMAND_FILE = "sample_demand_file"

# ---- node numbering: num_walk_nodes and microtransit_node_offset are derived from the network files since 2026-11-24
# (config.derive_node_numbering); micro_only_max_walk_node (731) is the area's last walk node since then (I-13) ----

# ---- costs ----
G_CAR_GAS_COST_PER_METER = "car_gas_cost_per_meter"  # network_algorithms.py: 0.00025 * link_length
G_F_GAS_PER_MILE = "f_gas_per_mile"  # F_GAS_PER_MILE
G_M_GAS_PER_MILE = "m_gas_per_mile"  # M_GAS_PER_MILE
G_FRT_OPERATING_COST_PER_VEH_HOUR = "frt_operating_cost_per_veh_hour"  # results.py: 170
G_MICRO_OPERATING_COST_PER_VEH_HOUR = "micro_operating_cost_per_veh_hour"  # results.py: 130

# ---- FRT line duration (output_performance_metrics.get_transit_line_duration) ----
G_FRT_SPEED_MPH = "frt_speed_mph"
G_FRT_DWELL_TIME_MIN = "frt_dwell_time_min"
G_FRT_DEAD_END_TIME_MIN = "frt_dead_end_time_min"

# ---- microtransit waiting time ----
G_DEFAULT_MICRO_WAIT_TIME = "default_micro_wait_time"  # update_network_files.py: 180 s

# ---- units (one meters-per-mile value since 2026-11-23: meters_per_mile_frt_lines 1609 and km_per_mile_fleetpy 1.609
# were merged into it; I-21) ----
G_METERS_PER_MILE = "meters_per_mile"  # MILE_METER

# ---- accessibility: accessibility_thresholds_min, fallback_employment_micro and fallback_employment_frt were
# removed on 2026-11-24 with the accessibility calculation ----

# ---- scenarios (each list has one element in the run) ----
G_OPERATING_PERIODS_SCENARIOS = "operating_periods_scenarios"  # OPERATING_PERIODS_SCENARIOS
G_VIRTUAL_STOP_SCENARIOS = "virtual_stop_scenarios"  # VIRTUAL_STOP_SCENARIOS
G_MICROTRANSIT_RUNNING_SCENARIOS = "microtransit_running_scenarios"  # MICROTRANSIT_RUNNING_SCENARIOS
G_REPOSITIONING_LIST = "repositioning_list"  # REPOSITIONING_LIST

# every key and its type, in the order of the file
PARAMETER_TYPES = {
    G_STUDY_AREA: STR,
    G_TRANSIT_FARE: FLOAT,
    G_MICROTRANSIT_DIST_BASED_RATE: FLOAT,
    G_MICROTRANSIT_START_FARE: FLOAT,
    G_FLEET_SIZE: INT,
    G_PK_FARE_FACTOR: FLOAT,
    G_OFF_PK_FARE_FACTOR: FLOAT,
    G_FIXED2MICRO_FACTOR: FLOAT,
    G_MICRO2FIXED_FACTOR: FLOAT,
    G_FRT_HEADWAY: INT,
    G_INITIAL_REJECTION_RATE: FLOAT,
    G_MICRO_REJECTION_PENALTY: FLOAT,
    G_RANDOM_SEED: INT,
    G_FARE_SCENARIO: INT,
    G_BASE_FRT_HEADWAY: INT,
    G_BASE_FRT_FARE: FLOAT,
    G_MAXIMUM_ITERATION: INT,
    G_CONVERGENCE_GAP: FLOAT,
    G_MODE_CHANGE_THRESHOLD: FLOAT,
    G_AGGREGATION: STR,
    G_REJECTION_RATE_WINDOW: INT,
    G_TIME_PERIODS: STR_LIST,
    G_PERIOD_START_H: NUMBER,
    G_PERIOD_END_H: NUMBER_LIST,
    G_PEAK_PERIODS: STR_LIST,
    G_FRT_OPERATING_HOURS: INT,
    G_PARKING_CHARGE_INTERVAL_MIN: INT,
    G_PARKING_RATE_PEAK: FLOAT,
    G_PARKING_RATE_OFFPEAK: FLOAT,
    G_ENABLE_NUM_TRANSFER_PENALTY: BOOL,
    G_CAR_GAS_COST_PER_METER: FLOAT,
    G_F_GAS_PER_MILE: FLOAT,
    G_M_GAS_PER_MILE: FLOAT,
    G_FRT_OPERATING_COST_PER_VEH_HOUR: INT,
    G_MICRO_OPERATING_COST_PER_VEH_HOUR: INT,
    G_FRT_SPEED_MPH: INT,
    G_FRT_DWELL_TIME_MIN: INT,
    G_FRT_DEAD_END_TIME_MIN: INT,
    G_DEFAULT_MICRO_WAIT_TIME: INT,
    G_METERS_PER_MILE: FLOAT,
    G_OPERATING_PERIODS_SCENARIOS: STR_LIST_LIST,
    G_VIRTUAL_STOP_SCENARIOS: INT_LIST,
    G_MICROTRANSIT_RUNNING_SCENARIOS: STR_LIST,
    G_REPOSITIONING_LIST: BOOL_LIST,
    G_DEMAND_UPSCALING: BOOL,
    G_DEMAND_SAMPLE_SHARE: FLOAT,
    G_SAMPLE_DEMAND_FILE: STR,
}

# the keys of the study area's file area_parameters.csv (user's decision A, docs/study_area_inputs.md): the area's
# virtual-stop share, base FRT service and FRT line data, and its local prices and costs (the node numbering was here
# until it was derived from the network files on 2026-11-24). Every other key is in the model file.
AREA_PARAMETERS = (
    G_VIRTUAL_STOP_SCENARIOS,
    G_BASE_FRT_HEADWAY,
    G_BASE_FRT_FARE,
    G_FRT_OPERATING_HOURS,
    G_FRT_SPEED_MPH,
    G_FRT_DWELL_TIME_MIN,
    G_FRT_DEAD_END_TIME_MIN,
    G_FRT_OPERATING_COST_PER_VEH_HOUR,
    G_MICRO_OPERATING_COST_PER_VEH_HOUR,
    G_F_GAS_PER_MILE,
    G_M_GAS_PER_MILE,
    G_CAR_GAS_COST_PER_METER,
    G_PARKING_CHARGE_INTERVAL_MIN,
    G_PARKING_RATE_PEAK,
    G_PARKING_RATE_OFFPEAK,
    G_TIME_PERIODS,  # the time periods: since 2026-11-24 (before: in the model file, as day_start_h ... day_end_h)
    G_PERIOD_START_H,
    G_PERIOD_END_H,
    G_PEAK_PERIODS,
)
MODEL_PARAMETERS = tuple(key for key in PARAMETER_TYPES if key not in AREA_PARAMETERS)
