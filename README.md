<<<<<<< HEAD
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
=======
# jmeter-stagevalidation-htmlreport
This script processes a JMeter JTL (log) file to generate a comprehensive HTML performance test report. 

Features:
1. Read Avg, 90P, 99P, TPS, Error Rate from envirnment property and compare against actuals from JTL File. These metrics need to be present for script to run
2. Read Threshold from envirnment property and applies to Response time metrics.
3. Generates HTML Report
4. Sends 0 or 1 to pipeline stage to pass or fail the stage
>>>>>>> 2cfff83e205cf1267f01dae2952b4dd80e5efdfc
