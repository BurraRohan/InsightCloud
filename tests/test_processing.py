"""
test_processing.py — Tests for InsightCloud data processing module.
Tests Pandas analysis, summary stats, groupby, and column stats.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from processing import get_summary, get_grouped_stats, get_column_stats


# ─── Test DataFrames ──────────────────────────────────────

@pytest.fixture
def sample_df():
    """Create a sample sales DataFrame for testing."""
    return pd.DataFrame({
        "product": ["Widget A", "Widget B", "Widget A", "Widget C", "Widget B"],
        "region": ["North", "South", "East", "North", "West"],
        "sales": [1200, 800, 1500, 600, 950],
        "units": [24, 16, 30, 12, 19],
    })


@pytest.fixture
def df_with_nulls():
    """Create a DataFrame with null values for testing."""
    return pd.DataFrame({
        "name": ["Alice", "Bob", None, "Diana"],
        "score": [85, None, 72, 90],
        "grade": ["A", "B", "C", None],
    })


@pytest.fixture
def numeric_df():
    """Create a purely numeric DataFrame."""
    return pd.DataFrame({
        "temperature": [22.5, 25.0, 18.3, 30.1, 27.8],
        "humidity": [65, 70, 80, 55, 60],
        "pressure": [1013, 1010, 1015, 1008, 1012],
    })


# ─── Summary Tests ────────────────────────────────────────

def test_summary_returns_dict(sample_df):
    """Test that get_summary returns a dictionary."""
    result = get_summary(sample_df)
    assert isinstance(result, dict)


def test_summary_has_shape(sample_df):
    """Test that summary includes correct shape."""
    result = get_summary(sample_df)
    assert result["shape"]["rows"] == 5
    assert result["shape"]["columns"] == 4


def test_summary_has_columns(sample_df):
    """Test that summary includes column names."""
    result = get_summary(sample_df)
    assert "product" in result["columns"]
    assert "sales" in result["columns"]
    assert len(result["columns"]) == 4


def test_summary_has_dtypes(sample_df):
    """Test that summary includes data types."""
    result = get_summary(sample_df)
    assert "product" in result["dtypes"]
    assert "int64" in result["dtypes"]["sales"]


def test_summary_has_describe(sample_df):
    """Test that summary includes descriptive statistics."""
    result = get_summary(sample_df)
    assert "describe" in result
    assert isinstance(result["describe"], dict)


def test_summary_has_null_counts(sample_df):
    """Test that summary includes null counts."""
    result = get_summary(sample_df)
    assert result["null_counts"]["product"] == 0
    assert result["null_counts"]["sales"] == 0


def test_summary_null_detection(df_with_nulls):
    """Test that nulls are correctly detected."""
    result = get_summary(df_with_nulls)
    assert result["null_counts"]["name"] == 1
    assert result["null_counts"]["score"] == 1
    assert result["null_counts"]["grade"] == 1


def test_summary_has_preview(sample_df):
    """Test that summary includes first 5 rows preview."""
    result = get_summary(sample_df)
    assert "preview" in result
    assert len(result["preview"]) == 5


def test_summary_preview_has_correct_data(sample_df):
    """Test that preview contains actual data values."""
    result = get_summary(sample_df)
    first_row = result["preview"][0]
    assert first_row["product"] == "Widget A"
    assert first_row["sales"] == 1200


# ─── Grouped Stats Tests ─────────────────────────────────

def test_grouped_stats_basic(sample_df):
    """Test basic groupby operation."""
    result = get_grouped_stats(sample_df, "product", "sales")
    assert "results" in result
    assert result["group_column"] == "product"
    assert result["agg_column"] == "sales"


def test_grouped_stats_correct_values(sample_df):
    """Test that grouped values are correct."""
    result = get_grouped_stats(sample_df, "product", "sales")
    # Widget A: 1200 + 1500 = 2700
    assert result["results"]["Widget A"] == 2700
    # Widget B: 800 + 950 = 1750
    assert result["results"]["Widget B"] == 1750


def test_grouped_stats_sorted_descending(sample_df):
    """Test that results are sorted by value descending."""
    result = get_grouped_stats(sample_df, "product", "sales")
    values = list(result["results"].values())
    assert values == sorted(values, reverse=True)


def test_grouped_stats_has_total(sample_df):
    """Test that total sum is included."""
    result = get_grouped_stats(sample_df, "product", "sales")
    assert result["total"] == 5050  # 1200+800+1500+600+950


def test_grouped_stats_invalid_group_column(sample_df):
    """Test that invalid group column raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        get_grouped_stats(sample_df, "nonexistent", "sales")


def test_grouped_stats_invalid_agg_column(sample_df):
    """Test that invalid agg column raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        get_grouped_stats(sample_df, "product", "nonexistent")


# ─── Column Stats Tests ──────────────────────────────────

def test_column_stats_numeric(numeric_df):
    """Test numeric column statistics."""
    result = get_column_stats(numeric_df, "temperature")
    assert result["type"] == "numeric"
    assert result["mean"] is not None
    assert result["median"] is not None
    assert result["min"] == 18.3
    assert result["max"] == 30.1


def test_column_stats_categorical(sample_df):
    """Test categorical column statistics."""
    result = get_column_stats(sample_df, "product")
    assert result["type"] == "categorical"
    assert "value_counts" in result
    assert result["most_common"] is not None


def test_column_stats_null_count(df_with_nulls):
    """Test that column stats include null count."""
    result = get_column_stats(df_with_nulls, "score")
    assert result["null_count"] == 1


def test_column_stats_unique_count(sample_df):
    """Test that unique count is correct."""
    result = get_column_stats(sample_df, "product")
    assert result["unique_count"] == 3  # Widget A, B, C


def test_column_stats_invalid_column(sample_df):
    """Test that invalid column raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        get_column_stats(sample_df, "nonexistent")


def test_column_stats_has_quartiles(numeric_df):
    """Test that numeric stats include quartiles."""
    result = get_column_stats(numeric_df, "temperature")
    assert "q25" in result
    assert "q75" in result
    assert result["q25"] < result["q75"]
