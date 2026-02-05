from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from core.security import verify_token
from services.pdf_service import pdf_to_json
from repositorys.report_repository import save_report, get_user_reports, get_report_by_id

report_router = APIRouter()

@report_router.post("/pdf-to-json")
async def pdf_to_json_router(
    file: UploadFile = File(...),
    payload: dict = Depends(verify_token)
):
    """
    Convertit un fichier PDF en JSON et le sauvegarde
    
    - **file**: Le fichier PDF à convertir
    - **token**: JWT token requis dans le header Authorization
    
    Retourne les données extraites du PDF en JSON
    """
    try:
        # Vérifier que c'est un PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être un PDF"
            )
        
        # Lire le contenu du fichier
        pdf_bytes = await file.read()
        
        if len(pdf_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Le fichier PDF est vide"
            )
        
        # Convertir PDF en JSON
        result = pdf_to_json(pdf_bytes)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Erreur lors de la conversion du PDF")
            )
        
        # Sauvegarder le rapport en base de données
        user_id = payload.get("user_id")
        report_id = save_report(
            user_id=user_id,
            filename=file.filename,
            content=result.get("content"),
            extracted_data=result.get("metadata")
        )
        
        return {
            "success": True,
            "report_id": report_id,
            "filename": file.filename,
            "message": "Fichier PDF converti et enregistré avec succès",
            "data": {
                "content": result.get("content"),
                "metadata": result.get("metadata")
            }
        }
        
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )

@report_router.get("/reports")
async def get_user_reports_router(payload: dict = Depends(verify_token)):
    """
    Récupère tous les rapports de l'utilisateur authentifié
    Nécessite un JWT token valid
    """
    try:
        user_id = payload.get("user_id")
        reports = get_user_reports(user_id)
        
        return {
            "success": True,
            "total": len(reports),
            "reports": reports
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )

@report_router.get("/reports/{report_id}")
async def get_report_router(
    report_id: str,
    payload: dict = Depends(verify_token)
):
    """
    Récupère un rapport spécifique par son ID
    """
    try:
        report = get_report_by_id(report_id)
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail="Rapport non trouvé"
            )
        
        # Vérifier que l'utilisateur a accès à ce rapport
        if report.get("user_id") != payload.get("user_id"):
            raise HTTPException(
                status_code=403,
                detail="Accès refusé à ce rapport"
            )
        
        return {
            "success": True,
            "report": report
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur: {str(e)}"
        )
