# jmeter-stagevalidation-htmlreport
This script processes a JMeter JTL (log) file to generate a comprehensive HTML performance test report. 

Features:
1. Read Avg, 90P, 99P, TPS, Error Rate from envirnment property and compare against actuals from JTL File. These metrics need to be present for script to run
2. Read Threshold from envirnment property and applies to Response time metrics.
3. Generates HTML Report
4. Sends 0 or 1 to pipeline stage to pass or fail the stage
