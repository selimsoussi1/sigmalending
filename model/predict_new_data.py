import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# Load the NEW dataset you want to predict on
new_df = pd.read_csv(r"C:\Users\GIGABYTE\Desktop\structured\structured_dataset60.csv", low_memory=False)

# 1. Load the Saved Preprocessing Objects and Model
training_columns = joblib.load('training_columns.pkl')
scaler = joblib.load('scaler.pkl')
imputer_num = joblib.load('imputer_num.pkl')
imputer_cat = joblib.load('imputer_cat.pkl')
label_encoders = joblib.load('label_encoders.pkl')
model = joblib.load('loan_default_model.pkl')

print(f"Model expects {len(training_columns)} features")

# 2. Create a custom imputation function that handles missing features
def safe_impute(imputer, df, expected_features):
    """
    Safely apply imputation, handling missing features by adding them with default values
    """
    # Create a copy of the dataframe
    df_copy = df.copy()
    
    # Add missing features with NaN values
    missing_features = set(expected_features) - set(df_copy.columns)
    for feature in missing_features:
        df_copy[feature] = np.nan
    
    # Keep only the expected features in the right order
    df_copy = df_copy[expected_features]
    
    # Apply imputation
    return pd.DataFrame(imputer.transform(df_copy), 
                       columns=expected_features, 
                       index=df_copy.index)

# 3. Apply the same cleaning steps as training
new_df_clean = new_df.copy()

# Drop non-predictive columns (same as training)
non_predictive_cols = ['id', 'member_id', 'url', 'desc', 'title', 'zip_code', 'issue_d', 'pymnt_plan', 'initial_list_status', 
                       'out_prncp', 'out_prncp_inv', 'total_pymnt', 'total_pymnt_inv', 'total_rec_prncp', 
                       'total_rec_int', 'total_rec_late_fee', 'recoveries', 'collection_recovery_fee', 
                       'last_pymnt_d', 'last_pymnt_amnt', 'next_pymnt_d', 'last_credit_pull_d', 
                       'hardship_flag', 'hardship_type', 'hardship_reason', 'hardship_status', 
                       'deferral_term', 'hardship_amount', 'hardship_start_date', 'hardship_end_date', 
                       'payment_plan_start_date', 'hardship_length', 'hardship_dpd', 'hardship_loan_status', 
                       'orig_projected_additional_accrued_interest', 'hardship_payoff_balance_amount', 
                       'hardship_last_payment_amount', 'disbursement_method', 'debt_settlement_flag', 
                       'debt_settlement_flag_date', 'settlement_status', 'settlement_date', 
                       'settlement_amount', 'settlement_percentage', 'settlement_term', 'loan_status']

cols_to_drop = [col for col in non_predictive_cols if col in new_df_clean.columns]
new_df_clean = new_df_clean.drop(columns=cols_to_drop, errors='ignore')

print(f"After dropping non-predictive columns: {new_df_clean.shape}")

# 4. Apply safe imputation
print("Applying numerical imputation...")
new_df_imputed_num = safe_impute(imputer_num, new_df_clean, imputer_num.feature_names_in_)

print("Applying categorical imputation...")
new_df_imputed_cat = safe_impute(imputer_cat, new_df_clean, imputer_cat.feature_names_in_)

# Combine the results
new_df_clean = pd.concat([new_df_imputed_num, new_df_imputed_cat], axis=1)

# Remove duplicate columns (if any)
new_df_clean = new_df_clean.loc[:, ~new_df_clean.columns.duplicated()]

print(f"After imputation: {new_df_clean.shape}")

# 5. Encode categorical variables using the saved label encoders
for col, le in label_encoders.items():
    if col in new_df_clean.columns:
        new_df_clean[col] = new_df_clean[col].astype(str)
        # Handle unseen categories by mapping to most frequent
        unseen_mask = ~new_df_clean[col].isin(le.classes_)
        if unseen_mask.any():
            most_frequent = le.classes_[0]
            new_df_clean.loc[unseen_mask, col] = most_frequent
        new_df_clean[col] = le.transform(new_df_clean[col])

# 6. One-Hot Encode low cardinality columns
low_cardinality_cols = ['term', 'grade', 'home_ownership', 'verification_status', 'application_type']
for col in low_cardinality_cols:
    if col in new_df_clean.columns:
        dummies = pd.get_dummies(new_df_clean[col], prefix=col)
        new_df_clean = new_df_clean.drop(columns=[col])
        new_df_clean = pd.concat([new_df_clean, dummies], axis=1)

print(f"After one-hot encoding: {new_df_clean.shape}")

# 7. Align with training data structure
missing_cols = set(training_columns) - set(new_df_clean.columns)
for col in missing_cols:
    new_df_clean[col] = 0

extra_cols = set(new_df_clean.columns) - set(training_columns)
new_df_clean = new_df_clean.drop(columns=extra_cols)

new_df_clean = new_df_clean[training_columns]

print(f"Final shape after alignment: {new_df_clean.shape}")
print(f"Missing columns added: {len(missing_cols)}")
print(f"Extra columns removed: {len(extra_cols)}")

# 8. Scale the features
new_data_scaled = scaler.transform(new_df_clean)

# 9. MAKE PREDICTIONS!
predictions = model.predict(new_data_scaled)
prediction_probabilities = model.predict_proba(new_data_scaled)

# 10. Add predictions to original dataframe
new_df['model_prediction'] = predictions  # 0 = Charged Off, 1 = Fully Paid
new_df['probability_fully_paid'] = prediction_probabilities[:, 1]  # Probability of class 1
new_df['probability_charged_off'] = prediction_probabilities[:, 0]  # Probability of class 0

# 11. Display and save results
print("\n" + "="*50)
print("PREDICTION RESULTS")
print("="*50)
print(f"Total loans predicted: {len(new_df)}")
print(f"Predicted to default (0): {(predictions == 0).sum()} ({(predictions == 0).mean()*100:.1f}%)")
print(f"Predicted to be fully paid (1): {(predictions == 1).sum()} ({(predictions == 1).mean()*100:.1f}%)")

print("\nFirst 10 predictions:")
result_cols = ['id', 'loan_amnt', 'term', 'int_rate', 'grade', 'model_prediction', 
               'probability_fully_paid', 'probability_charged_off']
if 'id' in new_df.columns:
    print(new_df[result_cols].head(10))
else:
    print(new_df[['loan_amnt', 'term', 'int_rate', 'grade', 'model_prediction', 
                 'probability_fully_paid', 'probability_charged_off']].head(10))

# Save results
output_path = 'new_data_with_predictions.csv'
new_df.to_csv(output_path, index=False)
print(f"\nPredictions saved to '{output_path}'")

# Show prediction statistics
print("\nPrediction Statistics:")
print(f"Average probability of full payment: {new_df['probability_fully_paid'].mean():.3f}")
print(f"Range: {new_df['probability_fully_paid'].min():.3f} - {new_df['probability_fully_paid'].max():.3f}")

# Show distribution of predictions
print(f"\nDefault risk distribution:")
risk_bins = pd.cut(new_df['probability_charged_off'], 
                   bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                   include_lowest=True)
print(risk_bins.value_counts().sort_index())

# Show top features influencing predictions (if available)
if hasattr(model, 'feature_importances_'):
    print("\nTop 10 most important features for this prediction:")
    feature_importance = pd.Series(model.feature_importances_, index=training_columns)
    top_features = feature_importance.nlargest(10)
    print(top_features)