from google import genai
from google.genai.types import GenerateContentConfig
from google import genai
import os

from pydantic import BaseModel, Field
from typing import Literal

from google.genai.types import GenerateContentConfig
# Define the exact structure of the output you need
class LoanApplicationData(BaseModel):  # Rename the model to reflect the data source
    """Structured data extracted from a business bank statement."""
    
    # Extract total credits as a proxy for monthly income
    monthly_credits: float = Field(
        ..., 
        description="The total credit amount for the statement period, as a float."
    )
    
    # Confirm account holder type
    is_limited_company: bool = Field(
        ...,
        description="True if the account name is a limited company (e.g., 'LTD'), False otherwise."
    )
    
    # Extract total monthly loan/financing repayments made
    total_loan_repayments: float = Field(
        ...,
        description="The sum of all monthly debits identified as loan or financing repayments (e.g., Funding Circle, SAN UK BUS LOANS)."
    )
    
    # The statement covers a 31-day period
    statement_start_date: str = Field(
        ...,
        description="The start date of the statement period (e.g., 1 March 2025)."
    )

def filter_financial_text_with_gemini_from_text(statement_text: str,my_api_key:str) -> str:
    client = genai.Client(api_key=my_api_key) 
    """
    Uses the Gemini API to analyze a text string (from OCR) and extract 
    only the core financial and transactional data, filtering out boilerplate 
    text. This prepares the output for final numerical parsing via Regex.

    Args:
        client: The configured google.genai.Client instance.
        statement_text: The full text string extracted from the bank statement via OCR.

    Returns:
        A clean string containing only the essential financial data (summary and transactions).
    """
    
    # --- 1. Define the System Instruction (LLM Role) ---
    system_instruction = (
        "You are an expert financial extraction analyst. Your task is strictly to "
        "locate, extract, and format specific text data points from a bank statement."
    )
    
    # --- 2. Define the Targeted Prompt ---
    # The prompt tells the model exactly what to keep and what to discard.
    prompt_text = (
        "Analyze the following text. Extract ONLY the text from the 'Account Summary' section "
        "and ALL transactional data (Date, Payment type, Paid out, Paid in, Balance). "
        "Do NOT include any text related to contact details, legal information, FSCS, "
        "or interest rates, as those are not financial transactions. "
        "The output must be a single, clean text string containing only the essential financial data."
    )
    
    # --- 3. Configure the API Call ---
    config = GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.0  # Use low temperature for reliable extraction
    )
    print("Filtering text data using Gemini...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            # Pass the text string directly in the contents list
            contents=[
                statement_text, 
                prompt_text
            ],
            config=config
        )   
        return response.text
    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return ""

