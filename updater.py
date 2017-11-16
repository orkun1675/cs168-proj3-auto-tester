import os
import base64
import subprocess
from utils import bcolors
from github import Github, GithubException

BASE_DIR = os.path.dirname(__file__)
OFFICIAL_TEST_DIR = ".test/official/"
OFFICIAL_TEST_DIR_REPO = "projects/proj3_wan_optimizer/tests"
CUSTOM_TEST_DIR = ".test/custom"
CUSTOM_TEST_DIR_REPO = "custom_tests"

OFFICIAL_TESTS = {
    'simple_tests': ['send_less_than_one_block', 'send_exactly_one_block', 'send_exactly_one_block_both_directions'],
    'test_module': ['send_one_file', 'send_multiple_files', 'send_image_file'],
}

def get_official_tests():
    print(bcolors.OKBLUE + "Getting official tests." + bcolors.ENDC)
    github = Github("orkun1675", "Nukro5761")
    organization = github.get_organization("NetSys")
    repository = organization.get_repo("cs168fall17_student")
    if not create_test_directory(os.path.join(BASE_DIR, OFFICIAL_TEST_DIR), "official"):
        return
    result = download_directory(repository, OFFICIAL_TEST_DIR_REPO)
    if not result:
        return
    print(bcolors.OKGREEN + "Official tests fetched from GitHub. ({} new, {} updated)".format(*result) + bcolors.ENDC)

def get_custom_tests():
    print(bcolors.OKBLUE + "Getting custom (student built) tests." + bcolors.ENDC)
    github = Github("orkun1675", "Nukro5761")
    organization = github.get_organization("NetSys")
    repository = organization.get_repo("cs168fall17_student")
    if not create_test_directory(os.path.join(BASE_DIR, CUSTOM_TEST_DIR), "custom"):
        return
    result = download_directory(repository, CUSTOM_TEST_DIR_REPO)
    if not result:
        return
    print(bcolors.OKGREEN + "Custom tests fetched from GitHub. ({} new, {} updated)".format(*result) + bcolors.ENDC)

def create_test_directory(full_path, definition):
    if not os.path.exists(full_path):
        try:
            os.makedirs(full_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                print(bcolors.FAIL + 'Error creating {} test directory {}: {}'.format(definition, full_path, exc) + bcolors.ENDC)
                return False
    return True

def get_git_sha_of_file(file_path):
    result = subprocess.Popen("git hash-object " + file_path, shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    if "fatal" in result:
        return None
    return result

def download_directory(repository, directory_path):
    new_file_count, updated_file_count = 0, 0
    contents = repository.get_dir_contents(directory_path)
    for content in contents:
        if content.type == 'dir':
            download_directory(repository, content.path)
        else:
            try:
                file_path = os.path.join(BASE_DIR, OFFICIAL_TEST_DIR + content.name)
                file_sha = get_git_sha_of_file(file_path)
                if file_sha is None:
                    new_file_count += 1
                elif file_sha != content.sha:
                    updated_file_count += 1
                else:
                    continue
                file_content = repository.get_contents(content.path)
                file_data = base64.b64decode(file_content.content)
                with open(file_path, "w+") as file_out:
                    file_out.write(file_data)
            except (GithubException, IOError) as exc:
                print(bcolors.FAIL + 'Error downloading file {}: {}'.format(content.path, exc) + bcolors.ENDC)
                return False
    return new_file_count, updated_file_count 