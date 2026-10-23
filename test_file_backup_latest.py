from colorama import Fore, Style
import time
import csv
import os
import subprocess
import logging

import numpy
import pandas as pd
import torch
from ax.core.data import Data
from ax.core.experiment import Experiment
from ax.core.objective import MultiObjective, Objective
from ax.core.optimization_config import (
    MultiObjectiveOptimizationConfig,
    ObjectiveThreshold,
)
from ax.core import ChoiceParameter
from ax.core.parameter import ParameterType, RangeParameter
from ax.core.search_space import SearchSpace
from ax.metrics.noisy_function import GenericNoisyFunctionMetric

# Model registry for creating multi-objective optimization models.
from ax.modelbridge.registry import Models
from ax.runners.synthetic import SyntheticRunner
from ax.service.utils.report_utils import exp_to_df

# Plotting imports and initialization
from botorch.utils.multi_objective.box_decompositions.dominated import (
    DominatedPartitioning,
)
from matplotlib import pyplot as plt
from matplotlib.cm import ScalarMappable
from botorch.utils.multi_objective.pareto import is_non_dominated
from ax.core.parameter_constraint import ParameterConstraint

# ----------------------------------------------------------------------------------------------------------------------
# from colorama import Fore, Style
# import time
# import csv
# import os
# import subprocess
# import logging
#
# import numpy as np
# import pandas as pd
# import torch
#
# from ax.core import (
#     ChoiceParameter,
#     Data,
#     Experiment,
#     Objective,
#     ParameterType,
#     RangeParameter,
#     SearchSpace,
# )
# from ax.core.optimization_config import OptimizationConfig
# from ax.core.parameter_constraint import ParameterConstraint
# from ax.metrics.noisy_function import GenericNoisyFunctionMetric
# from ax.modelbridge.registry import Models
# from ax.runners.synthetic import SyntheticRunner
# from ax.service.utils.report_utils import exp_to_df
#
# from botorch.utils.multi_objective.box_decompositions.dominated import DominatedPartitioning
# from botorch.utils.multi_objective.pareto import is_non_dominated
# from matplotlib import pyplot as plt
# from matplotlib.cm import ScalarMappable
# ----------------------------------------------------------------------------------------------------------------------
folder_name = str("LG_submission_results_R2")
optimization_folder_path = os.path.join("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output",
                                        folder_name)
indv_res_folder_path = os.path.join("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output",
                                    folder_name, "indv_res")
agg_sim_output_folder_path = os.path.join(optimization_folder_path, "per_itr_agg_sim_output")
os.makedirs(optimization_folder_path, exist_ok=True)
os.makedirs(indv_res_folder_path, exist_ok=True)
os.makedirs(agg_sim_output_folder_path, exist_ok=True)
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

PARAM_COLS = [
    "Transit Fare ($)",
    "Micro distance based fare ($/mile)",
    "Micro start fare ($)",
    "Fleet size",
    "Peak fare factor",
    "Micro to fixed factor",
    "FRT Headway (min)"
]

OBJECTIVE_COLS = [
    "Total subsidy ($)",
    "Total mob. Logsum increase with micro"
]
# For Lemon Grove
METRIC_COLS = ['car_users',
               'car_mode_share (%)',
               'trsit_mode_users (W_M_F)',
               'transit_mode_share (%)',
               'pure_M_users',
               'M_mode_share (%)',
               'M_trips',
               'pure_F_users',
               'F_mode_share (%)',
               'F_trips',
               'pure_walk_users',
               'W_mode_share (%)',
               'walk_users',
               'M_pls_F_users',
               'M_pls_F_mode_share (%)',
               'F_oper_cost ($)',
               'M_oper_cost ($)',
               'F_revenue ($)',
               'M_revenue ($)',
               'Total_T_revenue ($)',
               'tot_sub ($)',
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
               'avg_M_fare',
               'avg_F_fare',
               'avg_T_fare',
               'avg_auto_gas_cost',
               'tt_o_pckt_cost ($)',
               'tt_mob_lgsm_inc_with_micro',
               'tt_gen_cost',
               'tt_mode_switch',
               'M_avg_wait_time (s)',
               'F_avg_wait_time (s)',
               'avg_walk_time (s)',
               'tt_walk_time (h)',
               'car_VMT (mi)',
               'M_VMT (mi)',
               'M_PMT (mi)',
               'M_PMT/M_VMT',
               'F_VMT (mi)',
               'F_PMT (mi)',
               'F_PMT/F_VMT',
               'tt_VMT (mi)',
               'tt_walk_dist (mi)',
               'wghted_acc_emp_5_min',
               'wghted_acc_emp_10_min',
               'wghted_acc_emp_15_min',
               'M_util_rate (%)',
               'M_veh_occ',
               'M_avg_speed (mph)',
               'fleetpy_wait',
               'rejection_rate'
               ]

