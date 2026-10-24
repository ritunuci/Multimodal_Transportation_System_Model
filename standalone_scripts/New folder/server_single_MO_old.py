# ----------------------------------------------------------------------------------------------------------------------
import numpy as np
import socket
import subprocess
import pickle
import csv
import time  # To add a delay between script runs if necessary
import threading


def run_script():
    subprocess.run(["C:/ProgramData/Anaconda3/python", "run_examples_new.py"])
    time.sleep(5)
    print("\n\n")

def update_csv_with_train_x(values):
    # a, b = map(round, values)
    a, b = values
    a1 = float(a)
    b1 = float(b/1609.34)
    input_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/Input_parameter/input_parameter.csv"
    with open(input_csv_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Update the required values
    rows[1][5] = str(a1)  # "transit_fare ($)" in .csv file
    rows[1][6] = str(b1)  # "microtransit_dist_based_rate ($/meter)" in .csv file

    # Write the updated rows back to the CSV file
    with open(input_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    time.sleep(2)
def collect_output():
    # Output path for debug demand
    output_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/downtown_sd/output_folder" \
                      "/downtown_sd_debug_evaluation_zonal_partition_False.csv"

    # Output path for full demand
    # output_csv_path = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/lemon_grove/output_folder" \
    #                       "/lemon_grove_evaluation_zonal_partition_False.csv"


    with open(output_csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        # csvreader = csv.DictReader(csvfile)
        # for data in csvreader:

        x = rows[3][36]  # "sub_per_T_rider" ($) in .csv file
        y = rows[3][50]  # "tt_mob_lgsm_inc_with_micro" in .csv file

        # x = float(data["sub_per_T_rider"])
        # y = float(data["wghted_acc_emp_15_min"])

        value_1 = -float(x)
        value_2 = float(y)
    return [value_1, value_2]


def handle_client(conn, addr):
    print('Connected by', addr)
    with conn:
        while True:
            data = conn.recv(52097)  # Increased buffer size for larger data
            if not data:
                break
            train_x = pickle.loads(data)  # Deserialize train_x

            all_outputs = []

            for values in train_x:
                # Update CSV with the current value of train_x
                update_csv_with_train_x(values)

                # Run the script
                run_script()
                # time.sleep(5)

                # Collect the output
                print("Collecting the output...")
                output = collect_output()
                all_outputs.append(output)

                # Optionally, add a delay to ensure the script has time to finish
                # time.sleep(1)

            # Serialize and send back the collected output
            serialized_output = pickle.dumps(all_outputs)
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
