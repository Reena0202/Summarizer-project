import time
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import nltk
nltk.download('punkt_tab')
import os
import shutil
from helper import *

app = FastAPI()

# Directory to store uploaded PDFs
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve static HTML files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload-pdf/")
def upload_pdf(request: Request, file: UploadFile = File(...)):
    """Accept a PDF upload and save it to disk."""
    if not file.filename.lower().endswith(".pdf"):
        return HTMLResponse(content="Only PDF files are allowed.", status_code=400)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = text_extract(file_path)
    summary = summarize_with_sumy(text)
    insert_into_db(str(time.time()), filename = file.filename, summary = summary)

    return templates.TemplateResponse("display.html", {"request": request, "summary": summary, "filename": file.filename})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)