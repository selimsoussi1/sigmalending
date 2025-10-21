
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
import joblib
import warnings
from datetime import datetime
import uvicorn


app = FastAPI(
    title="Loan Decision API",
    description="AI-powered loan application decision system",
    version="1.0.0"
)

# Pydantic models for request/response
class LoanApplication(BaseModel):
    loan_amnt: float
    term: str
    int_rate: float
    grade: str
    sub_grade: str
    emp_length: str
    home_ownership: str
    annual_inc: float
    verification_status: str
    purpose: str
    addr_state: str
    dti: float
    delinq_2yrs: int
    fico_range_low: int
    fico_range_high: int
    inq_last_6mths: int
    mths_since_last_delinq: Optional[int] = None
    open_acc: int
    pub_rec: int
    revol_bal: float
    revol_util: float
    total_acc: int
    application_type: str
    last_fico_range_low: int
    last_fico_range_high: int

class DecisionResponse(BaseModel):
    decision: str
    probability_fully_paid: float
    probability_charged_off: float
    risk_level: str
    recommendation: str
    timestamp: str
    application_id: Optional[str] = None

class BatchResponse(BaseModel):
    results: List[Dict[str, Any]]
    processed_count: int
    success_count: int
    error_count: int
    timestamp: str

class LoanDecisionSystem:
    def __init__(self):
        """Initialize the loan decision system"""
        try:
            self.training_columns = joblib.load('training_columns.pkl')
            self.scaler = joblib.load('scaler.pkl')
            self.imputer_num = joblib.load('imputer_num.pkl')
            self.imputer_cat = joblib.load('imputer_cat.pkl')
            self.label_encoders = joblib.load('label_encoders.pkl')
            self.model = joblib.load('loan_default_model.pkl')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")
    
    def predict_single_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction for a single client"""
        client_df = pd.DataFrame([client_data])
        client_clean = self._preprocess_client(client_df)
        client_scaled = self.scaler.transform(client_clean)
        
        prediction = self.model.predict(client_scaled)[0]
        prediction_probabilities = self.model.predict_proba(client_scaled)[0]
        
        return self._format_result(prediction, prediction_probabilities)
    
    def _preprocess_client(self, client_df):
        """Internal preprocessing method"""
        non_predictive_cols = ['id', 'member_id', 'url', 'desc', 'title', 'zip_code', 'issue_d', 'pymnt_plan', 
                              'initial_list_status', 'out_prncp', 'out_prncp_inv', 'total_pymnt', 
                              'total_pymnt_inv', 'total_rec_prncp', 'total_rec_int', 'total_rec_late_fee', 
                              'recoveries', 'collection_recovery_fee', 'last_pymnt_d', 'last_pymnt_amnt', 
                              'next_pymnt_d', 'last_credit_pull_d', 'hardship_flag', 'hardship_type', 
                              'hardship_reason', 'hardship_status', 'deferral_term', 'hardship_amount', 
                              'hardship_start_date', 'hardship_end_date', 'payment_plan_start_date', 
                              'hardship_length', 'hardship_dpd', 'hardship_loan_status', 
                              'orig_projected_additional_accrued_interest', 'hardship_payoff_balance_amount', 
                              'hardship_last_payment_amount', 'disbursement_method', 'debt_settlement_flag', 
                              'debt_settlement_flag_date', 'settlement_status', 'settlement_date', 
                              'settlement_amount', 'settlement_percentage', 'settlement_term', 'loan_status']
        
        cols_to_drop = [col for col in non_predictive_cols if col in client_df.columns]
        client_clean = client_df.drop(columns=cols_to_drop, errors='ignore')
        
        client_imputed_num = self._safe_impute(self.imputer_num, client_clean)
        client_imputed_cat = self._safe_impute(self.imputer_cat, client_clean)
        client_clean = pd.concat([client_imputed_num, client_imputed_cat], axis=1)
        client_clean = client_clean.loc[:, ~client_clean.columns.duplicated()]
        
        for col, le in self.label_encoders.items():
            if col in client_clean.columns:
                client_clean[col] = client_clean[col].astype(str)
                if client_clean[col].iloc[0] not in le.classes_:
                    client_clean[col] = le.classes_[0]
                client_clean[col] = le.transform(client_clean[col])
        
        low_cardinality_cols = ['term', 'grade', 'home_ownership', 'verification_status', 'application_type']
        for col in low_cardinality_cols:
            if col in client_clean.columns:
                dummies = pd.get_dummies(client_clean[col], prefix=col)
                client_clean = client_clean.drop(columns=[col])
                client_clean = pd.concat([client_clean, dummies], axis=1)
        
        missing_cols = set(self.training_columns) - set(client_clean.columns)
        for col in missing_cols:
            client_clean[col] = 0
        
        extra_cols = set(client_clean.columns) - set(self.training_columns)
        client_clean = client_clean.drop(columns=extra_cols)
        client_clean = client_clean[self.training_columns]
        
        return client_clean
    
    def _safe_impute(self, imputer, df):
        df_copy = df.copy()
        missing_features = set(imputer.feature_names_in_) - set(df_copy.columns)
        for feature in missing_features:
            df_copy[feature] = np.nan
        df_copy = df_copy[imputer.feature_names_in_]
        return pd.DataFrame(imputer.transform(df_copy), 
                           columns=imputer.feature_names_in_, 
                           index=df_copy.index)
    
    def _format_result(self, prediction, probabilities):
        return {
            'prediction': 'Fully Paid' if prediction == 1 else 'Charged Off',
            'probability_fully_paid': round(probabilities[1] * 100, 2),
            'probability_charged_off': round(probabilities[0] * 100, 2),
            'risk_level': self._get_risk_level(probabilities[0]),
            'recommendation': self._get_recommendation(probabilities[0])
        }
    
    def _get_risk_level(self, default_probability):
        if default_probability < 0.1: return "Low Risk"
        elif default_probability < 0.3: return "Medium Risk"
        elif default_probability < 0.5: return "High Risk"
        else: return "Very High Risk"
    
    def _get_recommendation(self, default_probability):
        if default_probability < 0.1: return "APPROVE - Low risk, standard terms"
        elif default_probability < 0.3: return "APPROVE - Medium risk, consider higher interest rate"
        elif default_probability < 0.5: return "CONSIDER - High risk, require collateral or co-signer"
        else: return "REJECT - Very high risk of default"

# Initialize the system
decision_system = LoanDecisionSystem()

@app.get("/")
async def root():
    return {"message": "Loan Decision API", "status": "active", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/loan-decision", response_model=DecisionResponse)
async def evaluate_loan(application: LoanApplication, application_id: Optional[str] = None):
    """
    Evaluate a single loan application
    """
    try:
        result = decision_system.predict_single_client(application.dict())
        
        return DecisionResponse(
            decision=result['prediction'],
            probability_fully_paid=result['probability_fully_paid'],
            probability_charged_off=result['probability_charged_off'],
            risk_level=result['risk_level'],
            recommendation=result['recommendation'],
            timestamp=datetime.now().isoformat(),
            application_id=application_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Processing failed: {str(e)}")

@app.post("/api/loan-decisions/batch", response_model=BatchResponse)
async def evaluate_loans_batch(applications: List[LoanApplication]):
    """
    Evaluate multiple loan applications in batch
    """
    results = []
    success_count = 0
    error_count = 0
    
    for i, application in enumerate(applications):
        try:
            result = decision_system.predict_single_client(application.dict())
            results.append({
                "application_index": i,
                "status": "success",
                "result": result
            })
            success_count += 1
        except Exception as e:
            results.append({
                "application_index": i,
                "status": "error",
                "error": str(e)
            })
            error_count += 1
    
    return BatchResponse(
        results=results,
        processed_count=len(applications),
        success_count=success_count,
        error_count=error_count,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/model-info")
async def get_model_info():
    """
    Get information about the trained model
    """
    return {
        "model_type": "XGBoost",
        "training_features": len(decision_system.training_columns),
        "feature_importance": {
            "last_fico_range_low": 0.202329,
            "last_fico_range_high": 0.199891,
            "term_60_months": 0.037414,
            "int_rate": 0.037227
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002) 