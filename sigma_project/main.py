from flask import Flask, request, jsonify
import os
import shutil
from celery_app import celery_app
from celery.result import AsyncResult
from dotenv import load_dotenv
import uuid
from tasks import process_pdf_task # Assuming your task is in tasks.py
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

load_dotenv()  

# Access environment variables
TESSERACT_PATH="Tesseract-OCR/tesseract.exe"
POPPLER_PATH="Poppler/poppler-25.07.0/Library/bin"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


@app.route("/upload-pdf/", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    # Generate unique filename to avoid collisions
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    print(TESSERACT_PATH,POPPLER_PATH)
    # Submit Celery task without importing it directly
    task = process_pdf_task.delay(file_path,TESSERACT_PATH,POPPLER_PATH,GOOGLE_API_KEY)
    return jsonify({"task_id": task.id, "status": "submitted"})


@app.route("/task-status/<task_id>", methods=["GET"])
def task_status(task_id):
    task_result = AsyncResult(task_id, app=celery_app)
    return jsonify({
        "status": task_result.state,
        "result": str(task_result.result) if task_result.successful() else None
    })


if __name__ == "__main__":
    app.run(debug=True)
