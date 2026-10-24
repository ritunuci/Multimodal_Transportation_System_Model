import inte_sys_mode_choice
import get_microtransit_skims as mt
import os

network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'
edges_dir = os.path.join(network_folder, 'edges.csv')

# virtual_stop=75
# virtual_stop_dir = os.path.join(network_folder, 'virtual_stops_%s.csv' % str(virtual_stop))
# virtual_stop_list = mt.read_virtual_stop(virtual_stop_dir)
# demand_node_vir_stop=mt.get_dmd_node_vir_stop(virtual_stop_list,edges_dir)
M_rq_id_list=[1,3,4,5]
# rq_id = 6
for rq_id in range(10):
    print("rq_id", rq_id)
    while (rq_id in M_rq_id_list):
        rq_id += 1
    M_rq_id_list.append(rq_id)
    M_rq_id_list=sorted(M_rq_id_list)
    print("rq_id",rq_id,"M_rq_id_list",M_rq_id_list)
# print(demand_node_vir_stop)
# M_share,D_share,F_share=inte_sys_mode_choice.MNL_choice()

# print("M_share",M_share,"D_share",D_share,"F_share",F_share)