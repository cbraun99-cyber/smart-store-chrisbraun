"""
scripts/data_preparation/prepare_products.py

This script reads data from the data/raw folder, cleans the data,
and writes the cleaned version to the data/prepared folder.

Tasks:
- Remove duplicates
- Handle missing values
- Remove outliers
- Ensure consistent formatting
- Add and clean product-related columns (StockQuantity, ProductCategory)

"""

#####################################
# Import Modules at the Top
#####################################

# Import from Python Standard Library
import pathlib
import sys

# Import from external packages (requires a virtual environment)
import pandas as pd
import numpy as np

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


def add_product_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add product-related columns: StockQuantity and ProductCategory.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with new columns added.
    """
    logger.info(f"FUNCTION START: add_product_columns with dataframe shape={df.shape}")

    # Add StockQuantity (numeric) - inventory levels
    if 'StockQuantity' not in df.columns:
        np.random.seed(42)  # For reproducible results
        # Generate realistic stock quantities with some data quality issues
        stock_quantities = np.random.choice(
            [0, 5, 10, 25, 50, 100, 250, 500, 1000, -10, None],
            size=len(df),
            p=[0.05, 0.1, 0.15, 0.2, 0.15, 0.15, 0.1, 0.05, 0.03, 0.01, 0.01],
        )
        df['StockQuantity'] = stock_quantities
        logger.info("Added StockQuantity column")

    # Add ProductCategory (category) - product classification
    if 'ProductCategory' not in df.columns:
        np.random.seed(42)
        # Generate product categories with some data quality issues
        categories = np.random.choice(
            [
                'Electronics',
                'Clothing',
                'Home',
                'Sports',
                'ELECTRONICS',
                'clothing',
                'Home Goods',
                'Sports Equipment',
                None,
            ],
            size=len(df),
            p=[0.25, 0.2, 0.2, 0.15, 0.05, 0.05, 0.05, 0.04, 0.01],
        )
        df['ProductCategory'] = categories
        logger.info("Added ProductCategory column")

    logger.info(f"New columns added: StockQuantity, ProductCategory")
    return df


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

    # Remove duplicates based on ProductID (assuming it's the unique identifier)
    if 'ProductID' in df.columns:
        df = df.drop_duplicates(subset=['ProductID'])
        logger.info("Removed duplicates based on ProductID")
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
    Specific handling for product data with new columns.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with missing values handled.
    """
    logger.info(f"FUNCTION START: handle_missing_values with dataframe shape={df.shape}")

    # Log missing values by column before handling
    missing_by_col = df.isna().sum()
    logger.info(f"Missing values by column before handling:\n{missing_by_col}")

    # Handle missing ProductID - critical field, remove rows
    if 'ProductID' in df.columns:
        initial_count = len(df)
        df = df[df['ProductID'].notna()]
        removed_count = initial_count - len(df)
        logger.info(f"Removed {removed_count} rows with missing ProductID")

    # Handle missing StockQuantity - fill with 0 (out of stock)
    if 'StockQuantity' in df.columns:
        df['StockQuantity'] = df['StockQuantity'].fillna(0).astype(int)
        logger.info("Filled missing StockQuantity with 0")

    # Handle missing ProductCategory - fill with 'Uncategorized'
    if 'ProductCategory' in df.columns:
        df['ProductCategory'] = df['ProductCategory'].fillna('Uncategorized')
        logger.info("Filled missing ProductCategory with 'Uncategorized'")

    # Handle other potential missing values
    # Example for other product columns:
    # if 'ProductName' in df.columns:
    #     df['ProductName'] = df['ProductName'].fillna('Unknown Product')

    # Log missing values by column after handling
    missing_after = df.isna().sum()
    logger.info(f"Missing values by column after handling:\n{missing_after}")
    logger.info(f"{len(df)} records remaining after handling missing values.")
    return df


