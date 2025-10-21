from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class LoanApplicationBase(BaseModel):
    company_name: str
    company_number: str
    business_type: str
    industry: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    loan_amount: float
    loan_purpose: str
    annual_revenue: float
    years_in_business: int

class LoanApplicationCreate(LoanApplicationBase):
    uploaded_files: Optional[List[Dict]] = []

class LoanApplicationResponse(LoanApplicationBase):
    application_id: str
    status: str
    ai_decision: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AIAnalysisResponse(BaseModel):
    application_id: str
    decision: str
    confidence: float
    risk_level: str
    risk_score: float
    decision_factors: List[Dict]
    strengths: List[str]
    concerns: List[str]
    recommendation: str
    model_version: str
    analysis_timestamp: datetime

class AdminReviewRequest(BaseModel):
    final_decision: str
    admin_notes: str
    reviewed_by: str

class DashboardStats(BaseModel):
    total_applications: int
    pending_review: int
    approved: int
    rejected: int
    approval_rate: float
    average_processing_time: float
    risk_distribution: Dict[str, int]