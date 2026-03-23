"""
processing.py — Pandas data processing and analysis for InsightCloud.
Provides functions to analyze uploaded CSV datasets.
"""

from typing import Optional

import pandas as pd

from upload import load_file_as_df


def load_dataset(filename: str) -> Optional[pd.DataFrame]:
    """
    Load a CSV dataset using upload module's dual-mode loader.
    Works for both local and S3 storage modes.

    Args:
        filename: Name of the CSV file to load.

    Returns:
        pandas DataFrame, or None if file not found.
    """
    return load_file_as_df(filename)


def get_summary(df: pd.DataFrame) -> dict:
    """
    Generate a comprehensive summary of the DataFrame.

    Args:
        df: pandas DataFrame to analyze.

    Returns:
        Dictionary containing shape, columns, dtypes, descriptive statistics,
        null counts, and a preview of the first 5 rows.
    """
    return {
        "shape": {
            "rows": df.shape[0],
            "columns": df.shape[1]
        },
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "describe": df.describe(include="all").to_dict(),
        "null_counts": {col: int(count) for col, count in df.isnull().sum().items()},
        "preview": df.head(5).to_dict(orient="records")
    }


def get_grouped_stats(df: pd.DataFrame, group_col: str, agg_col: str) -> dict:
    """
    Group data by a column and aggregate another column by sum.

    Args:
        df: pandas DataFrame to analyze.
        group_col: Column name to group by.
        agg_col: Column name to aggregate (sum).

    Returns:
        Dictionary with grouped results sorted by aggregated value (descending).

    Raises:
        ValueError: If specified columns don't exist in the DataFrame.
    """
    if group_col not in df.columns:
        raise ValueError(f"Column '{group_col}' not found in dataset.")
    if agg_col not in df.columns:
        raise ValueError(f"Column '{agg_col}' not found in dataset.")

    grouped = (
        df.groupby(group_col)[agg_col]
        .sum()
        .sort_values(ascending=False)
    )

    return {
        "group_column": group_col,
        "agg_column": agg_col,
        "results": grouped.to_dict(),
        "total": float(grouped.sum())
    }


def get_column_stats(df: pd.DataFrame, column: str) -> dict:
    """
    Get detailed statistics for a single column.

    For numeric columns: mean, median, min, max, std, quartiles.
    For categorical columns: value_counts, unique count, most common.

    Args:
        df: pandas DataFrame to analyze.
        column: Column name to analyze.

    Returns:
        Dictionary with column statistics.

    Raises:
        ValueError: If specified column doesn't exist in the DataFrame.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in dataset.")

    col_data = df[column]
    stats = {
        "column": column,
        "dtype": str(col_data.dtype),
        "total_values": len(col_data),
        "null_count": int(col_data.isnull().sum()),
        "unique_count": int(col_data.nunique())
    }

    if pd.api.types.is_numeric_dtype(col_data):
        # Numeric column statistics
        stats.update({
            "type": "numeric",
            "mean": float(col_data.mean()) if not col_data.empty else None,
            "median": float(col_data.median()) if not col_data.empty else None,
            "min": float(col_data.min()) if not col_data.empty else None,
            "max": float(col_data.max()) if not col_data.empty else None,
            "std": float(col_data.std()) if not col_data.empty else None,
            "q25": float(col_data.quantile(0.25)) if not col_data.empty else None,
            "q75": float(col_data.quantile(0.75)) if not col_data.empty else None,
        })
    else:
        # Categorical column statistics
        value_counts = col_data.value_counts().head(10)  # Top 10 values
        stats.update({
            "type": "categorical",
            "value_counts": value_counts.to_dict(),
            "most_common": str(value_counts.index[0]) if not value_counts.empty else None,
            "most_common_count": int(value_counts.iloc[0]) if not value_counts.empty else None,
        })

    return stats
