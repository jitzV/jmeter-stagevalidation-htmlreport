# JMeter Report Project

## Installation

1. Clone the repository:
    ```sh
    git clone <repository_url>
    cd 14_PythonJmeterProject
    ```

2. Install the required dependencies:
    ```sh
    pip install .
    ```

## Usage

To generate the JMeter report, run the following command:
```sh
generate-jmeter-report
```

This will execute the `main` function in the `jmeter_report.report_generator` module.

## Environment Variables

Ensure the following environment variables are set before running the script:

- `JTL_FILE_DIR`: The directory where your JTL files are located.
- `JTL_THRESHOLD_PCT`: The threshold percentage for validation.

Example:
```sh
export JTL_FILE_DIR=/path/to/jtl/files
export JTL_THRESHOLD_PCT=10
```

On Windows:
```cmd
set JTL_FILE_DIR=d:\path\to\jtl\files
set JTL_THRESHOLD_PCT=10
```


-- Run unit test - 
python -m unittest discover -s /d:/_MyLearnings/PycharmProjects/14_PythonJmeterProject/tests

--Run program
generate-jmeter-report