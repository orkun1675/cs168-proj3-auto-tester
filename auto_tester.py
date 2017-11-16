import updater
from utils import bcolors

if __name__ == "__main__":
    print(bcolors.BOLD + bcolors.HEADER + "=== Auto Tester v0.1 ===" + bcolors.ENDC)
    updater.get_official_tests()
    updater.get_custom_tests()