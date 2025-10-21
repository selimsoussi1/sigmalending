import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score, f1_score
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import joblib

# Load the dataset
df = pd.read_csv(r"C:\Users\GIGABYTE\Desktop\structured\structured_dataset60.csv", low_memory=False)

# 1. Define the Target Variable
df = df[df['loan_status'].isin(['Fully Paid', 'Charged Off'])]
df['loan_status_binary'] = (df['loan_status'] == 'Fully Paid').astype(int)

# 2. Drop Obvious Non-Predictive Columns
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
                       'settlement_amount', 'settlement_percentage', 'settulation_term', 'loan_status']
df_clean = df.drop(columns=non_predictive_cols, errors='ignore')

# 3. Handle Missing Values
threshold = 0.5
missing_percentages = df_clean.isnull().sum() / len(df_clean)
cols_to_drop = missing_percentages[missing_percentages > threshold].index
df_clean = df_clean.drop(columns=cols_to_drop)

num_cols = df_clean.select_dtypes(include=[np.number]).columns
cat_cols = df_clean.select_dtypes(include=['object']).columns

imputer_num = SimpleImputer(strategy='median')
df_clean[num_cols] = imputer_num.fit_transform(df_clean[num_cols])

imputer_cat = SimpleImputer(strategy='constant', fill_value='missing')
df_clean[cat_cols] = imputer_cat.fit_transform(df_clean[cat_cols])

# 4. Encode Categorical Variables
low_cardinality_cols = [col for col in cat_cols if df_clean[col].nunique() < 10]
high_cardinality_cols = [col for col in cat_cols if df_clean[col].nunique() >= 10]

print(f"Low cardinality columns ({len(low_cardinality_cols)}): {low_cardinality_cols}")
print(f"High cardinality columns ({len(high_cardinality_cols)}): {high_cardinality_cols}")

# One-Hot Encoding for low cardinality
df_clean = pd.get_dummies(df_clean, columns=low_cardinality_cols)

# Label Encoding for high cardinality
label_encoders = {}
for col in high_cardinality_cols:
    le = LabelEncoder()
    df_clean[col] = le.fit_transform(df_clean[col].astype(str))
    label_encoders[col] = le

# 5. Split Data into Features and Target
X = df_clean.drop('loan_status_binary', axis=1)
y = df_clean['loan_status_binary']

# 6. Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 7. Scale the Features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training set shape: {X_train_scaled.shape}")
print(f"Test set shape: {X_test_scaled.shape}")
print(f"Target distribution - Train: {np.bincount(y_train)}")
print(f"Target distribution - Test: {np.bincount(y_test)}")

# 8. Evaluate Baseline Models with Cross-Validation
def evaluate_model_cv(model, X, y, cv=5):
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc')
    print(f"{model.__class__.__name__} CV ROC-AUC Score: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores):.4f})")
    return np.mean(cv_scores)

models = {
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'Random Forest': RandomForestClassifier(random_state=42, n_jobs=-1),
    'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss', use_label_encoder=False)
}

print("\n=== Cross-Validation Results ===")
cv_results = {}
for name, model in models.items():
    print(f"\n--- Evaluating {name} ---")
    score = evaluate_model_cv(model, X_train_scaled, y_train)
    cv_results[name] = score

# 9. Hyperparameter Tuning for XGBoost
param_dist_xgb = {
    'n_estimators': [100, 200, 500],
    'max_depth': [3, 6, 9],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.8, 0.9, 1.0],
    'colsample_bytree': [0.8, 0.9, 1.0]
}

xgb = XGBClassifier(random_state=42, eval_metric='logloss', use_label_encoder=False)
random_search_xgb = RandomizedSearchCV(estimator=xgb,
                                       param_distributions=param_dist_xgb,
                                       n_iter=20,
                                       scoring='roc_auc',
                                       cv=3,
                                       verbose=1,
                                       random_state=42,
                                       n_jobs=-1)

print("\n--- Starting RandomizedSearchCV for XGBoost ---")
random_search_xgb.fit(X_train_scaled, y_train)

print("Best parameters found: ", random_search_xgb.best_params_)
print("Best CV score: ", random_search_xgb.best_score_)

# 10. Final Evaluation on Test Set
best_model = random_search_xgb.best_estimator_

y_pred = best_model.predict(X_test_scaled)
y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]

print("\n=== Final Evaluation on Test Set ===")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("ROC-AUC Score:", roc_auc_score(y_test, y_pred_proba))
print("F1 Score:", f1_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 11. Feature Importance Analysis
plt.figure(figsize=(10, 12))
feat_importances = pd.Series(best_model.feature_importances_, index=X.columns)
feat_importances.nlargest(15).plot(kind='barh')
plt.title('Top 15 Most Important Features')
plt.tight_layout()
plt.savefig('feature_importance.png')  # Save the plot
plt.show()

print("\nTop 10 most important features:")
print(feat_importances.nlargest(10))

# 12. Save Model and Preprocessing Artifacts
joblib.dump(best_model, 'loan_default_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(imputer_num, 'imputer_num.pkl')
joblib.dump(imputer_cat, 'imputer_cat.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')
joblib.dump(X_train.columns.tolist(), 'training_columns.pkl')
joblib.dump(num_cols.tolist(), 'num_cols.pkl')
joblib.dump(cat_cols.tolist(), 'cat_cols.pkl')
joblib.dump(low_cardinality_cols, 'low_cardinality_cols.pkl')
joblib.dump(high_cardinality_cols, 'high_cardinality_cols.pkl')

print("\nModel and preprocessing artifacts saved successfully.")
print("Files created:")
print("- loan_default_model.pkl (the trained model)")
print("- scaler.pkl (fitted StandardScaler)")
print("- imputer_num.pkl (fitted numerical imputer)")
print("- imputer_cat.pkl (fitted categorical imputer)")
print("- label_encoders.pkl (fitted label encoders)")
print("- training_columns.pkl (list of feature columns)")