"""
genai.py — GenAI integration with TRIPLE MODE for InsightCloud.

AI_MODE=gemini  → Uses Google Gemini 2.5 Flash (FREE — no credit card)
AI_MODE=groq    → Uses Groq LLaMA 3.3 70B (FREE — no credit card, super fast)
AI_MODE=bedrock → Uses AWS Bedrock Claude 3 Haiku (for AWS production)

Gemini free tier: 250 requests/day, 10 requests/minute
Groq free tier: 14,400 requests/day, 30 requests/minute
Get keys at: https://ai.google.dev (Gemini) | https://console.groq.com (Groq)

All modes use the SAME prompt engineering:
- Context injection: real dataset info sent with every query
- Few-shot example: teaches the model the desired answer format
- Result: AI answers ONLY based on the uploaded CSV data
"""

import json
from typing import Optional

import pandas as pd

from config import (
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    BEDROCK_MODEL_ID,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    is_bedrock_mode,
    is_groq_mode,
)


def get_bedrock_client():
    """
    Create and return a boto3 Bedrock Runtime client.

    Uses explicit credentials if provided (for local development),
    otherwise falls back to IAM role credentials (recommended for EC2).

    Returns:
        boto3 Bedrock Runtime client instance.
    """
    import boto3

    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        return boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    else:
        return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def get_gemini_model():
    """
    Create and return a Google Gemini client.

    Uses the free Gemini API key from .env.
    Get your free key at: https://ai.google.dev

    Returns:
        google.genai.Client instance.
    """
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)
    return client


def get_groq_client():
    """
    Create and return a Groq client.

    Uses the free Groq API key from .env.
    Get your free key at: https://console.groq.com
    No credit card needed.

    Returns:
        groq.Groq client instance.
    """
    from groq import Groq

    return Groq(api_key=GROQ_API_KEY)


def build_context(df: pd.DataFrame) -> str:
    """
    Extract real data from the pandas DataFrame to inject into the prompt.
    This is SHARED between all AI modes (Gemini, Groq, Bedrock).
    Ensures the AI ONLY answers based on the actual uploaded dataset.

    Args:
        df: pandas DataFrame of the uploaded dataset.

    Returns:
        Formatted string containing dataset context for the LLM.
    """
    column_info = "\n".join(f"  - {col}: {df[col].dtype}" for col in df.columns)

    null_info = "\n".join(
        f"  - {col}: {df[col].isnull().sum()} missing" for col in df.columns
    )

    try:
        describe_str = df.describe(include="all").to_string()
    except Exception:
        describe_str = "Unable to generate summary statistics."

    try:
        sample_str = df.head(5).to_string(index=False)
    except Exception:
        sample_str = "Unable to generate sample data."

    context = f"""DATASET OVERVIEW:
- Total Rows: {df.shape[0]}
- Total Columns: {df.shape[1]}

COLUMN NAMES AND DATA TYPES:
{column_info}

SUMMARY STATISTICS:
{describe_str}

FIRST 5 ROWS (Sample Data):
{sample_str}

NULL/MISSING VALUES PER COLUMN:
{null_info}"""

    return context.strip()


def get_system_prompt() -> str:
    """
    Shared system prompt used by ALL AI modes (Gemini, Groq, Bedrock).
    Contains few-shot example to teach the model the desired answer format.

    Returns:
        System prompt string with instructions and few-shot example.
    """
    return """You are InsightCloud AI, a data analyst assistant built into a cloud-native analytics platform.

Your job is to answer questions about the user's uploaded CSV dataset. You MUST:
1. ONLY use information from the dataset provided below. Never make up data.
2. Reference specific numbers, percentages, and column values from the actual data.
3. Be concise but thorough.
4. If the question cannot be answered from the available data, explain exactly why.
5. Provide actionable recommendations when relevant.

EXAMPLE OF THE FORMAT YOU SHOULD FOLLOW:

User question: "Which product had the highest sales?"
Good answer: "**Widget A** leads with total sales of ₹45,000 across all regions, accounting for 38% of total revenue. It outperformed Widget B (₹28,000) by 60.7%. The strongest performance was in the North region (₹18,500). Recommendation: Consider increasing Widget A inventory in high-performing regions."

Bad answer: "Based on the data, it appears that one product may have higher sales than others." (Too vague, no specific numbers)

Now answer the user's question using ONLY the dataset below. Always include specific numbers."""


def build_user_message(question: str, df: pd.DataFrame) -> str:
    """
    Build the user message with dataset context.
    Shared between all AI modes.

    Args:
        question: The user's natural language question.
        df: pandas DataFrame of the uploaded dataset.

    Returns:
        Formatted user message string with dataset context.
    """
    dataset_context = build_context(df)
    return f"""Here is the actual uploaded dataset:

{dataset_context}

---

User Question: {question}

Provide a clear, data-specific insight with exact numbers from the dataset above."""


