import os
BASE_DIR = os.getcwd()
import sys
import updater
import executer
import argparse
import getpass
from helper import bcolors
from constants import *

def main():
    BASE_DIR = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]

    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
    parser.add_argument(
        "--part",
        dest="part",
        required=True,
        type=int,
        help="Which WanOptimizer to test; use '1' for simple_wan_optimizer and '2' for lbfs_wan_optimizer.")
    parser.add_argument(
        "--update",
        dest="update",
        action="store_true",
        help="Fetch the newest official and custom tests from GitHub.")
    parser.add_argument(
        "--project-dir",
        dest="project_dir",
        type=str,
        help="If your project3 files are in a different directory you can specify it here."
    )
    parser.add_argument(
        "--tests",
        dest="tests",
        nargs='*',
        help="Specify the names of tests you want to run (instead of running all tests).")
    parser.add_argument(
        "--colorless",
        dest="colorless",
        action="store_true",
        help="Disable the use of color codes when printing to the console.")
    args = parser.parse_args()

    if args.colorless:
        bcolors.disable()
    print(bcolors.BOLD + bcolors.HEADER + "=== {} ===".format(APP_DESCRIPTION) + bcolors.ENDC)

    if args.update:
        print("In order to download tests using the GitHub API we need your credentials. These will not be saved to disk.")
        username = raw_input(bcolors.BOLD + "GitHub username/email: " + bcolors.ENDC)
        password = getpass.getpass(prompt=bcolors.BOLD + 'GitHub password: ' + bcolors.ENDC)
        success = updater.get_official_tests(username, password)
        success = success and updater.get_custom_tests(username, password)
        if not success:
            print(bcolors.WARNING + "Updater failed." + bcolors.ENDC)
            sys.exit()
    else:
        if not os.path.exists(os.path.join(BASE_DIR, OFFICIAL_TEST_DIR)) or not os.path.exists(os.path.join(BASE_DIR, CUSTOM_TEST_DIR)):
            print(bcolors.FAIL + "Local tests files not found. Make sure to fetch them using the '--update' flag." + bcolors.ENDC)
            sys.exit()

    if args.part == 1:
        middlebox_module_name = 'simple_wan_optimizer'
        testing_part_1 = True
    elif args.part == 2:
        middlebox_module_name = 'lbfs_wan_optimizer'
        testing_part_1 = False
    else:
        print(bcolors.FAIL + "The type argument can either be '1' or '2' for part1 and part2 of the project respectively." + bcolors.ENDC)
        sys.exit()

    saved_path = False
    if args.project_dir:
        try:
            project_dir = os.path.expanduser(args.project_dir)
            sys.path.append(project_dir)
            saved_path = os.getcwd()
            os.chdir(project_dir)
        except Exception as exc:
            print(bcolors.FAIL + 'Could not switch to project directory {}: {}'.format(project_dir, exc) + bcolors.ENDC)
            sys.exit()
    else:
        sys.path.append(BASE_DIR)

    if args.tests is not None:
        for i in range(len(args.tests)):
            if args.tests[i].endswith(".py"):
                args.tests[i] = args.tests[i][:-3]

    executer.clear_log_file()
    executer.run_official(middlebox_module_name, testing_part_1, args.tests)

    try:
        custom_test_dir = os.path.join(BASE_DIR, CUSTOM_TEST_DIR)
        os.chdir(custom_test_dir)
    except Exception as exc:
        print(bcolors.FAIL + 'Could not switch to custom test directory {}: {}'.format(custom_test_dir, exc) + bcolors.ENDC)
        sys.exit()
    
    executer.run_custom(middlebox_module_name, testing_part_1, args.tests)

    if saved_path:
        try:
            os.chdir(saved_path)
        except Exception:
            pass