"""Enhanced Unified Data Preparation Module.

File: src/analytics_project/data_prep.py
Processes all three datasets with comprehensive cleaning and preparation.
"""

import pathlib
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any

# === CORRECT PATH CALCULATION ===
# Go up 3 levels from src/analytics_project/data_prep.py to reach project root
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))
# === END PATH FIX ===

from utils.logger import logger
from utils.data_scrubber import DataScrubber

# Set up paths as constants
DATA_DIR: pathlib.Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: pathlib.Path = DATA_DIR / "raw"
PREPARED_DATA_DIR: pathlib.Path = DATA_DIR / "prepared"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PREPARED_DATA_DIR.mkdir(exist_ok=True)


def read_and_log(path: pathlib.Path) -> pd.DataFrame:
    """Read a CSV at the given path into a DataFrame, with friendly logging."""
    try:
        logger.info(f"Reading raw data from {path}.")
        df = pd.read_csv(path)
        logger.info(
            f"{path.name}: loaded DataFrame with shape {df.shape[0]} rows x {df.shape[1]} cols"
        )
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return pd.DataFrame()


def save_prepared_data(df: pd.DataFrame, filename: str) -> None:
    """Save prepared data to CSV."""
    if df.empty:
        logger.error(f"Cannot save empty DataFrame for {filename}")
        return

    output_path = PREPARED_DATA_DIR.joinpath(filename)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved prepared data to {output_path} ({df.shape[0]} rows)")


def prepare_customers_data() -> pd.DataFrame:
    """Prepare customer data using DataScrubber and custom logic."""
    logger.info("=== PREPARING CUSTOMERS DATA ===")

    df = read_and_log(RAW_DATA_DIR.joinpath("customers_data.csv"))
    if df.empty:
        return pd.DataFrame()

    original_shape = df.shape

    # Use DataScrubber for common cleaning tasks
    scrubber = DataScrubber(df)

    # Clean column names
    scrubber.clean_column_names(case='lower', replace_spaces=True)

    # Remove duplicates
    scrubber.remove_duplicates(subset=['customerid'])

    # Handle missing values
    missing_strategy = {
        'customerid': 'drop',
        'loyaltypoints': 'fill_0',
        'customersegment': 'fill_unknown',
    }
    scrubber.handle_missing_values(strategy=missing_strategy)

    # Convert numeric columns
    scrubber.convert_to_numeric(['loyaltypoints'])

    # Custom customer-specific logic (from your original script)
    df = scrubber.df

    # Add customer columns if they don't exist
    if 'loyaltypoints' not in df.columns:
        np.random.seed(42)
        loyalty_points = np.random.choice(
            [0, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000],
            size=len(df),
            p=[0.1, 0.15, 0.15, 0.15, 0.1, 0.1, 0.08, 0.07, 0.05, 0.03, 0.02],
        )
        df['loyaltypoints'] = loyalty_points

    if 'customersegment' not in df.columns:
        np.random.seed(42)
        segments = np.random.choice(
            ['Premium', 'Standard', 'Basic', 'New'],
            size=len(df),
            p=[0.2, 0.4, 0.25, 0.15],
        )
        df['customersegment'] = segments

    # Clean loyalty points
    df['loyaltypoints'] = df['loyaltypoints'].clip(lower=0, upper=100000)

    # Standardize customer segments
    segment_mapping = {'PREMIUM': 'Premium', 'standard': 'Standard', 'BASIC': 'Basic', 'NEW': 'New'}
    df['customersegment'] = df['customersegment'].replace(segment_mapping)

    logger.info(f"Customers: {original_shape} → {df.shape}")
    return df


def prepare_products_data() -> pd.DataFrame:
    """Prepare products data using DataScrubber and custom logic."""
    logger.info("=== PREPARING PRODUCTS DATA ===")

    df = read_and_log(RAW_DATA_DIR.joinpath("products_data.csv"))
    if df.empty:
        return pd.DataFrame()

    original_shape = df.shape

    # Use DataScrubber for common cleaning tasks
    scrubber = DataScrubber(df)
    scrubber.clean_column_names(case='lower', replace_spaces=True)
    scrubber.remove_duplicates(subset=['productid'])

    # Handle missing values
    missing_strategy = {
        'productid': 'drop',
        'stockquantity': 'fill_0',
        'productcategory': 'fill_uncategorized',
    }
    scrubber.handle_missing_values(strategy=missing_strategy)
    scrubber.convert_to_numeric(['stockquantity'])

    df = scrubber.df

    # Custom product-specific logic
    if 'stockquantity' not in df.columns:
        np.random.seed(42)
        stock_quantities = np.random.choice(
            [0, 5, 10, 25, 50, 100, 250, 500, 1000],
            size=len(df),
            p=[0.05, 0.1, 0.15, 0.2, 0.15, 0.15, 0.1, 0.05, 0.05],
        )
        df['stockquantity'] = stock_quantities

    if 'productcategory' not in df.columns:
        np.random.seed(42)
        categories = np.random.choice(
            ['Electronics', 'Clothing', 'Home', 'Sports'],
            size=len(df),
            p=[0.3, 0.25, 0.25, 0.2],
        )
        df['productcategory'] = categories

    # Clean stock quantities
    df['stockquantity'] = df['stockquantity'].clip(lower=0, upper=10000)

    # Standardize product categories
    category_mapping = {
        'ELECTRONICS': 'Electronics',
        'clothing': 'Clothing',
        'Home Goods': 'Home',
        'Sports Equipment': 'Sports',
    }
    df['productcategory'] = df['productcategory'].replace(category_mapping)

    logger.info(f"Products: {original_shape} → {df.shape}")
    return df


