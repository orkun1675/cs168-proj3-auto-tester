import os
import sys
import traceback
from helper import bcolors
from constants import *

BASE_DIR = os.path.dirname(__file__)

def run_official(middlebox_module_name, testing_part_1):
    if not check_tests_exists(OFFICIAL_TEST_DIR, "official"):
        return
    print(bcolors.OKBLUE + "Running all official test cases against your code..." + bcolors.ENDC)
    test_dir = os.path.join(BASE_DIR, OFFICIAL_TEST_DIR)
    run_tests_in_dir(middlebox_module_name, testing_part_1, test_dir)
    
def run_custom(middlebox_module_name, testing_part_1):
    if not check_tests_exists(CUSTOM_TEST_DIR, "custom"):
        return
    print(bcolors.OKBLUE + "Running all custom (student built) test cases against your code..." + bcolors.ENDC)
    test_dir = os.path.join(BASE_DIR, CUSTOM_TEST_DIR)
    run_tests_in_dir(middlebox_module_name, testing_part_1, test_dir)
    
def run_tests_in_dir(middlebox_module_name, testing_part_1, test_dir):
    total_tests, passed_tests = 0, 0
    middlebox_module = __import__(middlebox_module_name)
    sys.path.append(test_dir)
    test_dir_files = [f for f in os.listdir(test_dir) if os.path.isfile(os.path.join(test_dir, f)) and f.endswith('.py')]

    for test_file_name in test_dir_files:
        file_module = __import__(os.path.splitext(test_file_name)[0])
        test_file_funcs = [f for f in dir(file_module) if callable(getattr(file_module, f))]
        for test_func_name in test_file_funcs:
            if "__" in test_func_name:
                continue
            test_func = getattr(file_module, test_func_name)
            if not hasattr(test_func, '__code__'):
                continue
            if test_func.__code__.co_argcount != 2:
                continue
            test_func_arg_names = test_func.__code__.co_varnames[:2]
            if test_func_arg_names[0] not in TEST_FUNC_ARG_0 or test_func_arg_names[1] not in TEST_FUNC_ARG_1:
                continue
            passed_tests += run_test(
                test_func,
                middlebox_module,
                testing_part_1)
            total_tests += 1

    if passed_tests == total_tests:
        print(bcolors.OKGREEN + "Success! Passed {}/{} tests.".format(passed_tests, total_tests) + bcolors.ENDC)
    else:
        print(bcolors.WARNING + "Failed {}/{} tests.".format(total_tests - passed_tests, total_tests) + bcolors.ENDC)

def check_tests_exists(TEST_DIR, definition):
    dir_path = os.path.join(BASE_DIR, TEST_DIR)
    num_files = len(os.listdir(dir_path))
    if num_files < 1:
        print(bcolors.WARNING + "No {} tests exist. Check for updates using the '--update' flag.".format(definition) + bcolors.ENDC)
        return False
    return True    

def run_test(test_function, middlebox_module, for_part_1):
    try:
        test_function(middlebox_module, for_part_1)
        print "Test {} passed".format(test_function.__name__)
        return 1
    except Exception:
        print "Test {} failed:\n{}".format(test_function.__name__, traceback.format_exc())
        return 0