def ask_with_gemini(question: str, df: pd.DataFrame) -> str:
    """
    Send query to Google Gemini 2.5 Flash (FREE tier).
    Used for LOCAL TESTING when AI_MODE=gemini.
    Free: 250 requests/day, no credit card needed.

    Args:
        question: The user's natural language question.
        df: pandas DataFrame of the uploaded dataset.

    Returns:
        AI-generated insight string, or error message.
    """
    try:
        client = get_gemini_model()

        full_prompt = get_system_prompt() + "\n\n" + build_user_message(question, df)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt,
            config={
                "temperature": 0.2,
                "max_output_tokens": 600,
            }
        )
        return response.text

    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "authentication" in error_msg.lower():
            return (
                "⚠️ Gemini API key not configured. Get your FREE key at "
                "https://ai.google.dev — just sign in with Google, no credit card needed."
            )
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            return (
                "⚠️ Gemini free tier rate limit reached. "
                "Switch to Groq: set AI_MODE=groq in .env and restart."
            )
        return f"⚠️ Gemini API error: {error_msg}"


def ask_with_groq(question: str, df: pd.DataFrame) -> str:
    """
    Send query to Groq LLaMA 3.3 70B (FREE tier).
    Used for LOCAL TESTING when AI_MODE=groq.
    Free: 14,400 requests/day, no credit card needed.
    Super fast inference — responses in under 1 second.

    Get your free key at: https://console.groq.com

    Args:
        question: The user's natural language question.
        df: pandas DataFrame of the uploaded dataset.

    Returns:
        AI-generated insight string, or error message.
    """
    try:
        client = get_groq_client()

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.2,
            max_tokens=600,
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": build_user_message(question, df)}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return (
                "⚠️ Groq API key not configured. Get your FREE key at "
                "https://console.groq.com — no credit card needed."
            )
        elif "rate_limit" in error_msg.lower() or "429" in error_msg:
            return (
                "⚠️ Groq rate limit reached. Wait 60 seconds or "
                "switch to Gemini: set AI_MODE=gemini in .env and restart."
            )
        return f"⚠️ Groq API error: {error_msg}"


def ask_with_bedrock(question: str, df: pd.DataFrame) -> str:
    """
    Send query to AWS Bedrock Mistral Ministral 3 8B.
    Used for AWS PRODUCTION when AI_MODE=bedrock.
    No approval form needed — available instantly.

    Args:
        question: The user's natural language question.
        df: pandas DataFrame of the uploaded dataset.

    Returns:
        AI-generated insight string, or error message.
    """
    try:
        client = get_bedrock_client()

        # Mistral uses a different format than Claude
        # System prompt goes as first message with role "system"
        request_body = json.dumps({
            "messages": [
                {
                    "role": "system",
                    "content": get_system_prompt()
                },
                {
                    "role": "user",
                    "content": build_user_message(question, df)
                }
            ],
            "max_tokens": 600,
            "temperature": 0.2,
        })

        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=request_body
        )

        response_body = json.loads(response["body"].read())
        answer = response_body["choices"][0]["message"]["content"]
        return answer

    except Exception as e:
        error_msg = str(e)
        if "AccessDeniedException" in error_msg:
            return (
                "⚠️ AWS Bedrock access denied. Check your IAM permissions "
                "for bedrock:InvokeModel."
            )
        elif "ThrottlingException" in error_msg:
            return "⚠️ Too many requests. Please wait and try again."
        elif "credentials" in error_msg.lower():
            return (
                "⚠️ AWS credentials not found. Configure credentials in .env "
                "or attach an IAM role to your EC2 instance."
            )
        elif "ValidationException" in error_msg:
            return (
                "⚠️ Model validation error. Check that the model ID is correct "
                "and available in your region."
            )
        return f"⚠️ Bedrock error: {error_msg}"


def ask_question(question: str, df: pd.DataFrame) -> tuple:
    """
    MAIN FUNCTION called by app.py.
    Automatically routes to Gemini, Groq, or Bedrock based on AI_MODE in .env.
    Returns both the answer and the response time.

    - AI_MODE=gemini  → Google Gemini 2.5 Flash (FREE, for local testing)
    - AI_MODE=groq    → Groq LLaMA 3.3 70B (FREE, super fast, for local testing)
    - AI_MODE=bedrock → AWS Bedrock Mistral 8B (for AWS production)

    Args:
        question: The user's natural language question.
        df: pandas DataFrame of the uploaded dataset.

    Returns:
        Tuple of (answer: str, response_time: float in seconds).
    """
    import time
    start = time.time()

    if is_bedrock_mode():
        answer = ask_with_bedrock(question, df)
    elif is_groq_mode():
        answer = ask_with_groq(question, df)
    else:
        answer = ask_with_gemini(question, df)

    elapsed = round(time.time() - start, 2)
    return answer, elapsed