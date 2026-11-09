from pyproj import Transformer
import os
import csv
from math import radians, cos, sin, asin, sqrt
from collections import OrderedDict
import math
import random
import mtsm_paths as mtsm

mile_meter=1609.34


class Link(object):


    def __init__(self, link_id=None, length=0,
                     from_node=0, to_node=0, flow=float(0.0), free_speed=0, free_flow_travel_time=0,
                     link_type=str(0)):
        self.link_id = link_id
        # self.link_id_text=link_id_text
        self.length = length # ft

        self.from_node = from_node
        self.to_node = to_node
        self.timestep = 0
        self.timesteps = 60
        self.timeinterval = 15.0  # seconds
        self.free_speed = free_speed  # ft/sec = 51.33*0.681818(converting fts to mph) = 34.9977 mph, 1.4667 (converting mph to fps)
        self.free_flow_time=free_flow_travel_time
        self._time = None
        self.density = 0.0  # veh/mile (ft to miles = ft*5280.0)
        # self.k_j = 160.002  # if we set this value to decimal, we can have a very low chance that fails to derivative.
        self.k_j = 160.002/5280.0  #0316 Siwei: k_j -> veh/ft
        self.v = 0.  # mph
        self.flow = flow  # vehicles, vph(bpr)
        self.k_t = 0.0
        self.use_exact = False
        self.truncate=False
        self.link_function = "m_Greenshield"  # "bpr", "m_Greenshield","triangularFD"
        self.SO = False
        self.random_init_vol = False

        self.u_max = self.free_speed  # mph
        # self.u_min = 10.0  # mph
        self.u_min = 10.0*1.4667  #Siwei: ft/s 10mph
        self.route = 0
        self.link_type=link_type


class Node(object):
    """
    Class for handling node object in Transportation Networks
 vv
    Parameters
    ----------
    node_id:    int
                identifier of a node

    """

    def __init__(self, node_id=0, node_XCOORD=0, node_YCOORD=0, is_stop_only=False, census_tract=0, node_in_fleetpy=0,
                 is_demand_node=0):

        self.node_id = node_id
        self.node_XCOORD = node_XCOORD
        self.node_YCOORD = node_YCOORD
        self.is_stop_only = is_stop_only
        self.census_tract = census_tract
        self.node_in_fleetpy = node_in_fleetpy
        self.is_demand_node = is_demand_node

