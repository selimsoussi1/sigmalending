from google import genai
import os
import json
from pydantic import BaseModel, Field
from typing import Literal
from google.genai.types import GenerateContentConfig

# --- Configuration (Keep your existing API key) ---
# NOTE: Ensure you replace the placeholder with your actual API key if running locally.


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
    property_value: str = Field(
        ...,
        description="The value of the property he owns."
    )
    loan_amounts: str = Field(
        ...,
        description="The total sum of the loans he/she requested ."
    )


# --- File Handling and API Call ---

# NOTE: The file path must be accessible. This assumes the file is already uploaded
# and the client is initialized. We will use the provided file path and name.

def generate_report(text,my_api_key):
 client = genai.Client(api_key=my_api_key) 
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
    "4. The sum of all loan repayments . "
    "5. The earliest statement date. "
    "6. Confirm if 'ALPHA PAINTS LIMITED' is a limited company. "
    "7. State any explicitly mentioned future Loan Intent. If none, state 'N/A'."
    "8. State if he has any property or real estate holdings mentioned in the statement. If none, state 'N/A'."
    "9. State the sum of the loan amounts  he requested in the statement and add it to mortgage costs if mentioned. If none, state 'N/A'"
    
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
    
    return extracted_object
 except Exception as e:
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
    except Exception as e:
     print(f"An error occurred during API call: {e}")
