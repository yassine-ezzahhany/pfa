import PyPDF2
import io
import os
import base64
from typing import Tuple
from openai import OpenAI

# Initialiser le client OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
ai_model = os.getenv("AI_MODEL", "gpt-4-vision-preview")
client = OpenAI(api_key=openai_api_key)

def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[bool, str, str]:
    """
    Extrait le texte d'un fichier PDF
    
    Args:
        pdf_bytes: Contenu du fichier PDF en bytes
        
    Returns:
        Tuple (success: bool, text: str, error_message: str)
    """
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

def analyze_pdf_with_ai(pdf_bytes: bytes, extracted_text: str) -> dict:
    """
    Analyse le PDF avec un modèle IA (OpenAI GPT-4 Vision) 
    pour extraire et structurer les données de manière intelligente
    
    Args:
        pdf_bytes: Contenu du fichier PDF en bytes
        extracted_text: Texte préalablement extrait du PDF
        
    Returns:
        dict contenant les données analysées par l'IA
    """
    try:
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY non configurée dans l'environnement")
        
        # Converter le PDF en base64 pour l'API vision
        pdf_base64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
        
        # Prompt pour analyser le rapport médical
        analysis_prompt = """
        Analysez le contenu du rapport médical fourni et structurez les informations en JSON.
        
        Extrachez et organisez les éléments suivants si présents:
        - Informations du patient (nom, prénom, âge, date de naissance, sexe)
        - Informations du médecin (nom, spécialité, établissement)
        - Diagnostic principal et secondaires
        - Symptômes observés
        - Examens et tests effectués (avec résultats si disponibles)
        - Traitements prescrits
        - Recommandations et conseils
        - Date de la consultation
        - Notes spéciales ou observations importantes
        
        Fournissez la réponse en JSON structuré et bien organisé.
        """
        
        # Appeler l'API OpenAI avec vision
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "text",
                            "text": f"Voici le texte extrait du PDF:\n\n{extracted_text[:4000]}"
                        }
                    ]
                }
            ]
        ) if "claude" in ai_model else client.chat.completions.create(
            model=ai_model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt
                        },
                        {
                            "type": "text",
                            "text": f"Voici le texte extrait du PDF:\n\n{extracted_text[:4000]}"
                        }
                    ]
                }
            ]
        )
        
        # Extraire la réponse
        response_text = message.content[0].text
        
        return {
            "success": True,
            "analysis": response_text,
            "model_used": ai_model
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors de l'analyse IA du PDF: {str(e)}",
            "model_used": ai_model
        }

def pdf_to_json(pdf_bytes: bytes) -> dict:
    """
    Convertit un PDF en JSON en utilisant l'IA pour l'analyse intelligente
    
    Args:
        pdf_bytes: Contenu du fichier PDF en bytes
        
    Returns:
        dict contenant les données extraites et analysées
    """
    # 1. Extraire le texte du PDF
    success, text, error = extract_text_from_pdf(pdf_bytes)
    
    if not success:
        return {
            "success": False,
            "error": error,
            "content": ""
        }
    
    # 2. Analyser avec l'IA
    ai_analysis = analyze_pdf_with_ai(pdf_bytes, text)
    
    # 3. Structurer la réponse
    json_data = {
        "success": ai_analysis.get("success", False),
        "content": text,
        "ai_analysis": ai_analysis.get("analysis", ""),
        "model_used": ai_analysis.get("model_used", ai_model),
        "metadata": {
            "total_pages": len(PyPDF2.PdfReader(io.BytesIO(pdf_bytes)).pages),
            "extracted": True,
            "ai_processed": True
        }
    }
    
    if not ai_analysis.get("success"):
        json_data["error"] = ai_analysis.get("error", "Erreur inconnue lors de l'analyse IA")
    
    return json_data
