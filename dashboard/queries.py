import os
import awswrangler as wr
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv


def get_config():
    """Get database and S3 configuration."""
    load_dotenv()
    return {
        'database': os.getenv('ATHENA_DATABASE', 'c21_nathan_t3_food_trucks_db'),
        'bucket': os.getenv('S3_BUCKET_NAME'),
        's3_output': f"s3://{os.getenv('S3_BUCKET_NAME')}/athena-results/"
    }


def query_daily_revenue(config):
    """Query daily revenue totals."""
    query = """
    SELECT 
        DATE(at) as date,
        COUNT(*) as transaction_count,
        SUM(total) as total_revenue,
        AVG(total) as avg_transaction_value
    FROM transactions
    GROUP BY DATE(at)
    ORDER BY date
    """
    df = wr.athena.read_sql_query(
        query, database=config['database'], s3_output=config['s3_output'])
    return df


def query_truck_performance(config):
    """Query performance metrics by truck."""
    query = """
    SELECT 
        truck_name,
        COUNT(transaction_id) as total_transactions,
        SUM(total) as total_revenue,
        AVG(total) as avg_transaction_value,
        fsa_rating,
        has_card_reader
    FROM transactions
    GROUP BY truck_name, fsa_rating, has_card_reader
    ORDER BY total_revenue DESC
    """
    df = wr.athena.read_sql_query(
        query, database=config['database'], s3_output=config['s3_output'])
    return df


def query_payment_methods(config):
    """Query revenue by payment method."""
    query = """
    SELECT 
        payment_method,
        COUNT(transaction_id) as transaction_count,
        SUM(total) as total_revenue,
        AVG(total) as avg_transaction_value
    FROM transactions
    GROUP BY payment_method
    ORDER BY total_revenue DESC
    """
    df = wr.athena.read_sql_query(
        query, database=config['database'], s3_output=config['s3_output'])
    return df


def query_hourly_patterns(config):
    """Query revenue patterns by hour of day."""
    query = """
    SELECT 
        HOUR(at) as hour_of_day,
        COUNT(*) as transaction_count,
        SUM(total) as total_revenue,
        AVG(total) as avg_transaction_value
    FROM transactions
    GROUP BY HOUR(at)
    ORDER BY hour_of_day
    """
    df = wr.athena.read_sql_query(
        query, database=config['database'], s3_output=config['s3_output'])
    return df


def query_day_of_week_patterns(config):
    """Query revenue patterns by day of week."""
    query = """
    SELECT 
        DAY_OF_WEEK(at) as day_of_week,
        COUNT(*) as transaction_count,
        SUM(total) as total_revenue,
        AVG(total) as avg_transaction_value
    FROM transactions
    GROUP BY DAY_OF_WEEK(at)
    ORDER BY day_of_week
    """
    df = wr.athena.read_sql_query(
        query, database=config['database'], s3_output=config['s3_output'])
    return df


def query_top_revenue_days(config):
    """Query top 10 revenue days."""
    query = """
    SELECT 
        DATE(at) as date,
        COUNT(*) as transaction_count,
        SUM(total) as total_revenue
    FROM transactions
    GROUP BY DATE(at)
    ORDER BY total_revenue DESC
    LIMIT 10
    """
    df = wr.athena.read_sql_query(
        query, database=config['database'], s3_output=config['s3_output'])
    return df


def save_query_results(outputs_dir='data/outputs'):
    """Execute all queries and save results."""
    Path(outputs_dir).mkdir(parents=True, exist_ok=True)
    config = get_config()

    queries = {
        'daily_revenue': query_daily_revenue,
        'truck_performance': query_truck_performance,
        'payment_methods': query_payment_methods,
        'hourly_patterns': query_hourly_patterns,
        'day_of_week_patterns': query_day_of_week_patterns,
        'top_revenue_days': query_top_revenue_days
    }

    for name, query_func in queries.items():
        print(f"Running query: {name}")
        df = query_func(config)
        output_path = f"{outputs_dir}/{name}.csv"
        df.to_csv(output_path, index=False)
        print(f"✓ Saved {name} ({len(df)} rows)")

    print(f"\n✓ All queries complete. Results saved to {outputs_dir}/")


if __name__ == "__main__":
    save_query_results()
