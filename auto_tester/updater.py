import os
import base64
import errno
import subprocess
from helper import bcolors
from github import Github, GithubException
from constants import *

from auto_tester import BASE_DIR

def get_official_tests(username, password):
    print(bcolors.OKBLUE + "Getting official tests." + bcolors.ENDC)
    try:
        github = Github(username, password)
        organization = github.get_organization(OFFICIAL_REPO_ORG)
        repository = organization.get_repo(OFFICIAL_REPO_NAME)
    except GithubException as exc:
        print(bcolors.FAIL + 'Error authenticating with the GitHub API: {}'.format(exc) + bcolors.ENDC)
        return False
    if not create_test_directory(os.path.join(BASE_DIR, OFFICIAL_TEST_DIR), "official"):
        return False
    result = download_directory(repository, OFFICIAL_REPO_DIR, OFFICIAL_TEST_DIR)
    if not result:
        return False
    print(bcolors.OKGREEN + "Official tests fetched from GitHub. ({} new, {} updated)".format(*result) + bcolors.ENDC)
    return True

def get_custom_tests(username, password):
    print(bcolors.OKBLUE + "Getting custom (student built) tests." + bcolors.ENDC)
    try:
        github = Github(username, password)
        organization = github.get_user(CUSTOM_REPO_USER)
        repository = organization.get_repo(CUSTOM_REPO_NAME)
    except GithubException as exc:
        print(bcolors.FAIL + 'Error authenticating with the GitHub API: {}'.format(exc) + bcolors.ENDC)
        return False
    if not create_test_directory(os.path.join(BASE_DIR, CUSTOM_TEST_DIR), "custom"):
        return
    result = download_directory(repository, CUSTOM_REPO_DIR, CUSTOM_TEST_DIR)
    if not result:
        return
    print(bcolors.OKGREEN + "Custom tests fetched from GitHub. ({} new, {} updated)".format(*result) + bcolors.ENDC)
    return True

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
    git_command = ["git", "hash-object", file_path]
    sp = subprocess.Popen(git_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    if err:
        return None
    return out.strip()

def download_directory(repository, directory_path, local_path):
    new_file_count, updated_file_count = 0, 0
    contents = repository.get_dir_contents(directory_path)
    delete_extra_files(local_path, [content.name for content in contents if content.type != 'dir'])
    for content in contents:
        if content.type == 'dir':
            download_directory(repository, content.path, local_path)
        else:
            try:
                file_path = os.path.join(BASE_DIR, local_path + content.name)
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

def delete_extra_files(local_path, file_names):
    delete_counter = 0
    dir_path = os.path.join(BASE_DIR, local_path)
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            if not file_name.endswith(".pyc") and file_name not in file_names:
                os.remove(file_path)
                delete_counter += 1
    if delete_counter > 0:
        print("{} old test file(s) deleted from {}.".format(delete_counter, local_path))