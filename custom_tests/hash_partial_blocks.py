# Author: Orkun Duman
# Testing if remaining smaller blocks are hashed
# correctly and used later for compression.
# 
# This addresses:
# https://github.com/NetSys/cs168fall17_student/blob/master/projects/proj3_wan_optimizer/spec.md#what-happens-when-a-stream-of-data-ends-and-a-full-block-of-data-hasnt-been-sent

import os
import sys

import client
import wan

def check_file_integrity(input_file_name, output_file_name):
    with open(input_file_name, "rb") as input_file:
        input_data = input_file.read()
    with open(output_file_name, "rb") as output_file:
        output_data = output_file.read()
    if input_data != output_data:
        raise Exception("The file received did not match the file sent: {}".format(input_file_name))
        return False
    return True

def compute_reduction(input_file_name, wide_area_network):
    with open(input_file_name, "rb") as input_file:
        input_data = input_file.read()
    extra_data_length = len(input_file_name) + len(client.FILENAME_DELIMITER)
    bytes_in_sent_file = len(input_data) + extra_data_length
    bytes_sent = wide_area_network.get_total_bytes_sent()
    reduction = (float(bytes_in_sent_file * 2 - bytes_sent) / float(bytes_in_sent_file * 2))
    return reduction

def hash_partial_blocks(middlebox_module, testing_part_1):
    expected_value_1 = 0.995 #For both parts.
    expected_value_2 = 0.9985 #For both parts.

    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize client connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2 = client.EndHost("client2", client2_address, middlebox2)

    # Define names of files.
    filenames = ["hash_partial_sample_1.txt", "hash_partial_sample_2.txt"]

    # Send both files back and forth.
    for file_id in range(len(filenames)):
        filename = filenames[file_id]
        for count in range(2):
            client1.send_file(filename, client2_address)
            output_file_name = "{}-{}".format("client2", filename)
            if not check_file_integrity(filename, output_file_name):
                return
            os.remove(output_file_name)
            if count == 0:
                # This is a hack! Don't do this!
                wide_area_network._Wan__total_bytes_sent = 0
        reduction_rate = compute_reduction(filename, wide_area_network)
        expected_value = expected_value_1 if file_id == 0 else expected_value_2
        if (reduction_rate < expected_value):
            raise Exception("Reduction ratio should be greater than " +
                            " {}, was {}.".format(expected_value, reduction_rate))