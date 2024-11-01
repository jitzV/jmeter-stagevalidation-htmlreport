import os
import sys
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize results to store HTML rows
html_rows = []

# Function to format duration based on length
def format_duration(seconds):
    if seconds >= 3600:  # More than an hour
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    elif seconds >= 60:  # More than a minute
        minutes = int(seconds // 60)
        sec = int(seconds % 60)
        return f"{minutes}m {sec}s"
    else:  # Less than a minute
        return f"{int(seconds)}s"

# Function to calculate HTTP code counts
def get_http_code_counts(jtl_df):
    if 'responseCode' in jtl_df.columns:
        return jtl_df['responseCode'].value_counts().to_dict()
    return {}

# Function to calculate TPS and error rate from JTL DataFrame
def calculate_metrics(jtl_df, transaction_name, expected_tps, expected_error_rate):
    # Filter the DataFrame for the specified transaction
    transaction_data = jtl_df[jtl_df['label'].str.lower() == transaction_name.lower()]
    total_transactions = transaction_data.shape[0]
    failed_transactions = transaction_data[transaction_data['success'] == 'false'].shape[0]

    if total_transactions == 0:
        logging.warning(f"No transactions found for {transaction_name}. Returning 0 TPS and 0 error rate.")
        return 0, 0, 0

    # Calculate start and end time
    start_time = transaction_data['timeStamp'].min()
    end_time = transaction_data['timeStamp'].max()

    # Calculate duration in seconds
    duration_seconds = (end_time - start_time) / 1000  # Convert milliseconds to seconds
    tps = total_transactions / duration_seconds if duration_seconds > 0 else 0
    error_rate = failed_transactions / total_transactions if total_transactions > 0 else 0

    # Debug information including expected values
    logging.info(f"\nDebug Info for {transaction_name}:")
    logging.info(f"  Expected TPS: {expected_tps}")
    logging.info(f"  Expected Error Rate: {expected_error_rate:.2f}")
    logging.info(f"  Actual TPS: {tps:.2f}")
    logging.info(f"  Actual Error Rate: {error_rate:.2f}")
    logging.info(f"  Total Transactions: {total_transactions}")
    logging.info(f"  Failed Transactions: {failed_transactions}\n")

    return tps, error_rate, total_transactions

# Read the JTL file directory and file name from environment variables
jtl_file_dir = os.getenv('JTL_FILE_DIR')
jtl_file_name = os.getenv('JTL_FILE_NAME')

# Construct the full path to the JTL file
if jtl_file_dir and jtl_file_name:
    jtl_file_path = os.path.join(jtl_file_dir, jtl_file_name)
else:
    logging.error("Error: JTL file directory or file name is not set in the environment variables.")
    sys.exit(1)

# Check if the JTL file exists
if not os.path.exists(jtl_file_path):
    logging.error(f"Error: Could not find JTL file at {jtl_file_path}")
    sys.exit(1)

# Load the JTL file into a pandas DataFrame
jtl_df = pd.read_csv(jtl_file_path)

# Check for required columns
required_columns = ['timeStamp', 'success', 'label']
missing_columns = [col for col in required_columns if col not in jtl_df.columns]

if missing_columns:
    logging.error(f"Error: Missing required columns in JTL file: {', '.join(missing_columns)}")
    sys.exit(1)

# Convert columns to appropriate types if necessary
jtl_df['timeStamp'] = jtl_df['timeStamp'].astype(int)
jtl_df['success'] = jtl_df['success'].astype(str).str.lower()

# Calculate overall test metrics
overall_start_time = pd.to_datetime(jtl_df['timeStamp'].min(), unit='ms').strftime('%Y-%m-%d %H:%M:%S')
overall_end_time = pd.to_datetime(jtl_df['timeStamp'].max(), unit='ms').strftime('%Y-%m-%d %H:%M:%S')
overall_duration_seconds = (jtl_df['timeStamp'].max() - jtl_df['timeStamp'].min()) / 1000
formatted_duration = format_duration(overall_duration_seconds)
overall_threads = len(jtl_df['threadName'].unique()) if 'threadName' in jtl_df.columns else 0

# Calculate HTTP code counts
http_code_counts = get_http_code_counts(jtl_df)

# Format HTTP code counts for display
http_code_html = ""
if http_code_counts:
    for code, count in sorted(http_code_counts.items()):
        http_code_html += f"""
        <div class="metric-item">
            <strong>HTTP {code}:</strong> {count}
        </div>"""
else:
    http_code_html = """
    <div class="metric-item">
        <strong>HTTP Codes:</strong> No data available
    </div>"""

# Initialize the pipeline result as passed
pipeline_result = 0

# Loop through all environment variables
for var_name, var_value in os.environ.items():
    if var_name.lower().endswith('_tps'):
        transaction_name = var_name[:-4]
        expected_tps = float(var_value)
        error_rate_var = transaction_name + '_ErrorRate'
        expected_error_rate = float(os.getenv(error_rate_var, 1.0))

        # Calculate metrics for the current transaction
        tps, error_rate, total_transactions = calculate_metrics(jtl_df, transaction_name, expected_tps, expected_error_rate)

        # Determine status and colors
        if tps >= expected_tps and error_rate <= expected_error_rate:
            status = "PASSED"
            status_color = "green"
        else:
            status = "FAILED"
            status_color = "red"
            pipeline_result = 1

        # Generate the HTML row for this transaction
        html_rows.append(f"""
            <tr>
                <td>{transaction_name}</td>
                <td>{total_transactions}</td>
                <td>{expected_tps}</td>
                <td>{expected_error_rate:.2f}</td>
                <td class="{'failed-value' if tps < expected_tps else ''}">{tps:.2f}</td>
                <td class="{'failed-value' if error_rate > expected_error_rate else ''}">{error_rate:.2f}</td>
                <td><span class="status-{status.lower()}">{status}</span></td>
            </tr>
        """)

# Generate HTML report
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JMeter Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
            margin-bottom: 30px;
        }}
        .metrics-box {{
            background-color: white;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            margin: 20px 0;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-radius: 6px;
            overflow: hidden;
        }}
        th, td {{
            padding: 12px;
            text-align: center;
        }}
        .status-passed {{
            background-color: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .status-failed {{
            background-color: #dc3545;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .failed-value {{
            color: #dc3545;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>JMeter Performance Test Report</h1>
        <div class="metrics-box">
            <div><strong>Start Time:</strong> {overall_start_time}</div>
            <div><strong>End Time:</strong> {overall_end_time}</div>
            <div><strong>Duration:</strong> {formatted_duration}</div>
            <div><strong>Total Threads:</strong> {overall_threads}</div>
            <div><strong>HTTP Response Codes:</strong> {http_code_html}</div>
        </div>
        <table>
            <tr>
                <th>Transaction Name</th>
                <th># of Samples</th>
                <th>Expected TPS</th>
                <th>Expected Error Rate</th>
                <th>Actual TPS</th>
                <th>Actual Error Rate</th>
                <th>Status</th>
            </tr>
            {''.join(html_rows)}
        </table>
    </div>
</body>
</html>
"""

# Write the HTML report to a file
report_file_path = os.path.join(jtl_file_dir, "jmeter_test_report.html")
with open(report_file_path, "w") as report_file:
    report_file.write(html_content)

logging.info(f"Report generated at {report_file_path}")

# Exit with the appropriate pipeline result
sys.exit(pipeline_result)
