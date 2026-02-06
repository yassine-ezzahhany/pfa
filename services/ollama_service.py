import requests
import json
import os
from typing import Dict, Tuple
from time import sleep

# Configuration Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_RETRY_ATTEMPTS = int(os.getenv("OLLAMA_RETRY_ATTEMPTS", "3"))

# Endpoint d'Ollama
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"


def check_ollama_health() -> Tuple[bool, str]:
    
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        response.raise_for_status()
        
        models = response.json().get("models", [])
        model_names = [m.get("name", "").split(":")[0] for m in models]
        
        if OLLAMA_MODEL.split(":")[0] not in model_names:
            return False, f"Modèle '{OLLAMA_MODEL}' non disponible. Modèles disponibles: {', '.join([m.get('name', '') for m in models])}"
        
        return True, f"Ollama est accessible. Modèle '{OLLAMA_MODEL}' trouvé."
        
    except requests.exceptions.ConnectionError:
        return False, f"Impossible de se connecter à Ollama ({OLLAMA_BASE_URL})"
    except requests.exceptions.Timeout:
        return False, "Timeout lors de la vérification d'Ollama"
    except Exception as e:
        return False, f"Erreur lors de la vérification d'Ollama: {str(e)}"


def call_ollama_with_retry(prompt: str, system_message: str = "") -> Tuple[bool, str]:
    
    messages = []
    
    if system_message:
        messages.append({
            "role": "system",
            "content": system_message
        })
    
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    for attempt in range(OLLAMA_RETRY_ATTEMPTS):
        try:
            response = requests.post(
                OLLAMA_CHAT_ENDPOINT,
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.3  # Basse température pour des réponses plus déterministes
                },
                timeout=OLLAMA_TIMEOUT
            )
            
            response.raise_for_status()
            
            result = response.json()
            content = result.get("message", {}).get("content", "").strip()
            
            if not content:
                if attempt < OLLAMA_RETRY_ATTEMPTS - 1:
                    sleep(2)
                    continue
                return False, "Réponse vide d'Ollama"
            
            return True, content
            
        except requests.exceptions.Timeout:
            error_msg = f"Timeout Ollama (tentative {attempt + 1}/{OLLAMA_RETRY_ATTEMPTS})"
            if attempt == OLLAMA_RETRY_ATTEMPTS - 1:
                return False, error_msg
            sleep(2)
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erreur de connexion Ollama: {str(e)}"
            if attempt == OLLAMA_RETRY_ATTEMPTS - 1:
                return False, error_msg
            sleep(2)
            
        except Exception as e:
            error_msg = f"Erreur Ollama: {str(e)}"
            if attempt == OLLAMA_RETRY_ATTEMPTS - 1:
                return False, error_msg
            sleep(2)
    
    return False, "Impossible de communiquer avec Ollama après plusieurs tentatives"


def extract_json_from_response(response_text: str) -> Tuple[bool, Dict]:
   
    try:
        # Essayer le parsing direct
        return True, json.loads(response_text)
        
    except json.JSONDecodeError:
        # Si parsing direct échoue, chercher le JSON dans le texte
        try:
            # Trouver le premier { et le dernier }
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end <= json_start:
                return False, {}
            
            json_text = response_text[json_start:json_end]
            return True, json.loads(json_text)
            
        except (json.JSONDecodeError, ValueError) as e:
            return False, {"error": f"JSON invalide: {str(e)}"}


def is_medical_report(extracted_text: str) -> Dict:
    system_message = """Tu es un expert médical qui analyse des documents.
Réponds UNIQUEMENT avec du JSON valide, sans aucun texte avant ou après.
Aucune explication, aucun markdown, juste le JSON."""
    
    validation_prompt = """Analysez ce texte et déterminez si c'est un rapport médical ou un document de santé.

Répondez STRICTEMENT en JSON valide:
{
    "is_medical_report": true ou false,
    "confidence": nombre entre 0 et 100,
    "reason": "explication courte en français"
}

Texte à analyser:

""" + extracted_text[:2000]

    success, response = call_ollama_with_retry(validation_prompt, system_message)
    
    if not success:
        return {
            "is_medical_report": False,
            "confidence": 0,
            "reason": f"Erreur Ollama: {response}"
        }
    
    json_ok, json_data = extract_json_from_response(response)
    
    if not json_ok:
        return {
            "is_medical": False,
            "confidence": 0,
            "reason": f"Réponse JSON invalide de Ollama"
        }
    
    return {
        "is_medical": json_data.get("is_medical_report", False),
        "confidence": json_data.get("confidence", 0),
        "reason": json_data.get("reason", "")
    }


def analyze_pdf_with_ai(extracted_text: str) -> Dict:
    
    system_message = """Tu es un expert médical spécialisé dans l'extraction d'informations cliniques.
Ton rôle est de lire un rapport médical et en extraire les informations clés en format JSON.

Réponds UNIQUEMENT avec du JSON valide et complet, sans aucun texte avant ou après.
Pas de markdown, pas d'explications, juste le JSON bien formaté."""
    
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
- Valider que le JSON est bien structuré

Rapport médical à analyser:

""" + extracted_text[:6000]  # Augmenter la limite de contexte

    success, response = call_ollama_with_retry(analysis_prompt, system_message)
    
    if not success:
        return {
            "success": False,
            "error": f"Erreur Ollama: {response}",
            "analysis": None,
            "model_used": OLLAMA_MODEL
        }
    
    json_ok, json_data = extract_json_from_response(response)
    
    if not json_ok:
        # Si le JSON est invalide, essayer de le corriger ou retourner l'erreur
        return {
            "success": False,
            "error": "Réponse JSON invalide d'Ollama",
            "analysis": None,
            "model_used": OLLAMA_MODEL,
            "raw_response": response
        }
    
    return {
        "success": True,
        "analysis": json_data,
        "model_used": OLLAMA_MODEL
    }


def test_ollama_connection() -> Dict:
   
    health_ok, health_msg = check_ollama_health()
    
    result = {
        "ollama_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "health_status": health_ok,
        "health_message": health_msg
    }
    
    if health_ok:
        # Tester avec un prompt simple
        test_prompt = "Réponds avec du JSON: {\"test\": \"ok\"}"
        success, response = call_ollama_with_retry(test_prompt)
        result["api_test"] = success
        result["api_message"] = response if success else f"Erreur: {response}"
    
    return result
