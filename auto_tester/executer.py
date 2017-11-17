import os
import sys
import time
import traceback
from StringIO import StringIO
from helper import bcolors
from constants import *
from auto_tester import BASE_DIR

def clear_log_file():
    try:
        with open(os.path.join(BASE_DIR, LOG_FILE), "w+") as log_file:
            log_file.truncate()
    except OSError:
        pass

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
    try:
        middlebox_module = __import__(middlebox_module_name)
    except ImportError as exc:
        print(bcolors.FAIL + "Could not import '{}'. Are you running this script from the project directory? If not, make sure to specify where your project is using the '--project-dir' flag.".format(middlebox_module_name) + bcolors.ENDC)
        return
    sys.path.append(test_dir)
    test_dir_files = [f for f in os.listdir(test_dir) if os.path.isfile(os.path.join(test_dir, f)) and f.endswith('.py')]

    for test_file_name in test_dir_files:
        file_last_modified = time.ctime(os.path.getmtime(os.path.join(test_dir, test_file_name)))
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
                testing_part_1,
                file_last_modified)
            total_tests += 1

    if passed_tests == total_tests:
        print(bcolors.OKGREEN + "Success! Passed {}/{} tests. StdOut/StdErr saved to {}.".format(passed_tests, total_tests, LOG_FILE) + bcolors.ENDC)
    else:
        print(bcolors.WARNING + "Failed {}/{} tests. Please see '{}' for details.".format(total_tests - passed_tests, total_tests, LOG_FILE) + bcolors.ENDC)

def check_tests_exists(TEST_DIR, definition):
    dir_path = os.path.join(BASE_DIR, TEST_DIR)
    if not os.path.exists(dir_path) or len(os.listdir(dir_path)) < 1:
        print(bcolors.WARNING + "No {} tests exist. Check for updates using the '--update' flag.".format(definition) + bcolors.ENDC)
        return False
    return True    

def run_test(test_function, middlebox_module, for_part_1, file_last_modified):
    old_stdout, old_stderr = sys.stdout, sys.stderr
    buffer = result = StringIO()
    test_start_time = time.time()
    try:
        sys.stdout, sys.stderr = buffer, buffer
        test_function(middlebox_module, for_part_1)
        sys.stdout, sys.stderr = old_stdout, old_stderr
        print("Test " + test_function.__name__ + " passed")
        error_string = None
    except Exception:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        print(bcolors.BOLD + "Test " + test_function.__name__ + bcolors.BOLD + " failed" + bcolors.ENDC)
        error_string = traceback.format_exc()
    test_runtime = round(time.time() - test_start_time, 2)
    with open(os.path.join(BASE_DIR, LOG_FILE), "a+") as log_file:
        log_file.write("###################################\n")
        log_file.write("#  Test Name: {}\n".format(test_function.__name__))
        log_file.write("#  Last Modified: {}\n".format(file_last_modified))
        log_file.write("#  Completed On: {}\n".format(time.ctime()))
        log_file.write("#  Runtime: {}s\n".format(test_runtime))
        log_file.write("###################################\n")
        log_file.write(buffer.getvalue())
        if error_string:
            log_file.write("{}\n".format(error_string))
        else:    
            log_file.write("No errors.\n\n")
    return 1 if error_string is None else 0