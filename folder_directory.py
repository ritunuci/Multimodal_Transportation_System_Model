import mtsm_paths as mtsm


def determine_dolders(study_area,zonal_partition,TRPartA,BayesianOptimization):

    if TRPartA==True:
        if BayesianOptimization==True:
            # STALE: demand_folder="D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/demand_data/%s" % str(study_area)
            # STALE: final_network_folder="D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/final_network_folder" % str(study_area)
            # STALE: output_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/output_folder" % str(study_area)
            if study_area == "lemon_grove":
                # self-contained data tree mtsm_data/ (docs/progress.md); zonal partition is not supported there
                demand_folder = mtsm.LG_DEMAND_DIR
                fleetpy_demand_folder = mtsm.LG_FLEETPY_DEMAND_DIR
                initial_network_folder = mtsm.LG_INITIAL_NETWORK_DIR
                final_network_folder = mtsm.LG_FINAL_NETWORK_DIR
                output_folder = mtsm.LG_OUTPUT_DIR
        else:
            mtsm.not_self_contained("BayesianOptimization=False")
            # STALE: demand_folder="D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/demand_data/%s" % str(study_area)
            # STALE: if study_area == "lemon_grove":
            # STALE:     fleetpy_demand_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network"
            # STALE:     if zonal_partition == True:
            # STALE:         initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/initial_network_folder/initial_network_4_zones" % str(study_area)
            # STALE:     else:
            # STALE:         initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/initial_network_folder/initial_network" % str(study_area)
            # STALE: final_network_folder="D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/final_network_folder" % str(study_area)
            # STALE: output_folder = "D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/output_folder" % str(study_area)
            #D:\Siwei_Micro_Transit\TR_PartA\Data\lemon_grove\output_folder


    else:
        mtsm.not_self_contained("TRPartA=False")
        # STALE: if study_area == "lemon_grove":
        # STALE:
        # STALE:     demand_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/demand_folder"
        # STALE:     if zonal_partition==False:
        # STALE:         initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/initial_network"
        # STALE:     else:
        # STALE:         initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/initial_network_4_zones"
        # STALE:     final_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/final_network"
        # STALE:     fleetpy_demand_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network"
        # STALE:     output_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/output_folder"

    return demand_folder,initial_network_folder,final_network_folder,fleetpy_demand_folder,output_folder
