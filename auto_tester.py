import os
import sys
import updater
import executer
import argparse
import getpass
from helper import bcolors
from constants import *

if __name__ == "__main__":
    print(bcolors.BOLD + bcolors.HEADER + "=== {} ===".format(APP_DESCRIPTION) + bcolors.ENDC)

    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
    parser.add_argument(
        "--project-dir", dest="project_dir",
        type=str, action="store",
        help="If your project3 files are in a different directory you can specify it here."
    )
    parser.add_argument(
        "--part", dest="part",
        required=True, type=int, action="store",
        help="Which WanOptimizer to test; use '1' for simple_wan_optimizer and '2' for lbfs_wan_optimizer.")
    parser.add_argument(
        "--update",
        dest="update",
        action="store_true",
        help="Fetch the newest official and custom tests from GitHub.")
    args = parser.parse_args()

    if args.update:
        username = raw_input("GitHub username/email: ")
        password = getpass.getpass(prompt='GitHub password: ')
        success = updater.get_official_tests(username, password)
        success = success and updater.get_custom_tests(username, password)
        if not success:
            print(bcolors.WARNING + "Updater failed." + bcolors.ENDC)
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

    if args.project_dir:
        try:
            project_dir = os.path.expanduser(args.project_dir)
            sys.path.append(project_dir)
            saved_path = os.getcwd()
            os.chdir(project_dir)
        except Exception as exc:
            print(bcolors.FAIL + 'Could not switch to project directory {}: {}'.format(project_dir, exc) + bcolors.ENDC)
            sys.exit()

    executer.run_official(middlebox_module_name, testing_part_1)
    executer.run_custom(middlebox_module_name, testing_part_1)

    if saved_path:
        try:
            os.chdir(saved_path)
        except Exception:
            pass