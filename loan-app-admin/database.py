from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./loan_applications.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LoanApplication(Base):
    __tablename__ = "loan_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String, unique=True, index=True)
    
    # Applicant Information
    company_name = Column(String)
    company_number = Column(String)
    business_type = Column(String)
    industry = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    
    # Financial Information
    loan_amount = Column(Float)
    loan_purpose = Column(String)
    annual_revenue = Column(Float)
    years_in_business = Column(Integer)
    
    # Credit Information (from form or extracted)
    interest_rate = Column(Float)
    debt_to_income = Column(Float)
    credit_score_min = Column(Integer)
    credit_score_max = Column(Integer)
    employment_length = Column(String)
    
    # Document Information
    uploaded_files = Column(JSON)
    documents_verified = Column(Boolean, default=False)
    
    # AI Analysis Results
    ai_decision = Column(String)  # 'approved', 'rejected', 'review_required'
    ai_confidence = Column(Float)  # 0-1 score
    risk_level = Column(String)  # 'low', 'medium', 'high', 'critical'
    risk_score = Column(Float)  # 0-100 score
    
    # Decision Justification
    decision_factors = Column(JSON)  # List of factors that influenced decision
    strengths = Column(JSON)  # Positive factors
    concerns = Column(JSON)  # Negative factors
    recommendation = Column(Text)
    
    # Admin Review
    admin_reviewed = Column(Boolean, default=False)
    final_decision = Column(String)  # 'approved', 'rejected', 'pending'
    admin_notes = Column(Text)
    reviewed_by = Column(String)
    reviewed_at = Column(DateTime)
    
    # Status Tracking
    status = Column(String, default='submitted')  # submitted, processing, reviewed, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

     # N8N Workflow Results
    ocr_data = Column(JSON)  # Store OCR extracted data
    ocr_processed_at = Column(DateTime)
    
    company_verification_data = Column(JSON)  # Company House verification results
    company_verified_at = Column(DateTime)
    company_house_status = Column(String)  # 'verified', 'pending', 'failed'
    
    file_processing_status = Column(String, default='pending')  # File processing status
    workflows_completed = Column(JSON)  # Track which workflows completed

class DecisionAudit(Base):
    __tablename__ = "decision_audit"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String, index=True)
    action = Column(String)  # 'ai_analysis', 'admin_review', 'status_change'
    details = Column(JSON)
    performed_by = Column(String)  # 'ai_model', 'admin'
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()