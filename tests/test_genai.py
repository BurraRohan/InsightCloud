"""
test_genai.py — Tests for InsightCloud GenAI module.
Tests context building, system prompt, and query routing.
Does NOT call actual AI APIs — tests the prompt engineering logic.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from genai import build_context, get_system_prompt, build_user_message


# ─── Test DataFrames ──────────────────────────────────────

@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "product": ["Widget A", "Widget B", "Widget A"],
        "sales": [1200, 800, 1500],
        "region": ["North", "South", "East"],
    })


@pytest.fixture
def df_with_nulls():
    """Create a DataFrame with nulls for testing."""
    return pd.DataFrame({
        "name": ["Alice", None, "Charlie"],
        "score": [85, 72, None],
    })


# ─── Context Building Tests ───────────────────────────────

def test_build_context_returns_string(sample_df):
    """Test that build_context returns a string."""
    context = build_context(sample_df)
    assert isinstance(context, str)
    assert len(context) > 0


def test_build_context_has_row_count(sample_df):
    """Test that context includes correct row count."""
    context = build_context(sample_df)
    assert "3" in context  # 3 rows


def test_build_context_has_column_count(sample_df):
    """Test that context includes correct column count."""
    context = build_context(sample_df)
    assert "3" in context  # 3 columns


def test_build_context_has_column_names(sample_df):
    """Test that context includes actual column names."""
    context = build_context(sample_df)
    assert "product" in context
    assert "sales" in context
    assert "region" in context


def test_build_context_has_dtypes(sample_df):
    """Test that context includes data types."""
    context = build_context(sample_df)
    assert "int64" in context or "float64" in context
    assert "object" in context


def test_build_context_has_sample_data(sample_df):
    """Test that context includes actual data values."""
    context = build_context(sample_df)
    assert "Widget A" in context
    assert "1200" in context
    assert "North" in context


def test_build_context_has_statistics(sample_df):
    """Test that context includes summary statistics."""
    context = build_context(sample_df)
    # Should contain describe() output
    assert "mean" in context.lower() or "count" in context.lower()


def test_build_context_has_null_info(df_with_nulls):
    """Test that context includes null/missing value info."""
    context = build_context(df_with_nulls)
    assert "missing" in context.lower() or "null" in context.lower()


def test_build_context_detects_nulls(df_with_nulls):
    """Test that context correctly reports null counts."""
    context = build_context(df_with_nulls)
    assert "1 missing" in context  # Both columns have 1 null


def test_build_context_overview_section(sample_df):
    """Test that context has dataset overview section."""
    context = build_context(sample_df)
    assert "DATASET OVERVIEW" in context


def test_build_context_column_section(sample_df):
    """Test that context has column names section."""
    context = build_context(sample_df)
    assert "COLUMN NAMES" in context


# ─── System Prompt Tests ──────────────────────────────────

def test_system_prompt_returns_string():
    """Test that system prompt is a non-empty string."""
    prompt = get_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 100


def test_system_prompt_has_instructions():
    """Test that system prompt contains key instructions."""
    prompt = get_system_prompt()
    assert "ONLY use information from the dataset" in prompt


def test_system_prompt_has_few_shot_example():
    """Test that system prompt contains a few-shot example."""
    prompt = get_system_prompt()
    assert "EXAMPLE" in prompt
    assert "Good answer" in prompt
    assert "Bad answer" in prompt


def test_system_prompt_requires_numbers():
    """Test that system prompt asks for specific numbers."""
    prompt = get_system_prompt()
    assert "specific numbers" in prompt.lower()


def test_system_prompt_mentions_recommendations():
    """Test that system prompt asks for recommendations."""
    prompt = get_system_prompt()
    assert "recommendation" in prompt.lower()


# ─── User Message Tests ───────────────────────────────────

def test_build_user_message_has_question(sample_df):
    """Test that user message includes the question."""
    msg = build_user_message("What is the top product?", sample_df)
    assert "What is the top product?" in msg


def test_build_user_message_has_context(sample_df):
    """Test that user message includes dataset context."""
    msg = build_user_message("test question", sample_df)
    assert "product" in msg
    assert "sales" in msg
    assert "Widget A" in msg


def test_build_user_message_has_instruction(sample_df):
    """Test that user message asks for data-specific insight."""
    msg = build_user_message("test", sample_df)
    assert "data-specific" in msg.lower() or "exact numbers" in msg.lower()


def test_build_user_message_different_questions(sample_df):
    """Test that different questions produce different messages."""
    msg1 = build_user_message("What are the trends?", sample_df)
    msg2 = build_user_message("Show top products", sample_df)
    assert msg1 != msg2


def test_build_user_message_same_context(sample_df):
    """Test that same DataFrame produces same context in messages."""
    msg1 = build_user_message("Q1", sample_df)
    msg2 = build_user_message("Q2", sample_df)
    # Both should have same data context, different questions
    assert "Widget A" in msg1
    assert "Widget A" in msg2