def prepare_sales_data() -> pd.DataFrame:
    """Prepare sales data using DataScrubber and custom logic."""
    logger.info("=== PREPARING SALES DATA ===")

    df = read_and_log(RAW_DATA_DIR.joinpath("sales_data.csv"))
    if df.empty:
        return pd.DataFrame()

    original_shape = df.shape

    # Use DataScrubber for common cleaning tasks
    scrubber = DataScrubber(df)
    scrubber.clean_column_names(case='lower', replace_spaces=True)
    scrubber.remove_duplicates(subset=['transactionid'])

    # Handle missing values
    missing_strategy = {
        'transactionid': 'drop',
        'saleamount': 'drop',
        'discountpercent': 'fill_0',
        'paymenttype': 'fill_unknown',
    }
    scrubber.handle_missing_values(strategy=missing_strategy)

    # Convert numeric columns
    scrubber.convert_to_numeric(['saleamount', 'discountpercent', 'customerid', 'productid'])

    # Remove outliers
    scrubber.remove_outliers_iqr('saleamount', multiplier=1.5)

    df = scrubber.df

    # Custom sales-specific logic
    # Clean discount percent
    df['discountpercent'] = df['discountpercent'].clip(lower=0, upper=100)

    # Standardize payment types
    payment_mapping = {
        'CREDIT': 'Credit',
        'Debit Card': 'Debit',
        'Digital': 'Digital Wallet',
        'credit': 'Credit',
        'CASH': 'Cash',
    }
    df['paymenttype'] = df['paymenttype'].replace(payment_mapping)

    # Standardize date format
    if 'saledate' in df.columns:
        df['saledate'] = pd.to_datetime(df['saledate'], errors='coerce')
        df = df[df['saledate'].notna()]
        df['saledate'] = df['saledate'].dt.strftime('%Y-%m-%d')

    logger.info(f"Sales: {original_shape} → {df.shape}")
    return df


def validate_data_integrity(
    customers_df: pd.DataFrame, products_df: pd.DataFrame, sales_df: pd.DataFrame
) -> None:
    """Validate relationships between datasets."""
    logger.info("=== VALIDATING DATA INTEGRITY ===")

    if not sales_df.empty:
        # Check for orphaned sales (customers that don't exist)
        if (
            not customers_df.empty
            and 'customerid' in customers_df.columns
            and 'customerid' in sales_df.columns
        ):
            orphaned_customer_sales = sales_df[
                ~sales_df['customerid'].isin(customers_df['customerid'])
            ]
            if not orphaned_customer_sales.empty:
                logger.warning(
                    f"Found {len(orphaned_customer_sales)} sales with non-existent customers"
                )

        # Check for orphaned sales (products that don't exist)
        if (
            not products_df.empty
            and 'productid' in products_df.columns
            and 'productid' in sales_df.columns
        ):
            orphaned_product_sales = sales_df[~sales_df['productid'].isin(products_df['productid'])]
            if not orphaned_product_sales.empty:
                logger.warning(
                    f"Found {len(orphaned_product_sales)} sales with non-existent products"
                )


def main() -> None:
    """Orchestrate the complete data preparation pipeline."""
    logger.info("Starting comprehensive data preparation pipeline...")

    # Prepare all datasets
    customers_df = prepare_customers_data()
    products_df = prepare_products_data()
    sales_df = prepare_sales_data()

    # Validate data integrity
    validate_data_integrity(customers_df, products_df, sales_df)

    # Save prepared data
    if not customers_df.empty:
        save_prepared_data(customers_df, "customers_prepared.csv")

    if not products_df.empty:
        save_prepared_data(products_df, "products_prepared.csv")

    if not sales_df.empty:
        save_prepared_data(sales_df, "sales_prepared.csv")

    # Summary
    logger.info("=== DATA PREPARATION SUMMARY ===")
    if not customers_df.empty:
        logger.info(f"Customers: {customers_df.shape[0]} records")
    if not products_df.empty:
        logger.info(f"Products: {products_df.shape[0]} records")
    if not sales_df.empty:
        logger.info(f"Sales: {sales_df.shape[0]} records")

    logger.info("Data preparation pipeline complete!")


if __name__ == "__main__":
    # Run the main pipeline
    main()