def clean_stock_quantity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean StockQuantity column - handle invalid values.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with cleaned StockQuantity.
    """
    logger.info(f"FUNCTION START: clean_stock_quantity with dataframe shape={df.shape}")

    if 'StockQuantity' in df.columns:
        # Handle negative stock quantities - set to 0
        negative_mask = df['StockQuantity'] < 0
        if negative_mask.any():
            logger.info(f"Found {negative_mask.sum()} negative StockQuantity values, setting to 0")
            df.loc[negative_mask, 'StockQuantity'] = 0

        # Handle extremely high stock quantities (potential data errors)
        high_stock_mask = df['StockQuantity'] > 10000
        if high_stock_mask.any():
            logger.info(
                f"Found {high_stock_mask.sum()} extremely high StockQuantity values, capping at 10000"
            )
            df.loc[high_stock_mask, 'StockQuantity'] = 10000

        logger.info(
            f"StockQuantity range: {df['StockQuantity'].min()} to {df['StockQuantity'].max()}"
        )
        logger.info(f"Average StockQuantity: {df['StockQuantity'].mean():.1f}")
        logger.info(f"Products with zero stock: {(df['StockQuantity'] == 0).sum()}")

    return df


def clean_product_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean ProductCategory column - standardize categories.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with cleaned ProductCategory.
    """
    logger.info(f"FUNCTION START: clean_product_category with dataframe shape={df.shape}")

    if 'ProductCategory' in df.columns:
        # Standardize category names
        category_mapping = {
            'ELECTRONICS': 'Electronics',
            'clothing': 'Clothing',
            'Home Goods': 'Home',
            'Sports Equipment': 'Sports',
            'ELECTRIC': 'Electronics',
            'CLOTHES': 'Clothing',
        }

        df['ProductCategory'] = df['ProductCategory'].replace(category_mapping)

        # Log category distribution
        category_counts = df['ProductCategory'].value_counts()
        logger.info(f"Product category distribution:\n{category_counts}")

    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outliers based on product data.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with outliers removed.
    """
    logger.info(f"FUNCTION START: remove_outliers with dataframe shape={df.shape}")
    initial_count = len(df)

    # Remove products with invalid ProductID
    if 'ProductID' in df.columns:
        # Check for obviously invalid product IDs (like 9999 from sales data)
        invalid_products = df[df['ProductID'].astype(str).str.contains('9999|0000')]
        if not invalid_products.empty:
            logger.info(f"Removed {len(invalid_products)} rows with invalid ProductID")
            df = df[~df['ProductID'].astype(str).str.contains('9999|0000', na=False)]

    # Remove extreme stock quantity outliers using IQR method
    if 'StockQuantity' in df.columns:
        Q1 = df['StockQuantity'].quantile(0.25)
        Q3 = df['StockQuantity'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        stock_outliers = df[
            (df['StockQuantity'] < lower_bound) | (df['StockQuantity'] > upper_bound)
        ]
        if not stock_outliers.empty:
            logger.info(
                f"Removed {len(stock_outliers)} products with extreme StockQuantity (IQR method)"
            )
            df = df[(df['StockQuantity'] >= lower_bound) & (df['StockQuantity'] <= upper_bound)]

    removed_count = initial_count - len(df)
    logger.info(f"Removed {removed_count} outlier rows")
    logger.info(f"{len(df)} records remaining after removing outliers.")
    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate data against business rules.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Validated DataFrame.
    """
    logger.info(f"FUNCTION START: validate_data with dataframe shape={df.shape}")

    # Validate ProductID uniqueness
    if 'ProductID' in df.columns:
        duplicate_products = df.duplicated(subset=['ProductID']).sum()
        if duplicate_products > 0:
            logger.warning(f"Found {duplicate_products} duplicate ProductIDs")

    # Validate StockQuantity range
    if 'StockQuantity' in df.columns:
        invalid_stock = df[(df['StockQuantity'] < 0) | (df['StockQuantity'] > 10000)]
        if not invalid_stock.empty:
            logger.warning(
                f"Found {len(invalid_stock)} products with StockQuantity outside valid range"
            )

    # Validate ProductCategory values
    if 'ProductCategory' in df.columns:
        valid_categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Uncategorized']
        invalid_categories = df[~df['ProductCategory'].isin(valid_categories)]
        if not invalid_categories.empty:
            logger.warning(f"Found {len(invalid_categories)} products with invalid ProductCategory")

    logger.info("Product data validation complete")
    return df


def standardize_formats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize the formatting of various columns.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with standardized formatting.
    """
    logger.info(f"FUNCTION START: standardize_formats with dataframe shape={df.shape}")

    # Standardize text fields
    if 'ProductName' in df.columns:
        df['ProductName'] = df['ProductName'].str.title()
        logger.info("Standardized ProductName to title case")

    if 'ProductCategory' in df.columns:
        df['ProductCategory'] = df['ProductCategory'].str.title()
        logger.info("Standardized ProductCategory to title case")

    # Ensure numeric fields are properly formatted
    if 'StockQuantity' in df.columns:
        df['StockQuantity'] = df['StockQuantity'].astype(int)
        logger.info("Ensured StockQuantity is integer type")

    logger.info("Completed standardizing formats")
    return df


def main() -> None:
    """
    Main function for processing product data.
    """
    logger.info("==================================")
    logger.info("STARTING prepare_products_data.py")
    logger.info("==================================")

    logger.info(f"Root         : {PROJECT_ROOT}")
    logger.info(f"data/raw     : {RAW_DATA_DIR}")
    logger.info(f"data/prepared: {PREPARED_DATA_DIR}")
    logger.info(f"scripts      : {SCRIPTS_DIR}")

    input_file = "products_data.csv"
    output_file = "products_prepared.csv"

    # Read raw data
    df = read_raw_data(input_file)

    # Record original shape
    original_shape = df.shape

    # Log initial dataframe information
    logger.info(f"Initial dataframe columns: {', '.join(df.columns.tolist())}")
    logger.info(f"Initial dataframe shape: {df.shape}")

    # Clean column names
    original_columns = df.columns.tolist()
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Log if any column names changed
    changed_columns = [
        f"{old} -> {new}" for old, new in zip(original_columns, df.columns) if old != new
    ]
    if changed_columns:
        logger.info(f"Cleaned column names: {', '.join(changed_columns)}")

    # Add product-related columns
    df = add_product_columns(df)

    # Remove duplicates
    df = remove_duplicates(df)

    # Handle missing values
    df = handle_missing_values(df)

    # Clean the new columns
    df = clean_stock_quantity(df)
    df = clean_product_category(df)

    # Remove outliers
    df = remove_outliers(df)

    # Validate data
    df = validate_data(df)

    # Standardize formats
    df = standardize_formats(df)

    # Save prepared data
    save_prepared_data(df, output_file)

    logger.info("==================================")
    logger.info(f"Original shape: {original_shape}")
    logger.info(f"Cleaned shape:  {df.shape}")
    logger.info("==================================")
    logger.info("FINISHED prepare_products_data.py")
    logger.info("==================================")


# -------------------
# Conditional Execution Block
# -------------------

if __name__ == "__main__":
    main()
