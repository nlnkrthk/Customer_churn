import pandas as pd
import logging
import os
from datetime import datetime

from customer_cleaner import CustomerCleaner


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# --------------------------------------------------
# 37. Load data
# --------------------------------------------------

def load_data(filepath):
    """
    Load customer data from a CSV file
    and log the row count.
    """

    df = pd.read_csv(filepath)

    logging.info(
        f"Loaded {len(df)} rows from {filepath}"
    )

    return df


# --------------------------------------------------
# 38. Build features
# --------------------------------------------------

def build_features(df):
    """
    Create all 6 engineered features
    and return the enriched DataFrame.
    """

    # Feature 1: tenure_bucket
    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"],
        include_lowest=True
    )

    # Feature 2: high_charge_flag
    median_charge = df["monthly_charges"].median()

    df["high_charge_flag"] = (
        df["monthly_charges"] > median_charge
    ).astype(int)

    # Feature 3: service_count
    service_cols = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies"
    ]

    # Convert service values to 0/1
    for col in service_cols:
        df[col] = df[col].map({
            "Yes": 1,
            "No": 0,
            "No internet service": 0
        })

    # Count services for each customer
    df["service_count"] = df[service_cols].sum(axis=1)

    # Feature 4: is_long_term_customer
    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)

    # Feature 5: has_streaming_bundle
    df["has_streaming_bundle"] = (
        (df["streaming_tv"] == 1) &
        (df["streaming_movies"] == 1)
    ).astype(int)

    # Feature 6: auto_pay_flag
    df["auto_pay_flag"] = (
        df["payment_method"]
        .str.contains(
            "automatic",
            case=False,
            na=False
        )
        .astype(int)
    )

    logging.info("Feature engineering completed.")

    return df


# --------------------------------------------------
# Pipeline
# --------------------------------------------------

def run_pipeline(file_path):

    logging.info("Starting customer pipeline.")

    # Step 1: Load data
    df = load_data(file_path)

    # Step 2: Clean data
    cleaner = CustomerCleaner(df)
    cleaned_df = cleaner.clean()

    logging.info(
        f"Data cleaning completed. Shape: {cleaned_df.shape}"
    )

    # Step 3: Build features
    feature_df = build_features(cleaned_df)

    logging.info(
        f"Feature engineering completed. Shape: {feature_df.shape}"
    )

    return cleaned_df, feature_df


# --------------------------------------------------
# 39. Save outputs
# --------------------------------------------------

def save_outputs(clean_df, feature_df, output_dir):
    """
    Save cleaned and feature-engineered DataFrames
    with timestamps in the filenames.
    """

    # Create output directory
    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # Generate timestamp
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    # Create filenames
    clean_file = os.path.join(
        output_dir,
        f"customer_cleaned_{timestamp}.csv"
    )

    feature_file = os.path.join(
        output_dir,
        f"customer_features_{timestamp}.csv"
    )

    # Save files
    clean_df.to_csv(
        clean_file,
        index=False
    )

    feature_df.to_csv(
        feature_file,
        index=False
    )

    logging.info(
        f"Cleaned data saved to: {clean_file}"
    )

    logging.info(
        f"Feature data saved to: {feature_file}"
    )

    return clean_file, feature_file

#43. Add a simple data quality check before saving: assert no nulls in monthly_charges, assert churn column has only 0/1 values
def validate_data(feature_df):
    """
    Perform basic data quality checks before saving.
    """

    # Check 1: monthly_charges should not contain nulls
    assert (
        feature_df["monthly_charges"].isna().sum() == 0
    ), "monthly_charges contains null values"

    # Check 2: churn should contain only 0 and 1
    assert (
        feature_df["churn"].isin([0, 1]).all()
    ), "churn column contains values other than 0 or 1"

    logging.info("Data quality checks passed.")

# 40. Main function to run the pipeline
#41 Add logging throughout: start time, step completion, row counts, output file paths
#42 Wrap each step in try/except — if any step fails, log the error and raise; do not silently continue

def main():
    """
    Run the complete customer data pipeline.
    """

    # Record pipeline start time
    start_time = datetime.now()

    logging.info("========================================")
    logging.info("Customer pipeline started")
    logging.info(f"Start time: {start_time}")
    logging.info("========================================")

    # ------------------------------------------
    # Step 1: Load data
    # ------------------------------------------

    try:
        df = load_data("customer_churn.csv")

        logging.info(
            f"Load step completed. Rows loaded: {len(df)}"
        )

    except Exception as e:
        logging.error(f"Load step failed: {e}")
        raise

    # ------------------------------------------
    # Step 2: Clean data
    # ------------------------------------------

    try:
        cleaner = CustomerCleaner(df)
        clean_df = cleaner.clean()

        logging.info(
            f"Clean step completed. "
            f"Rows after cleaning: {len(clean_df)}"
        )

    except Exception as e:
        logging.error(f"Clean step failed: {e}")
        raise

    # ------------------------------------------
    # Step 3: Build features
    # ------------------------------------------

    try:
        feature_df = build_features(clean_df.copy())

        logging.info(
            f"Feature engineering step completed. "
            f"Rows: {len(feature_df)}"
        )

    except Exception as e:
        logging.error(
            f"Feature engineering step failed: {e}"
        )
        raise

    # ------------------------------------------
    # Step 4: Data quality checks
    # ------------------------------------------

    try:
        validate_data(feature_df)

    except Exception as e:
        logging.error(
            f"Data quality check failed: {e}"
        )
        raise

    # ------------------------------------------
    # Step 5: Save outputs
    # ------------------------------------------

    try:
        clean_file, feature_file = save_outputs(
            clean_df,
            feature_df,
            "output"
        )

        logging.info("Save step completed.")
        logging.info(f"Cleaned file: {clean_file}")
        logging.info(f"Feature file: {feature_file}")

    except Exception as e:
        logging.error(
            f"Save step failed: {e}"
        )
        raise

    # ------------------------------------------
    # Pipeline completion
    # ------------------------------------------

    end_time = datetime.now()

    logging.info("========================================")
    logging.info(
        "Customer pipeline completed successfully"
    )
    logging.info(f"End time: {end_time}")
    logging.info("========================================")

# --------------------------------------------------
# Run pipeline
# --------------------------------------------------

if __name__ == "__main__":
    main()