from fastapi import FastAPI, File, UploadFile
from PyPDF2 import PdfReader

app = FastAPI(title="PDF to Text API")

@app.post("/pdf-to-text")
async def pdf_to_text(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Le fichier doit être un PDF"}

    reader = PdfReader(file.file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return {
        "filename": file.filename,
        "text": text
    }
