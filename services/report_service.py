import requests, inspect, json, re
from io import BytesIO
from typing import BinaryIO
from fastapi import UploadFile
from PyPDF2 import PdfReader
from repositorys.report_repository import (save_report, get_report_by_id as get_report_by_id_repository, get_user_reports as get_user_reports_repository)

def ask_mistral(prompt):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    return res.json()["response"]

def validate_pdf_upload(file: UploadFile) -> None:
    if file is None:
        raise ValueError("Le fichier est requis")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise ValueError("Le fichier doit être au format PDF")

async def pdf_to_text(pdf_file: bytes | BinaryIO | UploadFile) -> str:
    if isinstance(pdf_file, bytes):
        content = pdf_file
    elif hasattr(pdf_file, "read"):
        raw_content = pdf_file.read()
        content = await raw_content if inspect.isawaitable(raw_content) else raw_content
    else:
        raise ValueError("Unsupported PDF input type")

    if not content:
        raise ValueError("The PDF file is empty")

    if not isinstance(content, (bytes, bytearray)):
        raise ValueError("Invalid PDF content: bytes expected")

    reader = PdfReader(BytesIO(bytes(content)))

    pages_text: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages_text.append(page_text)

    return "\n".join(pages_text).strip()

def check_if_medical_report(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Text is required")

    prompt = (
        "You are a strict classifier. Determine if the input is a medical report. "
        "Return ONLY a valid JSON object with this exact schema: "
        '{"is_medical_report": true/false}. '
        "No explanation, no markdown, no extra keys.\n\n"
        f"Input text:\n{text}"
    )

    response = ask_mistral(prompt).strip()

    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", response)
        if not match:
            raise ValueError("Invalid model response format")
        parsed = json.loads(match.group(0))

    is_medical_report = bool(parsed.get("is_medical_report", False))
    return {"is_medical_report": is_medical_report}


def extract_medical_report_json(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Text is required")

    analysis_prompt = """Analysez ce rapport médical et structurez TOUTES les informations en JSON.

Répondez avec STRICTEMENT ce JSON (complétez tous les champs disponibles):
{
    "patient": {
        "nom": "nom complet ou vide",
        "age": "âge numérique ou vide",
        "sexe": "M, F ou vide"
    },
    "diagnostic": ["liste des diagnostics observés"],
    "symptomes": ["liste des symptômes"],
    "traitements": ["liste des traitements prescrits"],
    "examens": ["liste des examens et résultats"],
    "resume_medical": "résumé clinique en 2-3 phrases",
    "medecin": "nom du médecin si disponible",
    "date_consultation": "date ou vide",
    "observations": "observations spéciales"
}

IMPORTANT:
- Les listes ne doivent jamais être vides, mettre au minimum 1 élément par catégorie trouvée
- Utiliser uniquement du français
- Être exhaustif dans l'extraction
- Valider que le JSON est bien structuré"""

    full_prompt = f"{analysis_prompt}\n\nTexte du rapport à analyser:\n{text}"
    response = ask_mistral(full_prompt).strip()

    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", response)
        if not match:
            raise ValueError("Invalid model response format")
        parsed = json.loads(match.group(0))

    if not isinstance(parsed, dict):
        raise ValueError("Invalid model response format")

    return parsed





async def process_pdf_report(file: UploadFile, user_id: str) -> dict:
    validate_pdf_upload(file)

    extracted_text = await pdf_to_text(file)
    classification = check_if_medical_report(extracted_text)

    if not classification["is_medical_report"]:
        raise ValueError("Le document fourni n'est pas un rapport médical")

    extracted_json = extract_medical_report_json(extracted_text)
    document_id = save_report(
        user_id=user_id,
        filename=file.filename,
        extracted_data=extracted_json
    )

    return {
        "document_id": document_id,
    }


def get_report_by_id_service(report_id: str, user_id: str) -> dict:
    report = get_report_by_id_repository(report_id)
    if not report:
        raise ValueError("Rapport non trouvé")

    if str(report.get("user_id")) != str(user_id):
        raise ValueError("Accès non autorisé à ce rapport")

    return report


def get_user_reports_service(user_id: str) -> list[dict]:
    return get_user_reports_repository(user_id)



