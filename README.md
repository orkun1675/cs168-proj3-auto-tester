# Auto Tester for CS168 Project 3

This simple python executable helps you test your project before submitting it. It downloads the most recent officially released and student written (custom) tests from GitHub to run them. It aims to be easy to use and maintain. It does not require a list of test names and uses reflection to crawl directories looking for test files to run. All test logs are stored in a single file with useful statistics for easier debugging.

## How to use?

1. Make sure you have the Python API for GitHub installed  
  a. using pip: `pip install PyGithub` (or `pip2 install PyGithub`)  
  b. using anaconda: `conda install -c conda-forge pygithub `
2. Download the executable [auto_tester.zip](https://www.dropbox.com/s/ptx91j2z174j9w5/auto_tester.zip?dl=1) and save it into your project directory
3. Open up the terminal and run the command `python auto_tester.zip --part 1`

## Accepted Flags

Here are a list of flags you can pass in when running the tester.

| Flag            | Explanation                              | Values            | Required                                 |
| -------------   | ---------------------------------------  | ----------------  | -----                                    |
| `-h`            | view help for each possible flag         | None              | No                                       |
| `--part`        | specify which part of the project to test| `1` or `2`        | Yes                                      |
| `--update`      | fetch test updates from GitHub           | None              | only if running for first time           |
| `--tests`       | don't run all tests, only the listed ones| space separated list of test names | No                      |
| `--project-dir` | specify where the proj3 folders are      | directory string  | only if running from different directory |
| `--colorless`   | don't use color codes in the terminal    | None              | No                                       |

## Security Concerns

The user is asked for their GitHub credentials when running with the `--update` flag. This is required since the GitHub API heavily limits the number of calls from un-authenticated clients. However, the username and password information is never stored in disk (it is kept in memory). The credentials are used to sign in with the [PyGithub](https://github.com/PyGithub/PyGithub) library which in term uses the [GitHub API v3](https://developer.github.com/v3/). As a result, all calls are made through HTTPS.

## Contribution

Please open a pull request if you want to submit a student written (custom) test.