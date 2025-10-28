from pdf2image import convert_from_path

import pytesseract

import easyocr
def scanned_ocr_extraction(path,Tesseract,Poppler):
 TESSERACT_PATH = Tesseract
 pytesseract.pytesseract.tesseract_cmd =TESSERACT_PATH
 POPPLER_PATH = Poppler
 pages = convert_from_path(path, dpi=300,poppler_path=POPPLER_PATH)  # dpi=300 for better OCR
 reader = easyocr.Reader(['en'])
 all_text = ""
 for i, page in enumerate(pages):
    # Convert PIL image to numpy array
    import numpy as np
    page_array = np.array(page)
    result = reader.readtext(page_array)
    page_text = " ".join([text for _, text, _ in result])
    all_text += page_text + "\n"
    print(all_text)

 return(all_text)


