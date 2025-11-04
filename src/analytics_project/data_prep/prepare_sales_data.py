"""
scripts/data_preparation/prepare_sales.py

This script reads data from the data/raw folder, cleans the data,
and writes the cleaned version to the data/prepared folder.

Tasks:
- Remove duplicates
- Handle missing values
- Remove outliers
- Ensure consistent formatting
- Clean DiscountPercent and PaymentType columns

"""

#####################################
# Import Modules at the Top
#####################################

# Import from Python Standard Library
import pathlib
import sys

# Import from external packages (requires a virtual environment)
import pandas as pd

# Ensure project root is in sys.path for local imports (now 3 parents are needed)
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))

# Import local modules (e.g. utils/logger.py)
from utils.logger import logger

# Optional: Use a data_scrubber module for common data cleaning tasks
from utils.data_scrubber import DataScrubber


# Constants
SCRIPTS_DATA_PREP_DIR: pathlib.Path = (
    pathlib.Path(__file__).resolve().parent
)  # Directory of the current script
SCRIPTS_DIR: pathlib.Path = SCRIPTS_DATA_PREP_DIR.parent
PROJECT_ROOT: pathlib.Path = SCRIPTS_DIR.parent
DATA_DIR: pathlib.Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: pathlib.Path = DATA_DIR / "raw"
PREPARED_DATA_DIR: pathlib.Path = DATA_DIR / "prepared"  # place to store prepared data


# Ensure the directories exist or create them
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PREPARED_DATA_DIR.mkdir(exist_ok=True)

#####################################
# Define Functions - Reusable blocks of code / instructions
#####################################


def read_raw_data(file_name: str) -> pd.DataFrame:
    """
    Read raw data from CSV.

    Args:
        file_name (str): Name of the CSV file to read.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    logger.info(f"FUNCTION START: read_raw_data with file_name={file_name}")
    file_path = RAW_DATA_DIR.joinpath(file_name)
    logger.info(f"Reading data from {file_path}")
    df = pd.read_csv(file_path)
    logger.info(f"Loaded dataframe with {len(df)} rows and {len(df.columns)} columns")

    # Data profiling
    logger.info(f"Column datatypes: \n{df.dtypes}")
    logger.info(f"Number of unique values: \n{df.nunique()}")

    return df


def save_prepared_data(df: pd.DataFrame, file_name: str) -> None:
    """
    Save cleaned data to CSV.

    Args:
        df (pd.DataFrame): Cleaned DataFrame.
        file_name (str): Name of the output file.
    """
    logger.info(
        f"FUNCTION START: save_prepared_data with file_name={file_name}, dataframe shape={df.shape}"
    )
    file_path = PREPARED_DATA_DIR.joinpath(file_name)
    df.to_csv(file_path, index=False)
    logger.info(f"Data saved to {file_path}")


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with duplicates removed.
    """
    logger.info(f"FUNCTION START: remove_duplicates with dataframe shape={df.shape}")
    initial_count = len(df)

    # Remove duplicates based on TransactionID (unique identifier for sales)
    if 'TransactionID' in df.columns:
        df = df.drop_duplicates(subset=['TransactionID'])
        logger.info("Removed duplicates based on TransactionID")
    else:
        df = df.drop_duplicates()
        logger.info("Removed duplicates across all columns")

    removed_count = initial_count - len(df)
    logger.info(f"Removed {removed_count} duplicate rows")
    logger.info(f"{len(df)} records remaining after removing duplicates.")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values by filling or dropping.
    Specific handling for sales data with new columns.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with missing values handled.
    """
    logger.info(f"FUNCTION START: handle_missing_values with dataframe shape={df.shape}")

    # Log missing values by column before handling
    missing_by_col = df.isna().sum()
    logger.info(f"Missing values by column before handling:\n{missing_by_col}")

    # Handle missing CampaignID - fill with -1 to indicate no campaign
    if 'CampaignID' in df.columns:
        df['CampaignID'] = df['CampaignID'].fillna(-1).astype(int)
        logger.info("Filled missing CampaignID with -1")

    # Handle missing SaleAmount - these are problematic, remove rows
    if 'SaleAmount' in df.columns:
        initial_count = len(df)
        df = df[df['SaleAmount'].notna()]
        removed_count = initial_count - len(df)
        logger.info(f"Removed {removed_count} rows with missing SaleAmount")

    # Handle missing DiscountPercent - fill with 0 (no discount)
    if 'DiscountPercent' in df.columns:
        df['DiscountPercent'] = df['DiscountPercent'].fillna(0.0)
        logger.info("Filled missing DiscountPercent with 0.0")

    # Handle missing PaymentType - fill with 'Unknown'
    if 'PaymentType' in df.columns:
        df['PaymentType'] = df['PaymentType'].fillna('Unknown')
        logger.info("Filled missing PaymentType with 'Unknown'")

    # Log missing values by column after handling
    missing_after = df.isna().sum()
    logger.info(f"Missing values by column after handling:\n{missing_after}")
    logger.info(f"{len(df)} records remaining after handling missing values.")
    return df


def clean_discount_percent(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean DiscountPercent column - handle invalid values.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with cleaned DiscountPercent.
    """
    logger.info(f"FUNCTION START: clean_discount_percent with dataframe shape={df.shape}")

    if 'DiscountPercent' in df.columns:
        initial_count = len(df)

        # Convert to numeric, coercing errors to NaN
        df['DiscountPercent'] = pd.to_numeric(df['DiscountPercent'], errors='coerce')

        # Handle negative discounts - set to 0
        negative_mask = df['DiscountPercent'] < 0
        if negative_mask.any():
            logger.info(f"Found {negative_mask.sum()} negative discount values, setting to 0")
            df.loc[negative_mask, 'DiscountPercent'] = 0.0

        # Handle discounts over 100% - cap at 100
        over_100_mask = df['DiscountPercent'] > 100
        if over_100_mask.any():
            logger.info(f"Found {over_100_mask.sum()} discount values > 100%, capping at 100")
            df.loc[over_100_mask, 'DiscountPercent'] = 100.0

        # Fill any new NaN values created during conversion
        df['DiscountPercent'] = df['DiscountPercent'].fillna(0.0)

        logger.info(
            f"DiscountPercent range: {df['DiscountPercent'].min():.1f}% to {df['DiscountPercent'].max():.1f}%"
        )

    return df


