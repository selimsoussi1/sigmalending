from is_scanned import is_scanned_pdf
from easyocr_script import scanned_ocr_extraction
pdf_path = "samples/2 prop sheet 1.pdf"
is_scanned = is_scanned_pdf(pdf_path)
print(is_scanned)
t=""
if is_scanned:
    print("PDF is scanned. Extracting text with OCR...")
    t=scanned_ocr_extraction(path=pdf_path)
else:
    print("PDF is text-based. No OCR needed.")
    from ocr_text import extract_text_from_pdf
    t=extract_text_from_pdf(pdf_path)
print(t)

d=t
from spacy_processing import identify_entities_with_spacy
l=identify_entities_with_spacy(d)
context=""
for e in l[0:1500]:
    print(e["label"])
    print(e["context"])
    context+=f"{e['context']}\n"
print(len(l))
from tokens import count_tokens
print(count_tokens(context))
from report import generate_report
z=generate_report(context)
income=0
loan_amount=0
from predictor import predict_loan_approval
if(float(z.monthly_credits>0)):
    income=z.monthly_credits
    loan_amount=z.total_loan_repayments
else:
    p=z.property_value
    l=z.loan_amounts
    numbers_only = ''.join(c for c in p if c.isdigit() or c == '.')
    numbers_only2 = ''.join(c for c in l if c.isdigit() or c == '.')
    income=float(numbers_only)
    loan_amount=float(numbers_only2)
predict_loan_approval(income,loan_amount)