import spacy
from typing import List

# Load a small spaCy model (you would need to install this: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Please install the spaCy model: python -m spacy download en_core_web_sm")
    
def find_loan_repayments_with_spacy(filtered_text: str) -> float:
    """
    Uses spaCy to identify loan repayment debits based on keywords near MONEY entities.
    """
    doc = nlp(filtered_text)
    total_repayments = 0.0
    hsbc_lenders = ["HSBC PLCLOANS", "ALDEMORE", "FUNDING CIRCLE"] 
    lender_keywords=hsbc_lenders
    # Iterate through all recognized entities in the text
    for entity in doc.ents:
        # Check if the entity is a recognized currency amount
        if entity.label_ == "MONEY":
            
            # Look at the words surrounding the money amount (context window)
            context = entity.text.upper() + " " + doc[entity.start - 5 : entity.end + 5].text.upper()
            
            # Check if any lender keyword is in the context
            is_loan_repayment = False
            for keyword in lender_keywords:
                if keyword.upper() in context:
                    is_loan_repayment = True
                    break

            # If it's a loan repayment, we need to ensure it was "Paid out" (Debit).
            # This check is still tricky without knowing the exact table structure. 
            # Assuming the LLM or your OCR preserved the "Paid out" column structure:
            if is_loan_repayment and ('PAID OUT' in context or 'DEBIT' in context or 'DD' in context):
                try:
                    # Clean the amount (remove non-digits except dot)
                    amount = float(re.sub(r'[^\d.]', '', entity.text))
                    total_repayments += amount
                except ValueError:
                    continue # Skip if cleanup fails

    return total_repayments

# --- Example Usage for HSBC Statement ---

# Replace 't' with the clean, filtered text from your Gemini call
# Note: You would run this after the LLM filtering step.
# loan_total = find_loan_repayments_with_spacy(t, hsbc_lenders)
# print(f"Loan Repayments found by spaCy: {loan_total}")
# Expected Output: ~887.37 (for the HSBC PLCLOANS payment)
def identify_entities_with_spacy(filtered_text: str):
    """
    Processes text using spaCy's NER to identify relevant entities 
    for financial parsing (Money, Organization, Date).

    Args:
        filtered_text: The clean text string containing only financial data.

    Returns:
        A list of dictionaries, where each dict represents a found entity 
        with its text, label, and position.
    """
    
    # Process the document text
    doc = nlp(filtered_text)
    
    # Define which labels are most useful for bank statement analysis
    FINANCIAL_LABELS = ["MONEY", "ORG", "DATE", "CARDINAL"]
    entities = []
    for ent in doc.ents:
        if ent.label_ in FINANCIAL_LABELS:
            entities.append({
                "text": ent.text.strip(),
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                # Include the surrounding context to help with classification (e.g., Paid In vs. Paid Out)
                "context": doc[ent.start - 5: ent.end + 5].text.strip().replace('\n', ' ')
            })
    return  entities