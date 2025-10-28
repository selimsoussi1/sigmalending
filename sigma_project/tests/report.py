from google import genai
import os
import json
from pydantic import BaseModel, Field
from typing import Literal
from google.genai.types import GenerateContentConfig

# --- Configuration (Keep your existing API key) ---
# NOTE: Ensure you replace the placeholder with your actual API key if running locally.
MY_API_KEY = "AIzaSyDaU59ZtQgZuyqYB-3_ngUlPc9NQpTQ6Ms"
client = genai.Client(api_key=MY_API_KEY) 

# --- Pydantic Model for Structured Output ---
class FinancialSummary(BaseModel):
    """Structured financial data extracted from a business bank statement."""
    
    # Core Income & Expense Metrics
    monthly_credits: float = Field(
        ..., 
        description="The Total Credits (Payments In) for the statement period, as a float."
    )
    total_expenses: float = Field(
        ..., 
        description="The absolute value of Total Debits (Payments Out) for the statement period, as a float."
    )
    closing_balance: float = Field(
        ...,
        description="The account balance at the close of the statement period."
    )
    
    # Loan & Business Metrics
    total_loan_repayments: float = Field(
        ...,
        description="The sum of all monthly debits identified as loan or financing repayments (e.g., Funding Circle, SAN UK BUS LOANS). Use 0.00 if none are mentioned."
    )
    loan_intent: str = Field(
        ...,
        description="If the document mentions a reason for a future loan application, state it. Otherwise, state 'N/A'."
    )
    is_limited_company: bool = Field(
        ...,
        description="True if the account name is a limited company (e.g., 'LTD' or 'LIMITED'), False otherwise."
    )
    statement_start_date: str = Field(
        ...,
        description="The start date of the statement period (e.g., 1 March 2025)."
    )

# --- File Handling and API Call ---

# NOTE: The file path must be accessible. This assumes the file is already uploaded
# and the client is initialized. We will use the provided file path and name.

def generate_report(text):
# 1. Configuration: Set the LLM's role and force JSON output matching the Pydantic schema
 config = GenerateContentConfig(
    system_instruction=(
        "You are an expert financial analyst. Extract all required values strictly "
        "from the document, calculate sums where necessary, and ensure the output "
        "exactly matches the provided JSON schema."
    ),
    response_mime_type="application/json",
    response_schema=FinancialSummary,
    temperature=0.0  # Keep low for reliable extraction and math
)

# 2. Updated Prompt (Implementing your new instructions)
# The prompt is simplified to focus on the essential metrics.
 prompt_text = (
    "Extract the following exact figures from the bank statement: "
    "1. Total Credits (Payments In). "
    "2. Total Expenses (Total Debits/Payments Out, use the absolute value). "
    "3. The Closing Balance. "
    "4. The sum of all loan repayments (look for 'SAN UK BUS LOANS' or 'Funding Circle'). "
    "5. The earliest statement date. "
    "6. Confirm if 'ALPHA PAINTS LIMITED' is a limited company. "
    "7. State any explicitly mentioned future Loan Intent. If none, state 'N/A'."
)

# 3. Call the API
 
 try:
    response = client.models.generate_content(
        model="gemini-2.5-pro", 
        contents=[
            text, 
            prompt_text
        ],
        config=config
    )

    # 4. Process the response
    json_data = response.text
    print("\n--- Extracted JSON Data ---")
    print(json_data)
    print("---------------------------")

    # Convert the JSON string into a Pydantic object for easy access
    extracted_object = FinancialSummary.model_validate_json(json_data)
    
    # Corrected printing of the extracted data
    print(f"Statement Start: {extracted_object.statement_start_date}")
    print(f"Income (Credits): ${extracted_object.monthly_credits:,.2f}")
    print(f"Expenses (Debits): ${extracted_object.total_expenses:,.2f}")
    print(f"Closing Balance: ${extracted_object.closing_balance:,.2f}")
    print(f"Loan Repayments: ${extracted_object.total_loan_repayments:,.2f}")
    print(f"Loan Intent: {extracted_object.loan_intent}")
    print(f"Is Limited Co: {extracted_object.is_limited_company}")
    return json_data
 except Exception as e:
    print(f"An error occurred during API call: {e}")
