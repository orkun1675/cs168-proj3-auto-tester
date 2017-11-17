# Author: by Grayson Chao

import os
import sys

import client
import test_utils
import wan

from simple_tests import simple_send_test

def cache_is_not_flow_specific(middlebox_module, testing_part_1):
    """ Checks that a given block appears in the cache at most once.
    First, client 1 sends a file to client 2 and client 3.
    Then both client 2 and client 3 send the file back to client 1.
    If your cache is flow-specific, you will end up with duplicate blocks.
    """
    middlebox1 = middlebox_module.WanOptimizer()
    middlebox2 = middlebox_module.WanOptimizer()
    wide_area_network = wan.Wan(middlebox1, middlebox2)

    # Iniitialize client connected to middlebox 1.
    client1_address = "1.2.3.4"
    client1 = client.EndHost("client1", client1_address, middlebox1)

    # Initialize client A, connected to middlebox 2.
    client2_address = "5.5.5.5"
    client2 = client.EndHost("client2", client2_address, middlebox2)

    # Initialize client B, connected to middlebox 2.
    client3_address = "6.6.6.6"
    client3 = client.EndHost("client3", client3_address, middlebox2)

    filename = "8000B.txt"
    client1.send_file(filename, client2_address)
    client1.send_file(filename, client3_address)

    if len(set(middlebox1.cache.values())) > len(middlebox1.cache.values()):
        raise Exception("SRC middlebox has duplicate cache entries: %s" %
                        middlebox1.cache)

    client2.send_file(filename, client1_address)
    client3.send_file(filename, client1_address)

    if len(set(middlebox2.cache.values())) > len(middlebox2.cache.values()):
        raise Exception("DST middlebox has duplicate cache entries: %s" %
                        middlebox2.cache)