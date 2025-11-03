import pandas as pd
import random

# Read the sales data from the correct location
file_path = 'data/raw/sales_data.csv'
df = pd.read_csv(file_path)

print(f"Loaded {len(df)} rows from {file_path}")

# Add DiscountPercent column with intentional data quality issues
discount_options = [
    0.0,
    0.0,
    5.0,
    5.0,
    10.0,
    10.0,
    15.0,
    15.0,
    20.0,
    25.0,
    8.5,
    12.5,
    7.5,
    3.0,
    None,
    -5.0,
    150.0,
]
df['DiscountPercent'] = [random.choice(discount_options) for _ in range(len(df))]

# Add PaymentType column with intentional data quality issues
payment_options = [
    "Credit",
    "Credit",
    "Debit",
    "Debit",
    "Cash",
    "Cash",
    "Digital",
    "Digital",
    "CREDIT",
    "credit",
    "Debit Card",
    "Credit Card",
    "CASH",
    "Debit-Card",
    None,
]
df['PaymentType'] = [random.choice(payment_options) for _ in range(len(df))]

# Save back to the same file (overwrites original)
df.to_csv(file_path, index=False)
print(f"Done! Updated {file_path} with new columns:")
print(" - DiscountPercent (numeric)")
print(" - PaymentType (category)")
print(f"Total rows: {len(df)}")

# Show a sample of the extended data
print("\nSample of extended data (first 5 rows):")
print(df[['TransactionID', 'SaleAmount', 'DiscountPercent', 'PaymentType']].head())
