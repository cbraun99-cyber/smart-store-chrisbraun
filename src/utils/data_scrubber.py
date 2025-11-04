"""
utils/data_scrubber.py

Data cleaning utilities for common data preparation tasks.
"""

import pandas as pd
from utils.logger import logger


class DataScrubber:
    """
    A class for common data cleaning operations.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to clean.
        """
        self.df = df.copy()
        logger.info(f"DataScrubber initialized with DataFrame shape: {self.df.shape}")

    def remove_duplicate_records(self) -> pd.DataFrame:
        """
        Remove duplicate rows from the DataFrame.

        Returns:
            pd.DataFrame: DataFrame with duplicates removed.
        """
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates()
        removed_count = initial_count - len(self.df)

        logger.info(f"Removed {removed_count} duplicate records")
        logger.info(f"Records remaining: {len(self.df)}")

        return self.df

    def clean_column_names(self) -> pd.DataFrame:
        """
        Standardize column names: strip, lowercase, replace spaces.

        Returns:
            pd.DataFrame: DataFrame with cleaned column names.
        """
        original_columns = self.df.columns.tolist()
        self.df.columns = (
            self.df.columns.str.strip()
            .str.lower()
            .str.replace(' ', '_')
            .str.replace(r'[^\w_]', '', regex=True)
        )

        # Log changes
        changed_columns = [
            f"{old} -> {new}" for old, new in zip(original_columns, self.df.columns) if old != new
        ]
        if changed_columns:
            logger.info(f"Cleaned column names: {', '.join(changed_columns)}")

        return self.df

    def get_missing_summary(self) -> pd.Series:
        """
        Get summary of missing values.

        Returns:
            pd.Series: Series with missing value counts per column.
        """
        return self.df.isna().sum()
