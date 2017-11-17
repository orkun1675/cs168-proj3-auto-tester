# Author: by Nicole Rasquinha

import os
import sys

import client
import wan

def one_sender_multiple_sends(middlebox_module, testing_part_1):
    total_count = 0
    sent_files = 2

    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Initialize clients 1 which is connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize clients 2 which is connected to middlebox 2.
    client2_address = "5.6.7.8"
    client2 = client.EndHost("client2", client2_address, middlebox2)

    filename = "sample.txt"
    with open(filename, "rb") as input_file:
        input_data = input_file.read()

    # Send the sample file from client 1 to both clients 3 and 4.
    client1.send_file(filename, client2_address)

    # Make sure that the files have the same contents.
    receiver = "client2"
    output_file_name = "{}-{}".format(receiver, filename)
    with open(output_file_name, "rb") as output_file:
        result_data = output_file.read()
    # Remove the output file just created.
    os.remove(output_file_name)

    if input_data == result_data:
        total_count += 1

    # Send same file to client 2 again.
    client1.send_file(filename, client2_address)

    # Make sure that the files have the same contents.
    receiver = "client2"
    output_file_name = "{}-{}".format(receiver, filename)
    with open(output_file_name, "rb") as output_file:
        result_data = output_file.read()
    # Removing the output file just created
    os.remove(output_file_name)

    if input_data == result_data:
        total_count += 1

    if total_count != sent_files:
        raise Exception(
            "send_mutiple_files failed, because the all files" +
            "received did not match the file sent. Files received correctly:" +
            " {} and files sent are: {}\n".format(
                total_count,
                sent_files))