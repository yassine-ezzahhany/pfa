import PyPDF2
import io
import os
from typing import Tuple
from services.ollama_service import (
    is_medical_report as ollama_is_medical_report,
    analyze_pdf_with_ai as ollama_analyze_pdf_with_ai,
    check_ollama_health
)

# Configuration Ollama
ai_model = os.getenv("OLLAMA_MODEL", "mistral")

def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[bool, str, str]:
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        total_pages = len(pdf_reader.pages)
        
        if total_pages == 0:
            return False, "", "Le PDF ne contient aucune page"
        
        extracted_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            extracted_text += f"--- Page {page_num + 1} ---\n{text}\n"
        
        return True, extracted_text, ""
        
    except Exception as e:
        return False, "", f"Erreur lors de l'extraction du PDF: {str(e)}"

def is_medical_report(extracted_text: str) -> dict:
    return ollama_is_medical_report(extracted_text)

def analyze_pdf_with_ai(pdf_bytes: bytes, extracted_text: str) -> dict:
    
    return ollama_analyze_pdf_with_ai(extracted_text)

def pdf_to_json(pdf_bytes: bytes) -> dict:
    # 1. Extraire le texte du PDF
    success, text, error = extract_text_from_pdf(pdf_bytes)
    
    if not success:
        return {
            "success": False,
            "error": error,
            "content": ""
        }
    
    # 2. Vérifier que c'est un rapport médical
    validation = is_medical_report(text)
    
    if not validation.get("is_medical"):
        return {
            "success": False,
            "error": f"Ce document n'est pas un rapport médical. Raison: {validation.get('reason')}",
            "content": "",
            "validation": validation
        }
    
    # 3. Analyser avec Ollama
    ai_analysis = analyze_pdf_with_ai(pdf_bytes, text)
    
    if not ai_analysis.get("success"):
        return {
            "success": False,
            "error": ai_analysis.get("error", "Erreur inconnue lors de l'analyse IA"),
            "raw_content": "",
            "structured_data": None
        }
    
    # 4. Structurer la réponse
    json_data = {
        "success": True,
        "raw_content": text,
        "structured_data": ai_analysis.get("analysis", ""),
        "model_used": ai_analysis.get("model_used", ai_model),
        "metadata": {
            "total_pages": len(PyPDF2.PdfReader(io.BytesIO(pdf_bytes)).pages),
            "extracted": True,
            "ai_processed": True,
            "medical_validated": True,
            "validation_confidence": validation.get("confidence", 0)
        }
    }
    
    return json_data