# Task 263 — Create predict.py: load the best model from models/ at module level

import joblib
import pandas as pd


# Load the trained Decision Tree model once when this module is imported
model = joblib.load("models/tree_churn.pkl")

print("Churn model loaded successfully!")


# Task 264 — Define preprocess_input(tenure, monthly_charges, contract_type, service_count) — creates a properly encoded single-row DataFrame matching the training feature columns

def preprocess_input(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):
    # Create the features required by the trained model
    data = {
        "tenure": tenure,
        "monthly_charges": monthly_charges,

        # Not supplied by the current API
        "total_charges": 0,

        "service_count": service_count,

        # Default values for features not supplied by the API
        "high_charge_flag": 0,
        "is_long_term_customer": int(tenure >= 24),
        "auto_pay_flag": 0,
        "has_streaming_bundle": 0,

        # Contract one-hot encoding
        "contract_Month-to-month": int(
            contract_type == "Month-to-month"
        ),
        "contract_One year": int(
            contract_type == "One year"
        ),
        "contract_Two year": int(
            contract_type == "Two year"
        ),

        # Internet service is not supplied by the current API
        "internet_service_DSL": 0,
        "internet_service_Fiber optic": 0,
        "internet_service_No": 0
    }

    # Create a single-row DataFrame
    input_df = pd.DataFrame([data])

    return input_df


# Task 265 — Define predict_churn(tenure, monthly_charges, contract_type, service_count) — calls preprocess_input, then model.predict() and predict_proba()

# Task 266 — Return {"risk_score": float, "prediction": "Likely to churn" / "Unlikely to churn", "confidence": float}

def predict_churn(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):
    # Preprocess the incoming customer data
    input_df = preprocess_input(
        tenure=tenure,
        monthly_charges=monthly_charges,
        contract_type=contract_type,
        service_count=service_count
    )

    # Get the predicted class
    prediction = model.predict(input_df)[0]

    # Get probability of churn
    risk_score = model.predict_proba(input_df)[0][1]

    # Convert prediction to business-friendly text
    if prediction == 1:
        prediction_text = "Likely to churn"
    else:
        prediction_text = "Unlikely to churn"

    # Confidence = probability of the predicted class
    confidence = model.predict_proba(input_df)[0][prediction]

    return {
        "risk_score": float(risk_score),
        "prediction": prediction_text,
        "confidence": float(confidence)
    }