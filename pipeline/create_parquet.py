import pandas as pd
from pathlib import Path


def create_time_partitioned_parquet():
    """Create time-partitioned parquet files from combined data."""
    df = pd.read_csv('data/clean/combined_data.csv')
    df['at'] = pd.to_datetime(df['at'])
    df['year'] = df['at'].dt.year
    df['month'] = df['at'].dt.month
    df['day'] = df['at'].dt.day

    for (year, month, day), group in df.groupby(['year', 'month', 'day']):
        partition_dir = Path(
            f'data/parquet/year={year}/month={month:02d}/day={day:02d}')
        partition_dir.mkdir(parents=True, exist_ok=True)
        group.drop(['year', 'month', 'day'], axis=1).to_parquet(
            partition_dir / 'transactions.parquet', index=False)
        print(f"✓ Created year={year}/month={month:02d}/day={day:02d}")


def create_dimension_parquet():
    """Create dimension table parquet files."""
    Path('data/parquet/dimensions').mkdir(parents=True, exist_ok=True)
    pd.read_csv('data/clean/trucks_clean.csv').to_parquet(
        'data/parquet/dimensions/trucks.parquet', index=False)
    pd.read_csv('data/clean/payment_methods_clean.csv').to_parquet(
        'data/parquet/dimensions/payment_methods.parquet', index=False)
    print("✓ Created dimension tables")


def create_parquet_files():
    """Main parquet creation pipeline."""
    create_time_partitioned_parquet()
    create_dimension_parquet()


if __name__ == "__main__":
    create_parquet_files()
