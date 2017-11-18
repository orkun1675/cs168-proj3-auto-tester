import os
import sys

import client
import wan

def send_just_over_one_block(middlebox_module, testing_part_1):
    """ Sends a file that contains a bit over on block.

        Verifies that when you send the last packet of this file
        you send out the packetized block and then send out the
        remaining bytes in the buffer.

        To demonstrate, we must make sure that if you sent out 
        the 8000 bytes below, you do not send a fin on the packet
        with bytes 7500 to 8000 but you do send one for the byte
        with the last 500 bytes of the file.

        |____|____|____|____|____|__|   |__|
         1500 3000 4500 6000 7500 8000   500
    """
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
    if testing_part_1:
        filename = "8500a.txt"
    else:
        filename = "just_over_block_pt_2.txt"
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