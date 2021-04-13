import network_constructor
import node_functions
import json
import random
import threading
import message_controller
import file_manager


def done():
    print('Percentage of nodes who received the test message so far:')
    while True:
        number_of_done_nodes = 0
        for node in range(data['number_of_nodes']):
            msg_received_already = file_manager.read_field_in_file(f'temporary/{node}.json', 'msg_received')
            if msg_received_already:
                number_of_done_nodes += 1
        if number_of_done_nodes == data['number_of_nodes']:
            file_manager.update_field_in_file('temporary/keep_working.json', 'keep_working', False)
            break
        else:
            print(str(number_of_done_nodes * 100 /data['number_of_nodes']) + ' %')
            print('please hold.. simulation is still running!')


def analyze(the_network):
    number_of_redundant_msgs = 0
    finality_time = 0
    for node in the_network:
        number_of_redundant_msgs += file_manager.read_field_in_file(f'temporary/{node}.json', 'num_of_redundant_msgs')
        delivery_time = file_manager.read_field_in_file(f'temporary/{node}.json', 'message_delivery_time')
        if delivery_time > finality_time:
            finality_time = delivery_time
    print(f'Total number of redundant messages = {number_of_redundant_msgs}')
    print(f'It would take a total of {finality_time} ms to deliver the message to all nodes from the source node')


def worker(node_id, NT, NS_criteria):
    keep_working = True
    while keep_working:
        new_messages = message_controller.get_message(node_id, NT)
        for message in new_messages:
            # print(f'{node_id} says: I received a new message.')
            msg_received = file_manager.read_field_in_file(f'temporary/{node_id}.json', 'msg_received')
            if msg_received:
                number_of_msg_received = file_manager.read_field_in_file(f'temporary/{node_id}.json', 'num_of_redundant_msgs')
                file_manager.update_field_in_file(f'temporary/{node_id}.json', 'num_of_redundant_msgs', number_of_msg_received+1)
            else:
                file_manager.update_field_in_file(f'temporary/{node_id}.json', 'msg_received', True)
            message_controller.send_message(message, NT, NS_criteria, node_id)
        keep_working = file_manager.read_field_in_file('temporary/keep_working.json', 'keep_working')


def return_NS_criteria(k):
    if k == 0:
        return "neighbors belonging to nodes' ONSs "
    if k == 1:
        return "neighbors having the least RTT"
    if k == 2:
        return "randomly selected neighbors"


file_manager.clean_directory()
with open('simulation_parameters.json', 'r') as file:
    data = json.load(file)
network = network_constructor.construct_network()
MST = node_functions.construct_MST(network)
number_of_nodes = data['number_of_nodes']
for i in range(number_of_nodes):
    network.nodes[i]['MST'] = MST
    network.nodes[i]['ONS'] = node_functions.find_ONS(MST, i)
    if not network.nodes[i]['ONS']:
        print('ONS is empty for node {i+1}')
print('Network is ready to test..!')
source_node = random.randint(0, number_of_nodes-1)
print('Source node is randomly selected: node ' + str(source_node))
file_manager.write_file('temporary/keep_working.json', {'keep_working': True})
for k in range(3):
    threads = []
    network_constructor.get_network_ready(network)
    NOW = input("next?(Y/N)")
    if NOW in ['Y', 'y']:
        print(f"The test message will now be sent by the preselected random node with {return_NS_criteria(k)} ")
        print('simulation started... messages are being shared between nodes. Please wait..!')
        message_controller.send_message({'message': 'random_text',
                                         'total_propagation_time': 0}, network, k, source_node)
        file_manager.update_field_in_file('temporary/keep_working.json', 'keep_working', True)
        checker_thread = threading.Thread(target=done)
        checker_thread.start()
        threads.append(checker_thread)
        for i in range(number_of_nodes):
            thread = threading.Thread(target=worker, args=(i, network, k,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    print("All nodes have successfully received the message now.")
    analyze(network)
print('done')
