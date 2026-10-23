import numpy
import pandas as pd
import csv
import os
import subprocess
import time

folder_name = str("downtown_sd_headway_testing_R1")
headway_test_folder_path = os.path.join("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output",
                                        folder_name)
os.makedirs(headway_test_folder_path, exist_ok=True)

for headway in [20,30,60]:
    input_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/Input_parameter/input_parameter.csv"
    with open(input_csv_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Update the required values
    rows[1][13] = int(headway)  # "frt_headway" in .csv file
    with open(input_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    time.sleep(1)

    subprocess.run(["C:/Users/ritun_uci/.conda/envs/fleetpy_backup/python", "run_examples_new.py"])
    time.sleep(1)

    output_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/downtown_sd/output_folder" \
                      "/downtown_sd_evaluation_zonal_partition_False.csv"

    output_csv_df = pd.read_csv(output_csv_path)
    output_csv_df.to_csv(os.path.join(headway_test_folder_path, f"output_headway_{headway}.csv"), index=False)