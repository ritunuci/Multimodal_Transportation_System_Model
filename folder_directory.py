
def determine_dolders(study_area,dt_sd_full_trnst_ntwk,zonal_partition,TRPartA,BayesianOptimization):

    if TRPartA==True:
        if BayesianOptimization==True:
            #D:\Siwei_Micro_Transit\Bayesian_Optimization\demand_data\downtown_sd
            demand_folder="D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/demand_data/%s" % str(study_area)
            if study_area == "downtown_sd":
                #D:\Siwei_Micro_Transit\TR_PartA\Data\downtown_sd\initial_network_folder\initial_full_transit_network
                fleetpy_demand_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/example_demand/matched/example_network"
                if zonal_partition == True:
                    #D:\Siwei_Micro_Transit\Bayesian_Optimization\downtown_sd\initial_network_folder\initial_full_transit_network
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/initial_network_folder/initial_full_transit_network_4_zones" % str(study_area)
                else:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/initial_network_folder/initial_full_transit_network" % str(study_area)
            if study_area == "lemon_grove":
                fleetpy_demand_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network"
                if zonal_partition == True:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/initial_network_folder/initial_network_4_zones" % str(study_area)
                else:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/initial_network_folder/initial_network" % str(study_area)
                    #D:\Siwei_Micro_Transit\TR_PartA\Data\lemon_grove\initial_network_folder\initial_network
            final_network_folder="D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/final_network_folder" % str(study_area)
            output_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/%s/output_folder" % str(study_area)
            #D:\Siwei_Micro_Transit\TR_PartA\Data\lemon_grove\output_folder
        else:
            demand_folder="D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/demand_data/%s" % str(study_area)
            if study_area == "downtown_sd":
                #D:\Siwei_Micro_Transit\TR_PartA\Data\downtown_sd\initial_network_folder\initial_full_transit_network
                fleetpy_demand_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/example_demand/matched/example_network"
                if zonal_partition == True:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/initial_network_folder/initial_full_transit_network_4_zones" % str(study_area)
                else:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/initial_network_folder/initial_full_transit_network" % str(study_area)
            if study_area == "lemon_grove":
                fleetpy_demand_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network"
                if zonal_partition == True:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/initial_network_folder/initial_network_4_zones" % str(study_area)
                else:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/initial_network_folder/initial_network" % str(study_area)
                    #D:\Siwei_Micro_Transit\TR_PartA\Data\lemon_grove\initial_network_folder\initial_network
            final_network_folder="D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/final_network_folder" % str(study_area)
            output_folder = "D:/Ritun/Siwei_Micro_Transit/TR_PartA/Data/%s/output_folder" % str(study_area)
            #D:\Siwei_Micro_Transit\TR_PartA\Data\lemon_grove\output_folder


    else:
        if study_area == "downtown_sd":
            demand_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/demand_folder"
            if dt_sd_full_trnst_ntwk==True:
                if zonal_partition==True:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/initial_full_transit_network_4_zones"
                else:
                    initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/initial_full_transit_network"
            else:
                initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/initial_network"
            final_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/final_network"
            fleetpy_demand_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/example_demand/matched/example_network"
            output_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/output_folder"

        if study_area == "lemon_grove":

            demand_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/demand_folder"
            if zonal_partition==False:
                initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/initial_network"
            else:
                initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/initial_network_4_zones"
            final_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/final_network"
            fleetpy_demand_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/data/demand/lemon_grove_example_demand/matched/lemon_grove_example_network"
            output_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/output_folder"

    return demand_folder,initial_network_folder,final_network_folder,fleetpy_demand_folder,output_folder
