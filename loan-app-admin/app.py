from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import uuid
import random
import asyncio
import requests
import os
import shutil
from pathlib import Path

# N8N Configuration
N8N_BASE_URL = "https://selim789.app.n8n.cloud"
N8N_WEBHOOK_PATH = "/webhook-test/webhook"
N8N_FULL_URL = f"{N8N_BASE_URL}{N8N_WEBHOOK_PATH}"

# Configuration des dossiers
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Database setup
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# Create new database to avoid schema conflicts
DATABASE_URL = "sqlite:///./loan_applications_professional.db"
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
    
    # AI Analysis Results
    ai_decision = Column(String, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    risk_score = Column(Float, nullable=True)
    decision_factors = Column(JSON, nullable=True)
    strengths = Column(JSON, nullable=True)
    concerns = Column(JSON, nullable=True)
    recommendation = Column(Text, nullable=True)
    
    # N8N Workflow Results
    ocr_data = Column(JSON, nullable=True)
    company_verification_data = Column(JSON, nullable=True)
    company_house_status = Column(String, nullable=True)
    
    # File Information
    uploaded_files = Column(JSON, nullable=True)
    
    # Status
    status = Column(String, default='submitted')
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    ocr_processed_at = Column(DateTime, nullable=True)
    company_verified_at = Column(DateTime, nullable=True)

class DecisionAudit(Base):
    __tablename__ = "decision_audit"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String, index=True)
    action = Column(String)
    details = Column(JSON)
    performed_by = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI App
