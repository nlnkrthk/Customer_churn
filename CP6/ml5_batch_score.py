# Task 271 — Create batch_score.py

import pandas as pd
from datetime import datetime

from predict import predict_churn


print("Batch scoring job started!")

# Task 272 — Load all customers from the customer ML features CSV

df = pd.read_csv(
    r"D:\training\python\CUSTOMER RETENTION INTELLIGENCE SYSTEM\CP1\customer_features.csv"
)

print("Customer data loaded successfully!")
print("Shape:", df.shape)

print("\nColumns:")
print(df.columns.tolist())


# Task 273 — Apply predict_churn() to every customer using df.apply()

def score_customer(row):

    result = predict_churn(
        tenure=row["tenure"],
        monthly_charges=row["monthly_charges"],
        contract_type=row["contract"],
        service_count=row["service_count"]
    )

    return pd.Series({
        "risk_score": result["risk_score"],
        "prediction": result["prediction"],
        "confidence": result["confidence"]
    })


# Score every customer
scores = df.apply(score_customer, axis=1)

print("Batch prediction completed!")

print("\nFirst 10 predictions:")
print(scores.head(10))

# Task 274 — Extract risk_score, prediction, and confidence into new columns

df["risk_score"] = scores["risk_score"]
df["prediction"] = scores["prediction"]
df["confidence"] = scores["confidence"]

print("Prediction columns added successfully!")

print("\nUpdated data:")
print(
    df[
        [
            "customer_id",
            "risk_score",
            "prediction",
            "confidence"
        ]
    ].head(10)
)

# Task 275 — Add a scoring_date column using today's date

df["scoring_date"] = datetime.today().strftime("%Y-%m-%d")

print("Scoring date added successfully!")

print("\nScoring date:")
print(df["scoring_date"].head())

# Task 276 — Save customer_risk_table to CSV

risk_table = df[
    [
        "customer_id",
        "risk_score",
        "prediction",
        "confidence",
        "scoring_date"
    ]
].copy()

output_path = "customer_risk_table.csv"

risk_table.to_csv(
    output_path,
    index=False
)

print("customer_risk_table saved successfully!")
print("Rows saved:", len(risk_table))
print("Output file:", output_path)

# Task 277 — Print a summary of Likely to churn vs Unlikely to churn

prediction_counts = risk_table["prediction"].value_counts()

print("\nPredicted churn distribution:")
print(prediction_counts)

print("\nPredicted churn distribution as percentages:")
print(
    risk_table["prediction"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

# Task 278 — Print the top 10 highest-risk customers and cross-check with SQL6

top_10_risk = risk_table.sort_values(
    by="risk_score",
    ascending=False
).head(10)

print("\nTop 10 highest-risk customers:")
print(top_10_risk.to_string(index=False))

'''
# Task 279 — Explain how batch scoring would be added as Task 7 in the DE7 Airflow DAG

The batch scoring job would be added as Task 7 after the existing data
engineering tasks have created the customer_ml_features dataset.

Task 7 would execute batch_score.py, load the latest customer features,
apply the trained churn model to all customers, and create the
customer_risk_table.

The customer_risk_table would then be available for the React dashboard,
FastAPI endpoints, retention team, and future AI assistant.

Airflow would run this task on the required schedule, such as daily,
so that customer churn risk is refreshed automatically.

The task should only run after the feature-generation tasks have completed
successfully, ensuring that batch scoring always uses the latest data.
'''