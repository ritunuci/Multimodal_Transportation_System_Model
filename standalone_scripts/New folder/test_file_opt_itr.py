from colorama import Fore, Style
import pickle
import socket
import time
import csv
import os
import subprocess
import logging
from pathlib import Path

from ax import optimize
from ax.core import ParameterType, RangeParameter, SearchSpace, MultiObjective, Objective, ObjectiveThreshold
from ax.core.experiment import Experiment
from ax.core.optimization_config import (
    MultiObjectiveOptimizationConfig,
    ObjectiveThreshold,
)
from ax.runners.synthetic import SyntheticRunner
from ax.metrics.noisy_function import GenericNoisyFunctionMetric
from botorch.utils.sampling import draw_sobol_samples

import numpy
import pandas as pd
import torch
from ax.core.data import Data
from ax.core.experiment import Experiment
from ax.core.metric import Metric
from ax.core.objective import MultiObjective, Objective
from ax.core.optimization_config import (
    MultiObjectiveOptimizationConfig,
    ObjectiveThreshold,
)
from ax.core import ChoiceParameter
from ax.core.parameter import ParameterType, RangeParameter
from ax.core.search_space import SearchSpace
from ax.metrics.noisy_function import GenericNoisyFunctionMetric
from ax.modelbridge.cross_validation import compute_diagnostics, cross_validate

# Analysis utilities, including a method to evaluate hypervolumes
from ax.modelbridge.modelbridge_utils import observed_hypervolume

# Model registry for creating multi-objective optimization models.
from ax.modelbridge.registry import Models
from ax.models.torch.botorch_modular.surrogate import Surrogate
from ax.plot.contour import plot_contour
from ax.plot.diagnostic import tile_cross_validation
from ax.plot.pareto_frontier import plot_pareto_frontier
from ax.plot.pareto_utils import compute_posterior_pareto_frontier
from ax.runners.synthetic import SyntheticRunner
from ax.service.utils.report_utils import exp_to_df
from ax.core.generator_run import GeneratorRun

# Plotting imports and initialization
from ax.utils.notebook.plotting import init_notebook_plotting, render
from botorch.models.fully_bayesian import SaasFullyBayesianSingleTaskGP
from botorch.test_functions.multi_objective import DTLZ2
from botorch.utils.multi_objective.box_decompositions.dominated import (
    DominatedPartitioning,
)
from matplotlib import pyplot as plt
from matplotlib.cm import ScalarMappable
from botorch.utils.multi_objective.pareto import is_non_dominated
from ax.plot.pareto_frontier import plot_pareto_frontier
from ax.core.parameter_constraint import ParameterConstraint
from ax import SumConstraint

# ----------------------------------------------------------------------------------------------------------------------
folder_name = str("downtown_sd_preloaded_continue")
optimization_folder_path = os.path.join("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output", folder_name)
indv_res_folder_path = os.path.join("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output", folder_name, "indv_res")
os.makedirs(optimization_folder_path, exist_ok=True)
os.makedirs(indv_res_folder_path, exist_ok=True)
RESULTS_CSV_PATH = os.path.join(optimization_folder_path, "per_call_results.csv")

log_file_path = os.path.join(optimization_folder_path, "run_log.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, mode="w"),
        logging.StreamHandler()  # keep console output too
    ]
)

logger = logging.getLogger(__name__)

# Precomputed Sobol results (inputs + objectives + other metrics)
sobol_results_csv = r"D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/sobol_results_downtown_sd_55.csv"

# NEW: Precomputed optimization history (e.g., first 122 BO iterations: inputs + objectives + other metrics)
opt_history_csv = r"D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/downtown_sd_opt_results_122.csv"
# Make sure this CSV has the same parameter, objective, and OTHER_METRIC_COLS columns

# ----------------------------------------------------------------------------------------------------------------------
def run_script():
    subprocess.run(["C:/Users/Autonomicity/.conda/envs/fleetpy/python", "run_examples_new_parking.py"])
    time.sleep(1)