HEADERS = PARAM_COLS + OBJECTIVE_COLS + METRIC_COLS + ['iteration_type']


def init_per_call_results_csv():
    # Overwrite at the start of the run with a fresh header row
    with open(RESULTS_CSV_PATH, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)


def append_per_call_row(param_values, objective_values, metric_values, iteration_type):
    """
    param_values: list/tuple in the same order as PARAM_COLS (your param_names order)
    objective_values: [Total subsidy ($), Total mob. Logsum increase with micro]
    metric_values: list matching METRIC_COLS length (will be padded/truncated as needed)
    iteration_type: str
    """
    # Safety: coerce lengths to match columns
    m_needed = len(METRIC_COLS)
    mv = list(metric_values)
    if len(mv) < m_needed:
        mv = mv + [None] * (m_needed - len(mv))
    elif len(mv) > m_needed:
        mv = mv[:m_needed]

    row = list(param_values) + list(objective_values) + mv + [iteration_type]
    with open(RESULTS_CSV_PATH, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(row)


# Initialize the CSV immediately at startup
init_per_call_results_csv()


def run_script():
    subprocess.run(["C:/Users/Autonomicity/.conda/envs/fleetpy/python", "run_examples_new_parking.py"])
    time.sleep(1)


def update_csv_with_train_x(values):
    a, b, c, d, e, h, f = values
    a1 = float(a)  # transit fare ($)
    b1 = float(b)  # Micro distance based fare ($/mile)
    c1 = float(c)  # Micro start fare ($)
    d1 = int(d)  # Fleet size
    e1 = float(e)  # Peak fare factor
    h1 = float(h)  # Micro to fixed factor
    f1 = int(f)  # FRT headway
    input_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/Input_parameter/input_parameter.csv"
    with open(input_csv_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Update the required values
    rows[1][5] = str(a1)  # "transit_fare ($)" in .csv file
    rows[1][6] = str(b1)  # "microtransit_dist_based_rate ($/mile)" in .csv file
    rows[1][7] = str(c1)  # "microtransit_start_fare ($)" in .csv file
    rows[1][8] = d1  # "Fleet_size" in .csv file

    rows[1][9] = e1  # "PkFareFactor" in .csv file
    rows[1][12] = h1  # "Micro2FixedFactor" in .csv file
    rows[1][13] = f1  # "frt_headway" in .csv file

    # Write the updated rows back to the CSV file
    with open(input_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    time.sleep(1)


def collect_output(iteration_type: str, values):
    output_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/lemon_grove/output_folder" \
                      "/lemon_grove_evaluation_zonal_partition_False.csv"

    # output_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/downtown_sd/output_folder" \
    #                   "/downtown_sd_debug_evaluation_zonal_partition_False.csv"

    a, b, c, d, e, h, f = values

    # indv_res_csv_path = f"D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/downtown_sd/output_folder/" \
    #                     f"debug_individual_results_micro_M_fsize_{int(d)}_op_hr_15_hw_{int(f)}_virstop_75_scen_10.csv"

    indv_res_csv_path = f"D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/lemon_grove/output_folder/" \
                        f"individual_results_micro_M_fsize_{int(d)}_op_hr_15_hw_{int(f)}_virstop_75_scen_10.csv"

    output_csv_df = pd.read_csv(output_csv_path)
    output_csv_df.to_csv(os.path.join(agg_sim_output_folder_path, f"agg_sim_output_{iteration_type}.csv"), index=False)

    indv_res_df = pd.read_csv(indv_res_csv_path)
    indv_res_df.to_csv(os.path.join(indv_res_folder_path, f"indiv_res_{iteration_type}.csv"), index=False)

    with open(output_csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

        # For Micro + FRT
        x1 = rows[3][30]  # "tt_sub" ($) in .csv file
        y1 = float(rows[3][50])  # "tt_mob_lgsm_inc_with_micro" in .csv file
        # For FRT only
        x2 = rows[2][30]  # "tt_sub" ($) in .csv file
        y2 = float(rows[2][50])  # "tt_mob_lgsm_inc_with_micro" in .csv file
        # a1 = [float(val) for idx, val in enumerate(rows[3]) if idx not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 30, 50, 72]]
        a1 = [float(val) for idx, val in enumerate(rows[3]) if idx not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 72]]  # For Lemon Grove

        # USE THIS PART WHEN THERE IS MICRO UPSCALING HAPPENING
        # F_oper_cost_base = float(rows[2][25])
        # F_revenue_base = float(rows[2][27])
        # subsidy_base = F_oper_cost_base - 4 * F_revenue_base
        #
        # F_oper_cost = float(rows[3][25])
        # M_oper_cost = float(rows[3][26])
        # F_revenue = float(rows[3][27])
        # M_revenue = float(rows[3][28])
        # subsidy_FRT_micro = F_oper_cost + M_oper_cost - 4 * F_revenue - 4 * M_revenue
        #
        # value_11 = -(subsidy_FRT_micro - subsidy_base)      # Subsidy delta
        # value_21 = 4 * (y1 - y2)    # mobility logsum delta   # Make it 5 for Downtown SD

        # USE THIS PART WHEN THERE IS NO MICRO UPSCALING HAPPENING
        value_11 = -(float(x1) - float(x2))        # Subsidy delta
        value_21 = (y1 - y2)      # mobility logsum delta

    return [value_11, value_21], a1


# Function for Exchanging Input and Output with the Simulation (Fleetpy)
def send_instruction(train_x, iteration_type):
    train_x_array = train_x.numpy()
    all_outputs = []
    other_metrics = []
    for values in train_x_array:
        update_csv_with_train_x(values)
        run_script()
        output, other_metric = collect_output(iteration_type, values)
        all_outputs.append(output)
        other_metrics.append(other_metric)
    all_outputs_array = numpy.array(all_outputs)
    other_metrics_array = numpy.array(other_metrics)

    received_output_list = all_outputs_array.tolist()[0]
    received_other_metrics_list = other_metrics_array.tolist()[0]

    # Write into the per_call_results.csv file
    append_per_call_row(
        param_values=values,  # 7 params in order
        objective_values=output,  # [subsidy, logsum inc]
        metric_values=other_metric,  # long vector
        iteration_type=iteration_type
    )

    return received_output_list, received_other_metrics_list


# Parameters for Ax experiment
N_BATCH = 390  # Number of iterations in optimization loop   # used 150 before
BATCH_SIZE = 1  # Number of candidate points to be generated   # used 1 before
n_samples = 170  # Initial sobol samples for training             # used 40 before
# dimension = 3   # Number of input parameters
ref_point = [-15000, 0]  # TODO: If -50000 is used then in 'metric_a': 'lower_is_better=False' to be used
tkwargs = {
    "dtype": torch.double,
    "device": torch.device("cuda" if torch.cuda.is_available() else "cpu"),
}

num_samples = 256
warmup_steps = 512
# ----------------------------------------------------------------------------------------------------------------------
# TODO: Search Space Definition for Discrete variables (i.e., the variables can take only certain values) Ax also
#  supports categorical variables

param_transit_fare = RangeParameter(name="Transit Fare ($)", lower=1.0, upper=5.0, parameter_type=ParameterType.FLOAT)
param_micro_dist_fare = RangeParameter(name="Micro distance based fare ($/mile)", lower=0.0, upper=5.0,
                                       parameter_type=ParameterType.FLOAT)
param_micro_start_fare = RangeParameter(name="Micro start fare ($)", lower=0.0, upper=3.0,
                                        parameter_type=ParameterType.FLOAT)
param_fleet_size = RangeParameter(name="Fleet size", lower=2.0, upper=7.0, parameter_type=ParameterType.INT)
param_peak_fare_factor = RangeParameter(name="Peak fare factor", lower=1.0, upper=4.0,
                                        parameter_type=ParameterType.FLOAT)
param_micro_fixed_factor = RangeParameter(name="Micro to fixed factor", lower=0.0, upper=1.0,
                                          parameter_type=ParameterType.FLOAT)
frt_headway = RangeParameter(name="FRT Headway (min)", lower=10.0, upper=30.0,
                             parameter_type=ParameterType.INT)

# Define the constraint
constraint = ParameterConstraint(
    constraint_dict={
        "Micro distance based fare ($/mile)": -1.0,
        "Micro start fare ($)": -1.0
    },
    bound=-0.5
)

search_space = SearchSpace(
    parameters=[param_transit_fare, param_micro_dist_fare, param_micro_start_fare, param_fleet_size,
                param_peak_fare_factor, param_micro_fixed_factor, frt_headway], parameter_constraints=[constraint]

)

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


def evaluate_objectives(x_sorted, iteration_type):
    start_time = time.time()
    input_data = torch.tensor(x_sorted).unsqueeze(0)
    print(f"{Fore.RED}send_instruction is being called for input {input_data} {Style.RESET_ALL}")
    logger.info(f"Send_instruction is being called for input {input_data}")
    _last_output, _last_other_metrics = send_instruction(input_data, iteration_type)
    end_time = time.time()
    duration = end_time - start_time
    log_path = f"D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/{folder_name}" \
               f"/indiv_call_timings_eval.csv"
    file_exists = os.path.isfile(log_path)
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["evaluation_time_(sec)"])
        writer.writerow([duration])

    return _last_output, _last_other_metrics


param_names = ["Transit Fare ($)", "Micro distance based fare ($/mile)", "Micro start fare ($)", "Fleet size",
               "Peak fare factor", "Micro to fixed factor", "FRT Headway (min)"]


def f1(x) -> float:
    x_sorted = [x[p_name] for p_name in param_names]
    input_tuple = tuple(x_sorted)
    global sobol_counter_f1
    global iteration_type
    global optimization_itr_counter
    if input_tuple not in objective_cache:
        if sobol_counter_f1 <= num_sobol_samples:
            iteration_type = f"training_itr_{sobol_counter_f1}"
            print(f"{Fore.GREEN}f1 evaluating for sobol input: {input_tuple}{Style.RESET_ALL}")
            logger.info(f"f1 evaluating for sobol input: {input_tuple}")
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
    if sobol_counter_f2 <= num_sobol_samples:
        print(f"{Fore.BLUE}f2 evaluating for sobol input: {input_tuple}{Style.RESET_ALL}")
        logger.info(f"f2 evaluating for sobol input: {input_tuple}")
    else:
        print(f"{Fore.BLUE}f2 evaluating for candidate input: {input_tuple}{Style.RESET_ALL}")
        logger.info(f"f2 evaluating for candidate input: {input_tuple}")
    sobol_counter_f2 += 1
    print(f"{Fore.BLUE}f2 objective output: {objective_cache[input_tuple][0][1]}{Style.RESET_ALL}\n")
    logger.info(f"f2 objective output: {objective_cache[input_tuple][0][1]}")
    return float(objective_cache[input_tuple][0][1])


# metric_a = GenericNoisyFunctionMetric(name="Total subsidy ($)", f=f1, noise_sd=0.0, lower_is_better=False)
# metric_b = GenericNoisyFunctionMetric(name="Total mob. Logsum increase with micro", f=f2, noise_sd=0.0,
#                                       lower_is_better=False)

metric_a = GenericNoisyFunctionMetric(name="Total subsidy ($)", f=f1, lower_is_better=False)
metric_b = GenericNoisyFunctionMetric(name="Total mob. Logsum increase with micro", f=f2, lower_is_better=False)

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


training_start_time = time.time()
experiment = build_experiment()


def initialize_experiment(experiment):
    sobol = Models.SOBOL(search_space=experiment.search_space)
    experiment.new_batch_trial(sobol.gen(n_samples)).run()
    return experiment.fetch_data()


data = initialize_experiment(experiment)

training_end_time = time.time()
training_duration = training_end_time - training_start_time
print(f"\n{Fore.GREEN}Training duration is {training_duration:.2f} seconds")

optimization_start_time = time.time()
# Run optimization using qNEHVI acquisition function
hv_list = []
for i in range(1, N_BATCH + 1):
    if i == 0:
        print(f"\n\n{Fore.RED}Sobol Samples End Here{Style.RESET_ALL}")
        logger.info(f"Sobol Samples End Here")
        print(f"{Fore.RED}Optimization Loop Starts Here{Style.RESET_ALL}\n\n")
        logger.info(f"Optimization Loop Starts Here")

    model = Models.BOTORCH_MODULAR(
        experiment=experiment,
        data=data,
    )

    # Generate new candidates
    generator_run = model.gen(BATCH_SIZE)

    # Create and run the batch trial
    trial = experiment.new_batch_trial(generator_run=generator_run)
    trial.run()

    # Fetch data and update
    data = Data.from_multiple_data([data, trial.fetch_data()])

    # Extract input data and objectives from the trial
    exp_df = exp_to_df(experiment)
    outcomes = torch.tensor(exp_df[["Total subsidy ($)", "Total mob. Logsum increase with micro"]].values, **tkwargs)

    # Collect input parameters, objective values, and other metrics
    inputs = generator_run.arms  # Input parameter sets
    objectives = exp_df[["Total subsidy ($)", "Total mob. Logsum increase with micro"]].values
    # ------------------------------------------------------------------------------------------------------------------
    # Compute hypervolume
    partitioning = DominatedPartitioning(ref_point=torch.tensor(ref_point, **tkwargs), Y=outcomes)
    try:
        hv = partitioning.compute_hypervolume().item()
    except:
        hv = 0
        print("Failed to compute hypervolume")
    hv_list.append(hv)
    print(f"{Fore.MAGENTA}Iteration {i}, Hypervolume: {hv}{Style.RESET_ALL}")
    logger.info(f"Iteration {i}, Hypervolume: {hv}")

optimization_end_time = time.time()
optimization_duration = optimization_end_time - optimization_start_time
print(f"\n{Fore.GREEN}Optimization duration is {optimization_duration:.2f} seconds")
# ----------------------------------------------------------------------------------------------------------------------
# Save inputs and objectives as per new method
df = exp_to_df(experiment).sort_values(by=["trial_index"])
df.to_csv(os.path.join(optimization_folder_path, "optimization_result_new_method.csv"), index=False)
# ----------------------------------------------------------------------------------------------------------------------
# Non Dominant Data Collection (Work on this part)
all_objectives_tensor = torch.tensor(all_objectives_opt_itr)  # This does not include sobol iterations
all_inputs_tensor = torch.tensor(all_inputs_opt_itr)  # This does not include sobol iterations
all_other_metrics_tensor = torch.tensor(all_other_metrics_opt_itr)  # This does not include sobol iterations

sorted_indices = all_objectives_tensor[:, 0].sort()[1]

all_objectives_tensor_sorted = all_objectives_tensor[sorted_indices]
all_inputs_sorted = all_inputs_tensor[sorted_indices]
all_other_metrics_sorted = all_other_metrics_tensor[sorted_indices]

non_dominated_mask = is_non_dominated(all_objectives_tensor_sorted)

final_non_dominated_input_tensor = all_inputs_sorted[non_dominated_mask]
final_non_dominated_objective_tensor = all_objectives_tensor_sorted[non_dominated_mask]
final_non_dominated_other_metrics_tensor = all_other_metrics_sorted[non_dominated_mask]

df_non_dom_inputs = pd.DataFrame(final_non_dominated_input_tensor.numpy(),
                                 columns=PARAM_COLS)
df_non_dom_objectives = pd.DataFrame(final_non_dominated_objective_tensor.numpy(),
                                     columns=OBJECTIVE_COLS)
df_non_dom_metrics = pd.DataFrame(final_non_dominated_other_metrics_tensor.numpy(),
                                  columns=METRIC_COLS)

df_total_non_dom = pd.concat([df_non_dom_inputs, df_non_dom_objectives, df_non_dom_metrics], axis=1)
df_total_non_dom.to_csv(os.path.join(optimization_folder_path, "non_dominated_data_old_method.csv"), index=False)
# ----------------------------------------------------------------------------------------------------------------------
# Work on this part
# Save the results to a CSV file
final_all_inputs = numpy.array(all_inputs)
final_all_objectives = numpy.array(all_objectives)
final_all_other_metrics = numpy.array(all_other_metrics)

df_inputs = pd.DataFrame(all_inputs,
                         columns=PARAM_COLS)
df_objectives = pd.DataFrame(all_objectives, columns=OBJECTIVE_COLS)
df_other_metrics = pd.DataFrame(all_other_metrics, columns=METRIC_COLS)

# Concatenate all data and save to output file
df_total = pd.concat([df_inputs, df_objectives, df_other_metrics], axis=1)
df_total.to_csv(os.path.join(optimization_folder_path, "result_old_method.csv"), index=False)
# ----------------------------------------------------------------------------------------------------------------------
opt_iter_labels = numpy.repeat(numpy.arange(1, N_BATCH + 1), BATCH_SIZE)[:len(all_objectives_opt_itr)]
sorted_idx = all_objectives_tensor[:, 0].sort()[1].cpu().numpy()
non_dom_mask_np = non_dominated_mask.cpu().numpy()
non_dominated_batch_numbers = opt_iter_labels[sorted_idx][non_dom_mask_np]
df_total_non_dom["non_dom_batch_num"] = non_dominated_batch_numbers
df_total_non_dom.to_csv(os.path.join(optimization_folder_path, "non_dominated_data_old_method_with_batch_num.csv"),
                        index=False)
# ----------------------------------------------------------------------------------------------------------------------
print(f"Hypervolumes: {hv_list}")
print(f"Non-dom batch numbers: {non_dominated_batch_numbers}")
# ----------------------------------------------------------------------------------------------------------------------
