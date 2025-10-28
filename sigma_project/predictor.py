import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# --- 1. Load the existing dataset and initial clean-up ---
# The snippet uses 'credit_risk_dataset.csv'
file_name = "samples/credit_risk_dataset.csv"
def predict_loan_approval(income,loan_amount):
 try:
    df = pd.read_csv(file_name)
 except FileNotFoundError:
    print(f"Error: The file '{file_name}' was not found. Please ensure it is available.")
    exit()

# Clean up the existing data for modeling
 df = df.dropna(subset=['person_emp_length', 'loan_int_rate'])
# Map target and binary categorical features
 df['cb_person_default_on_file'] = df['cb_person_default_on_file'].map({'Y': 1, 'N': 0})
# One-hot encode multi-category features
 df = pd.get_dummies(df, columns=['person_home_ownership', 'loan_intent', 'loan_grade'], drop_first=True)

# --- 2. Define New Applicant Inputs (Using requested features) ---
# We use the raw requested features for a hypothetical new applicant
 new_applicant_inputs = {
    'person_income':income,
    'loan_amnt': loan_amount,
    # The loan_percent_income is calculated directly from the inputs
    'loan_percent_income':  (loan_amount) / income  ,
    # Other necessary demographic data (these must be provided for the prediction template)
    'person_age': 35,
    'person_emp_length': 5.0,
    'loan_int_rate': 12.5,
    'cb_person_default_on_file': 0, # Example: Assume no prior default
    'cb_person_cred_hist_length': 10
}


# --- 3. Feature Preparation (Training Data) ---
# We define the feature columns to be ALL columns in the cleaned dataframe, 
# ensuring that person_income, loan_amnt, and loan_percent_income are included.
 feature_columns = [col for col in df.columns if col != 'loan_status']


# --- 4. Prepare data for Prediction (New Applicant) ---

# Create a template for the new applicant using the first row as a structural guide
 new_applicant_df = df.iloc[0:1].copy()
 new_applicant_df['loan_status'] = -1 # Reset target variable

# Set the new applicant's specific values using the inputs
 new_applicant_df['person_age'] = new_applicant_inputs['person_age']
 new_applicant_df['person_income'] = new_applicant_inputs['person_income']
 new_applicant_df['person_emp_length'] = new_applicant_inputs['person_emp_length']
 new_applicant_df['loan_amnt'] = new_applicant_inputs['loan_amnt']
 new_applicant_df['loan_int_rate'] = new_applicant_inputs['loan_int_rate']
 new_applicant_df['loan_percent_income'] = new_applicant_inputs['loan_percent_income']
 new_applicant_df['cb_person_default_on_file'] = new_applicant_inputs['cb_person_default_on_file']
 new_applicant_df['cb_person_cred_hist_length'] = new_applicant_inputs['cb_person_cred_hist_length']

# Ensure the new applicant template only includes columns present in the training features.
# For one-hot encoded features, they retain the values from the template row for simplicity,
# but in a real app, these would be set based on the applicant's categorical answers.
 for col in new_applicant_df.columns:
    if col not in feature_columns:
        # Drop any columns that may have been introduced but are not in the training set features
        new_applicant_df = new_applicant_df.drop(columns=[col])


# --- 5. Model Training and Prediction ---

 X = df[feature_columns]
 y = df['loan_status']

# Align the new applicant data to the training features (crucial for consistent feature order)
 X_new = new_applicant_df[feature_columns]

# Split data (standard practice)
 X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a simple Logistic Regression model
 model = LogisticRegression(max_iter=1000)
 model.fit(X_train, y_train)

# Predict for the new applicant
 prediction = model.predict(X_new)
# prediction_proba is [P(Status=0=Non-Default), P(Status=1=Default)]
 prediction_proba = model.predict_proba(X_new)[0]


# --- 6. Output Results and Confidence-Based Decision (FIXED Confidence Score) ---
 print("--- Model Performance on Historical Data (Training Validation) ---")
 y_pred = model.predict(X_test)
 print(f"Test Accuracy: {accuracy_score(y_test, y_pred):.2f}")

 print("\n--- Prediction for New Applicant (Focusing on Income, Loan Amt, Pct Income) ---")

 hard_prediction = prediction[0]
 predicted_prob_default = prediction_proba[1] # P(Status=1 = Default)

# CRITICAL FIX: Confidence Score is the predicted probability of the predicted class.
 if hard_prediction == 0:
    # Prediction is Non-Default (Status=0)
    confidence_score = prediction_proba[0]
    predicted_label_text = "Low Risk (Status=0)"
 else:
    # Prediction is Default (Status=1)
    confidence_score = prediction_proba[1]
    predicted_label_text = "High Risk (Status=1)"

 CONFIDENCE_THRESHOLD = 0.75

# Apply the user's confidence-based rule
 if confidence_score >= CONFIDENCE_THRESHOLD:
    if hard_prediction == 0:
        final_decision = "Approve (High Confidence)"
        interpretation = f"The model is highly confident ({confidence_score:.2%}) that the applicant is Low Risk. Confident decision made."
    else:
        final_decision = "Reject (High Confidence)"
        interpretation = f"The model is highly confident ({confidence_score:.2%}) that the applicant is High Risk. Confident decision made."
 else:
    final_decision = "Pending Approval/Rejection (Review Required)"
    interpretation = f"The model's confidence in its prediction is only {confidence_score:.2%}, which is below the {CONFIDENCE_THRESHOLD:.0%} threshold. This is a moderate-risk case that requires manual human review, further documentation, or adjustment of loan terms."


 print(f"Applicant Income: ${new_applicant_inputs['person_income']:.2f}")
 print(f"Requested Loan Amount: ${new_applicant_inputs['loan_amnt']:.2f}")
 print(f"Loan-to-Income Ratio (loan_percent_income): {new_applicant_inputs['loan_percent_income']}")
 print("-" * 30)
 print(f"Predicted Risk Label: {predicted_label_text}")
 print(f"Probability of Default (Status=1): {predicted_prob_default:.2%}")
 print(f"Model Confidence in Prediction: {confidence_score:.2%}")
 print("-" * 30)
 print(f"Final Decision: {final_decision}")
 print(f"\nInterpretation: {interpretation}")
 return final_decision, interpretation