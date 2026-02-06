import os
import pandas as pd


def load_raw_data():
    """Load and deduplicate raw data."""
    trucks = pd.read_csv(
        'data/raw/DIM_Truck.csv').drop_duplicates(subset=['truck_id'])
    payment = pd.read_csv(
        'data/raw/DIM_Payment_Method.csv').drop_duplicates(subset=['payment_method_id'])
    transactions = pd.read_csv(
        'data/raw/FACT_Transaction.csv').drop_duplicates(subset=['transaction_id'])
    return trucks, payment, transactions


def clean_transactions(transactions):
    """Clean transaction data."""
    transactions['at'] = pd.to_datetime(transactions['at'])
    transactions['total'] = pd.to_numeric(
        transactions['total'], errors='coerce')
    transactions = transactions[transactions['total'] > 0].dropna(
        subset=['transaction_id', 'truck_id', 'total', 'at'])
    return transactions


def create_combined_dataset(transactions, trucks, payment):
    """Merge all tables into combined dataset."""
    return transactions.merge(trucks, on='truck_id', how='left').merge(payment, on='payment_method_id', how='left')


def save_clean_data(trucks, payment, transactions, combined):
    """Save cleaned data to CSV files."""
    os.makedirs('data/clean', exist_ok=True)
    trucks.to_csv('data/clean/trucks_clean.csv', index=False)
    payment.to_csv('data/clean/payment_methods_clean.csv', index=False)
    transactions.to_csv('data/clean/transactions_clean.csv', index=False)
    combined.to_csv('data/clean/combined_data.csv', index=False)


def transform_data():
    """Main transformation pipeline."""
    trucks, payment, transactions = load_raw_data()
    transactions = clean_transactions(transactions)
    combined = create_combined_dataset(transactions, trucks, payment)
    save_clean_data(trucks, payment, transactions, combined)
    print(
        f"✓ Cleaned {len(trucks)} trucks, {len(payment)} payment methods, {len(transactions)} transactions")


if __name__ == "__main__":
    transform_data()
