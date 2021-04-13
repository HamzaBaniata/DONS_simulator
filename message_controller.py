import sys
import random
import file_manager

already_send_message_to = set()


def get_message(node_id, simulation_network):
    received_messages = []
    path = f'temporary/{node_id}.json'
    while simulation_network.nodes[node_id]['received_msgs'].qsize() != 0:
        received_messages.append(simulation_network.nodes[node_id]['received_msgs'].get())
    total_propagation_time = file_manager.read_field_in_file(path, 'message_delivery_time')
    for message in received_messages:
        if message['total_propagation_time'] > total_propagation_time:
            file_manager.update_field_in_file(path, 'message_delivery_time', message['total_propagation_time'])
    return received_messages


def send_message(message, simulation_network, NS_criteria, sender_id):
    neighbors_to_share_msg_with = select_neighbors(simulation_network, NS_criteria, sender_id)
    for key in neighbors_to_share_msg_with:
        if NS_criteria == 0 and key not in already_send_message_to:
            modified_message = message
            modified_message['total_propagation_time'] += neighbors_to_share_msg_with[key]
            simulation_network.nodes[key]['received_msgs'].put(modified_message)
            already_send_message_to.add(key)
        if NS_criteria in [1, 2]:
            modified_message = message
            modified_message['total_propagation_time'] += neighbors_to_share_msg_with[key]
            simulation_network.nodes[key]['received_msgs'].put(modified_message)


def select_neighbors(network, NS_criteria, sender_id):
    my_neighbors = network.nodes[sender_id]['registered_neighbors']
    if NS_criteria == 0:
        return network.nodes[sender_id]['ONS']
    if NS_criteria == 1:
        least_RTT = sys.maxsize
        selected_neighbor = None
        for neighbor in my_neighbors:
            message_received = file_manager.read_field_in_file(f'temporary/{neighbor}.json', 'msg_received')
            if my_neighbors[neighbor] < least_RTT and not message_received:
                least_RTT = my_neighbors[neighbor]
                selected_neighbor = neighbor
        if selected_neighbor is None:
            return select_neighbors(network, 2, sender_id)
        else:
            return {selected_neighbor: least_RTT}
    if NS_criteria == 2:
        list_of_neighbors = list(my_neighbors.keys())
        random_neighbor = random.choice(list_of_neighbors)
        neighbor_weight = my_neighbors[random_neighbor]
        return {random_neighbor: neighbor_weight}

