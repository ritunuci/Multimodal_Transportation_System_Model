import  os
import csv
from collections import OrderedDict
output_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/output_folder"

evaluation_file = os.path.join(output_folder, "all_scenario_evaluation.csv")
# demand_fil e =os.path.join(demand_folder ,"trips_nodes_study_area_with_beta.csv")



def process_result(transit_mode_ridership,net_cost_dict,transit_mode_share_per_sub_dict,tot_mob_logsum_inc_with_micro_per_sub_dict,
                   total_switch_mode_per_sub_dict,M_avg_wait_time_dict,F_avg_wait_time_dict,avg_walk_time_per_dict):
    with open(evaluation_file) as f:
        csvreader = csv.DictReader(f)
        for data in csvreader:
            headway=data["headway"]
            virtual_stop = data["virtual_stop"]
            fleet_size = data["fleet_size"]
            operating_periods = data["operating_periods"]
            transit_mode_share = float(data["transit_mode_share"])
            transit_mode_ridership[transit_mode_share]=(headway,virtual_stop,fleet_size,operating_periods)
            F_oper_cost = float(data["F_oper_cost"])
            M_oper_cost = float(data["M_oper_cost"])
            revenue = float(data["revenue"])
            net_cost=F_oper_cost+M_oper_cost-revenue
            net_cost_dict[net_cost]=(headway,virtual_stop,fleet_size,operating_periods)
            transit_mode_share_per_sub=transit_mode_share/(net_cost)
            transit_mode_share_per_sub_dict[transit_mode_share_per_sub]=(headway,virtual_stop,fleet_size,operating_periods)
            tot_mob_logsum_inc_with_micro = float(data["tot_mob_logsum_inc_with_micro"])
            tot_mob_logsum_inc_with_micro_per_sub=tot_mob_logsum_inc_with_micro/(net_cost)
            tot_mob_logsum_inc_with_micro_per_sub_dict[tot_mob_logsum_inc_with_micro_per_sub]=(headway,virtual_stop,fleet_size,operating_periods)
            total_switch_mode = float(data["total_switch_mode"])
            total_switch_mode_per_sub = total_switch_mode / (net_cost)
            total_switch_mode_per_sub_dict[total_switch_mode_per_sub]=(headway,virtual_stop,fleet_size,operating_periods)
            M_avg_wait_time = float(data["M_avg_wait_time"])
            M_avg_wait_time_dict[M_avg_wait_time]=(headway,virtual_stop,fleet_size,operating_periods)
            F_avg_wait_time = float(data["F_avg_wait_time"])
            # print("F_avg_wait_time",F_avg_wait_time)
            F_avg_wait_time_dict[F_avg_wait_time] = (headway, virtual_stop, fleet_size, operating_periods)
            avg_walk_time = float(data["avg_walk_time"])
            avg_walk_time_per_dict[avg_walk_time] = (headway, virtual_stop, fleet_size, operating_periods)

        transit_mode_ridership = OrderedDict(sorted(transit_mode_ridership.items(),reverse=True))
        net_cost_dict = OrderedDict(sorted(net_cost_dict.items()))
        transit_mode_share_per_sub_dict = OrderedDict(sorted(transit_mode_share_per_sub_dict.items(),reverse=True))
        tot_mob_logsum_inc_with_micro_per_sub_dict = OrderedDict(sorted(tot_mob_logsum_inc_with_micro_per_sub_dict.items(),reverse=True))
        total_switch_mode_per_sub_dict = OrderedDict(sorted(total_switch_mode_per_sub_dict.items(),reverse=True))
        M_avg_wait_time_dict = OrderedDict(sorted(M_avg_wait_time_dict.items()))
        F_avg_wait_time_dict = OrderedDict(sorted(F_avg_wait_time_dict.items()))
        avg_walk_time_per_dict = OrderedDict(sorted(avg_walk_time_per_dict.items()))

    f.close()

    return transit_mode_ridership, net_cost_dict, transit_mode_share_per_sub_dict,tot_mob_logsum_inc_with_micro_per_sub_dict,total_switch_mode_per_sub_dict, M_avg_wait_time_dict, F_avg_wait_time_dict,avg_walk_time_per_dict







if __name__ == '__main__':
    transit_mode_ridership = OrderedDict()
    net_cost_dict = OrderedDict()
    transit_mode_share_per_sub_dict = OrderedDict()
    tot_mob_logsum_inc_with_micro_per_sub_dict = OrderedDict()
    total_switch_mode_per_sub_dict = OrderedDict()
    M_avg_wait_time_dict = OrderedDict()
    F_avg_wait_time_dict = OrderedDict()
    avg_walk_time_per_dict = OrderedDict()

    transit_mode_ridership, net_cost_dict, transit_mode_share_per_sub_dict, tot_mob_logsum_inc_with_micro_per_sub_dict, total_switch_mode_per_sub_dict, M_avg_wait_time_dict, F_avg_wait_time_dict, avg_walk_time_per_dict=process_result(transit_mode_ridership, net_cost_dict, transit_mode_share_per_sub_dict,
                       tot_mob_logsum_inc_with_micro_per_sub_dict,
                       total_switch_mode_per_sub_dict, M_avg_wait_time_dict, F_avg_wait_time_dict,
                       avg_walk_time_per_dict)
    # microtransit="micro"
    # nodes_emp,MGRA_node_dict=create_nodes_emp_dict(debug=True)
    i=0
    for dictionary in [transit_mode_ridership, net_cost_dict, transit_mode_share_per_sub_dict,tot_mob_logsum_inc_with_micro_per_sub_dict,total_switch_mode_per_sub_dict, M_avg_wait_time_dict, F_avg_wait_time_dict,avg_walk_time_per_dict]:
        # for key, value in dictionary.items():
    #     # print first key
        print("i",i,"dictionary",dictionary,"\n")
        i+=1
            # after getting first key break loop
