"""
Lambda function to generate daily HTML report from the data lake.
Queries Athena for transaction data and generates an HTML summary.
"""
import boto3
import pandas as pd
from datetime import datetime, timedelta
import time
import os


def get_aws_clients():
    """Initialize AWS clients."""
    return {
        's3': boto3.client('s3'),
        'athena': boto3.client('athena')
    }


def get_config():
    """Get environment configuration."""
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    return {
        's3_bucket': s3_bucket,
        'athena_database': os.getenv('ATHENA_DATABASE', 'c21_nathan_t3_food_trucks_db'),
        'athena_output': f's3://{s3_bucket}/athena-results/'
    }


def run_athena_query(query, athena_client, config):
    """Execute Athena query and return results as DataFrame."""
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': config['athena_database']},
        ResultConfiguration={'OutputLocation': config['athena_output']}
    )

    query_execution_id = response['QueryExecutionId']

    while True:
        result = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id)
        state = result['QueryExecution']['Status']['State']

        if state == 'SUCCEEDED':
            break
        elif state in ['FAILED', 'CANCELLED']:
            raise Exception(
                f"Query failed: {result['QueryExecution']['Status']['StateChangeReason']}")

        time.sleep(1)

    results = athena_client.get_query_results(
        QueryExecutionId=query_execution_id)

    columns = [col['Label']
               for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]

    def extract_value(field):
        """Extract value from Athena result field."""
        if 'VarCharValue' in field:
            return field['VarCharValue']
        elif 'BigIntValue' in field:
            return field['BigIntValue']
        elif 'IntegerValue' in field:
            return field['IntegerValue']
        elif 'DoubleValue' in field:
            return field['DoubleValue']
        elif 'BooleanValue' in field:
            return field['BooleanValue']
        else:
            return ''

    rows = [[extract_value(field) for field in row['Data']]
            for row in results['ResultSet']['Rows'][1:]]

    return pd.DataFrame(rows, columns=columns)


def get_yesterday_date():
    """Get yesterday's date in YYYY-MM-DD format."""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


def generate_report_data(athena_client, config):
    """Query Athena for report data."""
    report_date = get_yesterday_date()

    summary_query = f"""
    SELECT 
        COUNT(*) as total_transactions,
        ROUND(SUM(CAST(total AS DOUBLE)), 2) as total_revenue,
        ROUND(AVG(CAST(total AS DOUBLE)), 2) as avg_transaction
    FROM transactions
    WHERE CAST(at AS DATE) = DATE '{report_date}'
    """

    trucks_query = f"""
    SELECT 
        truck_name,
        COUNT(*) as transactions,
        ROUND(SUM(CAST(total AS DOUBLE)), 2) as revenue
    FROM transactions
    WHERE CAST(at AS DATE) = DATE '{report_date}'
    GROUP BY truck_name
    ORDER BY revenue DESC
    """

    payment_query = f"""
    SELECT 
        payment_method,
        COUNT(*) as transactions,
        ROUND(SUM(CAST(total AS DOUBLE)), 2) as revenue
    FROM transactions
    WHERE CAST(at AS DATE) = DATE '{report_date}'
    GROUP BY payment_method
    ORDER BY revenue DESC
    """

    summary = run_athena_query(summary_query, athena_client, config)
    trucks = run_athena_query(trucks_query, athena_client, config)
    payments = run_athena_query(payment_query, athena_client, config)

    return {
        'date': report_date,
        'summary': summary,
        'trucks': trucks,
        'payments': payments
    }


def generate_html_report(data):
    """Generate HTML report from data."""
    summary = data['summary'].iloc[0]
    report_date = data['date']

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>T3 Food Trucks Daily Report - {report_date}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .kpi-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .kpi-label {{
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th {{
            background-color: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding: 20px;
            font-size: 0.9em;
        }}
        .highlight {{
            color: #667eea;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚚 T3 Food Trucks</h1>
        <p>Daily Performance Report - {report_date}</p>
    </div>

    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">£{summary['total_revenue']}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Transactions</div>
            <div class="kpi-value">{summary['total_transactions']}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Transaction</div>
            <div class="kpi-value">£{summary['avg_transaction']}</div>
        </div>
    </div>

    <div class="section">
        <h2>Top Performing Trucks</h2>
        <table>
            <thead>
                <tr>
                    <th>Truck Name</th>
                    <th>Transactions</th>
                    <th>Revenue</th>
                </tr>
            </thead>
            <tbody>
"""

    for _, row in data['trucks'].iterrows():
        html += f"""
                <tr>
                    <td>{row['truck_name']}</td>
                    <td>{row['transactions']}</td>
                    <td class="highlight">£{row['revenue']}</td>
                </tr>
"""

    html += """
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Payment Methods</h2>
        <table>
            <thead>
                <tr>
                    <th>Payment Method</th>
                    <th>Transactions</th>
                    <th>Revenue</th>
                </tr>
            </thead>
            <tbody>
"""

    for _, row in data['payments'].iterrows():
        html += f"""
                <tr>
                    <td>{row['payment_method']}</td>
                    <td>{row['transactions']}</td>
                    <td class="highlight">£{row['revenue']}</td>
                </tr>
"""

    html += f"""
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p>T3 Food Trucks Data Analytics Platform</p>
    </div>
</body>
</html>
"""

    return html


def save_report_to_s3(html_report, report_date, s3_client, config):
    """Save HTML report to S3."""
    s3_key = f"reports/daily-report-{report_date}.html"

    s3_client.put_object(
        Bucket=config['s3_bucket'],
        Key=s3_key,
        Body=html_report,
        ContentType='text/html'
    )

    print(f"Report saved to s3://{config['s3_bucket']}/{s3_key}")
    return s3_key


def generate_and_save_report():
    """Main function to generate and save daily report."""
    clients = get_aws_clients()
    config = get_config()

    print("Generating daily report...")

    data = generate_report_data(clients['athena'], config)

    html_report = generate_html_report(data)

    s3_key = save_report_to_s3(
        html_report, data['date'], clients['s3'], config)

    print(f"✓ Report generated successfully for {data['date']}")

    return {
        'report_url': f"s3://{config['s3_bucket']}/{s3_key}",
        'date': data['date'],
        'html_content': html_report
    }


def lambda_handler(event, context):
    """Lambda handler function."""
    try:
        result = generate_and_save_report()

        return {
            'statusCode': 200,
            'message': 'Report generated successfully',
            'report_url': result['report_url'],
            'date': result['date'],
            'html_content': result['html_content']
        }

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return {
            'statusCode': 500,
            'message': 'Error generating report',
            'error': str(e)
        }


if __name__ == "__main__":
    generate_and_save_report()
