import fitz  # PyMuPDF

# Open the PDF
def extract_text_from_pdf(file):
 pdf = fitz.open(file)

 text = ""
 for page in pdf:
    text += page.get_text()

 print(text)
 return text