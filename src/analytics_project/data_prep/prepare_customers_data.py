"""
scripts/data_preparation/prepare_customers.py

This script reads customer data from the data/raw folder, cleans the data,
and writes the cleaned version to the data/prepared folder.
"""

#####################################
# Import Modules at the Top
#####################################
import pathlib
import sys
import pandas as pd
import numpy as np

# Ensure project root is in sys.path for local imports
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent))

from utils.logger import logger
from utils.data_scrubber import DataScrubber

# Constants
PROJECT_ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR: pathlib.Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: pathlib.Path = DATA_DIR / "raw"
PREPARED_DATA_DIR: pathlib.Path = DATA_DIR / "prepared"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PREPARED_DATA_DIR.mkdir(exist_ok=True)

#####################################
# Define Functions
#####################################


def read_raw_data(file_name: str) -> pd.DataFrame:
    """Read raw data from CSV."""
    logger.info(f"FUNCTION START: read_raw_data with file_name={file_name}")
    file_path = RAW_DATA_DIR.joinpath(file_name)
    logger.info(f"Reading data from {file_path}")

    # Check if file exists
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded dataframe with {len(df)} rows and {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return pd.DataFrame()


def save_prepared_data(df: pd.DataFrame, file_name: str) -> None:
    """Save cleaned data to CSV."""
    if df.empty:
        logger.error("Cannot save empty DataFrame")
        return

    logger.info(
        f"FUNCTION START: save_prepared_data with file_name={file_name}, dataframe shape={df.shape}"
    )
    file_path = PREPARED_DATA_DIR.joinpath(file_name)
    df.to_csv(file_path, index=False)
    logger.info(f"Data saved to {file_path}")


def add_customer_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add customer-related columns: LoyaltyPoints and CustomerSegment."""
    if df.empty:
        logger.warning("Cannot add columns to empty DataFrame")
        return df

    logger.info(f"FUNCTION START: add_customer_columns with dataframe shape={df.shape}")

    # Add LoyaltyPoints (numeric)
    if 'LoyaltyPoints' not in df.columns:
        np.random.seed(42)
        loyalty_points = np.random.choice(
            [0, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000, None],
            size=len(df),
            p=[0.1, 0.15, 0.15, 0.15, 0.1, 0.1, 0.08, 0.07, 0.05, 0.03, 0.01, 0.01],
        )
        df['LoyaltyPoints'] = loyalty_points
        logger.info("Added LoyaltyPoints column")

    # Add CustomerSegment (category)
    if 'CustomerSegment' not in df.columns:
        np.random.seed(42)
        segments = np.random.choice(
            ['Premium', 'Standard', 'Basic', 'PREMIUM', 'standard', 'New', None],
            size=len(df),
            p=[0.2, 0.4, 0.25, 0.05, 0.05, 0.04, 0.01],
        )
        df['CustomerSegment'] = segments
        logger.info("Added CustomerSegment column")

    logger.info(f"New columns added: LoyaltyPoints, CustomerSegment")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows."""
    if df.empty:
        return df

    logger.info(f"FUNCTION START: remove_duplicates with dataframe shape={df.shape}")
    initial_count = len(df)

    if 'CustomerID' in df.columns:
        df = df.drop_duplicates(subset=['CustomerID'])
        logger.info("Removed duplicates based on CustomerID")
    else:
        df = df.drop_duplicates()
        logger.info("Removed duplicates across all columns")

    removed_count = initial_count - len(df)
    logger.info(f"Removed {removed_count} duplicate rows")
    logger.info(f"{len(df)} records remaining after removing duplicates.")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values."""
    if df.empty:
        return df

    logger.info(f"FUNCTION START: handle_missing_values with dataframe shape={df.shape}")

    # Log missing values before handling
    missing_before = df.isna().sum()
    logger.info(f"Missing values before handling:\n{missing_before}")

    # Handle missing CustomerID - critical field, remove rows
    if 'CustomerID' in df.columns:
        initial_count = len(df)
        df = df[df['CustomerID'].notna()]
        removed_count = initial_count - len(df)
        logger.info(f"Removed {removed_count} rows with missing CustomerID")

    # Handle missing LoyaltyPoints - fill with 0
    if 'LoyaltyPoints' in df.columns:
        df['LoyaltyPoints'] = df['LoyaltyPoints'].fillna(0).astype(int)
        logger.info("Filled missing LoyaltyPoints with 0")

    # Handle missing CustomerSegment - fill with 'Unknown'
    if 'CustomerSegment' in df.columns:
        df['CustomerSegment'] = df['CustomerSegment'].fillna('Unknown')
        logger.info("Filled missing CustomerSegment with 'Unknown'")

    # Log missing values after handling
    missing_after = df.isna().sum()
    logger.info(f"Missing values after handling:\n{missing_after}")
    logger.info(f"{len(df)} records remaining after handling missing values.")
    return df


def clean_loyalty_points(df: pd.DataFrame) -> pd.DataFrame:
    """Clean LoyaltyPoints column."""
    if df.empty:
        return df

    logger.info(f"FUNCTION START: clean_loyalty_points with dataframe shape={df.shape}")

    if 'LoyaltyPoints' in df.columns:
        # Handle negative loyalty points
        negative_mask = df['LoyaltyPoints'] < 0
        if negative_mask.any():
            logger.info(f"Found {negative_mask.sum()} negative LoyaltyPoints, setting to 0")
            df.loc[negative_mask, 'LoyaltyPoints'] = 0

        # Cap extremely high loyalty points
        high_points_mask = df['LoyaltyPoints'] > 100000
        if high_points_mask.any():
            logger.info(
                f"Found {high_points_mask.sum()} extremely high LoyaltyPoints, capping at 100000"
            )
            df.loc[high_points_mask, 'LoyaltyPoints'] = 100000

        logger.info(
            f"LoyaltyPoints range: {df['LoyaltyPoints'].min()} to {df['LoyaltyPoints'].max()}"
        )

    return df


def clean_customer_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Clean CustomerSegment column."""
    if df.empty:
        return df

    logger.info(f"FUNCTION START: clean_customer_segment with dataframe shape={df.shape}")

    if 'CustomerSegment' in df.columns:
        # Standardize segment names
        segment_mapping = {
            'PREMIUM': 'Premium',
            'standard': 'Standard',
            'NEW': 'New',
            'new': 'New',
            'BASIC': 'Basic',
        }

        df['CustomerSegment'] = df['CustomerSegment'].replace(segment_mapping)

        # Log segment distribution
        segment_counts = df['CustomerSegment'].value_counts()
        logger.info(f"Customer segment distribution:\n{segment_counts}")

    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Remove outliers."""
    if df.empty:
        return df

    logger.info(f"FUNCTION START: remove_outliers with dataframe shape={df.shape}")
    initial_count = len(df)

    # Remove customers with invalid CustomerID
    if 'CustomerID' in df.columns:
        invalid_customers = df[df['CustomerID'] == 9999]
        if not invalid_customers.empty:
            logger.info(f"Removed {len(invalid_customers)} rows with invalid CustomerID 9999")
            df = df[df['CustomerID'] != 9999]

    # Remove extremely high loyalty points outliers
    if 'LoyaltyPoints' in df.columns:
        q99 = df['LoyaltyPoints'].quantile(0.99)
        extreme_loyalty_mask = df['LoyaltyPoints'] > q99
        if extreme_loyalty_mask.any():
            logger.info(
                f"Removed {extreme_loyalty_mask.sum()} customers with extremely high loyalty points (> {q99})"
            )
            df = df[~extreme_loyalty_mask]

    removed_count = initial_count - len(df)
    logger.info(f"Removed {removed_count} outlier rows")
    logger.info(f"{len(df)} records remaining after removing outliers.")
    return df


def validate_customer_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate customer data."""
    if df.empty:
        return df

    logger.info(f"FUNCTION START: validate_customer_data with dataframe shape={df.shape}")

    # Validate CustomerID uniqueness
    if 'CustomerID' in df.columns:
        duplicate_customers = df.duplicated(subset=['CustomerID']).sum()
        if duplicate_customers > 0:
            logger.warning(f"Found {duplicate_customers} duplicate CustomerIDs")

    # Validate CustomerSegment values
    if 'CustomerSegment' in df.columns:
        valid_segments = ['Premium', 'Standard', 'Basic', 'New', 'Unknown']
        invalid_segments = df[~df['CustomerSegment'].isin(valid_segments)]
        if not invalid_segments.empty:
            logger.warning(f"Found {len(invalid_segments)} rows with invalid CustomerSegment")

    # Validate LoyaltyPoints range
    if 'LoyaltyPoints' in df.columns:
        invalid_points = df[(df['LoyaltyPoints'] < 0) | (df['LoyaltyPoints'] > 100000)]
        if not invalid_points.empty:
            logger.warning(
                f"Found {len(invalid_points)} rows with LoyaltyPoints outside valid range"
            )

    logger.info("Customer data validation completed")
    return df


#####################################
# Main Function
#####################################


def main() -> None:
    """Main function for processing customer data."""
    logger.info("==================================")
    logger.info("STARTING prepare_customers_data.py")
    logger.info("==================================")

    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"Raw data dir: {RAW_DATA_DIR}")
    logger.info(f"Prepared data dir: {PREPARED_DATA_DIR}")

    input_file = "customers_data.csv"
    output_file = "customers_prepared.csv"

    # Read raw data
    df = read_raw_data(input_file)

    # Check if data was loaded
    if df.empty:
        logger.error("No data loaded - cannot proceed with cleaning")
        return

    # Record original shape
    original_shape = df.shape
    logger.info(f"Initial dataframe shape: {df.shape}")

    # Clean column names
    if not df.empty:
        original_columns = df.columns.tolist()
        df.columns = [str(col).strip() for col in df.columns]

        changed_columns = [
            f"{old} -> {new}" for old, new in zip(original_columns, df.columns) if old != new
        ]
        if changed_columns:
            logger.info(f"Cleaned column names: {', '.join(changed_columns)}")

    # Apply all cleaning functions
    df = add_customer_columns(df)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = clean_loyalty_points(df)
    df = clean_customer_segment(df)
    df = remove_outliers(df)
    df = validate_customer_data(df)

    # Save prepared data
    save_prepared_data(df, output_file)

    logger.info("==================================")
    logger.info(f"Original shape: {original_shape}")
    logger.info(f"Cleaned shape:  {df.shape}")
    logger.info("==================================")
    logger.info("FINISHED prepare_customers_data.py")


if __name__ == "__main__":
    main()
