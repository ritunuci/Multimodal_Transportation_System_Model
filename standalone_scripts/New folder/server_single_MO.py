# ----------------------------------------------------------------------------------------------------------------------
import numpy as np
import socket
import subprocess
import pickle
import csv
import time  # To add a delay between script runs if necessary
import threading
import pandas as pd
import os

def run_script():
    subprocess.run(["C:/ProgramData/Anaconda3/python", "run_examples_new.py"])
    time.sleep(5)
    print("\n\n")
def update_csv_with_train_x(values):

    a, b, c = values

    a1 = float(a)           # transit fare ($)
    b1 = float(b/1609.34)   # Micro distance based fare ($/meter)
    c1 = float(c)           # Micro start fare ($)
    input_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/Input_parameter/input_parameter.csv"
    with open(input_csv_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Update the required values
    rows[1][5] = str(a1)  # "transit_fare ($)" in .csv file
    rows[1][6] = str(b1)  # "microtransit_dist_based_rate ($/meter)" in .csv file
    rows[1][7] = str(c1)  # "microtransit_start_fare ($)" in .csv file
    # Write the updated rows back to the CSV file
    with open(input_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    time.sleep(2)
def collect_output():

    output_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/lemon_grove/output_folder" \
                      "/lemon_grove_evaluation_zonal_partition_False.csv"


    # output_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/lemon_grove/output_folder" \
    #                       "/lemon_grove_evaluation_zonal_partition_False.csv"


    with open(output_csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        # csvreader = csv.DictReader(csvfile)
        # for data in csvreader:

        # x = rows[3][36]  # "sub_per_T_rider" ($) in .csv file
        x = rows[3][30]  # "tt_sub" ($) in .csv file
        y = rows[3][50]  # "tt_mob_lgsm_inc_with_micro" in .csv file

        # a5 = [float(val) for idx, val in enumerate(rows[3]) if idx not in [0,1,2,3,4,5,6,7,8,9,36,50,72]]
        a5 = [float(val) for idx, val in enumerate(rows[3]) if idx not in [0,1,2,3,4,5,6,7,8,9,30,50,72]]
        value_1 = -float(x)
        value_2 = float(y)

        # value_3 = float(a1)   #TODO
        # value_4 = int(a2)
        # value_5 = float(a3)
        # value_6 = float(a4)

    # new_file = f"output_{i}.csv"
    # df = pd.read_csv(output_csv_path)
    # new_directory = 'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/'
    # 'Lemon_Grove/Fleet_Size_5/full_output_collect/'
    #
    # new_path = os.path.join(new_directory, new_file)
    # df.to_csv(new_path, index=False)

    # return [value_1, value_2], [value_3, value_4, value_5, value_6]   #TODO

    return [value_1, value_2], a5

def handle_client(conn, addr):
    print('Connected by', addr)
    with conn:
        while True:
            data = conn.recv(4096)  # Increased buffer size for larger data
            if not data:
                break
            train_x = pickle.loads(data)  # Deserialize train_x

            all_outputs = []
            other_metrics = []     #TODO

            for values in train_x:
                # Update CSV with the current value of train_x
                update_csv_with_train_x(values)

                # Run the script
                run_script()
                # time.sleep(5)

                # Collect the output
                print("Collecting the output...")
                output, other_metric = collect_output()    #TODO
                all_outputs.append(output)
                other_metrics.append(other_metric)         #TODO

                # Optionally, add a delay to ensure the script has time to finish
                # time.sleep(1)

            # Serialize and send back the collected output
            serialized_output = pickle.dumps((all_outputs, other_metrics))   #TODO
            conn.sendall(serialized_output)
            print('Results sent back to the client.')

def start_server():
    host = '127.0.0.1'  # Localhost
    port = 52097

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Server started, waiting for connections...")
        while True:
            conn, addr = s.accept()
            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
