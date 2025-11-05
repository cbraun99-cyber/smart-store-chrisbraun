"""
utils/data_scrubber.py

A reusable DataScrubber class for common data cleaning tasks.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from utils.logger import logger


class DataScrubber:
    """
    A reusable class for common data cleaning operations.
    """

    def __init__(self, df: pd.DataFrame = None):
        """
        Initialize the DataScrubber with a DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to clean
        """
        self.df = df
        self.original_shape = df.shape if df is not None else (0, 0)

    def set_dataframe(self, df: pd.DataFrame) -> None:
        """Set or update the DataFrame to clean."""
        self.df = df
        self.original_shape = df.shape

    def get_summary(self) -> Dict[str, Any]:
        """Get cleaning summary."""
        if self.df is None:
            return {}

        return {
            'original_shape': self.original_shape,
            'current_shape': self.df.shape,
            'rows_removed': self.original_shape[0] - self.df.shape[0],
            'columns_removed': self.original_shape[1] - self.df.shape[1],
        }

    def clean_column_names(self, case: str = 'lower', replace_spaces: bool = True) -> pd.DataFrame:
        """
        Clean column names by standardizing case and replacing spaces.

        Args:
            case (str): 'lower', 'upper', or 'title'
            replace_spaces (bool): Whether to replace spaces with underscores

        Returns:
            pd.DataFrame: DataFrame with cleaned column names
        """
        if self.df is None or self.df.empty:
            return self.df

        logger.info("Cleaning column names")
        original_columns = self.df.columns.tolist()

        # Apply case transformation
        if case == 'lower':
            self.df.columns = [str(col).lower() for col in self.df.columns]
        elif case == 'upper':
            self.df.columns = [str(col).upper() for col in self.df.columns]
        elif case == 'title':
            self.df.columns = [str(col).title() for col in self.df.columns]

        # Replace spaces with underscores
        if replace_spaces:
            self.df.columns = [col.replace(' ', '_') for col in self.df.columns]

        # Log changes
        changed_columns = [
            f"{old} -> {new}" for old, new in zip(original_columns, self.df.columns) if old != new
        ]
        if changed_columns:
            logger.info(f"Cleaned column names: {', '.join(changed_columns)}")

        return self.df

    def remove_duplicates(self, subset: List[str] = None) -> pd.DataFrame:
        """
        Remove duplicate rows.

        Args:
            subset (List[str]): Columns to consider for identifying duplicates

        Returns:
            pd.DataFrame: DataFrame with duplicates removed
        """
        if self.df is None or self.df.empty:
            return self.df

        logger.info("Removing duplicates")
        initial_count = len(self.df)

        if subset and all(col in self.df.columns for col in subset):
            self.df = self.df.drop_duplicates(subset=subset)
            logger.info(f"Removed duplicates based on columns: {subset}")
        else:
            self.df = self.df.drop_duplicates()
            logger.info("Removed duplicates across all columns")

        removed_count = initial_count - len(self.df)
        logger.info(f"Removed {removed_count} duplicate rows")
        logger.info(f"{len(self.df)} records remaining after removing duplicates.")

        return self.df

    def handle_missing_values(self, strategy: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Handle missing values using specified strategies.

        Args:
            strategy (Dict): Dictionary mapping column names to handling strategies
                           Example: {'column1': 'drop', 'column2': 'fill_0', 'column3': 'fill_unknown'}

        Returns:
            pd.DataFrame: DataFrame with missing values handled
        """
        if self.df is None or self.df.empty:
            return self.df

        logger.info("Handling missing values")

        # Log missing values before handling
        missing_before = self.df.isna().sum()
        logger.info(f"Missing values before handling:\n{missing_before}")

        if strategy:
            for column, method in strategy.items():
                if column in self.df.columns:
                    if method == 'drop':
                        initial_count = len(self.df)
                        self.df = self.df[self.df[column].notna()]
                        removed_count = initial_count - len(self.df)
                        logger.info(f"Removed {removed_count} rows with missing {column}")
                    elif method == 'fill_0':
                        self.df[column] = self.df[column].fillna(0)
                        logger.info(f"Filled missing {column} with 0")
                    elif method == 'fill_unknown':
                        self.df[column] = self.df[column].fillna('Unknown')
                        logger.info(f"Filled missing {column} with 'Unknown'")
                    elif method == 'fill_mean':
                        mean_val = self.df[column].mean()
                        self.df[column] = self.df[column].fillna(mean_val)
                        logger.info(f"Filled missing {column} with mean: {mean_val}")

        # Log missing values after handling
        missing_after = self.df.isna().sum()
        logger.info(f"Missing values after handling:\n{missing_after}")

        return self.df

    def convert_to_numeric(self, columns: List[str]) -> pd.DataFrame:
        """
        Convert specified columns to numeric type.

        Args:
            columns (List[str]): List of column names to convert

        Returns:
            pd.DataFrame: DataFrame with converted columns
        """
        if self.df is None or self.df.empty:
            return self.df

        logger.info(f"Converting columns to numeric: {columns}")

        for col in columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                logger.info(f"Converted {col} to numeric type")

        return self.df

    def remove_outliers_iqr(self, column: str, multiplier: float = 1.5) -> pd.DataFrame:
        """
        Remove outliers using the Interquartile Range (IQR) method.

        Args:
            column (str): Column name to check for outliers
            multiplier (float): IQR multiplier for outlier detection

        Returns:
            pd.DataFrame: DataFrame with outliers removed
        """
        if self.df is None or self.df.empty or column not in self.df.columns:
            return self.df

        logger.info(f"Removing outliers from {column} using IQR method")
        initial_count = len(self.df)

        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        outliers_mask = (self.df[column] < lower_bound) | (self.df[column] > upper_bound)

        if outliers_mask.any():
            self.df = self.df[~outliers_mask]
            logger.info(f"Removed {outliers_mask.sum()} outliers from {column}")
            logger.info(f"Bounds: lower={lower_bound:.2f}, upper={upper_bound:.2f}")

        removed_count = initial_count - len(self.df)
        logger.info(f"Removed {removed_count} outlier rows")

        return self.df

    def standardize_categorical(self, column: str, mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Standardize categorical values using a mapping dictionary.

        Args:
            column (str): Column name to standardize
            mapping (Dict): Dictionary mapping old values to new values

        Returns:
            pd.DataFrame: DataFrame with standardized categorical values
        """
        if self.df is None or self.df.empty or column not in self.df.columns:
            return self.df

        logger.info(f"Standardizing categorical values in {column}")

        self.df[column] = self.df[column].replace(mapping)

        # Log value counts after standardization
        value_counts = self.df[column].value_counts()
        logger.info(f"Value distribution after standardization:\n{value_counts}")

        return self.df

    def validate_data(self, rules: Dict[str, Any]) -> pd.DataFrame:
        """
        Validate data against specified rules.

        Args:
            rules (Dict): Dictionary of validation rules
                        Example: {
                            'unique_columns': ['id'],
                            'range_checks': {'age': (0, 150)},
                            'categorical_checks': {'status': ['active', 'inactive']}
                        }

        Returns:
            pd.DataFrame: Validated DataFrame
        """
        if self.df is None or self.df.empty:
            return self.df

        logger.info("Validating data against rules")

        # Check uniqueness
        if 'unique_columns' in rules:
            for col in rules['unique_columns']:
                if col in self.df.columns:
                    duplicates = self.df.duplicated(subset=[col]).sum()
                    if duplicates > 0:
                        logger.warning(f"Found {duplicates} duplicate values in {col}")

        # Check ranges
        if 'range_checks' in rules:
            for col, (min_val, max_val) in rules['range_checks'].items():
                if col in self.df.columns:
                    out_of_range = self.df[(self.df[col] < min_val) | (self.df[col] > max_val)]
                    if not out_of_range.empty:
                        logger.warning(f"Found {len(out_of_range)} values outside range in {col}")

        # Check categorical values
        if 'categorical_checks' in rules:
            for col, valid_values in rules['categorical_checks'].items():
                if col in self.df.columns:
                    invalid_values = self.df[~self.df[col].isin(valid_values)]
                    if not invalid_values.empty:
                        logger.warning(f"Found {len(invalid_values)} invalid values in {col}")

        logger.info("Data validation completed")
        return self.df
