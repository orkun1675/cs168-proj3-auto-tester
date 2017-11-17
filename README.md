# Auto Tester for CS168 Project 3

This simple python executable helps you test your project before submitting it. It downloads the most recent officially released and student written (custom) tests from GitHub to run them. It aims to be easy to use and maintain. It does not require a list of test names and uses reflection to crawl directories looking for test files to run. All test logs are stored in a single file with useful statistics for easier debugging.

## How to use?

1. Download the executable [auto_tester.zip](https://www.dropbox.com/s/ptx91j2z174j9w5/auto_tester.zip?dl=1) and save it into your project directory
2. Open up the terminal and run the command `python auto_tester.zip --part 1`

## Accepted Flags

Here are a list of flags you can pass in when running the tester.

| Flag          | Values           | Required  |
| ------------- |:-------------:| -----:|
| `--part`        | `1` or `2` | Yes |
| `--update`      | None      |   only if running for first time |
| `--project-dir` | directory string      |    only if running from different directory |


## Contribution

Please open a pull request if you want to submit a student written (custom) test.