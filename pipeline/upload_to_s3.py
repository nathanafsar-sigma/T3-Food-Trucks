import os
import awswrangler as wr
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv


def get_bucket_name():
    """Get S3 bucket name from environment."""
    load_dotenv()
    return os.getenv('S3_BUCKET_NAME')


def upload_time_partitioned_data(bucket_name):
    """Uploads time-partitioned parquet files to S3."""
    parquet_files = list(
        Path('data/parquet').glob('year=*/month=*/day=*/transactions.parquet'))

    for local_file in parquet_files:
        parts = local_file.parts
        year_idx = next(i for i, p in enumerate(
            parts) if p.startswith('year='))
        year, month, day = parts[year_idx], parts[year_idx +
                                                  1], parts[year_idx + 2]

        s3_path = f"s3://{bucket_name}/inputs/transactions/{year}/{month}/{day}/transactions.parquet"
        df = pd.read_parquet(local_file)
        wr.s3.to_parquet(df=df, path=s3_path, index=False)
        print(f"✓ Uploaded {year}/{month}/{day}")


def upload_dimension_tables(bucket_name):
    """Uploads dimension table parquet files to S3."""
    for local_file in Path('data/parquet/dimensions').glob('*.parquet'):
        s3_path = f"s3://{bucket_name}/inputs/dimensions/{local_file.name}"
        df = pd.read_parquet(local_file)
        wr.s3.to_parquet(df=df, path=s3_path, index=False)
        print(f"✓ Uploaded {local_file.name}")


def upload_to_s3():
    """Main upload pipeline."""
    bucket_name = get_bucket_name()
    upload_time_partitioned_data(bucket_name)
    upload_dimension_tables(bucket_name)
    print(f"\n✓ Upload complete: s3://{bucket_name}/")


if __name__ == "__main__":
    upload_to_s3()
