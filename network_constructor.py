import networkx as nx
import json
from itertools import combinations
import random
from multiprocessing import Queue
import file_manager


def construct_network():
    with open('simulation_parameters.json', 'r') as file:
        data = json.load(file)
    number_of_nodes = data['number_of_nodes']
    network_model = data['network_model(1:ER,2:BA)']
    parameter = data['parameter (ER:0<p<=1,BA:1<=m<n)']
    constructed_network = None
    connected = False
    while not connected:
        if network_model == 1:
            constructed_network = construct_ER_network(number_of_nodes, float(parameter))
        if network_model == 2:
            constructed_network = construct_BA_network(number_of_nodes, int(parameter))
        connected = nx.is_connected(constructed_network)
    print('connected?: ' + str(connected))
    print('[SUCCESS] Network is built')
    print(constructed_network.name)
    return constructed_network


def construct_ER_network(number_of_nodes, probability_of_edges):
    network = nx.Graph()
    network.name = 'Erdös – Rényi(ER)'
    for i in range(number_of_nodes):
        network.add_node(i)
        network.nodes[i]['registered_neighbors'] = {}
        network.nodes[i]['ONS'] = {}
        network.nodes[i]['received_msgs'] = Queue()
        network.nodes[i]['alive'] = True
        network.nodes[i]['MST'] = []
    for u, v in combinations(network, 2):
        if random.random() < probability_of_edges:
            if u != v:
                network.add_edge(u, v, weight=random.randint(1, 100))
                network.nodes[u]['registered_neighbors'][v] = network.edges[u, v]['weight']
                network.nodes[v]['registered_neighbors'][u] = network.edges[u, v]['weight']
    get_network_ready(network)
    return network


def construct_BA_network(number_of_nodes, parameter):
    network = nx.barabasi_albert_graph(number_of_nodes, parameter)
    network.name = 'Barabási – Albert(BA)'
    for i in range(number_of_nodes):
        network.nodes[i]['registered_neighbors'] = {}
        network.nodes[i]['ONS'] = {}
        network.nodes[i]['received_msgs'] = Queue()
        network.nodes[i]['alive'] = True
        network.nodes[i]['MST'] = []
    get_network_ready(network)
    for u, v in combinations(network, 2):
        if network.has_edge(u, v) and 'weight' not in network.edges[u, v]:
            network.edges[u, v]['weight'] = random.randint(1, 100)
            network.nodes[u]['registered_neighbors'][v] = network.edges[u, v]['weight']
            network.nodes[v]['registered_neighbors'][u] = network.edges[u, v]['weight']
    return network


def get_network_ready(network):
    with open('simulation_parameters.json', 'r') as file:
        data = json.load(file)
    number_of_nodes = data['number_of_nodes']
    clear_properties = {'msg_received': False,
                        'num_of_redundant_msgs': 0,
                        'message_delivery_time': 0}
    for i in range(number_of_nodes):
        path = f'temporary/{i}.json'
        file_manager.write_file(path, clear_properties)
    return network