def create_network_from_raw_edges(network_file,pre_node_dir,pre_edges_dir):
    # node_dict_fields=["node_index_pre","node_index_fleetpy","census_tract"]
    pre_node_fields = ["node_index", "is_stop_only", "pos_x", "pos_y", "census_tract", "node_in_fleetpy",
                       "is_demand_node"]
    # ['node_index', 'is_stop_only', 'pos_x', 'pos_y']
    # node_index	is_stop_only	pos_x	pos_y

    edge_fields = ["from_node", "to_node", "distance", "travel_time", "source_edge_id"]
    # from_node	to_node	distance	travel_time	source_edge_id
    #specify network file and the output nodes and edges files
    # network_file = os.path.join(network_folder, 'network_edges.csv')
    # pre_node_dir = os.path.join(network_folder, 'pre_nodes.csv')
    # pre_edges_dir = os.path.join(network_folder, 'pre_edges.csv')

    # demand_nodes_dir=os.path.join(network_folder,'demand_nodes.csv')

    census_track_list = []
    demand_nodes = []
    n_demand_links = 0
    with open(pre_node_dir, 'w+', newline='') as csvfile_nodes:
        writer_node = csv.writer(csvfile_nodes, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer_node.writerow(pre_node_fields)

        with open(pre_edges_dir, "w+", newline='') as csvfile_edges:
            writer_edge = csv.writer(csvfile_edges, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer_edge.writerow(edge_fields)
            with open(network_file) as f:
                csvreader = csv.DictReader(f)
                nodes = {}
                links = []
                node_list = []
                for data in csvreader:
                    #             print(data)
                    origin_node = int(data["FNODE"])
                    origin_node_XCOORD = float(data["FRXCOORD"])
                    origin_node_YCOORD = float(data["FRYCOORD"])
                    origin_node_ct = int(data["L_TRACT"])
                    edge_id = data["ROADSEGID"]
                    to_node = int(data["TNODE"])
                    to_node_XCOORD = float(data["TOXCOORD"])
                    to_node_YCOORD = float(data["TOYCOORD"])
                    to_node_ct = int(data["R_TRACT"])
                    #             capacity = float(data[self.link_fields["capacity"]])
                    distance = float(data["LENGTH"]) / 3.28084  # length (meter)

                    if float(data['SPEED']) == 20:
                        n_demand_links += 1
                        if origin_node not in demand_nodes:
                            demand_nodes.append(origin_node)
                        if to_node not in demand_nodes:
                            demand_nodes.append(to_node)

                    if float(data['SPEED']) < 10.00:
                        free_speed = 10.00 / 2.23694
                    else:
                        free_speed = float(data['SPEED']) / 2.23694  # change mph to meter/second
                    name = str(data['RD20FULL'])

                    travel_time = distance / free_speed  # (sec)

                    edge_row_AB = [int(origin_node), int(to_node), float(distance), float(travel_time), float(edge_id)]
                    edge_row_BA = [int(to_node), int(origin_node), float(distance), float(travel_time), float(edge_id)]
                    writer_edge.writerow(edge_row_AB)
                    writer_edge.writerow(edge_row_BA)

                    if origin_node not in nodes:
                        if random.random() < 0.0035:
                            n = Node(node_id=origin_node, node_XCOORD=origin_node_XCOORD,
                                     node_YCOORD=origin_node_YCOORD, is_stop_only=True, census_tract=origin_node_ct)
                        else:
                            n = Node(node_id=origin_node, node_XCOORD=origin_node_XCOORD,
                                     node_YCOORD=origin_node_YCOORD, census_tract=origin_node_ct)
                        nodes[origin_node] = n

                    if to_node not in nodes:
                        if random.random() < 0.0035:
                            n = Node(node_id=to_node, node_XCOORD=to_node_XCOORD, node_YCOORD=to_node_YCOORD,
                                     is_stop_only=True, census_tract=to_node_ct)
                        else:
                            n = Node(node_id=to_node, node_XCOORD=to_node_XCOORD, node_YCOORD=to_node_YCOORD,
                                     census_tract=to_node_ct)
                        nodes[to_node] = n

                    l = Link(link_id=len(links), length=distance,
                             from_node=origin_node, to_node=to_node, flow=float(0.0), free_speed=free_speed)
                    links.append(l)
            f.close()
        csvfile_edges.close()

        nodes_keys = list(nodes.keys())
        nodes_keys.sort()
        sorted_nodes = {i: nodes[i] for i in nodes_keys}
        i = 0
        # print("nodes",sorted_nodes)
        for keys in sorted_nodes:
            #     print("keys",keys,"node_id",nodes[keys].node_id,"node_XCOORD",nodes[keys].node_XCOORD,"node_YCOORD",nodes[keys].node_YCOORD,"is_stop_only",nodes[keys].is_stop_only)
            sorted_nodes[keys].node_in_fleetpy = i
            if keys in demand_nodes:
                sorted_nodes[keys].is_demand_node = 1
            node_row = [int(sorted_nodes[keys].node_id), sorted_nodes[keys].is_stop_only,
                        float(sorted_nodes[keys].node_XCOORD), float(sorted_nodes[keys].node_YCOORD),
                        int(sorted_nodes[keys].census_tract), int(sorted_nodes[keys].node_in_fleetpy),
                        int(sorted_nodes[keys].is_demand_node)]
            if sorted_nodes[keys].census_tract not in census_track_list:
                census_track_list.append(sorted_nodes[keys].census_tract)

            writer_node.writerow(node_row)
            i += 1
    csvfile_nodes.close()

    print("census tract:", len(census_track_list))
    print("number of demand links:", n_demand_links, "number of demand nodes:", len(demand_nodes))
    # return demand_nodes

def write_node_edge_from_pre_node_edge(node_dir,edges_dir,pre_node_dir,pre_edges_dir):
    # pre_node_dir=os.path.join(network_folder,'pre_nodes.csv')
    # pre_edges_dir=os.path.join(network_folder,'pre_edges.csv')
    # Specify node and edge files
    # node_dir = os.path.join(network_folder, 'nodes.csv')
    # edges_dir = os.path.join(network_folder, 'edges.csv')
    # pre_node_fields=["node_index","is_stop_only","pos_x","pos_y","census_tract","node_in_fleetpy","is_demand_node"]
    node_fields = ["node_index", "is_stop_only", "pos_x", "pos_y"]

    ##############################
    # Adjust node files
    ###########################
    fleetpy_demand_node=[]
    with open(node_dir, 'w+', newline='') as csvfile_nodes:
        writer_node = csv.writer(csvfile_nodes, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer_node.writerow(node_fields)

        with open(pre_node_dir) as f_nodes:
            csvreader = csv.DictReader(f_nodes)
            nodes_fleetpy = {}

            for data in csvreader:
                #node_in_fleetpy	is_demand_node
                node_index = int(data["node_index"])
                node_in_fleetpy = int(data["node_in_fleetpy"])
                is_stop_only = data["is_stop_only"]
                pos_x = data["pos_x"]
                pos_y = data["pos_y"]
                is_demand_node = int(data["is_demand_node"])
                if is_demand_node==1:
                    fleetpy_demand_node.append(node_in_fleetpy)
                if node_index not in nodes_fleetpy:
                    nodes_fleetpy[node_index] = node_in_fleetpy

                node_row = [int(node_in_fleetpy), is_stop_only, pos_x, pos_y]
                writer_node.writerow(node_row)

        f_nodes.close()
    csvfile_nodes.close()

    # print("nodes_fleetpy",nodes_fleetpy)

    #########################
    # Adjust edge files
    ##############################

    with open(edges_dir, "w+", newline='') as csvfile_edges:
        writer_edge = csv.writer(csvfile_edges, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        edge_fields = ["from_node", "to_node", "distance", "travel_time", "source_edge_id"]
        writer_edge.writerow(edge_fields)

        with open(pre_edges_dir) as f_edges:
            csvreader = csv.DictReader(f_edges)
            for data in csvreader:
                # edge_fields=["from_node","to_node","distance","travel_time","source_edge_id"]
                from_node = nodes_fleetpy[int(data["from_node"])]
                to_node = nodes_fleetpy[int(data["to_node"])]
                distance = data["distance"]
                travel_time = data["travel_time"]
                source_edge_id = data["source_edge_id"]

                edge_row = [from_node, to_node, distance, travel_time, source_edge_id]
                writer_edge.writerow(edge_row)

        f_edges.close()
    csvfile_edges.close()
    return nodes_fleetpy,fleetpy_demand_node

def coordinate_convert(x1,y1):
    #2230,2875,3500


    transformer = Transformer.from_crs("EPSG:2230", "EPSG:4326")
    lat, lon = transformer.transform(x1, y1)
    return lat, lon

def convert_old_to_new_node_files(old_node_file,new_node_file):
    with open(new_node_file, 'w+', newline='') as f_new:
        fieldnames = ["node_index","is_stop_only","node_lat","node_lon"]
        writer = csv.DictWriter(f_new, fieldnames=fieldnames)
        writer.writeheader()

        with open(old_node_file) as f_old:
            csvreader = csv.DictReader(f_old)
            # depart_time	start	end	trip_id

            for data in csvreader:
                #             print(data)
                node_index = int(data["node_index"])

                is_stop_only = str(data["is_stop_only"])
                pos_x = float(data["pos_x"])
                pos_y = float(data["pos_y"])
                lat, lon=coordinate_convert(pos_x, pos_y)
                # print("node_index",node_index,"pos_x,pos_y",pos_x,pos_y,"lat, lon",lat, lon)
                writer.writerow(
                    {"node_index": node_index, "is_stop_only": is_stop_only,
                     "node_lat": lat,
                     "node_lon": lon})
        f_old.close()
    f_new.close()
    return True

def read_transit_nodes(transit_file):
    transit_nodes_list=[]
    with open(transit_file) as f_old:
        csvreader = csv.DictReader(f_old)
        # stop_id	stop_lat	stop_lon	string_id

        for data in csvreader:
            #             print(data)
            if data["stop_id"]:
            # print("stop_id",int(data["stop_id"]))
                stop_id = int(data["stop_id"])

                if stop_id not in transit_nodes_list:
                    transit_nodes_list.append(stop_id)


            # print("node_index",node_index,"pos_x,pos_y",pos_x,pos_y,"lat, lon",lat, lon)

    f_old.close()
    transit_nodes_list=sorted(transit_nodes_list)
    return transit_nodes_list

def select_transit_nodes(select_area_transit_nodes_list,origin_transit_nodes,new_selected_transit_nodes):
    with open(new_selected_transit_nodes, 'w+', newline='') as f_new:
        fieldnames = ["stop_id", "stop_lat", "stop_lon", "string_id"]
        # stop_id	stop_lat	stop_lon	string_id

        writer = csv.DictWriter(f_new, fieldnames=fieldnames)
        writer.writeheader()

        with open(origin_transit_nodes) as f_old:
            csvreader = csv.DictReader(f_old)
            # stop_id	stop_lat	stop_lon	string_id

            for data in csvreader:
                #             print(data)
                stop_id = int(data["stop_id"])

                stop_lat = float(data["stop_lat"])
                stop_lon = float(data["stop_lon"])
                string_id = str(data["string_id"])
                if stop_id in select_area_transit_nodes_list:
                    # print("node_index",node_index,"pos_x,pos_y",pos_x,pos_y,"lat, lon",lat, lon)
                    writer.writerow(
                        {"stop_id": stop_id, "stop_lat": stop_lat, "stop_lon": stop_lon, "string_id": string_id})
        f_old.close()
    f_new.close()
    return True

def select_transit_links(select_area_transit_nodes_list,original_transit_edges,new_transit_edges):
    with open(new_transit_edges, 'w+', newline='') as f_new:
        fieldnames = ["from_node", "to_node", "distance", "travel_time", "link_type", "route_id", "route_type"]
        writer = csv.DictWriter(f_new, fieldnames=fieldnames)
        writer.writeheader()

        with open(original_transit_edges) as f_old:
            csvreader = csv.DictReader(f_old)
            for data in csvreader:
                from_node = int(data["from_node"])
                to_node = int(data["to_node"])
                distance = float(data["distance"])*mile_meter
                travel_time = float(data["travel_time"])
                link_type = int(data["link_type"])
                route_id = str(data["route_id"])
                route_type = int(data["route_type"])

                if (from_node in select_area_transit_nodes_list) and (to_node in select_area_transit_nodes_list):
                    # print("node_index",node_index,"pos_x,pos_y",pos_x,pos_y,"lat, lon",lat, lon)
                    writer.writerow(
                        {"from_node": from_node, "to_node": to_node, "distance": distance, "travel_time": travel_time,
                         "link_type": link_type, "route_id": route_id, "route_type": route_type})
        f_old.close()
    f_new.close()
    return True


# Python 3 program to calculate Distance Between Two Points on Earth
def calculate_distance(lat1, lat2, lon1, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return (c * r)

def get_transit_node_lat_lon(new_selected_transit_nodes):
    transit_node_lat_lon = OrderedDict()
    transit_walk_nodes=OrderedDict()
    walk_transit_nodes=OrderedDict()
    with open(new_selected_transit_nodes) as f_old:
        csvreader = csv.DictReader(f_old)
        # stop_id	stop_lat	stop_lon	string_id
        #["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
        for data in csvreader:
            stop_id = int(data["stop_id"])
            stop_lat = float(data["stop_lat"])
            stop_lon = float(data["stop_lon"])
            string_id = int(data["string_id"])
            # stop_lon = float(data["stop_lon"])
            transit_node_lat_lon[stop_id]=(stop_lat,stop_lon,string_id)

    f_old.close()
    return transit_node_lat_lon

def get_walk_node_lat_lon(node_file):
    walk_node_lat_lon=OrderedDict()
    with open(node_file) as f_old:
        csvreader = csv.DictReader(f_old)
        # node_index	is_stop_only	node_lat	node_lon
        #["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
        for data in csvreader:
            node_index = int(data["node_index"])
            node_lat = float(data["node_lat"])
            node_lon = float(data["node_lon"])
            walk_node_lat_lon[node_index]=(node_lat,node_lon)

    f_old.close()
    return walk_node_lat_lon

def construct_supernetwork_walk_links(walk_network_edges,road_network_edges):

    with open(walk_network_edges, 'w+', newline='') as f_new:
        fieldnames = ["from_node", "to_node", "distance", "travel_time", "link_type"]
        #from_node	to_node	distance	travel_time	source_edge_id

        writer = csv.DictWriter(f_new, fieldnames=fieldnames)
        writer.writeheader()


        with open(road_network_edges) as f_old:
            csvreader = csv.DictReader(f_old)
            # node_index	is_stop_only	node_lat	node_lon
            #["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
            for data in csvreader:
                from_node = int(data["from_node"])
                to_node = int(data["to_node"])
                dist = float(data["distance"])
                travel_time = dist/1.6   #distance in meter/1.6 meter per second
                link_type = int(0)
                writer.writerow({"from_node": from_node, "to_node": to_node, "distance": dist, "travel_time": travel_time,
                                 "link_type": link_type})
        f_old.close()


    f_new.close()

    return True

def construct_super_network_transit_links(old_transit_edges,super_network_transit_edges):

    with open(super_network_transit_edges, 'w+', newline='') as f_new:
        fieldnames = ["from_node", "to_node", "distance", "travel_time", "link_type","route"] #route
        #from_node	to_node	distance	travel_time	link_type

        #from_node	to_node	distance	travel_time	source_edge_id

        writer = csv.DictWriter(f_new, fieldnames=fieldnames)
        writer.writeheader()

        with open(old_transit_edges) as f_old:
            csvreader = csv.DictReader(f_old)
            # node_index	is_stop_only	node_lat	node_lon
            #["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
            for data in csvreader:
                from_node = int(data["from_node"])
                from_node_F=transit_stop_super_network_dict[from_node]
                to_node = int(data["to_node"])
                to_node_F=transit_stop_super_network_dict[to_node]
                dist = float(data["distance"]) # 1mile=1609.34meter
                travel_time = float(data["travel_time"]) # second
                # travel_time = dist/1.6   #distance in meter/1.6 meter per second
                route_id_str=str(data["route_id"])
                route_id_str_=route_id_str[1:-1]
                try:
                    route_id=int(route_id_str_)
                    # print("route_id:",route_id)
                except:
                    route_id=int(route_id_str_.split(',')[0])
                    # print("route_id:", route_id)
                if route_id==120:
                    route_id=3
                link_type = int(1)
                writer.writerow({"from_node": from_node_F, "to_node": to_node_F, "distance": dist, "travel_time": travel_time,
                                 "link_type": link_type,"route":route_id})
        f_old.close()


    return True

def construct_super_network_microtransit_edges(road_network_edges,super_network_micro_transit_edges):
    with open(super_network_micro_transit_edges, 'w+', newline='') as f_new:
        fieldnames = ["from_node", "to_node", "distance", "travel_time", "link_type"]
        writer = csv.DictWriter(f_new, fieldnames=fieldnames)
        writer.writeheader()

        with open(road_network_edges) as f_old:
            csvreader = csv.DictReader(f_old)
            # node_index	is_stop_only	node_lat	node_lon
            #["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
            for data in csvreader:
                from_node = int(data["from_node"])
                from_node_M=walk_M_tr_node_dict[from_node]
                to_node = int(data["to_node"])
                to_node_M=walk_M_tr_node_dict[to_node]
                dist = float(data["distance"]) # meter
                travel_time = float(data["travel_time"])*1.4 # second

                # travel_time = dist/1.6   #distance in meter/1.6 meter per second
                link_type = int(4)
                writer.writerow({"from_node": from_node_M, "to_node": to_node_M, "distance": dist, "travel_time": travel_time,
                                 "link_type": link_type})
        f_old.close()
    f_new.close()

def construct_vitual_stops(old_node_file,new_network_folder):
    virtual_stop_dict = OrderedDict()
    for percentage in [50, 75, 100]:
        micro_transit_virtual_stops = os.path.join(new_network_folder,"micro_transit_%s_percent_virtual_stops.csv" % str(percentage))
        virtual_stop_dict[percentage] = []
        with open(micro_transit_virtual_stops, 'w+', newline='') as f_new:
            fieldnames = ["node_index", "is_stop_only", "pos_x", "pos_y", "node_in_micro_network"]
            # node_index	is_stop_only	pos_x	pos_y

            writer = csv.DictWriter(f_new, fieldnames=fieldnames)
            writer.writeheader()

            with open(old_node_file) as f_old:
                csvreader = csv.DictReader(f_old)
                # node_index	is_stop_only	node_lat	node_lon
                # ["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
                for data in csvreader:
                    node_index = int(data["node_index"])
                    is_stop_only = str(data["is_stop_only"])
                    pos_x = float(data["pos_x"])
                    pos_y = float(data["pos_y"])
                    node_in_micro_network = walk_M_tr_node_dict[node_index]
                    ran_num = random.random()
                    if ran_num <= (percentage / 100):
                        if node_index not in virtual_stop_dict[percentage]:
                            virtual_stop_dict[percentage].append(node_index)
                        writer.writerow(
                            {"node_index": node_index, "is_stop_only": is_stop_only, "pos_x": pos_x, "pos_y": pos_y,
                             "node_in_micro_network": node_in_micro_network})
            f_old.close()
        f_new.close()
    return virtual_stop_dict

def get_the_virtual_stops(percentage,new_network_folder):
    micro_transit_virtual_stops = os.path.join(new_network_folder,"micro_transit_%s_percent_virtual_stops.csv" % str(percentage))
    virtual_stop_list = []

    with open(micro_transit_virtual_stops) as f_old:
        csvreader = csv.DictReader(f_old)
        # node_index	is_stop_only	node_lat	node_lon
        # ["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
        for data in csvreader:
            node_index = int(data["node_index"])

            if node_index not in virtual_stop_list:
                virtual_stop_list.append(node_index)

    f_old.close()


    return virtual_stop_list

def get_transit_link_route():
    # preprocessing step: Transit_edges_new.csv and new_nodes_transit_network.csv were never copied into mtsm_data/
    mtsm.not_self_contained("get_transit_link_route (preprocessing)")
    # STALE: lemon_grove_network_folder = "D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove/"
    old_super_transit_network = os.path.join(lemon_grove_network_folder,
                                             "super_network_transit_edges.csv")  # without route id
    new_super_transit_network = os.path.join(lemon_grove_network_folder,
                                             "new_super_network_transit_edges.csv")  # adding route id
    # from_node	to_node	distance	travel_time	link_type
    raw_super_transit_network = os.path.join(lemon_grove_network_folder, "Transit_edges_new.csv")  # original node id
    # from_node	to_node	distance	travel_time	link_type	route_id	route_type

    # STALE: lemon_grove_network_folder = "D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove/"
    old_super_transit_network = os.path.join(lemon_grove_network_folder,
                                             "super_network_transit_edges.csv")  # without route id
    new_super_transit_network = os.path.join(lemon_grove_network_folder,
                                             "new_super_network_transit_edges.csv")  # adding route id
    # from_node	to_node	distance	travel_time	link_type
    raw_super_transit_network = os.path.join(lemon_grove_network_folder, "Transit_edges_new.csv")  # original node id
    # from_node	to_node	distance	travel_time	link_type	route_id	route_type

    raw_travel_time_nodes = OrderedDict()
    old_travel_time_nodes = OrderedDict()
    transit_nodes = []
    with open(old_super_transit_network) as f_W:
        csvreader = csv.DictReader(f_W)
        for data in csvreader:
            from_node_o = int(data["from_node"])
            to_node_o = int(data["to_node"])
            travel_time = float(data["travel_time"])
            old_travel_time_nodes[travel_time] = (from_node_o, to_node_o)
            if from_node_o not in transit_nodes:
                transit_nodes.append(from_node_o)
            if to_node_o not in transit_nodes:
                transit_nodes.append(to_node_o)
    f_W.close()

    with open(raw_super_transit_network) as f_W:
        csvreader = csv.DictReader(f_W)
        for data in csvreader:
            from_node_r = int(data["from_node"])
            to_node_r = int(data["to_node"])
            travel_time = float(data["travel_time"])
            raw_travel_time_nodes[travel_time] = (from_node_r, to_node_r)
    f_W.close()

    transit_node_raw_old_dict = OrderedDict()
    transit_node_raw_old_dict_rev = OrderedDict()
    for travel_time in old_travel_time_nodes:
        (from_node_o, to_node_o) = old_travel_time_nodes[travel_time]
        (from_node_r, to_node_r) = raw_travel_time_nodes[travel_time]
        if from_node_r not in transit_node_raw_old_dict:
            transit_node_raw_old_dict[from_node_r] = from_node_o
        if to_node_r not in transit_node_raw_old_dict:
            transit_node_raw_old_dict[to_node_r] = to_node_o

        if from_node_o not in transit_node_raw_old_dict_rev:
            transit_node_raw_old_dict_rev[from_node_o] = from_node_r
        if to_node_o not in transit_node_raw_old_dict_rev:
            transit_node_raw_old_dict_rev[to_node_o] = to_node_r

    # with open(new_super_transit_network, 'w+', newline='') as csvfile:
    #     fieldnames = ["from_node","to_node","distance","travel_time","link_type","route"]
    #     #from_node	to_node	distance	travel_time	link_type
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     with open(old_super_transit_network) as f_W:
    #         csvreader = csv.DictReader(f_W)
    #         for data in csvreader:

    # ="super_network_transit_edges.csv"
    print("transit_nodes", len(transit_nodes))
    print("transit_node_raw_old_dict", len(transit_node_raw_old_dict), "transit_node_raw_old_dict_rev",
          len(transit_node_raw_old_dict_rev))

    transit_link_route = OrderedDict()
    for study_area in ["downtown_sd", "lemon_grove"]:
        transit_link_route[study_area] = OrderedDict()
        if study_area == "downtown_sd":
            # STALE: network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'
            new_transit_network = os.path.join(network_folder, "new_nodes_transit_network.csv")
            old_super_transit_network = os.path.join(lemon_grove_network_folder,
                                                     "super_network_transit_edges.csv")  # without route id
            new_super_transit_network = os.path.join(lemon_grove_network_folder,
                                                     "new_super_network_transit_edges.csv")  # adding route id

        else:
            # STALE: network_folder = 'D:/Ritun/Siwei_Micro_Transit/Ritun/Lemon Grove'
            new_transit_network = os.path.join(network_folder, "Transit_edges_new.csv")
            old_super_transit_network = os.path.join(lemon_grove_network_folder,
                                                     "super_network_transit_edges.csv")  # without route id
            new_super_transit_network = os.path.join(lemon_grove_network_folder,
                                                     "new_super_network_transit_edges.csv")  # adding route id

        #     transit_link_route=OrderedDict()
        if study_area == "downtown_sd":
            with open(new_transit_network) as new_transit_f:
                # from_node	to_node	distance (meters)	travel_time (sec)	route
                csvreader = csv.DictReader(new_transit_f)

                for data in csvreader:
                    from_node = int(data["from_node"])
                    to_node = int(data["to_node"])
                    route = int(data["route"])
                    transit_link_route[study_area][(from_node, to_node)] = route

            new_transit_f.close()
        else:
            with open(new_transit_network) as new_transit_f:
                # from_node	to_node	distance	travel_time	link_type	route_id	route_type
                csvreader = csv.DictReader(new_transit_f)

                for data in csvreader:
                    transit_route = OrderedDict()

                    from_node = int(data["from_node"])
                    to_node = int(data["to_node"])
                    from_node_sp_network = transit_node_raw_old_dict[from_node]
                    to_node_sp_network = transit_node_raw_old_dict[to_node]
                    route_list = str(data["route_id"])
                    route_list = route_list[1:-1]
                    if len(route_list) > 3:
                        transit_route[0] = int(route_list.split(',')[0])
                        transit_route[1] = int(route_list.split(',')[1])
                        transit_link_route[study_area][(from_node_sp_network, to_node_sp_network)] = [transit_route[0],
                                                                                                      transit_route[1]]
                        if len(route_list) > 8:
                            transit_route[2] = int(route_list.split(',')[2])
                            transit_link_route[study_area][(from_node_sp_network, to_node_sp_network)] = [
                                transit_route[0], transit_route[1], transit_route[2]]
                    else:
                        transit_link_route[study_area][(from_node_sp_network, to_node_sp_network)] = int(route_list)
            #                 transit_link_route[study_area][(from_node_sp_network,to_node_sp_network)]=route

            new_transit_f.close()
# return transit_link_route
    return transit_link_route

def construct_initial_network(headway):
    # headway_scenarios = [10, 15, 20, 30, 60]
    headway_scenarios = [headway]
    microtransit_scenarios = ["micro", "non_micro"]
    time_periods = ["AM", "MD", "PM", "EV"]
    mtsm.not_self_contained("construct_initial_network (preprocessing)")
    transit_link_route=get_transit_link_route()
    for study_area in ["downtown_sd", "lemon_grove"]:

        # STALE: if study_area == "lemon_grove":
        # STALE:     initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/initial_network"
        # STALE: else:
        # STALE:     initial_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/initial_network"
        # STALE:     network_folder = 'D:/Ritun/Siwei_Micro_Transit/Data/0719_input'

        for virstop in [50, 75, 100]:
            for headway in headway_scenarios:
                for microtransit in microtransit_scenarios:
                    if microtransit == "micro":
                        #                 for time_period in time_periods:
                        initial_network_scen_dir = os.path.join(initial_network_folder,
                                                                "initial_super_network_%s_hw_%s_virstop_%s.csv" % (
                                                                str(microtransit), str(headway), str(virstop)))
                        #             print("initial_network_scen_dir",initial_network_scen_dir)
                        with open(initial_network_scen_dir, 'w+', newline='') as csvfile:
                            fieldnames = ["from_node", "to_node", "distance", "travel_time", "link_type", "route"]
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()

                            if study_area == "lemon_grove":
                                #                         print("here")
                                WalkMicroFix_network = os.path.join(initial_network_folder,
                                                                    "super_network_%s_virstop_%s_hw_edges.csv" % (
                                                                    str(virstop), str(20)))
                            else:
                                WalkMicroFix_network = os.path.join(network_folder,
                                                                    "walk_micro_fix_transit_edges_%s_virstop.csv" % str(
                                                                        virstop))
                            with open(WalkMicroFix_network) as f_W:
                                csvreader = csv.DictReader(f_W)
                                for data in csvreader:

                                    link_type = int(data["link_type"])
                                    from_node = int(data["from_node"])
                                    to_node = int(data["to_node"])
                                    distance = float(data["distance"])
                                    if link_type == 1:
                                        route = transit_link_route[study_area][(from_node, to_node)]
                                    else:
                                        route = int(-1)

                                    if link_type == 0:
                                        walk_speed = 1.251  # 1.251 meter/secon, 2.8mile/hr
                                        travel_time = distance / walk_speed
                                    else:
                                        travel_time = float(data["travel_time"])

                                    if link_type == 2:
                                        if travel_time > 0:
                                            waiting_time = headway * 60 / 2  # transit stop waiting time according to headway
                                            travel_time = waiting_time
                                    if microtransit == "non_micro":
                                        if link_type == 4 or link_type == 5:
                                            break

                                    writer.writerow({'from_node': from_node, 'to_node': to_node, 'distance': distance,
                                                     'travel_time': travel_time, "link_type": link_type,
                                                     "route": route})

                            f_W.close()
                        csvfile.close()
                    else:
                        initial_network_scen_dir = os.path.join(initial_network_folder,
                                                                "initial_super_network_%s_hw_%s.csv" % (
                                                                str(microtransit), str(headway)))
                        #             print("initial_network_scen_dir",initial_network_scen_dir)
                        with open(initial_network_scen_dir, 'w+', newline='') as csvfile:
                            fieldnames = ["from_node", "to_node", "distance", "travel_time", "link_type", "route"]
                            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                            writer.writeheader()

                            if study_area == "lemon_grove":
                                WalkMicroFix_network = os.path.join(initial_network_folder,
                                                                    "super_network_%s_virstop_%s_hw_edges.csv" % (
                                                                    str(virstop), str(20)))
                            else:
                                WalkMicroFix_network = os.path.join(network_folder,
                                                                    "walk_micro_fix_transit_edges_%s_virstop.csv" % str(
                                                                        virstop))
                            with open(WalkMicroFix_network) as f_W:
                                csvreader = csv.DictReader(f_W)
                                for data in csvreader:

                                    link_type = int(data["link_type"])
                                    from_node = int(data["from_node"])
                                    to_node = int(data["to_node"])
                                    distance = float(data["distance"])

                                    if link_type == 1:
                                        route = transit_link_route[study_area][(from_node, to_node)]
                                    else:
                                        route = int(-1)

                                    if link_type == 0:
                                        walk_speed = 1.251  # 1.251 meter/secon, 2.8mile/hr
                                        travel_time = distance / walk_speed
                                    else:
                                        travel_time = float(data["travel_time"])

                                    if link_type == 2:
                                        if travel_time > 0:
                                            waiting_time = headway * 60 / 2  # transit stop waiting time according to headway
                                            travel_time = waiting_time
                                    if microtransit == "non_micro":
                                        if link_type == 4 or link_type == 5:
                                            break

                                    writer.writerow({'from_node': from_node, 'to_node': to_node, 'distance': distance,
                                                     'travel_time': travel_time, "link_type": link_type,
                                                     "route": route})

                            f_W.close()
                        csvfile.close()

# def update_initial_net_with_bayesian_headway(headway):        #TODO: This is discurded
#     initial_net_folder = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/lemon_grove/initial_network_folder/" \
#                          "initial_network"
#     base_initial_net_file_micro = os.path.join(initial_net_folder, "base_super_network_lemon_grove_micro_hw_10_virstop_75.csv")
#     updated_initial_net_file_micro = os.path.join(initial_net_folder, f"initial_super_network_micro_hw_{headway}_virstop_75.csv")
#
#     base_initial_net_file_non_micro = os.path.join(initial_net_folder,
#                                                "base_super_network_lemon_grove_non_micro_hw_10.csv")
#     updated_initial_net_file_non_micro = os.path.join(initial_net_folder,
#                                             f"initial_super_network_non_micro_hw_{headway}.csv")
#
#     copy_folder = "D:/Ritun/Siwei_Micro_Transit/Data/0719_input/lemon_grove/initial_network"
#
#     with open(updated_initial_net_file_micro, 'w+', newline='') as updated_file_1:
#         fieldnames_1 = ["from_node", "to_node", "distance", "travel_time", "link_type", "route"]
#         writer_1 = csv.DictWriter(updated_file_1, fieldnames=fieldnames_1)
#         writer_1.writeheader()
#
#         with open(base_initial_net_file_micro) as base_file_1:
#             csvreader = csv.DictReader(base_file_1)
#             for data in csvreader:
#                 from_node_1 = int(data["from_node"])
#                 to_node_1 = int(data["to_node"])
#                 distance_1 = float(data["distance"])
#                 travel_time_1 = float(data["travel_time"])
#                 link_type_1 = int(data["link_type"])
#                 route_1 = int(data["route"])
#
#                 if (link_type_1 == 2) and (travel_time_1 != 0):
#                     travel_time_1 = (headway*60)/2
#
#                 writer_1.writerow({'from_node': from_node_1, 'to_node': to_node_1, 'distance': distance_1,
#                                  'travel_time': travel_time_1, "link_type": link_type_1,
#                                  "route": route_1})
#
#     shutil.copy(updated_initial_net_file_micro, copy_folder)
#
#     with open(updated_initial_net_file_non_micro, 'w+', newline='') as updated_file_2:
#         fieldnames_2 = ["from_node", "to_node", "distance", "travel_time", "link_type", "route"]
#         writer_2 = csv.DictWriter(updated_file_2, fieldnames=fieldnames_2)
#         writer_2.writeheader()
#
#         with open(base_initial_net_file_non_micro) as base_file_2:
#             csvreader = csv.DictReader(base_file_2)
#             for data in csvreader:
#                 from_node_2 = int(data["from_node"])
#                 to_node_2 = int(data["to_node"])
#                 distance_2 = float(data["distance"])
#                 travel_time_2 = float(data["travel_time"])
#                 link_type_2 = int(data["link_type"])
#                 route_2 = int(data["route"])
#
#                 if (link_type_2 == 2) and (travel_time_2 != 0):
#                     travel_time_2 = (headway*60)/2
#
#                 writer_2.writerow({'from_node': from_node_2, 'to_node': to_node_2, 'distance': distance_2,
#                                  'travel_time': travel_time_2, "link_type": link_type_2,
#                                  "route": route_2})
#
#     shutil.copy(updated_initial_net_file_non_micro, copy_folder)


def creat_walk_transit_node_match(transit_node_lat_lon,walk_node_lat_lon,transit_walk_nodes_match):
    # walk_transit_node_dict=OrderedDict()
    transit_walk_node_dict = OrderedDict()
    #stop_id	stop_lat	stop_lon	string_id	walk_node

    with open(transit_walk_nodes_match, 'w+', newline='') as csvfile:
        fieldnames = ["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for transit_stop in transit_node_lat_lon:
            (stop_lat,stop_lon,string_id)=transit_node_lat_lon[transit_stop]
            min_dist=math.inf
            min_wlk_node_index=None
            for walk_node in walk_node_lat_lon:
                (node_lat, node_lon)=walk_node_lat_lon[walk_node]
                trst_wlk_dist=calculate_distance(stop_lat, node_lat, stop_lon, node_lon)
                if trst_wlk_dist<=min_dist:
                    min_dist=trst_wlk_dist
                    min_wlk_node_index=walk_node
            transit_walk_node_dict[transit_stop]=min_wlk_node_index
            # walk_transit_node_dict[min_wlk_node_index]=transit_stop

            writer.writerow({'stop_id': transit_stop, 'stop_lat': stop_lat, 'stop_lon': stop_lon,
                             'string_id': string_id, "walk_node": min_wlk_node_index})


    return transit_walk_node_dict

if __name__ == '__main__':
    mtsm.not_self_contained("process_network.py network construction (preprocessing)")

    new_downtown_sd=True
    #Convert the coordinates to lat and lon
    if new_downtown_sd==True:
        # STALE: new_network_folder = "D:/Ritun/Siwei_Micro_Transit/Data/Downtown_SD_New_Transit_network/Road_network"
        old_node_file = os.path.join(new_network_folder, "nodes.csv")
        new_node_file = os.path.join(new_network_folder, "new_nodes_for_fleetpy_input.csv")
    else:
        # STALE: new_network_folder="D:/Ritun/Siwei_Micro_Transit/Ritun/Latest network 2"
        old_node_file=os.path.join(new_network_folder,"nodes_for_fleetpy_input.csv")
        new_node_file = os.path.join(new_network_folder, "new_nodes_for_fleetpy_input.csv")
    # result=convert_old_to_new_node_files(old_node_file, new_node_file)

    if new_downtown_sd==True:
        # STALE: original_transit_folder="D:/Ritun/Siwei_Micro_Transit/Ritun/Jake B network code"
        origin_transit_nodes=os.path.join(original_transit_folder, "node_file.csv")
        selected_transit_nodes=os.path.join(new_network_folder,"Transit_nodes.csv")
        select_area_transit_nodes_list=read_transit_nodes(selected_transit_nodes)

        new_selected_transit_nodes=os.path.join(new_network_folder, "Transit_nodes_new.csv")
        # new_selected_transit_nodes = os.path.join(new_network_folder, "Transit_nodes_new.csv")
        transit_walk_nodes_match = os.path.join(new_network_folder, "Transit_walk_nodes_match.csv")
        result=select_transit_nodes(select_area_transit_nodes_list, origin_transit_nodes, new_selected_transit_nodes)

        # original_transit_edges=os.path.join(original_transit_folder,"network_file_avg_speed_method.csv")#####different transit lines have different speed
        original_transit_edges = os.path.join(original_transit_folder, "network_file.csv")#####different transit lines have same speed
        new_transit_edges=os.path.join(new_network_folder,"Transit_edges_new.csv")
        #from_node	to_node	distance	travel_time	link_type	route_id	route_type
        result = select_transit_links(select_area_transit_nodes_list,original_transit_edges,new_transit_edges)

        # dist=distance(lat1, lat2, lon1, lon2)
        walk_node_lat_lon = OrderedDict()
        # transit_node_lat_lon = OrderedDict()
        transit_walk_nodes = OrderedDict()
        walk_transit_nodes = OrderedDict()
        # get the transit nodes
        transit_node_lat_lon = get_transit_node_lat_lon(new_selected_transit_nodes)
        transit_node_lat_lon = OrderedDict(sorted(transit_node_lat_lon.items()))
        # get the walking nodes
        walk_node_lat_lon = get_walk_node_lat_lon(new_node_file)
        walk_node_lat_lon = OrderedDict(sorted(walk_node_lat_lon.items()))

        transit_walk_node_dict=creat_walk_transit_node_match(transit_node_lat_lon, walk_node_lat_lon, transit_walk_nodes_match)

        road_network_edges = os.path.join(new_network_folder, "edges.csv")
        walk_network_edges = os.path.join(new_network_folder, "super_network_walk_edges.csv")

        result = construct_supernetwork_walk_links(walk_network_edges, road_network_edges)

        transit_node_start_id = len(walk_node_lat_lon)
        transit_stop_super_network_dict = OrderedDict()
        # print("number of walking notes:",len(walk_node_lat_lon))

        pass
    else:
        # STALE: original_transit_folder="D:/Ritun/Siwei_Micro_Transit/Ritun/Jake B network code"
        origin_transit_nodes=os.path.join(original_transit_folder, "node_file.csv")
        selected_transit_nodes=os.path.join(new_network_folder,"Transit_nodes.csv")
        select_area_transit_nodes_list=read_transit_nodes(selected_transit_nodes)
        # print("transit_nodes_list",len(transit_nodes_list))

        new_selected_transit_nodes=os.path.join(new_network_folder, "Transit_nodes_new.csv")
        # new_selected_transit_nodes = os.path.join(new_network_folder, "Transit_nodes_new.csv")
        transit_walk_nodes_match = os.path.join(new_network_folder, "Transit_walk_nodes_match.csv")
        result=select_transit_nodes(select_area_transit_nodes_list, origin_transit_nodes, new_selected_transit_nodes)

        original_transit_edges=os.path.join(original_transit_folder,"network_file.csv")
        # original_transit_edges=os.path.join(original_transit_folder,"network_file_avg_speed_method.csv") #####different transit lines have different speed
        new_transit_edges=os.path.join(new_network_folder,"Transit_edges_new.csv")#####different transit lines have same speed
        #from_node	to_node	distance	travel_time	link_type	route_id	route_type
        result = select_transit_links(select_area_transit_nodes_list,original_transit_edges,new_transit_edges)

        # dist=distance(lat1, lat2, lon1, lon2)
        walk_node_lat_lon=OrderedDict()
        # transit_node_lat_lon = OrderedDict()
        transit_walk_nodes=OrderedDict()
        walk_transit_nodes=OrderedDict()
        #get the transit nodes
        transit_node_lat_lon=get_transit_node_lat_lon(new_selected_transit_nodes)
        transit_node_lat_lon = OrderedDict(sorted(transit_node_lat_lon.items()))
        #get the walking nodes
        walk_node_lat_lon=get_walk_node_lat_lon(new_node_file)
        walk_node_lat_lon = OrderedDict(sorted(walk_node_lat_lon.items()))
        transit_walk_node_dict, walk_transit_node_dict = creat_walk_transit_node_match(transit_node_lat_lon,walk_node_lat_lon,transit_walk_nodes_match)

        road_network_edges = os.path.join(new_network_folder,"edges_for_fleetpy_input.csv")
        walk_network_edges = os.path.join(new_network_folder, "super_network_walk_edges.csv")


        result=construct_supernetwork_walk_links(walk_network_edges, road_network_edges)

        transit_stop_super_network_dict=OrderedDict()
        node_id=16546
        transit_node_start_id = len(walk_node_lat_lon)

    for stop_id in transit_node_lat_lon:
        transit_stop_super_network_dict[stop_id]=transit_node_start_id
        transit_node_start_id+=1
    # print("transit_stop_super_network_keys_list:",transit_stop_super_network_dict.keys())
    # print("transit_stop_super_network_dict",transit_stop_super_network_dict)

    super_network_transit_edges = os.path.join(new_network_folder,"super_network_transit_edges.csv")
    # walk_network_edges = os.path.join(new_network_folder, "walk_network_edges.csv")
    result=construct_super_network_transit_links(new_transit_edges, super_network_transit_edges)

    M_tr_walk_node_dict=OrderedDict()
    walk_M_tr_node_dict=OrderedDict()
    microtransit_node_start_id=transit_node_start_id
    for walk_node in walk_node_lat_lon:
        M_tr_walk_node_dict[microtransit_node_start_id]=walk_node
        walk_M_tr_node_dict[walk_node] = microtransit_node_start_id
        microtransit_node_start_id+=1

    super_network_micro_transit_edges = os.path.join(new_network_folder, "super_network_micro_transit_edges.csv")

    result=construct_super_network_microtransit_edges(road_network_edges, super_network_micro_transit_edges)


    #construct the microtransit virtual stop files (50%, 75%, and 100%)
    virtual_stop_dict=construct_vitual_stops(old_node_file, new_network_folder)

    # virtual_stop_dict=OrderedDict()
    #construct super network
    # final_super_network_edges = os.path.join(new_network_folder, "final_super_network_edges.csv")
    # final_super_network_nodes = os.path.join(new_network_folder, "final_super_network_nodes.csv")
    transit_stop_walk_node_match_dict=OrderedDict()
    with open(transit_walk_nodes_match) as f_old:
        csvreader = csv.DictReader(f_old)
        # node_index	is_stop_only	node_lat	node_lon
        # ["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
        for data in csvreader:
            stop_id = int(data["stop_id"])
            super_stop_id=transit_stop_super_network_dict[stop_id] #convert the original stop id to super network transit stop id

            walk_node = int(data["walk_node"])
            transit_stop_walk_node_match_dict[super_stop_id]=walk_node

    f_old.close()

    final_super_network_nodes = os.path.join(new_network_folder, "super_network_nodes.csv")
    for headway in [10,15,20,30,60]:  #[20,30,60]
        for percentage in [50,75,100]: #[50,75,100]
            final_super_network_edges = os.path.join(new_network_folder, "super_network_%s_virstop_%s_hw_edges.csv" % (str(percentage),str(headway)))

            # virtual_stop_dict[percentage]=[]
            with open(final_super_network_edges, 'w+', newline='') as f_new:
                fieldnames = ["from_node", "to_node", "distance", "travel_time", "link_type","route"]
                #from_node	to_node	distance	travel_time	link_type
                writer = csv.DictWriter(f_new, fieldnames=fieldnames)
                writer.writeheader()
                #read the walking network
                with open(walk_network_edges) as f_old:
                    csvreader = csv.DictReader(f_old)
                    # node_index	is_stop_only	node_lat	node_lon
                    #["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
                    for data in csvreader:
                        from_node = int(data["from_node"])
                        to_node = int(data["to_node"])
                        distance = float(data["distance"])
                        travel_time = float(data["travel_time"])
                        link_type = int(data["link_type"])
                        writer.writerow({"from_node": from_node, "to_node": to_node, "distance": distance, "travel_time": travel_time,
                                         "link_type": link_type,"route":int(-1)})
                f_old.close()
                #read the fixed transit network
                with open(super_network_transit_edges) as f_old:
                    csvreader = csv.DictReader(f_old)
                    # node_index	is_stop_only	node_lat	node_lon
                    # ["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
                    transit_stop_list=[]
                    for data in csvreader:
                        from_node = int(data["from_node"])
                        from_node_walk=transit_stop_walk_node_match_dict[from_node]

                        to_node = int(data["to_node"])
                        to_node_walk = transit_stop_walk_node_match_dict[to_node]
                        distance = float(data["distance"])
                        travel_time = float(data["travel_time"])
                        link_type = int(data["link_type"])
                        route_id = int(data["route"])


                        wait_time_F=headway*60/2
                        writer.writerow({"from_node": from_node, "to_node": to_node, "distance": distance, "travel_time": travel_time,"link_type": link_type,"route":route_id})
                        #write walk to fixed transit connecting link
                        if from_node not in transit_stop_list:
                            transit_stop_list.append(from_node)
                            writer.writerow({"from_node": from_node_walk, "to_node": from_node, "distance": 0, "travel_time": wait_time_F,"link_type": int(2),"route":int(-1)})
                            writer.writerow({"from_node": from_node, "to_node":from_node_walk , "distance": 0, "travel_time": 0,"link_type": int(2),"route":int(-1)})
                        if to_node not in transit_stop_list:
                            transit_stop_list.append(to_node)
                            writer.writerow( {"from_node": to_node_walk, "to_node": to_node, "distance": 0, "travel_time": wait_time_F, "link_type": int(2),"route":int(-1)})
                            writer.writerow( {"from_node": to_node, "to_node": to_node_walk, "distance": 0, "travel_time": 0,  "link_type": int(2),"route":int(-1)})
                    aaa=0

                f_old.close()

                #write the microtransit edges
                with open(super_network_micro_transit_edges) as f_old:
                    csvreader = csv.DictReader(f_old)
                    # node_index	is_stop_only	node_lat	node_lon
                    # ["stop_id", "stop_lat", "stop_lon", "string_id", "walk_node"]
                    virtual_stop_list=[]
                    for data in csvreader:
                        from_node = int(data["from_node"])
                        #M_tr_walk_node_dict[node_id] = walk_node
                        from_node_walk=M_tr_walk_node_dict[from_node]
                        to_node = int(data["to_node"])
                        to_node_walk = M_tr_walk_node_dict[to_node]
                        distance = float(data["distance"])
                        travel_time = float(data["travel_time"])
                        link_type = int(data["link_type"])

                        wait_time_M=180
                        writer.writerow({"from_node": from_node, "to_node": to_node, "distance": distance, "travel_time": travel_time,"link_type": link_type,"route":int(-1)})
                        #write walk to micro transit connecting link
                        if from_node_walk in virtual_stop_dict[percentage]:
                            if from_node_walk not in virtual_stop_list:
                                virtual_stop_list.append(from_node_walk)
                                writer.writerow({"from_node": from_node_walk, "to_node": from_node, "distance": 0, "travel_time": wait_time_M,"link_type": int(5),"route":int(-1)})
                                writer.writerow({"from_node": from_node, "to_node":from_node_walk , "distance": 0, "travel_time": 0,"link_type": int(5),"route":int(-1)})
                        if to_node_walk in virtual_stop_dict[percentage]:
                            if to_node_walk not in virtual_stop_list:
                                virtual_stop_list.append(to_node_walk)
                                writer.writerow( {"from_node": to_node_walk, "to_node": to_node, "distance": 0, "travel_time": wait_time_M, "link_type": int(5),"route":int(-1)})
                                writer.writerow( {"from_node": to_node, "to_node": to_node_walk, "distance": 0, "travel_time": 0,  "link_type": int(5),"route":int(-1)})
                    virtual_stop_list=sorted(virtual_stop_list)
                    aaa=0

                f_old.close()






            f_new.close()


        # x2,y2=coordinate_convert(x1, y1)

    # from pyproj import Proj
    #
    # # p = Proj(proj='utm', zone=10, ellps='WGS84', preserve_units=False)
    # p = Proj(proj='WGS84', zone=10, ellps='EPSG:2230', preserve_units=False)
    # # p = Proj("EPSG:2230")
    # print('x=%12.3f y=%12.3f (feet)' % p(x1, y1))
    # x, y = p(- 117.1546493, 32.71626794)
    # # 32.71626794 - 117.1546493

    # print('x=%9.3f y=%11.3f' % (x, y))


    # print("lat, lon",lat, lon)