def clean_payment_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean PaymentType column - standardize categories.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with cleaned PaymentType.
    """
    logger.info(f"FUNCTION START: clean_payment_type with dataframe shape={df.shape}")

    if 'PaymentType' in df.columns:
        # Standardize payment types based on your data
        payment_mapping = {
            'CREDIT': 'Credit',
            'Debit Card': 'Debit',
            'Digital': 'Digital Wallet',
            'credit': 'Credit',
            'CASH': 'Cash',
        }

        df['PaymentType'] = df['PaymentType'].replace(payment_mapping)

        # Log payment type distribution
        payment_counts = df['PaymentType'].value_counts()
        logger.info(f"Payment type distribution:\n{payment_counts}")

    return df


def standardize_date_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize SaleDate to consistent format.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with standardized dates.
    """
    logger.info(f"FUNCTION START: standardize_date_format with dataframe shape={df.shape}")

    if 'SaleDate' in df.columns:
        initial_count = len(df)

        # Convert to datetime, handling multiple formats
        df['SaleDate'] = pd.to_datetime(df['SaleDate'], errors='coerce')

        # Remove rows with invalid dates
        invalid_dates = df['SaleDate'].isna()
        if invalid_dates.any():
            logger.info(f"Removed {invalid_dates.sum()} rows with invalid dates")
            df = df[~invalid_dates]

        # Format as YYYY-MM-DD for consistency
        df['SaleDate'] = df['SaleDate'].dt.strftime('%Y-%m-%d')

        removed_count = initial_count - len(df)
        logger.info(f"Removed {removed_count} rows with invalid dates")
        logger.info(f"Date range: {df['SaleDate'].min()} to {df['SaleDate'].max()}")

    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outliers based on SaleAmount.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with outliers removed.
    """
    logger.info(f"FUNCTION START: remove_outliers with dataframe shape={df.shape}")
    initial_count = len(df)

    # Remove negative sale amounts (invalid)
    if 'SaleAmount' in df.columns:
        negative_sales = df[df['SaleAmount'] < 0]
        if not negative_sales.empty:
            logger.info(f"Removed {len(negative_sales)} negative SaleAmount values")
            df = df[df['SaleAmount'] >= 0]

    # Remove extremely high sale amounts (potential data errors)
    if 'SaleAmount' in df.columns:
        # Use IQR method to identify outliers
        Q1 = df['SaleAmount'].quantile(0.25)
        Q3 = df['SaleAmount'].quantile(0.75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR

        high_sales_mask = df['SaleAmount'] > upper_bound
        if high_sales_mask.any():
            logger.info(
                f"Removed {high_sales_mask.sum()} extremely high sale amounts (> {upper_bound:.2f})"
            )
            df = df[~high_sales_mask]

    removed_count = initial_count - len(df)
    logger.info(f"Removed {removed_count} outlier rows")
    logger.info(f"{len(df)} records remaining after removing outliers.")
    return df


def validate_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate sales data against business rules.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Validated DataFrame.
    """
    logger.info(f"FUNCTION START: validate_sales_data with dataframe shape={df.shape}")

    # Validate TransactionID uniqueness
    if 'TransactionID' in df.columns:
        duplicate_transactions = df.duplicated(subset=['TransactionID']).sum()
        if duplicate_transactions > 0:
            logger.warning(f"Found {duplicate_transactions} duplicate TransactionIDs")

    # Validate SaleAmount range
    if 'SaleAmount' in df.columns:
        invalid_sales = df[(df['SaleAmount'] < 0) | (df['SaleAmount'] > 100000)]
        if not invalid_sales.empty:
            logger.warning(f"Found {len(invalid_sales)} sales with SaleAmount outside valid range")

    # Validate DiscountPercent range
    if 'DiscountPercent' in df.columns:
        invalid_discounts = df[(df['DiscountPercent'] < 0) | (df['DiscountPercent'] > 100)]
        if not invalid_discounts.empty:
            logger.warning(
                f"Found {len(invalid_discounts)} sales with DiscountPercent outside valid range"
            )

    # Validate PaymentType values
    if 'PaymentType' in df.columns:
        valid_payments = ['Credit', 'Debit', 'Cash', 'Digital Wallet', 'Unknown']
        invalid_payments = df[~df['PaymentType'].isin(valid_payments)]
        if not invalid_payments.empty:
            logger.warning(f"Found {len(invalid_payments)} sales with invalid PaymentType")

    logger.info("Sales data validation complete")
    return df


