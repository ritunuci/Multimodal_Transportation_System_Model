from collections import OrderedDict

def auto_sp_dict_init():
    agent_auto_visited_temp = OrderedDict()
    agent_auto_time_visited_temp = OrderedDict()
    agent_auto_dist_visited_temp = OrderedDict()
    agent_auto_fare_visited_temp = OrderedDict()
    # auto_gas_visited_temp = OrderedDict()
    agent_auto_path = OrderedDict()
    agent_auto_time_path = OrderedDict()
    agent_auto_time_path_all_ = OrderedDict()



    return agent_auto_visited_temp,agent_auto_time_visited_temp,agent_auto_dist_visited_temp,agent_auto_fare_visited_temp,agent_auto_path,agent_auto_time_path,agent_auto_time_path_all_


def F_transit_sp_dict_init():
    agent_visited_temp_F = OrderedDict()
    agent_time_visited_temp_F = OrderedDict()
    agent_dist_visited_temp_F = OrderedDict()
    agent_fare_visited_temp_F = OrderedDict()
    agent_path_F = OrderedDict()
    agent_time_path_F = OrderedDict()
    agent_transit_time_path_all_F = OrderedDict()
    agent_transit_dist_path_all_F = OrderedDict()



    return agent_visited_temp_F,agent_time_visited_temp_F,agent_dist_visited_temp_F,agent_fare_visited_temp_F,agent_path_F,agent_time_path_F,agent_transit_time_path_all_F,agent_transit_dist_path_all_F