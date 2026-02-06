import os
import pymysql
import pandas as pd
from dotenv import load_dotenv


def get_db_connection():
    """Establish database connection."""
    load_dotenv()
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )


def extract_tables():
    """Extract tables from database to CSV files."""
    connection = get_db_connection()
    os.makedirs('data/raw', exist_ok=True)

    tables = ['DIM_Truck', 'DIM_Payment_Method', 'FACT_Transaction']
    for table in tables:
        df = pd.read_sql(f"SELECT * FROM {table}", connection)
        df.to_csv(f'data/raw/{table}.csv', index=False)
        print(f"✓ Saved {table}")

    connection.close()


if __name__ == "__main__":
    extract_tables()
