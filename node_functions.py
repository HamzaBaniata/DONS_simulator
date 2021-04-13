import sys
import networkx as nx


def construct_MST(NT):
    # find the vertex with minimum weight
    dict_NT = nx.to_dict_of_dicts(NT)
    def Find_node_min_weight():
        min_weight_node = None
        min_weight = sys.maxsize
        for q in Q:
            if weights[q]['distance'] < min_weight:
                min_weight = weights[q]['distance']
                min_weight_node = q
        return min_weight_node

    G = nx.Graph()
    # initial Q
    Q = list(dict_NT.keys())
    G.add_nodes_from(dict_NT.keys())
    weights = {}
    parents = {}
    # initial weight and parent for each node
    for i in range(len(Q)):
        label = Q[i]
        weights[label] = {"distance": sys.maxsize}
        parents[label] = {"parent": None}

    # root node
    weights[Q[0]]['distance'] = 0
    while len(Q) >= 1:
        new_node = Find_node_min_weight ()
        Q.remove(new_node)
        for v in Q:
            if v in NT[new_node] and weights[v]['distance'] > NT[new_node][v]['weight']:
                weights[v]['distance'] = NT[new_node][v]['weight']
                parents[v]['parent'] = new_node

    tot_weight = 0
    for x in parents:
        y = parents[x]['parent']
        if y is not None:
            tot_weight += NT[x][y]['weight']
            w = NT[x][y]['weight']
            G.add_edge(x, y, weight=w)
            G.add_edge(y, x, weight=w)

    return G
    # print(tot_weight)
    # print(nx.to_dict_of_dicts(G, nodelist=list ( NT.keys () ), edge_data=None))


def find_ONS(MST, node_id):
    ONS = {}
    for key in MST:
        if key == node_id:
            for neighbor in MST[key]:
                ONS[neighbor] = MST[key][neighbor]['weight']
            break
    return ONS
