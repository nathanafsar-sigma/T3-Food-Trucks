"""
Main pipeline script that orchestrates the entire ETL process.
Extracts data from RDS, transforms it, converts to Parquet, and uploads to S3.
"""
import sys
from extract import extract_tables
from transform import transform_data
from create_parquet import create_parquet_files
from upload_to_s3 import upload_to_s3


def run_pipeline():
    """Run the complete ETL pipeline."""
    try:
        print("=" * 60)
        print("STARTING FOOD TRUCKS DATA PIPELINE")
        print("=" * 60)

        print("\n[1/4] EXTRACTING DATA FROM RDS...")
        extract_tables()

        print("\n[2/4] TRANSFORMING AND CLEANING DATA...")
        transform_data()

        print("\n[3/4] CREATING PARQUET FILES...")
        create_parquet_files()

        print("\n[4/4] UPLOADING TO S3...")
        upload_to_s3()

        print("\n" + "=" * 60)
        print("✓ PIPELINE COMPLETE")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ PIPELINE FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
