import mtsm_paths as mtsm


def determine_folders(study_area):

    # STALE: demand_folder="D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/demand_data/%s" % str(study_area)
    # STALE: final_network_folder="D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/final_network_folder" % str(study_area)
    # STALE: output_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/output_folder" % str(study_area)
    # the area's folders in mtsm_data/<area>/ (until 2026-11-24 a branch for study_area "lemon_grove" with the LG_*
    # constants)
    paths = mtsm.area_paths(study_area)
    demand_folder = paths.demand_dir
    fleetpy_demand_folder = paths.fleetpy_demand_dir
    initial_network_folder = paths.initial_network_dir
    final_network_folder = paths.final_network_dir
    output_folder = paths.output_dir



    return demand_folder,initial_network_folder,final_network_folder,fleetpy_demand_folder,output_folder
