from celery_app import celery_app
from is_scanned import is_scanned_pdf
from easyocr_script import scanned_ocr_extraction
from ocr_text import extract_text_from_pdf
from spacy_processing import identify_entities_with_spacy
from report import generate_report
from predictor import predict_loan_approval
@celery_app.task(name="process_pdf_task",bind=True)
def process_pdf_task(self,pdf_path,tesseract,poppler,my_api_key):
    print("Task started for:", pdf_path)
    print("Using Tesseract at:", tesseract)
    print("Using Poppler at:", poppler)
    try:
        is_scanned = is_scanned_pdf(pdf_path,tesseract,poppler)

        if is_scanned:
            text = scanned_ocr_extraction(pdf_path,tesseract,poppler)
        else:
            text = extract_text_from_pdf(pdf_path)

        entities = identify_entities_with_spacy(text)
        context = "\n".join(e["context"] for e in entities[:1500])

        report = generate_report(context,my_api_key)

        # Extract numeric values
        if float(report.monthly_credits) > 0:
            income = report.monthly_credits
            loan_amount = report.total_loan_repayments
        else:
            income = float(''.join(c for c in report.property_value if c.isdigit() or c == '.'))
            loan_amount = float(''.join(c for c in report.loan_amounts if c.isdigit() or c == '.'))

        prediction = predict_loan_approval(income, loan_amount)

        return {"status": "success", "income": income, "loan_amount": loan_amount, "prediction": prediction}
    
    except Exception as e:
        return {"status": "failed", "error": str(e)}
