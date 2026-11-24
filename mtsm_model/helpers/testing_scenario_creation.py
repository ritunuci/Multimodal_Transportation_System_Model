from collections import OrderedDict
import os

from mtsm_model import config

def scen_create(microtransit_setup_scenarios,virtual_stop_scenarios,operating_periods_scenarios,time_periods,fleet_size_scenarios,headway_scenarios,initial_network_folder,final_network_folder, base_FRT_headway = None, base_frt_headway_file = None):  # Ritun Jan 3
    # base_frt_headway_file: the FRT-only network at the base headway, an input (networks/super_network_frt_base_headway.csv;
    # until 2026-11-24 initial_network/initial_super_network_non_micro_hw_<base_FRT_headway>.csv, which a run at that
    # headway overwrote, I-05)
    initial_super_network_dir = OrderedDict()
    initial_super_network = OrderedDict()
    final_super_network_dir = OrderedDict()
    final_super_network = OrderedDict()
    for microtransit in microtransit_setup_scenarios:
        initial_super_network_dir[microtransit] = OrderedDict()
        initial_super_network[microtransit] = OrderedDict()
        final_super_network_dir[microtransit] = OrderedDict()
        final_super_network[microtransit] = OrderedDict()
        if microtransit == "micro_only":
            for virstop in virtual_stop_scenarios:
                initial_super_network_dir[microtransit][virstop] = OrderedDict()
                initial_super_network[microtransit][virstop] = OrderedDict()
                final_super_network_dir[microtransit][virstop] = OrderedDict()
                final_super_network[microtransit][virstop] = OrderedDict()
                for operating_periods in operating_periods_scenarios:  # fleetsize - influence the cost & mobility
                    M_operating_hrs = config.microtransit_operating_hours(operating_periods)
                    # initial_super_network_dir[microtransit][headway][virstop][M_operating_hrs] = OrderedDict()
                    # initial_super_network[microtransit][headway][virstop][M_operating_hrs] = OrderedDict()
                    final_super_network_dir[microtransit][virstop][M_operating_hrs] = OrderedDict()
                    final_super_network[microtransit][virstop][M_operating_hrs] = OrderedDict()

                    initial_super_network_dir[microtransit][virstop][M_operating_hrs] = os.path.join(initial_network_folder, "initial_super_network_%s_virstop_%s.csv" % (str(microtransit), str(virstop)))  # initial_super_network[microtransit][headway][virstop][time_period]=n_a.read_super_network(initial_super_network_dir)

                    for time_period in time_periods:
                        final_super_network_dir[microtransit][virstop][M_operating_hrs][time_period] = OrderedDict()
                        final_super_network[microtransit][virstop][M_operating_hrs][time_period] = OrderedDict()
                        for fleet_size in fleet_size_scenarios:
                            final_super_network_dir[microtransit][virstop][M_operating_hrs][time_period][
                                fleet_size] = os.path.join(final_network_folder,"final_super_network_%s_fsize_%s_ophr_%s_%s_virstop_%s.csv" % (str(microtransit), str(fleet_size), str(M_operating_hrs),
                                                           str(time_period), str(virstop)))

        else:
            for headway in headway_scenarios:
                initial_super_network_dir[microtransit][headway] = OrderedDict()
                initial_super_network[microtransit][headway] = OrderedDict()
                final_super_network_dir[microtransit][headway] = OrderedDict()
                final_super_network[microtransit][headway] = OrderedDict()
                if microtransit == "micro":
                    for virstop in virtual_stop_scenarios:
                        initial_super_network_dir[microtransit][headway][virstop] = OrderedDict()
                        initial_super_network[microtransit][headway][virstop] = OrderedDict()
                        final_super_network_dir[microtransit][headway][virstop] = OrderedDict()
                        final_super_network[microtransit][headway][virstop] = OrderedDict()
                        for operating_periods in operating_periods_scenarios:  # fleetsize - influence the cost & mobility
                            M_operating_hrs = config.microtransit_operating_hours(operating_periods)
                            # initial_super_network_dir[microtransit][headway][virstop][M_operating_hrs] = OrderedDict()
                            # initial_super_network[microtransit][headway][virstop][M_operating_hrs] = OrderedDict()
                            final_super_network_dir[microtransit][headway][virstop][M_operating_hrs] = OrderedDict()
                            final_super_network[microtransit][headway][virstop][M_operating_hrs] = OrderedDict()

                            initial_super_network_dir[microtransit][headway][virstop][M_operating_hrs] = os.path.join(
                                initial_network_folder, "initial_super_network_%s_hw_%s_virstop_%s.csv" % (
                                str(microtransit), str(headway), str(
                                    virstop)))  # initial_super_network[microtransit][headway][virstop][time_period]=n_a.read_super_network(initial_super_network_dir)

                            for time_period in time_periods:
                                final_super_network_dir[microtransit][headway][virstop][M_operating_hrs][
                                    time_period] = OrderedDict()
                                final_super_network[microtransit][headway][virstop][M_operating_hrs][
                                    time_period] = OrderedDict()
                                for fleet_size in fleet_size_scenarios:
                                    final_super_network_dir[microtransit][headway][virstop][M_operating_hrs][time_period][fleet_size] = os.path.join(final_network_folder,
                                                                                "final_super_network_%s_fsize_%s_ophr_%s_%s_hw_%s_virstop_%s.csv" % (
                                                                                str(microtransit), str(fleet_size),
                                                                                str(M_operating_hrs), str(time_period),
                                                                                str(headway), str(virstop)))
                else:
                    # print("WE ARE HERE!!!!!!!!!")
                    initial_super_network_dir[microtransit][base_FRT_headway] = base_frt_headway_file

    return initial_super_network_dir,initial_super_network,final_super_network_dir,final_super_network