def update_csv_with_train_x(values):
    a, b, c, d, e, h, f = values
    a1 = float(a)  # transit fare ($)
    b1 = float(b)  # Micro distance based fare ($/mile)
    c1 = float(c)  # Micro start fare ($)
    d1 = int(d)    # Fleet size
    e1 = float(e)  # Peak fare factor
    h1 = float(h)  # Micro to fixed factor
    f1 = int(f)    # FRT headway

    input_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/Input_parameter/input_parameter.csv"
    with open(input_csv_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Update the required values
    rows[1][5] = str(a1)   # "transit_fare ($)"
    rows[1][6] = str(b1)   # "microtransit_dist_based_rate ($/mile)"
    rows[1][7] = str(c1)   # "microtransit_start_fare ($)"
    rows[1][8] = str(d1)   # "Fleet_size"

    rows[1][9] = str(e1)   # "PkFareFactor"
    rows[1][12] = str(h1)  # "Micro2FixedFactor"
    rows[1][13] = str(f1)  # "frt_headway"

    # Write the updated rows back to the CSV file
    with open(input_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    time.sleep(1)


batch_num_list_sobol = []
batch_num_list_opt_itr = []


def collect_output(iteration_type: str, values):
    output_csv_path = (
        "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/downtown_sd/output_folder" \
                      "/downtown_sd_evaluation_zonal_partition_False.csv"
    )

    a, b, c, d, e, h, f = values
    indv_res_csv_path = (
        f"D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/downtown_sd/output_folder/" \
                        f"individual_results_micro_M_fsize_{int(d)}_op_hr_15_hw_{int(f)}_virstop_75_scen_10.csv"
    )

    indv_res_df = pd.read_csv(indv_res_csv_path)
    indv_res_df.to_csv(
        os.path.join(indv_res_folder_path, f"indiv_res_{iteration_type}.csv"),
        index=False
    )

    with open(output_csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

        x1 = rows[3][30]  # "tt_sub" ($)
        y1 = rows[3][50]  # "tt_mob_lgsm_inc_with_micro"
        # Extract "other metrics" (dropping some columns)
        a1 = [
            float(val)
            for idx, val in enumerate(rows[3])
            if idx not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 30, 50, 72]
        ]
        value_11 = -float(x1)     # Negative subsidy (maximization)
        value_21 = float(y1)

    return [value_11, value_21], a1


# Function for Exchanging Input and Output with the Simulation (Fleetpy)
def send_instruction(train_x, iteration_type):
    train_x_array = train_x.numpy()
    all_outputs = []
    all_other_metrics = []
    for values in train_x_array:
        update_csv_with_train_x(values)
        run_script()
        output, other_metric = collect_output(iteration_type, values)
        all_outputs.append(output)
        all_other_metrics.append(other_metric)
    all_outputs_array = numpy.array(all_outputs)
    all_other_metrics_array = numpy.array(all_other_metrics)

    received_output_list = all_outputs_array.tolist()[0]
    received_other_metrics_list = all_other_metrics_array.tolist()[0]

    return received_output_list, received_other_metrics_list


# ----------------------------------------------------------------------------------------------------------------------
# Parameters for Ax experiment
N_BATCH = 250        # Total number of optimization iterations (historical + new)
BATCH_SIZE = 1       # Number of candidate points per iteration
n_samples = 55      # Initial Sobol size (will be overwritten by CSV length)
ref_point = [-15000, 0]  # ref point for hypervolume

tkwargs = {
    "dtype": torch.double,
    "device": torch.device("cuda" if torch.cuda.is_available() else "cpu"),
}

num_samples = 256
warmup_steps = 512

# ----------------------------------------------------------------------------------------------------------------------
# Search Space
param_transit_fare = RangeParameter(
    name="Transit Fare ($)", lower=1.0, upper=5.0, parameter_type=ParameterType.FLOAT
)
param_micro_dist_fare = RangeParameter(
    name="Micro distance based fare ($/mile)",
    lower=0.0, upper=5.0,
    parameter_type=ParameterType.FLOAT
)
param_micro_start_fare = RangeParameter(
    name="Micro start fare ($)",
    lower=0.0, upper=3.0,
    parameter_type=ParameterType.FLOAT
)
param_fleet_size = RangeParameter(
    name="Fleet size",
    lower=2.0, upper=7.0,
    parameter_type=ParameterType.INT
)
param_peak_fare_factor = RangeParameter(
    name="Peak fare factor",
    lower=1.0, upper=4.0,
    parameter_type=ParameterType.FLOAT
)
param_micro_fixed_factor = RangeParameter(
    name="Micro to fixed factor",
    lower=0.0, upper=1.0,
    parameter_type=ParameterType.FLOAT
)
frt_headway = RangeParameter(
    name="FRT Headway (min)",
    lower=10.0, upper=30.0,
    parameter_type=ParameterType.INT
)

# Constraint: Micro distance based fare + start fare >= 0.5
constraint = ParameterConstraint(
    constraint_dict={
        "Micro distance based fare ($/mile)": -1.0,
        "Micro start fare ($)": -1.0
    },
    bound=-0.5
)

search_space = SearchSpace(
    parameters=[
        param_transit_fare,
        param_micro_dist_fare,
        param_micro_start_fare,
        param_fleet_size,
        param_peak_fare_factor,
        param_micro_fixed_factor,
        frt_headway
    ],
    parameter_constraints=[constraint]
)

# ----------------------------------------------------------------------------------------------------------------------
# Metric column names (other metrics)
OTHER_METRIC_COLS = [
    'car_users', 'car_mode_share (%)',
    'trsit_mode_users (W_M_F)',
    'transit_mode_share (%)',
    'pure_M_users', 'M_mode_share (%)',
    'M_trips', 'pure_F_users',
    'F_mode_share (%)', 'F_trips',
    'pure_walk_users',
    'W_mode_share (%)', 'walk_users',
    'M_pls_F_users',
    'M_pls_F_mode_share (%)',
    'F_oper_cost ($)',
    'M_oper_cost ($)', 'F_revenue ($)',
    'M_revenue ($)', 'Total_T_revenue ($)',
    'sub_per_F_trip ($)',
    'sub_per_F_rider ($)',
    'sub_per_M_trip ($)',
    'sub_per_M_rider ($)',
    'sub_per_T_trip ($)',
    'sub_per_T_rider ($)',
    'sub_per_M_pax_mile ($/mi)',
    'sub_per_F_pax_mile ($/mi)',
    'sub_per_T_pax_mile ($/mi)',
    'sub_per_M_VMT ($/mi)',
    'sub_per_F_VMT ($/mi)',
    'sub_per_T_VMT ($/mi)',
    'tt_auto_gas_cost ($)',
    'auto_gas_cost_per_mile ($/mi)',
    'avg_M_fare', 'avg_F_fare',
    'avg_T_fare',
    'avg_auto_gas_cost',
    'tt_o_pckt_cost ($)',
    'tt_gen_cost', 'tt_mode_switch',
    'M_avg_wait_time (s)',
    'F_avg_wait_time (s)',
    'avg_walk_time (s)',
    'tt_walk_time (h)', 'car_VMT (mi)',
    'M_VMT (mi)',
    'M_PMT (mi)', 'M_PMT/M_VMT',
    'F_VMT (mi)', 'F_PMT (mi)',
    'F_PMT/F_VMT', 'tt_VMT (mi)',
    'tt_walk_dist (mi)',
    'wghted_acc_emp_5_min',
    'wghted_acc_emp_10_min',
    'wghted_acc_emp_15_min',
    'M_util_rate (%)', 'M_veh_occ',
    'M_avg_speed (mph)'
]

# ----------------------------------------------------------------------------------------------------------------------
# Initialize lists to collect results
all_inputs = []
all_objectives = []
all_other_metrics = []

all_inputs_opt_itr = []
all_objectives_opt_itr = []
all_other_metrics_opt_itr = []

final_non_dominated_inputs = []
final_non_dominated_objectives = []
final_non_dominated_metrics = []

num_sobol_samples = n_samples
sobol_counter_f1 = 1
sobol_counter_f2 = 1
optimization_itr_counter = 1
iteration_type = None
objective_cache = {}

# Initialize hypervolume list (will be filled by loaders + optimization loop)
hv_list = []

# ----------------------------------------------------------------------------------------------------------------------
def evaluate_objectives(x_sorted, iteration_type):
    start_time = time.time()
    input_data = torch.tensor(x_sorted).unsqueeze(0)
    print(f"{Fore.RED}send_instruction is being called for input {input_data}{Style.RESET_ALL}")
    logger.info(f"Send_instruction is being called for input {input_data}")
    _last_output, _last_other_metrics = send_instruction(input_data, iteration_type)
    end_time = time.time()
    duration = end_time - start_time
    log_path = os.path.join(
        optimization_folder_path,
        "indiv_call_timings_eval.csv"
    )
    file_exists = os.path.isfile(log_path)
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["evaluation_time_(sec)"])
        writer.writerow([duration])

    return _last_output, _last_other_metrics


param_names = [
    "Transit Fare ($)",
    "Micro distance based fare ($/mile)",
    "Micro start fare ($)",
    "Fleet size",
    "Peak fare factor",
    "Micro to fixed factor",
    "FRT Headway (min)"
]


def f1(x) -> float:
    x_sorted = [x[p_name] for p_name in param_names]
    input_tuple = tuple(x_sorted)
    global sobol_counter_f1
    global iteration_type
    global optimization_itr_counter
    global num_sobol_samples

    if input_tuple not in objective_cache:
        if sobol_counter_f1 <= num_sobol_samples:
            iteration_type = f"training_itr_{sobol_counter_f1}"
            print(f"{Fore.GREEN}f1 evaluating for sobol input (should NOT happen now): {input_tuple}{Style.RESET_ALL}")
            logger.info(f"f1 evaluating for sobol input (should NOT happen now): {input_tuple}")
        else:
            iteration_type = f"optimization_itr_{optimization_itr_counter}"
            print(f"{Fore.GREEN}f1 evaluating for candidate input: {input_tuple}{Style.RESET_ALL}")
            logger.info(f"f1 evaluating for candidate input: {input_tuple}")
            optimization_itr_counter += 1

        output, other_metrics = evaluate_objectives(x_sorted, iteration_type)
        objective_cache[input_tuple] = (output, other_metrics)

        all_inputs.append(x_sorted)
        all_objectives.append(output)
        all_other_metrics.append(other_metrics)

        # New optimization iterations only (Sobol is preloaded from CSV)
        if sobol_counter_f1 > num_sobol_samples:
            all_inputs_opt_itr.append(x_sorted)
            all_objectives_opt_itr.append(output)
            all_other_metrics_opt_itr.append(other_metrics)

        print(f"{Fore.GREEN}f1 objective output:{objective_cache[input_tuple][0][0]}{Style.RESET_ALL}\n")
        logger.info(f"f1 objective output:{objective_cache[input_tuple][0][0]}")
    else:
        print(f"{Fore.GREEN}f1 obj. retrieving for input: {input_tuple}{Style.RESET_ALL}")
        logger.info(f"f1 obj. retrieving for input: {input_tuple}")
        print(f"{Fore.GREEN}f1 objective output from cache:{objective_cache[input_tuple][0][0]}{Style.RESET_ALL}\n")
        logger.info(f"f1 objective output from cache:{objective_cache[input_tuple][0][0]}")

        all_inputs.append(x_sorted)
        all_objectives.append(objective_cache[input_tuple][0])
        all_other_metrics.append(objective_cache[input_tuple][1])

        if sobol_counter_f1 > num_sobol_samples:
            all_inputs_opt_itr.append(x_sorted)
            all_objectives_opt_itr.append(objective_cache[input_tuple][0])
            all_other_metrics_opt_itr.append(objective_cache[input_tuple][1])

    sobol_counter_f1 += 1
    return float(objective_cache[input_tuple][0][0])


def f2(x) -> float:
    x_sorted = [x[p_name] for p_name in param_names]
    input_tuple = tuple(x_sorted)
    global sobol_counter_f2
    global num_sobol_samples

    if sobol_counter_f2 <= num_sobol_samples:
        print(f"{Fore.BLUE}f2 evaluating for sobol input (should NOT happen now): {input_tuple}{Style.RESET_ALL}")
        logger.info(f"f2 evaluating for sobol input (should NOT happen now): {input_tuple}")
    else:
        print(f"{Fore.BLUE}f2 evaluating for candidate input: {input_tuple}{Style.RESET_ALL}")
        logger.info(f"f2 evaluating for candidate input: {input_tuple}")
    sobol_counter_f2 += 1
    print(f"{Fore.BLUE}f2 objective output: {objective_cache[input_tuple][0][1]}{Style.RESET_ALL}\n")
    logger.info(f"f2 objective output: {objective_cache[input_tuple][0][1]}")
    return float(objective_cache[input_tuple][0][1])


metric_a = GenericNoisyFunctionMetric(
    name="Total subsidy ($)",
    f=f1,
    noise_sd=0.0,
    lower_is_better=False
)
metric_b = GenericNoisyFunctionMetric(
    name="Total mob. Logsum increase with micro",
    f=f2,
    noise_sd=0.0,
    lower_is_better=False
)

# MultiObjective setup
mo = MultiObjective(
    objectives=[Objective(metric=metric_a), Objective(metric=metric_b)],
)

objective_thresholds = [
    ObjectiveThreshold(metric=metric_a, bound=ref_point[0], relative=False),
    ObjectiveThreshold(metric=metric_b, bound=ref_point[1], relative=False),
]

optimization_config = MultiObjectiveOptimizationConfig(
    objective=mo,
    objective_thresholds=objective_thresholds,
)


# Build and initialize experiment
def build_experiment():
    experiment = Experiment(
        name="multi_obj_exp",
        search_space=search_space,
        optimization_config=optimization_config,
        runner=SyntheticRunner(),
    )
    return experiment


# ----------------------------------------------------------------------------------------------------------------------
# Load initial Sobol data from CSV
# def load_initial_data_from_csv(experiment, csv_path):
#     """
#     Read precomputed Sobol samples (inputs + objectives + other metrics) from CSV,
#     create a batch trial with those arms, build a Data object for the objectives,
#     and warm-start all in-memory tracking structures.
#     """
#     global objective_cache, all_inputs, all_objectives, all_other_metrics
#
#     df = pd.read_csv(csv_path)
#
#     # Parameter columns must match param_names
#     param_cols = param_names
#
#     # Objective columns in the CSV
#     obj_cols = ["Total subsidy ($)", "Total mob. Logsum increase with micro"]
#
#     # Create arms from parameters
#     arms = []
#     for _, row in df.iterrows():
#         params = {
#             "Transit Fare ($)": float(row["Transit Fare ($)"]),
#             "Micro distance based fare ($/mile)": float(row["Micro distance based fare ($/mile)"]),
#             "Micro start fare ($)": float(row["Micro start fare ($)"]),
#             "Fleet size": float(row["Fleet size"]),
#             "Peak fare factor": float(row["Peak fare factor"]),
#             "Micro to fixed factor": float(row["Micro to fixed factor"]),
#             "FRT Headway (min)": float(row["FRT Headway (min)"]),
#         }
#         arms.append(experiment.search_space.construct_arm(parameters=params))
#
#     # One batch trial containing all Sobol arms
#     # generator_run = GeneratorRun(arms=arms)
#     # trial = experiment.new_batch_trial(generator_run=generator_run)
#     # trial.mark_completed()
#
#     # One batch trial containing all Sobol arms
#     generator_run = GeneratorRun(arms=arms)
#     trial = experiment.new_batch_trial(generator_run=generator_run)
#
#     # Mark as running then completed (no simulation call!)
#     trial.mark_running()
#     trial.mark_completed()
#
#     # Build Ax Data for the two objectives (deterministic: sem = 0)
#     records = []
#     for arm, (_, row) in zip(trial.arms, df.iterrows()):
#         for metric_name in obj_cols:
#             records.append({
#                 "trial_index": trial.index,
#                 "arm_name": arm.name,
#                 "metric_name": metric_name,
#                 "mean": float(row[metric_name]),
#                 "sem": 0.0,
#             })
#
#     data = Data(df=pd.DataFrame.from_records(records))
#
#     # Warm-start internal caches so the rest of the script (plots, etc.) works
#     for _, row in df.iterrows():
#         x_sorted = [row[c] for c in param_cols]
#         input_tuple = tuple(x_sorted)
#
#         # Assume CSV already stores objectives with correct sign convention
#         output = [float(row[obj_cols[0]]), float(row[obj_cols[1]])]
#         other_metrics = [float(row[col]) for col in OTHER_METRIC_COLS]
#
#         objective_cache[input_tuple] = (output, other_metrics)
#         all_inputs.append(x_sorted)
#         all_objectives.append(output)
#         all_other_metrics.append(other_metrics)
#
#     return data, len(df)

def load_initial_data_from_csv(experiment, csv_path):
    """
    Read precomputed Sobol samples (inputs + objectives + other metrics) from CSV,
    create a batch trial with those arms, build a Data object for the objectives,
    and warm-start all in-memory tracking structures.
    """
    global objective_cache, all_inputs, all_objectives, all_other_metrics

    df = pd.read_csv(csv_path)

    # Parameter columns must match param_names
    param_cols = param_names

    # Objective columns in the CSV
    obj_cols = ["Total subsidy ($)", "Total mob. Logsum increase with micro"]

    # Create arms from parameters
    arms = []
    for _, row in df.iterrows():
        params = {
            "Transit Fare ($)": float(row["Transit Fare ($)"]),
            "Micro distance based fare ($/mile)": float(row["Micro distance based fare ($/mile)"]),
            "Micro start fare ($)": float(row["Micro start fare ($)"]),
            "Fleet size": float(row["Fleet size"]),
            "Peak fare factor": float(row["Peak fare factor"]),
            "Micro to fixed factor": float(row["Micro to fixed factor"]),
            "FRT Headway (min)": float(row["FRT Headway (min)"]),
        }
        arms.append(experiment.search_space.construct_arm(parameters=params))

    # One batch trial containing all Sobol arms
    generator_run = GeneratorRun(arms=arms)
    trial = experiment.new_batch_trial(generator_run=generator_run)
    # ⬆️ DO NOT mark_running / mark_completed; we just use trial.index

    # Build Ax Data for the two objectives (deterministic: sem = 0)
    records = []
    for arm, (_, row) in zip(trial.arms, df.iterrows()):
        for metric_name in obj_cols:
            records.append({
                "trial_index": trial.index,
                "arm_name": arm.name,
                "metric_name": metric_name,
                "mean": float(row[metric_name]),
                "sem": 0.0,
            })

    data = Data(df=pd.DataFrame.from_records(records))

    # Warm-start internal caches so the rest of the script (plots, etc.) works
    for _, row in df.iterrows():
        x_sorted = [row[c] for c in param_cols]
        input_tuple = tuple(x_sorted)

        # Assume CSV already stores objectives with correct sign convention
        output = [float(row[obj_cols[0]]), float(row[obj_cols[1]])]
        other_metrics = [float(row[col]) for col in OTHER_METRIC_COLS]

        objective_cache[input_tuple] = (output, other_metrics)
        all_inputs.append(x_sorted)
        all_objectives.append(output)
        all_other_metrics.append(other_metrics)

    return data, len(df)


# NEW: Load optimization history (e.g., first 122 BO iterations) from CSV
# def load_optimization_history_from_csv(experiment, data, csv_path):
#     """
#     Read previously evaluated optimization iterations (one candidate per iteration)
#     from CSV, create one completed trial per row (without calling the simulation),
#     extend Ax Data, warm-start caches and *_opt_itr lists, and compute hypervolume
#     after each of these iterations.
#     """
#     global objective_cache
#     global all_inputs, all_objectives, all_other_metrics
#     global all_inputs_opt_itr, all_objectives_opt_itr, all_other_metrics_opt_itr
#
#     df_opt = pd.read_csv(csv_path)
#     num_loaded = len(df_opt)
#     hv_prefix = []
#
#     for i, (_, row) in enumerate(df_opt.iterrows(), start=1):
#         # --- Create arm for this historical candidate ---
#         params = {
#             "Transit Fare ($)": float(row["Transit Fare ($)"]),
#             "Micro distance based fare ($/mile)": float(row["Micro distance based fare ($/mile)"]),
#             "Micro start fare ($)": float(row["Micro start fare ($)"]),
#             "Fleet size": float(row["Fleet size"]),
#             "Peak fare factor": float(row["Peak fare factor"]),
#             "Micro to fixed factor": float(row["Micro to fixed factor"]),
#             "FRT Headway (min)": float(row["FRT Headway (min)"]),
#         }
#         # arm = experiment.search_space.construct_arm(parameters=params)
#         # generator_run = GeneratorRun(arms=[arm])
#         #
#         # # One batch trial with this arm; mark as completed (no f1/f2, no FleetPy)
#         # trial = experiment.new_batch_trial(generator_run=generator_run)
#         # trial.mark_completed()
#
#         arm = experiment.search_space.construct_arm(parameters=params)
#         generator_run = GeneratorRun(arms=[arm])
#
#         # One batch trial with this arm; mark as running then completed (no f1/f2, no FleetPy)
#         trial = experiment.new_batch_trial(generator_run=generator_run)
#         trial.mark_running()
#         trial.mark_completed()
#
#         # --- Build Data for this trial (two objectives, deterministic) ---
#         records = []
#         for metric_name in ["Total subsidy ($)", "Total mob. Logsum increase with micro"]:
#             records.append({
#                 "trial_index": trial.index,
#                 "arm_name": arm.name,
#                 "metric_name": metric_name,
#                 "mean": float(row[metric_name]),
#                 "sem": 0.0,
#             })
#         trial_data = Data(df=pd.DataFrame.from_records(records))
#         data = Data.from_multiple_data([data, trial_data])
#
#         # --- Warm-start caches and lists ---
#         x_sorted = [row[p] for p in param_names]
#         input_tuple = tuple(x_sorted)
#
#         # Again assume CSV uses the same sign convention as runtime evaluation
#         output = [
#             float(row["Total subsidy ($)"]),
#             float(row["Total mob. Logsum increase with micro"]),
#         ]
#         other_metrics = [float(row[col]) for col in OTHER_METRIC_COLS]
#
#         objective_cache[input_tuple] = (output, other_metrics)
#
#         # Global "all" history
#         all_inputs.append(x_sorted)
#         all_objectives.append(output)
#         all_other_metrics.append(other_metrics)
#
#         # Optimization-iteration-only lists
#         all_inputs_opt_itr.append(x_sorted)
#         all_objectives_opt_itr.append(output)
#         all_other_metrics_opt_itr.append(other_metrics)
#
#         # --- Hypervolume after this iteration (Sobol + these i opt points) ---
#         exp_df = exp_to_df(experiment)
#         outcomes = torch.tensor(
#             exp_df[["Total subsidy ($)", "Total mob. Logsum increase with micro"]].values,
#             **tkwargs
#         )
#         partitioning = DominatedPartitioning(
#             ref_point=torch.tensor(ref_point, **tkwargs),
#             Y=outcomes,
#         )
#         try:
#             hv = partitioning.compute_hypervolume().item()
#         except Exception as e:
#             hv = 0.0
#             print("Failed to compute hypervolume for historical iter", i, ":", e)
#         hv_prefix.append(hv)
#
#     return data, hv_prefix, num_loaded

def load_optimization_history_from_csv(experiment, data, csv_path):
    """
    Read previously evaluated optimization iterations (one candidate per iteration)
    from CSV, create one trial per row (without calling the simulation),
    extend Ax Data, warm-start caches and *_opt_itr lists, and compute hypervolume
    after each of these iterations.
    """
    global objective_cache
    global all_inputs, all_objectives, all_other_metrics
    global all_inputs_opt_itr, all_objectives_opt_itr, all_other_metrics_opt_itr

    df_opt = pd.read_csv(csv_path)
    num_loaded = len(df_opt)
    hv_prefix = []

    for i, (_, row) in enumerate(df_opt.iterrows(), start=1):
        # --- Create arm for this historical candidate ---
        params = {
            "Transit Fare ($)": float(row["Transit Fare ($)"]),
            "Micro distance based fare ($/mile)": float(row["Micro distance based fare ($/mile)"]),
            "Micro start fare ($)": float(row["Micro start fare ($)"]),
            "Fleet size": float(row["Fleet size"]),
            "Peak fare factor": float(row["Peak fare factor"]),
            "Micro to fixed factor": float(row["Micro to fixed factor"]),
            "FRT Headway (min)": float(row["FRT Headway (min)"]),
        }
        arm = experiment.search_space.construct_arm(parameters=params)
        generator_run = GeneratorRun(arms=[arm])

        # One batch trial with this arm; no run / no status change
        trial = experiment.new_batch_trial(generator_run=generator_run)

        # --- Build Data for this trial (two objectives, deterministic) ---
        records = []
        for metric_name in ["Total subsidy ($)", "Total mob. Logsum increase with micro"]:
            records.append({
                "trial_index": trial.index,
                "arm_name": arm.name,
                "metric_name": metric_name,
                "mean": float(row[metric_name]),
                "sem": 0.0,
            })
        trial_data = Data(df=pd.DataFrame.from_records(records))
        data = Data.from_multiple_data([data, trial_data])

        # --- Warm-start caches and lists ---
        x_sorted = [row[p] for p in param_names]
        input_tuple = tuple(x_sorted)

        # Assume CSV uses the same sign convention as runtime evaluation
        output = [
            float(row["Total subsidy ($)"]),
            float(row["Total mob. Logsum increase with micro"]),
        ]
        other_metrics = [float(row[col]) for col in OTHER_METRIC_COLS]

        objective_cache[input_tuple] = (output, other_metrics)

        # Global "all" history
        all_inputs.append(x_sorted)
        all_objectives.append(output)
        all_other_metrics.append(other_metrics)

        # Optimization-iteration-only lists
        all_inputs_opt_itr.append(x_sorted)
        all_objectives_opt_itr.append(output)
        all_other_metrics_opt_itr.append(other_metrics)

        # --- Hypervolume after this iteration (Sobol + these i opt points) ---
        exp_df = exp_to_df(experiment)
        outcomes = torch.tensor(
            exp_df[["Total subsidy ($)", "Total mob. Logsum increase with micro"]].values,
            **tkwargs
        )
        partitioning = DominatedPartitioning(
            ref_point=torch.tensor(ref_point, **tkwargs),
            Y=outcomes,
        )
        try:
            hv = partitioning.compute_hypervolume().item()
        except Exception as e:
            hv = 0.0
            print("Failed to compute hypervolume for historical iter", i, ":", e)
        hv_prefix.append(hv)

    return data, hv_prefix, num_loaded

# ----------------------------------------------------------------------------------------------------------------------
# TRAINING / WARM-START (Sobol + historical optimization iterations)
training_start_time = time.time()
experiment = build_experiment()

# 1) Load precomputed Sobol design
data, num_sobol_loaded = load_initial_data_from_csv(experiment, sobol_results_csv)

# Sync Sobol counters
n_samples = num_sobol_loaded
num_sobol_samples = num_sobol_loaded
sobol_counter_f1 = num_sobol_samples + 1
sobol_counter_f2 = num_sobol_samples + 1

# Attach Sobol data
experiment.attach_data(data)

# 2) Load precomputed optimization iterations (e.g., first 122 iters)
data, hv_prefix, num_opt_loaded = load_optimization_history_from_csv(
    experiment, data, opt_history_csv
)

# Initialize hypervolume list with historical values
hv_list = hv_prefix.copy()

# Optimization iteration counter should continue from (num_opt_loaded + 1)
optimization_itr_counter = num_opt_loaded + 1

training_end_time = time.time()
training_duration = training_end_time - training_start_time
print(
    f"\n{Fore.GREEN}Training (loading Sobol + {num_opt_loaded} opt iters from CSV) "
    f"duration is {training_duration:.2f} seconds{Style.RESET_ALL}"
)
logger.info(
    f"Training (loading Sobol + {num_opt_loaded} opt iters from CSV) "
    f"duration is {training_duration:.2f} seconds"
)

# ----------------------------------------------------------------------------------------------------------------------
# OPTIMIZATION LOOP (qNEHVI using BOTORCH_MODULAR)
optimization_start_time = time.time()

# hv_list already contains hypervolumes for the historical optimization iterations
# num_opt_loaded is, for example, 122
start_iter = num_opt_loaded + 1

for i in range(start_iter, N_BATCH + 1):
    if i == start_iter:
        print(
            f"\n\n{Fore.RED}Sobol Samples (from CSV) + {num_opt_loaded} "
            f"historical opt iterations end here{Style.RESET_ALL}"
        )
        logger.info(
            f"Sobol Samples (from CSV) + {num_opt_loaded} historical opt iterations end here"
        )
        print(
            f"{Fore.RED}Optimization Loop continues here with new simulation calls{Style.RESET_ALL}\n\n"
        )
        logger.info("Optimization Loop continues here with new simulation calls")

    model = Models.BOTORCH_MODULAR(
        experiment=experiment,
        data=data,
    )

    # Generate new candidates
    generator_run = model.gen(BATCH_SIZE)

    # Create and run the batch trial (this WILL call f1/f2 -> FleetPy)
    trial = experiment.new_batch_trial(generator_run=generator_run)
    trial.run()

    # Fetch data for the new trial and update the "data" we pass to the model
    new_data = trial.fetch_data()
    data = Data.from_multiple_data([data, new_data])

    # Extract outcomes for hypervolume
    exp_df = exp_to_df(experiment)
    outcomes = torch.tensor(
        exp_df[["Total subsidy ($)", "Total mob. Logsum increase with micro"]].values,
        **tkwargs
    )

    # Compute hypervolume
    partitioning = DominatedPartitioning(ref_point=torch.tensor(ref_point, **tkwargs), Y=outcomes)
    try:
        hv = partitioning.compute_hypervolume().item()
    except Exception as e:
        hv = 0
        print("Failed to compute hypervolume:", e)
    hv_list.append(hv)
    print(f"{Fore.MAGENTA}Iteration {i}, Hypervolume: {hv}{Style.RESET_ALL}")
    logger.info(f"Iteration {i}, Hypervolume: {hv}")

optimization_end_time = time.time()
optimization_duration = optimization_end_time - optimization_start_time
print(f"\n{Fore.GREEN}Optimization duration is {optimization_duration:.2f} seconds{Style.RESET_ALL}")
logger.info(f"Optimization duration is {optimization_duration:.2f} seconds")

# ----------------------------------------------------------------------------------------------------------------------
# Save optimization results (full Ax experiment)
df = exp_to_df(experiment).sort_values(by=["trial_index"])
df.to_csv(os.path.join(optimization_folder_path, "optimization_result_new_method.csv"), index=False)

# ----------------------------------------------------------------------------------------------------------------------
# Non Dominant Data Collection (only optimization iterations stored in *_opt_itr lists)
if len(all_objectives_opt_itr) > 0:
    all_objectives_tensor = torch.tensor(all_objectives_opt_itr)    # does not include Sobol iterations
    all_inputs_tensor = torch.tensor(all_inputs_opt_itr)            # does not include Sobol iterations
    all_other_metrics_tensor = torch.tensor(all_other_metrics_opt_itr)

    sorted_indices = all_objectives_tensor[:, 0].sort()[1]

    all_objectives_tensor_sorted = all_objectives_tensor[sorted_indices]
    all_inputs_sorted = all_inputs_tensor[sorted_indices]
    all_other_metrics_sorted = all_other_metrics_tensor[sorted_indices]

    non_dominated_mask = is_non_dominated(all_objectives_tensor_sorted)

    final_non_dominated_input_tensor = all_inputs_sorted[non_dominated_mask]
    final_non_dominated_objective_tensor = all_objectives_tensor_sorted[non_dominated_mask]
    final_non_dominated_other_metrics_tensor = all_other_metrics_sorted[non_dominated_mask]

    df_non_dom_inputs = pd.DataFrame(
        final_non_dominated_input_tensor.numpy(),
        columns=param_names
    )
    df_non_dom_objectives = pd.DataFrame(
        final_non_dominated_objective_tensor.numpy(),
        columns=["Total subsidy ($)", "Total mob. Logsum increase with micro"]
    )
    df_non_dom_metrics = pd.DataFrame(
        final_non_dominated_other_metrics_tensor.numpy(),
        columns=OTHER_METRIC_COLS
    )

    df_total_non_dom = pd.concat(
        [df_non_dom_inputs, df_non_dom_objectives, df_non_dom_metrics],
        axis=1
    )
    df_total_non_dom.to_csv(
        os.path.join(optimization_folder_path, "non_dominated_data_old_method.csv"),
        index=False
    )
else:
    df_total_non_dom = pd.DataFrame(
        columns=param_names + ["Total subsidy ($)", "Total mob. Logsum increase with micro"] + OTHER_METRIC_COLS
    )

# ----------------------------------------------------------------------------------------------------------------------
# Save all data (Sobol-from-CSV + optimization) from our manual lists
final_all_inputs = numpy.array(all_inputs)
final_all_objectives = numpy.array(all_objectives)
final_all_other_metrics = numpy.array(all_other_metrics)

df_inputs = pd.DataFrame(final_all_inputs, columns=param_names)
df_objectives = pd.DataFrame(
    final_all_objectives,
    columns=["Total subsidy ($)", "Total mob. Logsum increase with micro"]
)
df_other_metrics = pd.DataFrame(
    final_all_other_metrics,
    columns=OTHER_METRIC_COLS
)

df_total = pd.concat([df_inputs, df_objectives, df_other_metrics], axis=1)
df_total.to_csv(os.path.join(optimization_folder_path, "result_old_method.csv"), index=False)

# ----------------------------------------------------------------------------------------------------------------------
# Plot 1: All Objective Points ('total_points.png')
batch_number = torch.cat(
    [
        torch.zeros(n_samples),
        torch.arange(1, N_BATCH + 1).repeat(BATCH_SIZE, 1).t().reshape(-1),
    ]
).numpy()

fig1, ax1 = plt.subplots(figsize=(12, 8))
sc1 = ax1.scatter(
    final_all_objectives[:, 0],
    final_all_objectives[:, 1],
    c=batch_number,
    alpha=0.8,
)
ax1.set_xlabel("Total Subsidy ($)", fontsize=14)
ax1.set_ylabel("Total Mobility Logsum Increase with Microtransit", fontsize=14)
ax1.tick_params(axis='both', labelsize=14)
norm1 = plt.Normalize(batch_number.min(), batch_number.max())
sm1 = ScalarMappable(norm=norm1, cmap='viridis')
sm1.set_array([])

cbar_ax1 = fig1.add_axes([0.96, 0.15, 0.01, 0.7])
cbar1 = fig1.colorbar(sm1, cax=cbar_ax1)
cbar1.ax.set_title("Iteration")
fig1.savefig(os.path.join(optimization_folder_path, 'total_points.png'), format='png', dpi=300)
plt.show()

# ----------------------------------------------------------------------------------------------------------------------
# Non-Dominant Points ('non_dominant_points.png')
if len(all_objectives_opt_itr) > 0:
    opt_iter_labels = numpy.repeat(
        numpy.arange(1, N_BATCH + 1),
        BATCH_SIZE
    )[:len(all_objectives_opt_itr)]

    all_objectives_tensor = torch.tensor(all_objectives_opt_itr)
    sorted_idx = all_objectives_tensor[:, 0].sort()[1].cpu().numpy()
    non_dom_mask_np = is_non_dominated(all_objectives_tensor[sorted_idx]).cpu().numpy()
    non_dominated_batch_numbers = opt_iter_labels[sorted_idx][non_dom_mask_np]

    df_total_non_dom["non_dom_batch_num"] = non_dominated_batch_numbers
    df_total_non_dom.to_csv(
        os.path.join(optimization_folder_path, "non_dominated_data_old_method_with_batch_num.csv"),
        index=False
    )

    fig2, ax2 = plt.subplots(figsize=(12, 8))
    sc2 = ax2.scatter(
        final_non_dominated_objective_tensor[:, 0].cpu().numpy(),
        final_non_dominated_objective_tensor[:, 1].cpu().numpy(),
        c=non_dominated_batch_numbers,
        alpha=0.8,
    )
    ax2.set_xlabel("Total Subsidy ($)", fontsize=14)
    ax2.set_ylabel("Total Mobility Logsum Increase with Microtransit", fontsize=14)
    ax2.tick_params(axis='both', labelsize=14)
    norm2 = plt.Normalize(non_dominated_batch_numbers.min(), non_dominated_batch_numbers.max())
    sm2 = ScalarMappable(norm=norm2, cmap='viridis')
    sm2.set_array([])
    cbar_ax2 = fig2.add_axes([0.95, 0.15, 0.01, 0.7])
    cbar2 = fig2.colorbar(sm2, cax=cbar_ax2)
    cbar2.ax.set_title("Iteration")
    cbar2.set_ticks(
        numpy.arange(non_dominated_batch_numbers.min(),
                     non_dominated_batch_numbers.max() + 1, 1)
    )
    fig2.savefig(os.path.join(optimization_folder_path, 'non_dominant_points.png'), format='png', dpi=300)
    plt.show()
else:
    print("No optimization iterations recorded in *_opt_itr; skipping non-dominant plot.")

# ----------------------------------------------------------------------------------------------------------------------
# HYPERVOLUME PLOTTING
iterations = numpy.arange(1, N_BATCH + 1)
fig3, ax3 = plt.subplots()
ax3.plot(iterations, hv_list)
ax3.set_xlabel("Iteration")
ax3.set_ylabel("Hypervolume")
fig3.savefig(os.path.join(optimization_folder_path, 'hypervolume_plot.png'), format='png', dpi=300)
plt.show()

print(f"Hypervolumes: {hv_list}")