import pandas as pd
import random

# Read your original data
df = pd.read_csv('sales_data.csv')

# Generate DiscountPercent (with intentional issues)
discounts = [0.0, 5.0, 10.0, 15.0, 20.0, 0.0, 8.5, 12.5, 7.5, 3.0, None, -5.0, 150.0]
df['DiscountPercent'] = [random.choice(discounts) for _ in range(len(df))]

# Generate PaymentType (with intentional issues)
payments = [
    "Credit",
    "Debit",
    "Cash",
    "Digital",
    "CREDIT",
    "credit",
    "Debit Card",
    "Credit Card",
    "CASH",
    None,
]
df['PaymentType'] = [random.choice(payments) for _ in range(len(df))]

# Save extended file
df.to_csv('sales_data_extended.csv', index=False)
