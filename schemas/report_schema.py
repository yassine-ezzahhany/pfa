from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ReportResponse(BaseModel):
    id: Optional[str] = None
    user_id: str
    filename: str
    content: str
    extracted_data: Optional[dict] = None
    created_at: Optional[datetime] = None
    
class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int

class PDFConversionResult(BaseModel):
    success: bool
    filename: str
    content: str
    message: Optional[str] = None
