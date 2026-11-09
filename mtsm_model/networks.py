"""Read the super-networks of an iteration (restructuring step 6, docs/entry_script_refactor_plan.md).

Moved unchanged from run_examples_new_parking.py.

"""
import network_algorithms as n_a
from mtsm_model import config


def read_iteration_networks(area, scen, iteration, converged):
    """Read the networks the travelers use in this iteration into initial_super_network / final_super_network:
    in iteration 0 the initial super-network with microtransit, later the final ones that the previous iteration
    updated with FleetPy's results (per time period); and the fixed-route-only network at the base headway.
    area: scenarios.StudyArea, scen: scenarios.Scenario."""
    microtransit_run, headway, virstop = scen.microtransit_run, scen.headway, scen.virstop
    M_operating_hrs, fleet_size, operating_periods = scen.M_operating_hrs, scen.fleet_size, scen.operating_periods
    time_periods = area.time_periods
    initial_super_network, initial_super_network_dir = area.initial_super_network, area.initial_super_network_dir
    final_super_network, final_super_network_dir = area.final_super_network, area.final_super_network_dir

    if microtransit_run == "micro_only":
        for time_period in time_periods:
            if iteration == 0:
                initial_super_network[microtransit_run][virstop][M_operating_hrs] = n_a.read_super_network(initial_super_network_dir[microtransit_run][virstop][M_operating_hrs])
            else:
                final_super_network[microtransit_run][virstop][M_operating_hrs][time_period][fleet_size]=n_a.read_super_network(final_super_network_dir[microtransit_run][virstop][M_operating_hrs][time_period][fleet_size])
    elif microtransit_run=="micro":
        for time_period in time_periods:
            if iteration == 0:
                #[microtransit][headway][virstop][M_operating_hrs][time_period]
                initial_super_network[microtransit_run][headway][virstop][M_operating_hrs] = n_a.read_super_network(initial_super_network_dir[microtransit_run][headway][virstop][M_operating_hrs])
            else:
                try:
                    final_super_network[microtransit_run][headway][virstop][M_operating_hrs][time_period][fleet_size]=n_a.read_super_network(final_super_network_dir[microtransit_run][headway][virstop][M_operating_hrs][time_period][fleet_size])
                except:
                    raise Exception("iteration",iteration,"converged",converged,"....headway",headway, "(mins),", "microtransit", microtransit_run,"; virtual_stop:", virstop, "(%),", "time_period", time_period,"; fleet_size:", fleet_size, "(veh)," ,"; operating_periods:", operating_periods,";")
    initial_super_network["non_micro"][
        config.BASE_FRT_HEADWAY] = n_a.read_super_network(
        initial_super_network_dir["non_micro"][
            config.BASE_FRT_HEADWAY])
