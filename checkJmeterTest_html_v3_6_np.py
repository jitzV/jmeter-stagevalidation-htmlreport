import os
import sys
import pandas as pd
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)


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


# Function to calculate JMeter-style percentiles
def jmeter_percentile(data, percentile):
    sorted_data = np.sort(data)
    index = int(np.ceil((percentile / 100) * len(data))) - 1
    return sorted_data[index]


# Function to calculate metrics from JTL DataFrame
def calculate_metrics(jtl_df, transaction_name, expected_tps, expected_error_rate, expected_avg, expected_90p,
                      expected_99p):
    transaction_data = jtl_df[jtl_df['label'].str.lower() == transaction_name.lower()]
    total_transactions = transaction_data.shape[0]
    failed_transactions = transaction_data[transaction_data['success'] == 'false'].shape[0]

    if total_transactions == 0:
        logging.warning(f"No transactions found for {transaction_name}. Returning 0 for all metrics.")
        return 0, 0, 0, 0, 0, 0

    start_time = transaction_data['timeStamp'].min()
    end_time = transaction_data['timeStamp'].max()
    duration_seconds = (end_time - start_time) / 1000

    tps = total_transactions / duration_seconds if duration_seconds > 0 else 0
    error_rate = failed_transactions / total_transactions if total_transactions > 0 else 0

    average = transaction_data['elapsed'].mean()
    percentile_90 = jmeter_percentile(transaction_data['elapsed'], 90)
    percentile_99 = jmeter_percentile(transaction_data['elapsed'], 99)

    logging.info(f"\nDebug Info for {transaction_name}:")
    logging.info(f" Expected TPS: {expected_tps}")
    logging.info(f" Actual TPS: {tps:.2f}")

    logging.info(f" Expected Error Rate: {expected_error_rate:.2f}")
    logging.info(f" Actual Error Rate: {error_rate:.2f}")

    logging.info(f" Expected Average: {expected_avg:.2f}")
    logging.info(f" Actual Average: {average:.2f}")

    logging.info(f" Expected 90th Percentile: {expected_90p:.2f}")
    logging.info(f" Actual 90th Percentile: {percentile_90:.2f}")

    logging.info(f" Expected 99th Percentile: {expected_99p:.2f}")
    logging.info(f" Actual 99th Percentile: {percentile_99:.2f}")
    
    logging.info(f" Total Transactions: {total_transactions}")
    logging.info(f" Failed Transactions: {failed_transactions}\n")

    return tps, error_rate, total_transactions, average, percentile_90, percentile_99


# Read the JTL file directory from environment variables
jtl_file_dir = os.getenv('JTL_FILE_DIR')

if not jtl_file_dir:
    logging.error("Error: JTL file directory is not set in the environment variables.")
    sys.exit(1)

# Check if the directory exists
if not os.path.exists(jtl_file_dir):
    logging.error(f"Error: Could not find directory {jtl_file_dir}")
    sys.exit(1)

# Get all JTL files in the directory
jtl_files = [f for f in os.listdir(jtl_file_dir) if f.endswith('.jtl') or f.endswith('.csv')]

if not jtl_files:
    logging.error(f"Error: No JTL files found in directory {jtl_file_dir}")
    sys.exit(1)

