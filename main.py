import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
nltk.download('punkt_tab')
import os
import shutil
import PyPDF2

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

def text_extract(file_path):
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def summarize_with_sumy(text, sentence_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentence_count)
    summarized_text = " ".join(str(sentence) for sentence in summary)
    return summarized_text

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

    return templates.TemplateResponse("display.html", {"request": request, "summary": summary, "filename": file.filename})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)