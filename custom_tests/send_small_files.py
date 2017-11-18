# Author: Orkun Duman
#
# Multiple tests that focus on sending small files (<= 1 block).

import os
import client
import simple_client
import test_utils
import wan

def compute_bytes_in_file(input_file_name):
    with open(input_file_name, "rb") as input_file:
        input_data = input_file.read()
    extra_data_length = len(input_file_name) + len(client.FILENAME_DELIMITER)
    bytes_in_sent_file = len(input_data) + extra_data_length
    return bytes_in_sent_file

def compute_reduction(bytes_in_sent_file, wide_area_network):
    bytes_sent = wide_area_network.get_total_bytes_sent()
    reduction = (float(bytes_in_sent_file * 2 - bytes_sent) / float(bytes_in_sent_file * 2))
    return reduction

def send_empty_file(middlebox_module, testing_part_1):
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2 = client.EndHost("client2", client2_address, middlebox2)

    # Send a file from client 1 to client 2.
    filename = "send_small_files_1.txt"
    client1.send_file(filename, client2_address)

    # Make sure that the files have the same contents.
    with open(filename, "rb") as input_file:
        input_data = input_file.read()
    output_file_name = "{}-{}".format("client2", filename)
    with open(output_file_name, "rb") as output_file:
        result_data = output_file.read()
    # Remove the output file just created.
    os.remove(output_file_name)

    if input_data != result_data:
        raise Exception(
            ("The file received did not match the file sent. File sent (size {}):\n{}\nFile " +
                "received (size {}):\n{}\n").format(len(input_data), input_data, len(result_data), result_data))

    # Make sure no extra bytes are sent.
    expected_bytes = compute_bytes_in_file(filename)
    sent_bytes = wide_area_network.get_total_bytes_sent()
    if expected_bytes != sent_bytes:
        raise Exception("An incorrect number of bytes were sent over the WAN. Expected {} bytes, but got {} bytes.".format(expected_bytes, sent_bytes))

def send_48_bytes(middlebox_module, testing_part_1):
    SPECIAL_BYTES = "flamed face and disreputable clothes, walked int"

    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(client1_address, middlebox1, client1_output_filename)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(client2_address, middlebox2, client2_output_filename)

    client1.send_data(SPECIAL_BYTES, client2_address)
    client1.send_fin(client2_address)
    # Verify that the correct data was received.
    if not client2.received_fin:
        raise Exception("Client 2 never received a fin")
    test_utils.verify_data_sent_equals_data_received(SPECIAL_BYTES, client2_output_filename)
    os.remove(client2_output_filename)

    client2.send_data(SPECIAL_BYTES, client1_address)
    client2.send_fin(client1_address)
    if not client1.received_fin:
        raise Exception("Client 1 never received a fin")
    test_utils.verify_data_sent_equals_data_received(SPECIAL_BYTES, client1_output_filename)
    os.remove(client1_output_filename)

    achieved_reduction = compute_reduction(len(SPECIAL_BYTES), wide_area_network)
    expected_reduction = 0.29
    if achieved_reduction < expected_reduction:
        raise Exception("Too many bytes were sent over the network. Expected reduction rate was {} but achieved only {}.".format(expected_reduction, achieved_reduction))

def send_one_byte_at_a_time(middlebox_module, testing_part_1):
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1_output_filename = "{}_output".format(client1_address)
    client1 = simple_client.SimpleClient(client1_address, middlebox1, client1_output_filename)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2_output_filename = "{}_output".format(client2_address)
    client2 = simple_client.SimpleClient(client2_address, middlebox2, client2_output_filename)

    sent_data = ""
    for _ in range(80000): # 8KB * 10 bytes so that we get a block end somewhere for part 2
        random_byte = os.urandom(1)
        client1.send_data(random_byte, client2_address)
        sent_data += random_byte
    client1.send_fin(client2_address)
    # Verify that the correct data was received.
    if not client2.received_fin:
        raise Exception("Client 2 never received a fin")
    test_utils.verify_data_sent_equals_data_received(sent_data, client2_output_filename)
    os.remove(client1_output_filename) # I have no idea why we need this.
    os.remove(client2_output_filename)