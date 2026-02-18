from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from core.security import verify_token

from services.report_service import get_report_by_id_service, process_pdf_report, get_user_reports_service


report_router = APIRouter()

@report_router.post("")
async def pdf_to_json(
	file: UploadFile = File(...),
	payload: dict = Depends(verify_token)
):
	try:
		user_id = payload.get("user_id")
		if not user_id:
			raise HTTPException(status_code=401, detail="Token invalide: user_id manquant")

		result = await process_pdf_report(file=file, user_id=user_id)

		return {
			"success": True,
			"document_id": result["document_id"],
		}
	except HTTPException:
		raise
	except ValueError as error:
		raise HTTPException(status_code=400, detail=str(error))
	except Exception as error:
		raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(error)}")


@report_router.get("/{report_id}")
async def get_report(report_id: str, payload: dict = Depends(verify_token)):
	try:
		user_id = payload.get("user_id")
		if not user_id:
			raise HTTPException(status_code=401, detail="Token invalide: user_id manquant")

		report = get_report_by_id_service(report_id=report_id, user_id=user_id)
		return {
			"success": True,
			"report": report,
		}
	except HTTPException:
		raise
	except ValueError as error:
		if "non trouvé" in str(error):
			raise HTTPException(status_code=404, detail=str(error))
		if "non autorisé" in str(error):
			raise HTTPException(status_code=403, detail=str(error))
		raise HTTPException(status_code=400, detail=str(error))
	except Exception as error:
		raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(error)}")
@report_router.get("")
async def get_user_reports(payload: dict = Depends(verify_token)):
	try:
		user_id = payload.get("user_id")
		if not user_id:
			raise HTTPException(status_code=401, detail="Token invalide: user_id manquant")

		reports = get_user_reports_service(user_id=user_id)
		return {
			"success": True,
			"reports": reports,
		}
	except HTTPException:
		raise
	except ValueError as error:
		raise HTTPException(status_code=400, detail=str(error))
	except Exception as error:
		raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(error)}")