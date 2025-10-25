import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import PyPDF2

app = FastAPI()

# Directory to store uploaded PDFs
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve static HTML files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_home():
    """Serve the upload page."""
    with open("static/index.html", "r") as f:
        return f.read()


@app.post("/upload-pdf/")
def upload_pdf(file: UploadFile = File(...)):
    """Accept a PDF upload and save it to disk."""
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(content={"error": "Only PDF files are allowed."}, status_code=400)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    #return text

    return {"message": f"File '{file.filename}' uploaded successfully!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)