app = FastAPI(title="Loan Application Admin API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze_application(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """AI analysis simulation for loan applications"""
    try:
        loan_amount = float(application_data.get('amount', 0))
        annual_revenue = float(application_data.get('annualRevenue', 1))
        years = int(application_data.get('yearsInBusiness', 0))
        
        # Calculate key ratios
        loan_to_revenue = loan_amount / annual_revenue if annual_revenue > 0 else 1
        
        # Risk factors
        factors = []
        risk_score = 0
        
        # Business stability (30%)
        if years >= 5:
            factors.append({
                "factor": "Established Business",
                "impact": "positive",
                "description": f"Business operating for {years} years",
                "value": f"{years} years"
            })
            risk_score += 10
        elif years >= 2:
            factors.append({
                "factor": "Growing Business",
                "impact": "neutral", 
                "description": f"Business has {years} years of operation",
                "value": f"{years} years"
            })
            risk_score += 20
        else:
            factors.append({
                "factor": "New Business",
                "impact": "negative",
                "description": f"Only {years} years of operation",
                "value": f"{years} years"
            })
            risk_score += 35
        
        # Financial health (35%)
        if loan_to_revenue <= 0.25:
            factors.append({
                "factor": "Conservative Loan",
                "impact": "positive",
                "description": "Loan is 25% or less of annual revenue",
                "value": f"{loan_to_revenue:.1%}"
            })
            risk_score += 10
        elif loan_to_revenue <= 0.5:
            factors.append({
                "factor": "Moderate Loan",
                "impact": "neutral",
                "description": "Loan is 25-50% of annual revenue", 
                "value": f"{loan_to_revenue:.1%}"
            })
            risk_score += 20
        else:
            factors.append({
                "factor": "Aggressive Loan",
                "impact": "negative",
                "description": "Loan exceeds 50% of annual revenue",
                "value": f"{loan_to_revenue:.1%}"
            })
            risk_score += 40
        
        # Revenue strength (35%)
        if annual_revenue >= 1000000:
            factors.append({
                "factor": "Strong Revenue",
                "impact": "positive",
                "description": "Annual revenue over $1M",
                "value": f"${annual_revenue:,.0f}"
            })
            risk_score += 10
        elif annual_revenue >= 500000:
            factors.append({
                "factor": "Good Revenue", 
                "impact": "neutral",
                "description": "Annual revenue $500K-$1M",
                "value": f"${annual_revenue:,.0f}"
            })
            risk_score += 20
        else:
            factors.append({
                "factor": "Limited Revenue",
                "impact": "negative",
                "description": "Annual revenue under $500K",
                "value": f"${annual_revenue:,.0f}"
            })
            risk_score += 30
        
        # Make decision
        if risk_score <= 30:
            return {
                "decision": "approved",
                "confidence": round(0.85 + random.uniform(0, 0.1), 2),
                "risk_level": "low",
                "risk_score": risk_score,
                "decision_factors": factors,
                "strengths": ["Strong business stability", "Conservative loan request", "Healthy revenue base"],
                "concerns": ["No significant concerns identified"],
                "recommendation": "STRONG APPROVAL - Excellent business profile with minimal risk. Recommend standard terms."
            }
        elif risk_score <= 50:
            return {
                "decision": "approved",
                "confidence": round(0.70 + random.uniform(0, 0.1), 2), 
                "risk_level": "medium",
                "risk_score": risk_score,
                "decision_factors": factors,
                "strengths": ["Reasonable business history", "Manageable loan amount"],
                "concerns": ["Some risk factors present but manageable"],
                "recommendation": "APPROVAL - Solid business profile. Recommend standard review process."
            }
        elif risk_score <= 70:
            return {
                "decision": "review_required",
                "confidence": round(0.60 + random.uniform(0, 0.1), 2),
                "risk_level": "high", 
                "risk_score": risk_score,
                "decision_factors": factors,
                "strengths": ["Business registration valid"],
                "concerns": ["Multiple risk factors need review", "Higher than average risk profile"],
                "recommendation": "REVIEW REQUIRED - Multiple risk factors present. Needs manual assessment."
            }
        else:
            return {
                "decision": "rejected",
                "confidence": round(0.75 + random.uniform(0, 0.1), 2),
                "risk_level": "critical",
                "risk_score": risk_score,
                "decision_factors": factors,
                "strengths": ["Application complete"],
                "concerns": ["Critical risk factors detected", "High probability of default"],
                "recommendation": "RECOMMEND REJECTION - Critical risk factors outweigh positive aspects."
            }
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return {
            "decision": "review_required",
            "confidence": 0.5,
            "risk_level": "unknown",
            "risk_score": 50,
            "decision_factors": [],
            "strengths": ["Application submitted"],
            "concerns": ["Analysis error - needs manual review"],
            "recommendation": "ANALYSIS ERROR - Requires manual assessment."
        }

async def trigger_n8n_workflow(workflow_type: str, payload: Dict) -> bool:
    """Trigger N8N workflows with your cloud instance"""
    try:
        webhook_url = N8N_FULL_URL
        
        enhanced_payload = {
            "workflowType": workflow_type,
            "timestamp": datetime.utcnow().isoformat(),
            "body": payload,
            "data": payload
        }
        
        print(f"Triggering N8N workflow: {workflow_type}")
        print(f"Sending to: {webhook_url}")
        
        response = requests.post(
            webhook_url, 
            json=enhanced_payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'LoanApp-System/3.0'
            },
            timeout=30
        )
        
        if response.status_code in [200, 201, 204]:
            print(f"N8N workflow triggered successfully: {workflow_type}")
            return True
        else:
            print(f"Failed to trigger {workflow_type}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error triggering {workflow_type}: {str(e)}")
        return False

async def trigger_all_workflows(application_id: str, application_data: Dict, files: List[Dict] = None):
    """Trigger all N8N workflows for an application"""
    try:
        base_payload = {
            "applicationId": application_id,
            "applicationData": application_data,
            "files": files or [],
            "submittedAt": datetime.utcnow().isoformat()
        }
        
        tasks = []
        
        # File Processing Workflow
        file_payload = base_payload.copy()
        tasks.append(trigger_n8n_workflow("file_processing", file_payload))
        
        # OCR Processing Workflow
        if files:
            ocr_payload = base_payload.copy()
            ocr_payload["filePaths"] = [f.get('path', '') for f in files if f]
            tasks.append(trigger_n8n_workflow("ocr_processing", ocr_payload))
        
        # Company Verification Workflow
        company_payload = base_payload.copy()
        company_payload["companyNumber"] = application_data.get('companyNumber', '')
        company_payload["companyName"] = application_data.get('companyName', '')
        tasks.append(trigger_n8n_workflow("company_verification", company_payload))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_workflows = sum(1 for r in results if r is True)
        print(f"Successfully triggered {successful_workflows}/3 workflows for {application_id}")
        
    except Exception as e:
        print(f"Error triggering workflows: {e}")

@app.get("/")
async def root():
    return {
        "message": "Loan Application Admin API", 
        "status": "active",
        "version": "3.0.0",
        "database": "loan_applications_professional.db",
        "endpoints": {
            "applications": "/api/applications",
            "upload": "/api/applications/upload",
            "stats": "/api/dashboard/stats",
            "docs": "/docs",
            "test_n8n": "/api/test-n8n-connection"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/applications")
async def create_application(application: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create new application with flexible field names"""
    try:
        application_id = str(uuid.uuid4())
        
        print(f"Received application data: {application}")
        
        # Map flexible field names to expected names
        field_mapping = {
            'company': 'companyName',
            'company_name': 'companyName',
            'first_name': 'firstName',
            'last_name': 'lastName',
            'loan_amount': 'amount',
            'purpose': 'loanPurpose',
            'revenue': 'annualRevenue',
            'years': 'yearsInBusiness'
        }
        
        # Normalize field names
        normalized_data = {}
        for key, value in application.items():
            normalized_key = field_mapping.get(key, key)
            normalized_data[normalized_key] = value
        
        # Validate required fields
        required_fields = ['companyName', 'firstName', 'lastName', 'email', 'amount']
        missing_fields = [field for field in required_fields if field not in normalized_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {', '.join(missing_fields)}. Received fields: {list(application.keys())}"
            )
        
        # Create application record
        db_app = LoanApplication(
            application_id=application_id,
            company_name=normalized_data.get('companyName', '')[:255],
            company_number=normalized_data.get('companyNumber', '')[:100],
            business_type=normalized_data.get('businessType', 'ltd'),
            industry=normalized_data.get('industry', 'other'),
            first_name=normalized_data.get('firstName', '')[:100],
            last_name=normalized_data.get('lastName', '')[:100],
            email=normalized_data.get('email', '')[:255],
            phone=normalized_data.get('phone', '')[:20],
            address=normalized_data.get('address', '')[:500],
            loan_amount=float(normalized_data.get('amount', 0)),
            loan_purpose=normalized_data.get('loanPurpose', 'working_capital'),
            annual_revenue=float(normalized_data.get('annualRevenue', 0)),
            years_in_business=int(normalized_data.get('yearsInBusiness', 0)),
            status='submitted'
        )
        
        db.add(db_app)
        db.commit()
        db.refresh(db_app)
        
        # Process in background with N8N workflows
        background_tasks.add_task(process_application_with_n8n, application_id, normalized_data, db)
        
        return {
            "application_id": application_id,
            "status": "submitted",
            "message": "Application received and processing started",
            "n8n_workflows_triggered": True,
            "received_fields": list(application.keys())
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating application: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")

@app.post("/api/debug/form-submission")
async def debug_form_submission(request: Request):
    """Debug endpoint to see what the form is sending"""
    try:
        body = await request.body()
        body_str = body.decode('utf-8')
        
        try:
            json_data = await request.json()
            content_type = "JSON"
        except:
            json_data = None
            content_type = "Form Data"
        
        headers = dict(request.headers)
        
        print("DEBUG FORM SUBMISSION:")
        print(f"Content-Type: {headers.get('content-type')}")
        print(f"Raw body: {body_str}")
        print(f"Parsed as: {content_type}")
        
        return {
            "content_type": headers.get('content-type'),
            "raw_body": body_str,
            "parsed_data": json_data,
            "headers": {k: v for k, v in headers.items() if k.lower() not in ['authorization', 'cookie']}
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/applications/upload")
async def create_application_with_files(
    background_tasks: BackgroundTasks,
    companyName: str = Form(...),
    companyNumber: str = Form(...),
    businessType: str = Form(...),
    industry: str = Form(...),
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    amount: float = Form(...),
    loanPurpose: str = Form(...),
    annualRevenue: float = Form(...),
    yearsInBusiness: int = Form(...),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    """Create new application with file uploads"""
    try:
        application_id = str(uuid.uuid4())
        
        # Save uploaded files
        saved_files = []
        for file in files:
            if file.filename:
                file_extension = Path(file.filename).suffix
                safe_filename = f"{application_id}_{uuid.uuid4()}{file_extension}"
                file_path = UPLOAD_DIR / safe_filename
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                saved_files.append({
                    "original_name": file.filename,
                    "saved_name": safe_filename,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "uploaded_at": datetime.utcnow().isoformat()
                })
        
        # Create application data
        application_data = {
            "companyName": companyName,
            "companyNumber": companyNumber,
            "businessType": businessType,
            "industry": industry,
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "phone": phone,
            "address": address,
            "amount": amount,
            "loanPurpose": loanPurpose,
            "annualRevenue": annualRevenue,
            "yearsInBusiness": yearsInBusiness
        }
        
        # Create application record
        db_app = LoanApplication(
            application_id=application_id,
            company_name=companyName,
            company_number=companyNumber,
            business_type=businessType,
            industry=industry,
            first_name=firstName,
            last_name=lastName,
            email=email,
            phone=phone,
            address=address,
            loan_amount=amount,
            loan_purpose=loanPurpose,
            annual_revenue=annualRevenue,
            years_in_business=yearsInBusiness,
            uploaded_files=saved_files,
            status='submitted'
        )
        
        db.add(db_app)
        db.commit()
        db.refresh(db_app)
        
        # Process in background with N8N workflows
        background_tasks.add_task(process_application_with_n8n, application_id, application_data, saved_files, db)
        
        return {
            "application_id": application_id,
            "status": "submitted",
            "message": "Application received with files",
            "uploaded_files": len(saved_files),
            "n8n_workflows_triggered": True
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")

async def process_application_with_n8n(application_id: str, application_data: dict, files: List[Dict] = None, db: Session = None):
    """Enhanced application processing with N8N workflows"""
    
    if db is None:
        db = next(get_db())
    
    await asyncio.sleep(2)
    
    app = db.query(LoanApplication).filter(LoanApplication.application_id == application_id).first()
    if not app:
        return
    
    try:
        # Run initial AI analysis
        print("Running Initial AI Analysis...")
        initial_analysis = analyze_application(application_data)
        
        # Update application with initial AI results
        app.ai_decision = initial_analysis["decision"]
        app.ai_confidence = initial_analysis["confidence"]
        app.risk_level = initial_analysis["risk_level"]
        app.risk_score = initial_analysis["risk_score"]
        app.decision_factors = initial_analysis["decision_factors"]
        app.strengths = initial_analysis["strengths"]
        app.concerns = initial_analysis["concerns"]
        app.recommendation = initial_analysis["recommendation"]
        app.status = 'initial_review'
        app.processed_at = datetime.utcnow()
        
        db.commit()
        
        # Trigger all N8N workflows
        await trigger_all_workflows(application_id, application_data, files)
        
        # Log successful processing
        audit_log = DecisionAudit(
            application_id=application_id,
            action="enhanced_processing_completed",
            details={
                "workflows_triggered": ["file_processing", "ocr", "company_verification"],
                "initial_decision": initial_analysis["decision"],
                "n8n_integration": True,
                "files_uploaded": len(files) if files else 0
            },
            performed_by="system"
        )
        db.add(audit_log)
        db.commit()
        
        print(f"Enhanced processing completed for {application_id}")
        
    except Exception as e:
        print(f"Error in enhanced processing: {e}")
        error_audit = DecisionAudit(
            application_id=application_id,
            action="processing_error",
            details={"error": str(e)},
            performed_by="system"
        )
        db.add(error_audit)
        db.commit()

@app.get("/api/applications")
async def get_applications(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all applications"""
    try:
        query = db.query(LoanApplication)
        if status and status != 'all':
            query = query.filter(LoanApplication.status == status)
        
        apps = query.order_by(LoanApplication.created_at.desc()).all()
        
        return [
            {
                "application_id": app.application_id,
                "company_name": app.company_name,
                "first_name": app.first_name,
                "last_name": app.last_name,
                "loan_amount": app.loan_amount,
                "annual_revenue": app.annual_revenue,
                "years_in_business": app.years_in_business,
                "ai_decision": app.ai_decision,
                "risk_level": app.risk_level,
                "risk_score": app.risk_score,
                "status": app.status,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "processed_at": app.processed_at.isoformat() if app.processed_at else None
            }
            for app in apps
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applications: {str(e)}")

@app.get("/api/applications/{application_id}")
async def get_application(application_id: str, db: Session = Depends(get_db)):
    """Get application details"""
    app = db.query(LoanApplication).filter(LoanApplication.application_id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {
        "application": {
            "basic_info": {
                "application_id": app.application_id,
                "company_name": app.company_name,
                "company_number": app.company_number,
                "business_type": app.business_type,
                "industry": app.industry,
                "applicant_name": f"{app.first_name} {app.last_name}",
                "email": app.email,
                "phone": app.phone,
                "address": app.address
            },
            "financial_info": {
                "loan_amount": app.loan_amount,
                "loan_purpose": app.loan_purpose,
                "annual_revenue": app.annual_revenue,
                "years_in_business": app.years_in_business
            },
            "ai_analysis": {
                "decision": app.ai_decision,
                "confidence": app.ai_confidence,
                "risk_level": app.risk_level,
                "risk_score": app.risk_score,
                "decision_factors": app.decision_factors,
                "strengths": app.strengths,
                "concerns": app.concerns,
                "recommendation": app.recommendation
            } if app.ai_decision else None,
            "n8n_results": {
                "ocr_data": app.ocr_data,
                "company_verification": app.company_verification_data,
                "company_house_status": app.company_house_status
            },
            "uploaded_files": app.uploaded_files,
            "status": app.status,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "processed_at": app.processed_at.isoformat() if app.processed_at else None
        }
    }

@app.get("/api/dashboard/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics - FIXED VERSION"""
    try:
        total = db.query(LoanApplication).count()
        pending = db.query(LoanApplication).filter(LoanApplication.status == 'submitted').count()
        
        # Use proper status check
        processed_query = db.query(LoanApplication).filter(
            LoanApplication.status.in_(['initial_review', 'processed', 'completed'])
        )
        processed = processed_query.count()
        
        # Risk distribution - safe handling
        risks = db.query(LoanApplication.risk_level).all()
        risk_dist = {}
        for risk in risks:
            risk_level = risk[0]
            if risk_level and risk_level != 'None':
                risk_dist[risk_level] = risk_dist.get(risk_level, 0) + 1
        
        # Decision distribution - safe handling
        decisions = db.query(LoanApplication.ai_decision).all()
        decision_dist = {}
        for decision in decisions:
            decision_type = decision[0]
            if decision_type and decision_type != 'None':
                decision_dist[decision_type] = decision_dist.get(decision_type, 0) + 1
        
        return {
            "total_applications": total,
            "pending_processing": pending,
            "ready_for_review": processed,
            "risk_distribution": risk_dist,
            "decision_distribution": decision_dist
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        # Return empty stats instead of error
        return {
            "total_applications": 0,
            "pending_processing": 0,
            "ready_for_review": 0,
            "risk_distribution": {},
            "decision_distribution": {}
        }

@app.post("/api/n8n/webhook/results")
async def receive_n8n_results(request: Request, db: Session = Depends(get_db)):
    """Receive results from N8N workflows"""
    try:
        # Get the raw request body first
        raw_body = await request.body()
        print(f"Raw N8N callback received: {raw_body.decode('utf-8')}")
        
        # Try to parse as JSON
        try:
            workflow_data = await request.json()
        except Exception as json_error:
            print(f"JSON parsing error: {json_error}")
            try:
                workflow_data = json.loads(raw_body.decode('utf-8'))
            except:
                workflow_data = {"raw_body": raw_body.decode('utf-8')}
        
        print(f"Parsed N8N callback: {workflow_data}")
        
        workflow_type = workflow_data.get('workflowType')
        application_id = workflow_data.get('applicationId')
        results = workflow_data.get('results', {})
        
        if not application_id:
            print("Missing applicationId in callback")
            return {"status": "error", "message": "Missing applicationId"}
        
        app = db.query(LoanApplication).filter(LoanApplication.application_id == application_id).first()
        if not app:
            print(f"Application not found: {application_id}")
            return {"status": "error", "message": "Application not found"}
        
        if workflow_type == "file_processing":
            # Store file processing results
            app.ocr_data = results
            app.ocr_processed_at = datetime.utcnow()
            
            audit_log = DecisionAudit(
                application_id=application_id,
                action="file_processing_completed",
                details={"results": results},
                performed_by="n8n_workflow"
            )
            db.add(audit_log)
            print(f"File processing results stored for {application_id}")
            
        elif workflow_type == "ocr_processing":
            # Store OCR results
            app.ocr_data = results
            app.ocr_processed_at = datetime.utcnow()
            
            audit_log = DecisionAudit(
                application_id=application_id,
                action="ocr_processing_completed",
                details={"extracted_fields": list(results.get('extracted_data', {}).keys())},
                performed_by="n8n_workflow"
            )
            db.add(audit_log)
            print(f"OCR results stored for {application_id}")
            
        elif workflow_type == "company_verification":
            # Store verification results
            app.company_verification_data = results
            app.company_verified_at = datetime.utcnow()
            app.company_house_status = results.get('company_data', {}).get('status', 'unknown')
            
            audit_log = DecisionAudit(
                application_id=application_id,
                action="company_verification_completed",
                details={"verification_status": results.get('company_data', {}).get('status')},
                performed_by="n8n_search_agent"
            )
            db.add(audit_log)
            print(f"Company verification results stored for {application_id}")
        else:
            print(f"Unknown workflow type: {workflow_type}")
        
        db.commit()
        print(f"{workflow_type} results processed for {application_id}")
        
        return {"status": "success", "message": f"{workflow_type} results processed"}
        
    except Exception as e:
        print(f"Error processing N8N results: {e}")
        if 'db' in locals():
            db.rollback()
        return {"status": "error", "message": str(e)}

@app.get("/api/test-n8n-connection")
async def test_n8n_connection():
    """Test connection to N8N cloud instance"""
    try:
        test_payload = {
            "workflowType": "test",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "test": True,
                "message": "Testing N8N connection from Loan App",
                "applicationId": "test-123"
            }
        }
        
        response = requests.post(N8N_FULL_URL, json=test_payload, timeout=10)
        
        return {
            "success": response.status_code in [200, 201, 204],
            "status_code": response.status_code,
            "n8n_url": N8N_FULL_URL,
            "message": "N8N connection test completed",
            "response_text": response.text[:200] if response.text else "No response body"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "n8n_url": N8N_FULL_URL,
            "message": "Failed to connect to N8N"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8005, reload=True)