for jtl_file_name in jtl_files:
    jtl_file_path = os.path.join(jtl_file_dir, jtl_file_name)

    # Load the JTL file into a pandas DataFrame
    jtl_df = pd.read_csv(jtl_file_path)

    # Check for required columns
    required_columns = ['timeStamp', 'success', 'label', 'elapsed']
    missing_columns = [col for col in required_columns if col not in jtl_df.columns]

    if missing_columns:
        logging.error(f"Error: Missing required columns in JTL file {jtl_file_name}: {', '.join(missing_columns)}")
        continue

    # Convert columns to appropriate types if necessary
    jtl_df['timeStamp'] = jtl_df['timeStamp'].astype(int)
    jtl_df['success'] = jtl_df['success'].astype(str).str.lower()
    jtl_df['elapsed'] = jtl_df['elapsed'].astype(float)

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
    html_rows = []

    # Loop through all environment variables
    for var_name, var_value in os.environ.items():
        if var_name.lower().endswith('_tps'):
            transaction_name = var_name[:-4]
            expected_tps = float(var_value)
            expected_error_rate = float(os.getenv(f"{transaction_name}_ErrorRate", 1.0))
            expected_avg = float(os.getenv(f"{transaction_name}_avg", 0))
            expected_90p = float(os.getenv(f"{transaction_name}_90P", 0))
            expected_99p = float(os.getenv(f"{transaction_name}_99P", 0))

            logging.info(f" Expected AVG: {expected_avg:.2f}")

            # Calculate metrics for the current transaction
            tps, error_rate, total_transactions, average, percentile_90, percentile_99 = calculate_metrics(
                jtl_df, transaction_name, expected_tps, expected_error_rate, expected_avg, expected_90p, expected_99p
            )

            # Determine status and colors
            status = "PASSED"
            status_color = "green"
            if (tps < expected_tps or
                    error_rate > expected_error_rate or
                    average > expected_avg or
                    percentile_90 > expected_90p or
                    percentile_99 > expected_99p):
                status = "FAILED"
                status_color = "red"
                pipeline_result = 1

            # Generate the HTML row for this transaction
            html_rows.append(f"""
                <tr>
                    <td>{transaction_name}</td>
                    <td>{total_transactions}</td>
                    <td>{expected_tps}</td>
                    <td class="{'failed-value' if tps < expected_tps else ''}">{tps:.2f}</td>
                    <td>{expected_error_rate:.2f}</td>
                    <td class="{'failed-value' if error_rate > expected_error_rate else ''}">{error_rate:.2f}</td>
                    <td>{expected_avg:.2f}</td>
                    <td class="{'failed-value' if average > expected_avg else ''}">{average:.2f}</td>
                    <td>{expected_90p:.2f}</td>
                    <td class="{'failed-value' if percentile_90 > expected_90p else ''}">{percentile_90:.2f}</td>
                    <td>{expected_99p:.2f}</td>
                    <td class="{'failed-value' if percentile_99 > expected_99p else ''}">{percentile_99:.2f}</td>
                    <td><span class="status-{status.lower()}">{status}</span></td>
                </tr>
            """)

    # Update the style section in the HTML content with these modified CSS rules
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>JMeter Test Report - {jtl_file_name}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
                color: #333;
            }}
            .container {{
                max-width: 95%;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow-x: auto;
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
                table-layout: fixed;
                min-width: 1200px;
            }}
            th, td {{
                padding: 12px 8px;
                text-align: center;
                word-wrap: break-word;
                font-size: 14px;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: 600;
            }}
            .status-passed {{
                background-color: #28a745;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: 600;
                display: inline-block;
                min-width: 70px;
            }}
            .status-failed {{
                background-color: #dc3545;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: 600;
                display: inline-block;
                min-width: 70px;
            }}
            .failed-value {{
                color: #dc3545;
                font-weight: 600;
            }}
            @media screen and (max-width: 1200px) {{
                .container {{
                    padding: 10px;
                    margin: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>JMeter Performance Test Report - {jtl_file_name}</h1>
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
                    <th>Actual TPS</th>
                    <th>Expected Error Rate</th>
                    <th>Actual Error Rate</th>
                    <th>Expected Avg (ms)</th>
                    <th>Actual Avg (ms)</th>
                    <th>Expected 90th (ms)</th>
                    <th>Actual 90th (ms)</th>
                    <th>Expected 99th (ms)</th>
                    <th>Actual 99th (ms)</th>
                    <th>Status</th>
                </tr>
                {''.join(html_rows)}
            </table>
        </div>
    </body>
    </html>
    """

    # Write the HTML report to a file
    report_file_path = os.path.join(jtl_file_dir, f"{os.path.splitext(jtl_file_name)[0]}_report.html")
    with open(report_file_path, "w") as report_file:
        report_file.write(html_content)

    logging.info(f"Report generated at {report_file_path}")

# Exit with the appropriate pipeline result
sys.exit(pipeline_result)
