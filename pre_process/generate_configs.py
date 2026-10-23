import os
import csv
from itertools import islice

fleet_size_folder = "D:/Ritun/Siwei_Micro_Transit/FleetPy_SanDiego/studies/example_study/scenarios"
fleet_size_scenario_input = os.path.join(fleet_size_folder, "example_ir_only.csv")
fleet_size_scenario_input_debug = os.path.join(fleet_size_folder, "debug_example_ir_only.csv")

# debug_example_ir_only.csv
study_area = "lemon_grove"  # "downtown_sd"

repositioning=True
# debug_mode=

for study_area in ["lemon_grove", "downtown_sd"]:
    for repositioning in [True,False]:
        for debug_mode in [True,False]:
            if repositioning == True:
                if debug_mode ==False:
                    for fleet_size in [5,10, 15, 20, 30]:
                        if study_area == "lemon_grove":
                            fleet_size_scenario_output = os.path.join(fleet_size_folder,"%s_example_ir_heuristics_repositioning_%s_veh.csv" % (str(study_area), str(fleet_size)))
                        else:
                            fleet_size_scenario_output = os.path.join(fleet_size_folder,"%s_example_ir_heuristics_repositioning_%s_veh.csv" % (str(study_area), str(fleet_size)))
                        with open(fleet_size_scenario_output, 'w+', newline='') as csvfile:
                            # op_module	scenario_name	rq_file	op_fleet_composition

                            fieldnames = ['op_module', 'scenario_name', 'rq_file', 'op_fleet_composition',"op_max_VR_con","forecast_f","op_repo_method","op_repo_horizons","op_repo_timestep"]
                            #op_module	scenario_name	rq_file	op_fleet_composition	op_max_VR_con	forecast_f	op_repo_method	op_repo_horizons	op_repo_timestep
                            #PoolingIRSOnly	example_pool_repo_AM_sc_1	fleetpy_demand.csv	default_vehtype:2	3		AlonsoMoraRepositioning	60


                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()


                            op_module = "PoolingIRSOnly"
                            scenario_name = "example_pool_repo_AM_sc_1"

                            rq_file = "%s_debug_%s_fleetpy_demand.csv" % (str(study_area), str(debug_mode))

                            op_fleet_composition = "default_vehtype:"+str(fleet_size)
                            op_max_VR_con = int(3)
                            op_repo_method = "AlonsoMoraRepositioning"
                            op_repo_horizons = int(60)
                            op_repo_timestep = int(300)

                            #                 print("op_fleet_composition",type(op_fleet_composition),op_fleet_composition,op_fleet_composition[:-2],op_fleet_composition[:-2]+str(fleet_size))
                            writer.writerow({'op_module': op_module, 'scenario_name': scenario_name, 'rq_file': rq_file,
                                             'op_fleet_composition': op_fleet_composition,'op_max_VR_con': op_max_VR_con,
                                             'op_repo_method': op_repo_method,'op_repo_horizons': op_repo_horizons,
                                             'op_repo_timestep': op_repo_timestep})

                        csvfile.close()
                else:
                    for fleet_size in [2, 3, 4]:
                        fleet_size_scenario_output_debug = os.path.join(fleet_size_folder, "%s_debug_example_ir_heuristics_repositioning_%s_veh.csv" % (str(study_area), str(fleet_size)))

                        with open(fleet_size_scenario_output_debug, 'w+', newline='') as csvfile:
                            # op_module	scenario_name	rq_file	op_fleet_composition

                            fieldnames = ['op_module', 'scenario_name', 'rq_file', 'op_fleet_composition',"op_max_VR_con","forecast_f","op_repo_method","op_repo_horizons","op_repo_timestep"]

                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()

                            op_module = "PoolingIRSOnly"
                            scenario_name = "example_pool_repo_AM_sc_1"

                            rq_file = "%s_debug_%s_fleetpy_demand.csv" % (str(study_area), str(debug_mode))

                            op_fleet_composition = "default_vehtype:" + str(fleet_size)
                            op_max_VR_con = int(3)
                            op_repo_method = "AlonsoMoraRepositioning"
                            op_repo_horizons = int(60)
                            op_repo_timestep = int(300)

                            #                 print("op_fleet_composition",type(op_fleet_composition),op_fleet_composition,op_fleet_composition[:-2],op_fleet_composition[:-2]+str(fleet_size))
                            writer.writerow({'op_module': op_module, 'scenario_name': scenario_name, 'rq_file': rq_file,
                                             'op_fleet_composition': op_fleet_composition, 'op_max_VR_con': op_max_VR_con,
                                             'op_repo_method': op_repo_method, 'op_repo_horizons': op_repo_horizons,
                                             'op_repo_timestep': op_repo_timestep})

                        csvfile.close()

            else:
                if debug_mode == False:
                    for fleet_size in [5,10, 15, 20, 30]:
                        if study_area == "lemon_grove":
                            fleet_size_scenario_output = os.path.join(fleet_size_folder, "%s_example_ir_only_%s_veh.csv" % ( str(study_area), str(fleet_size)))
                        else:
                            fleet_size_scenario_output = os.path.join(fleet_size_folder,
                                                                      "%s_example_ir_only_%s_veh.csv" % (
                                                                      str(study_area), str(fleet_size)))
                        with open(fleet_size_scenario_output, 'w+', newline='') as csvfile:
                            # op_module	scenario_name	rq_file	op_fleet_composition

                            fieldnames = ['op_module', 'scenario_name', 'rq_file', 'op_fleet_composition']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()


                            op_module = "PoolingIRSOnly"
                            scenario_name = "example_pool_irsonly_sc_1"

                            rq_file = "%s_debug_%s_fleetpy_demand.csv" % (str(study_area),str(debug_mode))


                            op_fleet_composition = "default_vehtype:" + str(fleet_size)

                            #                 print("op_fleet_composition",type(op_fleet_composition),op_fleet_composition,op_fleet_composition[:-2],op_fleet_composition[:-2]+str(fleet_size))
                            writer.writerow({'op_module': op_module, 'scenario_name': scenario_name, 'rq_file': rq_file,
                                             'op_fleet_composition': op_fleet_composition})

                        csvfile.close()
                else:
                    for fleet_size in [2, 3, 4]:
                        fleet_size_scenario_output_debug = os.path.join(fleet_size_folder, "%s_debug_example_ir_only_%s_veh.csv" % (str(study_area), str(fleet_size)))

                        with open(fleet_size_scenario_output_debug, 'w+', newline='') as csvfile:
                            # op_module	scenario_name	rq_file	op_fleet_composition

                            fieldnames = ['op_module', 'scenario_name', 'rq_file', 'op_fleet_composition']
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()


                                    #             print(data)
                            op_module = "PoolingIRSOnly"
                            scenario_name = "example_pool_irsonly_sc_1"
                            rq_file = "%s_debug_%s_fleetpy_demand.csv" % (str(study_area),str(debug_mode))

                            op_fleet_composition = "default_vehtype:" + str(fleet_size)

                            #                 print("op_fleet_composition",type(op_fleet_composition),op_fleet_composition,op_fleet_composition[:-2],op_fleet_composition[:-2]+str(fleet_size))
                            writer.writerow({'op_module': op_module, 'scenario_name': scenario_name, 'rq_file': rq_file,
                                             'op_fleet_composition': op_fleet_composition})

                        csvfile.close()


