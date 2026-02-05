from db.connection import db
from datetime import datetime
from bson.objectid import ObjectId

def save_report(user_id: str, filename: str, content: str, extracted_data: dict = None):
    """
    Enregistre un rapport en base de données
    """
    try:
        result = db.reports.insert_one({
            "user_id": user_id,
            "filename": filename,
            "content": content,
            "extracted_data": extracted_data,
            "created_at": datetime.now()
        })
        return str(result.inserted_id)
    except Exception as e:
        raise ValueError(f"Erreur lors de la sauvegarde du rapport: {str(e)}")

def get_user_reports(user_id: str):
    """
    Récupère tous les rapports d'un utilisateur
    """
    try:
        reports = list(db.reports.find({"user_id": user_id}))
        for report in reports:
            report["_id"] = str(report["_id"])
        return reports
    except Exception as e:
        raise ValueError(f"Erreur lors de la récupération des rapports: {str(e)}")

def get_report_by_id(report_id: str):
    """
    Récupère un rapport spécifique par ID
    """
    try:
        report = db.reports.find_one({"_id": ObjectId(report_id)})
        if report:
            report["_id"] = str(report["_id"])
        return report
    except Exception as e:
        raise ValueError(f"Erreur lors de la récupération du rapport: {str(e)}")

def delete_report(report_id: str):
    """
    Supprime un rapport
    """
    try:
        result = db.reports.delete_one({"_id": ObjectId(report_id)})
        return result.deleted_count > 0
    except Exception as e:
        raise ValueError(f"Erreur lors de la suppression du rapport: {str(e)}")