#####################################
# Define Main Function - The main entry point of the script
#####################################


def main() -> None:
    """
    Main function for processing data.
    """
    logger.info("==================================")
    logger.info("STARTING prepare_sales_data.py")
    logger.info("==================================")

    logger.info(f"Root         : {PROJECT_ROOT}")
    logger.info(f"data/raw     : {RAW_DATA_DIR}")
    logger.info(f"data/prepared: {PREPARED_DATA_DIR}")
    logger.info(f"scripts      : {SCRIPTS_DIR}")

    input_file = "sales_data.csv"
    output_file = "sales_prepared.csv"

    # Read raw data
    df = read_raw_data(input_file)

    # Record original shape
    original_shape = df.shape

    # Log initial dataframe information
    logger.info(f"Initial dataframe columns: {', '.join(df.columns.tolist())}")
    logger.info(f"Initial dataframe shape: {df.shape}")

    # Clean column names
    original_columns = df.columns.tolist()
    df.columns = df.columns.str.strip()

    # Log if any column names changed
    changed_columns = [
        f"{old} -> {new}" for old, new in zip(original_columns, df.columns) if old != new
    ]
    if changed_columns:
        logger.info(f"Cleaned column names: {', '.join(changed_columns)}")

    # Standardize date format first
    df = standardize_date_format(df)

    # Remove duplicates
    df = remove_duplicates(df)

    # Handle missing values
    df = handle_missing_values(df)

    # Clean the new columns
    df = clean_discount_percent(df)
    df = clean_payment_type(df)

    # Remove outliers
    df = remove_outliers(df)

    # Validate data
    df = validate_sales_data(df)

    # Save prepared data
    save_prepared_data(df, output_file)

    logger.info("==================================")
    logger.info(f"Original shape: {original_shape}")
    logger.info(f"Cleaned shape:  {df.shape}")
    logger.info("==================================")
    logger.info("FINISHED prepare_sales_data.py")
    logger.info("==================================")


#####################################
# Conditional Execution Block
# Ensures the script runs only when executed directly
# This is a common Python convention.
#####################################

if __name__ == "__main__":
    main()
