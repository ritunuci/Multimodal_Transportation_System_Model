import time
import csv
import os
import subprocess
import pandas as pd
# ----------------------------------------------------------------------------------------------------------------------
folder_name = str("SD_submission_naive_results")
optimization_folder_path = os.path.join("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output",
                                        folder_name)
indv_res_folder_path = os.path.join("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output",
                                    folder_name, "indv_res")
agg_sim_output_folder_path = os.path.join(optimization_folder_path, "per_itr_agg_sim_output")
os.makedirs(optimization_folder_path, exist_ok=True)
os.makedirs(indv_res_folder_path, exist_ok=True)
os.makedirs(agg_sim_output_folder_path, exist_ok=True)

def run_script():
    subprocess.run(["C:/Users/Autonomicity/.conda/envs/fleetpy/python", "run_examples_new_parking.py"])
    time.sleep(1)

def update_csv_with_train_x(d1, f1):
    input_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/Input_parameter/input_parameter.csv"
    with open(input_csv_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    rows[1][8] = d1  # "Fleet_size" in .csv file
    rows[1][13] = f1  # "frt_headway" in .csv file

    # Write the updated rows back to the CSV file
    with open(input_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    time.sleep(1)

def collect_output(d, f):
    output_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/downtown_sd/output_folder" \
                      "/downtown_sd_evaluation_zonal_partition_False.csv"

    indv_res_csv_path = f"D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/downtown_sd/output_folder/" \
                        f"individual_results_micro_M_fsize_{int(d)}_op_hr_15_hw_{int(f)}_virstop_75_scen_10.csv"

    output_csv_df = pd.read_csv(output_csv_path)
    output_csv_df.to_csv(os.path.join(agg_sim_output_folder_path, f"agg_sim_output_fl_{d}_headway_{f}.csv"), index=False)

    indv_res_df = pd.read_csv(indv_res_csv_path)
    indv_res_df.to_csv(os.path.join(indv_res_folder_path, f"indiv_res_fl_{d}_headway_{f}.csv"), index=False)

fl_sizes = [3, 4, 5, 6, 7]
hw_list = [10, 15, 20, 25, 30]

for i in range(5):
    fls = fl_sizes[i]
    hw = hw_list[i]
    update_csv_with_train_x(fls, hw)
    run_script()
    collect_output(fls, hw)

