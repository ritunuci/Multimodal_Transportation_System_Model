import mtsm_paths as mtsm


def determine_dolders(study_area):

    # STALE: demand_folder="D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/demand_data/%s" % str(study_area)
    # STALE: final_network_folder="D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/final_network_folder" % str(study_area)
    # STALE: output_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/output_folder" % str(study_area)
    if study_area == "lemon_grove":
        # self-contained data tree mtsm_data/ (docs/progress.md)
        demand_folder = mtsm.LG_DEMAND_DIR
        fleetpy_demand_folder = mtsm.LG_FLEETPY_DEMAND_DIR
        initial_network_folder = mtsm.LG_INITIAL_NETWORK_DIR
        final_network_folder = mtsm.LG_FINAL_NETWORK_DIR
        output_folder = mtsm.LG_OUTPUT_DIR



    return demand_folder,initial_network_folder,final_network_folder,fleetpy_demand_folder,output_folder
