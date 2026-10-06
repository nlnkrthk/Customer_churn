# Activity 185 - Write load_to_staging(filepath, engine): load the valid CSV into stg_customer_raw

import csv
import os
import pandas as pd
from sqlalchemy import create_engine


EXPECTED_COLS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]


def detect_files():
    landing_dir = "data/landing"

    files = []

    for filename in os.listdir(landing_dir):
        if filename.endswith(".csv"):
            files.append(os.path.join(landing_dir, filename))

    return files


def validate_schema(filepath):
    with open(filepath, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))

    return header == EXPECTED_COLS, header


def load_to_staging(filepath, engine):
    df = pd.read_csv(filepath)

    df.to_sql(
        "stg_customer_raw",
        engine,
        if_exists="replace",
        index=False
    )

    return len(df)


# Test Activity 185
engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecomdb"
)

files = detect_files()

for file in files:

    valid, header = validate_schema(file)

    if valid:
        row_count = load_to_staging(file, engine)

        print("File:", file)
        print("Status: LOADED")
        print("Rows:", row_count)


# Activity 186 - Write log_ingestion(filename, status, rows, reason): record ingestion result in ingestion_log

def log_ingestion(filename, status, rows, reason, engine):
    query = """
        INSERT INTO ingestion_log
        (filename, status, row_count, reason)
        VALUES (%s, %s, %s, %s)
    """

    with engine.connect() as connection:
        connection.exec_driver_sql(
            query,
            (filename, status, rows, reason)
        )
        connection.commit()



# Activity 187 - Write process_landing(): orchestrate detect → validate → load → log

def process_landing(engine):
    files = detect_files()

    for filepath in files:

        filename = os.path.basename(filepath)

        # Step 1: Validate schema
        valid, header = validate_schema(filepath)

        if not valid:
            reason = "Column mismatch. Expected 21 columns in exact order."

            log_ingestion(
                filename,
                "REJECTED",
                0,
                reason,
                engine
            )

            print(f"File: {filename}")
            print("Status: REJECTED")
            print(f"Reason: {reason}")

            continue

        # Step 2: Load valid file into staging
        row_count = load_to_staging(filepath, engine)

        # Step 3: Log successful ingestion
        log_ingestion(
            filename,
            "LOADED",
            row_count,
            None,
            engine
        )

        print(f"File: {filename}")
        print("Status: LOADED")
        print(f"Rows: {row_count}")



# Activity 187 - Run the complete landing-folder ingestion process

if __name__ == "__main__":
    process_landing(engine)