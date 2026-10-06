# Activity 196 - Write build_features(): read cleaned_customers and generate the 6 CP4 features
# File: features.py

import pandas as pd
from sqlalchemy import create_engine


# Database connection
engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecomdb"
)


def build_features(engine):

    # Read cleaned customer data from MySQL
    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    print("Rows read from cleaned_customers:", len(df))


    # ---------------------------------------------------------
    # Feature 1 - tenure_bucket_code
    # CP4 logic:
    # 0-12, 13-24, 25-48, 49-72
    # ---------------------------------------------------------

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"],
        include_lowest=True
    )

    df["tenure_bucket_code"] = (
        df["tenure_bucket"].cat.codes
    )


    # ---------------------------------------------------------
    # Feature 2 - high_charge_flag
    # CP4 logic:
    # monthly_charges > current batch median
    # ---------------------------------------------------------

    median_charge = df["monthly_charges"].median()

    df["high_charge_flag"] = (
        df["monthly_charges"] > median_charge
    ).astype(int)


    # ---------------------------------------------------------
    # Feature 3 - service_count
    # CP4 logic:
    # Yes = 1
    # No = 0
    # No internet service = 0
    # ---------------------------------------------------------

    service_cols = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies"
    ]

    for col in service_cols:

        df[col] = df[col].map({
            "Yes": 1,
            "No": 0,
            "No internet service": 0
        })

    df["service_count"] = (
        df[service_cols].sum(axis=1)
    )


    # ---------------------------------------------------------
    # Feature 4 - is_long_term_customer
    # CP4 logic:
    # tenure >= 24 → 1
    # tenure < 24  → 0
    # ---------------------------------------------------------

    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)


    # ---------------------------------------------------------
    # Feature 5 - has_streaming_bundle
    # CP4 logic:
    # streaming_tv == 1 AND streaming_movies == 1
    # ---------------------------------------------------------

    df["has_streaming_bundle"] = (
        (df["streaming_tv"] == 1) &
        (df["streaming_movies"] == 1)
    ).astype(int)


    # ---------------------------------------------------------
    # Feature 6 - auto_pay_flag
    # CP4 logic:
    # payment method contains "automatic"
    # ---------------------------------------------------------

    df["auto_pay_flag"] = (
        df["payment_method"]
        .str.contains("automatic", case=False)
        .astype(int)
    )


    # ---------------------------------------------------------
    # Select the 6 final ML features
    # ---------------------------------------------------------

    feature_cols = [
        "tenure_bucket_code",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    feature_df = df[
        feature_cols
    ].copy()


    # Write features to MySQL
    feature_df.to_sql(
        "customer_ml_features",
        engine,
        if_exists="replace",
        index=False
    )

    print(
        "Rows written to customer_ml_features:",
        len(feature_df)
    )

    return feature_df


# Activity 197 - Verify feature logic matches CP4 definitions exactly
# File: features.py

def validate_feature_logic(engine):

    # Read source data
    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    # Read generated features
    features = pd.read_sql(
        "SELECT * FROM customer_ml_features",
        engine
    )


    # ---------------------------------------------------------
    # Check 1 - tenure_bucket_code
    # ---------------------------------------------------------

    expected_bucket = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"],
        include_lowest=True
    ).cat.codes

    assert (
        features["tenure_bucket_code"].tolist()
        == expected_bucket.tolist()
    )

    print("PASS - tenure_bucket_code matches CP4")


    # ---------------------------------------------------------
    # Check 2 - high_charge_flag
    # ---------------------------------------------------------

    median_charge = df["monthly_charges"].median()

    expected_high_charge = (
        df["monthly_charges"] > median_charge
    ).astype(int)

    assert (
        features["high_charge_flag"].tolist()
        == expected_high_charge.tolist()
    )

    print(
        f"PASS - high_charge_flag matches CP4 "
        f"(median={median_charge})"
    )


    # ---------------------------------------------------------
    # Check 3 - service_count
    # ---------------------------------------------------------

    service_cols = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies"
    ]

    service_df = df[service_cols].copy()

    for col in service_cols:

        service_df[col] = service_df[col].map({
            "Yes": 1,
            "No": 0,
            "No internet service": 0
        })

    expected_service_count = (
        service_df.sum(axis=1)
    )

    assert (
        features["service_count"].tolist()
        == expected_service_count.tolist()
    )

    print("PASS - service_count matches CP4")


    # ---------------------------------------------------------
    # Check 4 - is_long_term_customer
    # ---------------------------------------------------------

    expected_long_term = (
        df["tenure"] >= 24
    ).astype(int)

    assert (
        features["is_long_term_customer"].tolist()
        == expected_long_term.tolist()
    )

    print("PASS - is_long_term_customer matches CP4")


    # ---------------------------------------------------------
    # Check 5 - has_streaming_bundle
    # ---------------------------------------------------------

    streaming_tv = df["streaming_tv"].map({
        "Yes": 1,
        "No": 0,
        "No internet service": 0
    })

    streaming_movies = df["streaming_movies"].map({
        "Yes": 1,
        "No": 0,
        "No internet service": 0
    })

    expected_streaming_bundle = (
        (streaming_tv == 1) &
        (streaming_movies == 1)
    ).astype(int)

    assert (
        features["has_streaming_bundle"].tolist()
        == expected_streaming_bundle.tolist()
    )

    print("PASS - has_streaming_bundle matches CP4")


    # ---------------------------------------------------------
    # Check 6 - auto_pay_flag
    # ---------------------------------------------------------

    expected_auto_pay = (
        df["payment_method"]
        .str.contains("automatic", case=False)
        .astype(int)
    )

    assert (
        features["auto_pay_flag"].tolist()
        == expected_auto_pay.tolist()
    )

    print("PASS - auto_pay_flag matches CP4")

# Activity 198 - Validate feature row count equals cleaned customer row count
# File: features.py

def validate_row_count(engine):

    # Count rows in cleaned source table
    cleaned_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM cleaned_customers",
        engine
    )["count"].iloc[0]

    # Count rows in feature table
    feature_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM customer_ml_features",
        engine
    )["count"].iloc[0]

    # Fail immediately if counts do not match
    assert cleaned_count == feature_count, (
        f"Row count mismatch: "
        f"cleaned_customers={cleaned_count}, "
        f"customer_ml_features={feature_count}"
    )

    print(
        f"PASS - Row count check: "
        f"cleaned={cleaned_count}, "
        f"features={feature_count}"
    )


# Activity 199 - Validate all 6 feature columns exist and contain no NULLs
# File: features.py

def validate_feature_schema(engine):

    # Expected 6 ML feature columns from CP4
    expected_features = [
        "tenure_bucket_code",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    # Read feature table
    features = pd.read_sql(
        "SELECT * FROM customer_ml_features",
        engine
    )

    # ---------------------------------------------------------
    # Check 1 - All required columns exist
    # ---------------------------------------------------------

    missing_columns = [
        col for col in expected_features
        if col not in features.columns
    ]

    assert not missing_columns, (
        f"Missing feature columns: {missing_columns}"
    )

    print("PASS - All 6 feature columns are present")


    # ---------------------------------------------------------
    # Check 2 - No NULL values in feature columns
    # ---------------------------------------------------------

    for col in expected_features:

        null_count = features[col].isna().sum()

        assert null_count == 0, (
            f"{col} contains {null_count} NULL values"
        )

        print(
            f"PASS - {col} NULL check: {null_count} NULLs"
        )


# Activity 200 - Spot-check 3 customers against CP4 feature output
# File: features.py

# Activity 200 - Spot-check 3 customers against CP4 feature output
# File: features.py

def spot_check_features(engine):

    # Read the original cleaned data used by CP4
    cp4_df = pd.read_csv(
        r"D:\training\python\CUSTOMER RETENTION INTELLIGENCE SYSTEM\CP1\customer_cleaned.csv"
    )

    # Read DE4 feature table
    de4_df = pd.read_sql(
        "SELECT * FROM customer_ml_features",
        engine
    )

    # The six final features
    feature_cols = [
        "tenure_bucket_code",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    # ---------------------------------------------------------
    # Reproduce CP4 feature logic
    # ---------------------------------------------------------

    # Feature 1 - tenure_bucket_code
    cp4_df["tenure_bucket"] = pd.cut(
        cp4_df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"],
        include_lowest=True
    )

    cp4_df["tenure_bucket_code"] = (
        cp4_df["tenure_bucket"].cat.codes
    )

    # Feature 2 - high_charge_flag
    median_charge = cp4_df["monthly_charges"].median()

    cp4_df["high_charge_flag"] = (
        cp4_df["monthly_charges"] > median_charge
    ).astype(int)

    # Service columns
    service_cols = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies"
    ]

    for col in service_cols:

        cp4_df[col] = cp4_df[col].map({
            "Yes": 1,
            "No": 0,
            "No internet service": 0
        })

    # Feature 3 - service_count
    cp4_df["service_count"] = (
        cp4_df[service_cols].sum(axis=1)
    )

    # Feature 4 - is_long_term_customer
    cp4_df["is_long_term_customer"] = (
        cp4_df["tenure"] >= 24
    ).astype(int)

    # Feature 5 - has_streaming_bundle
    cp4_df["has_streaming_bundle"] = (
        (cp4_df["streaming_tv"] == 1) &
        (cp4_df["streaming_movies"] == 1)
    ).astype(int)

    # Feature 6 - auto_pay_flag
    cp4_df["auto_pay_flag"] = (
        cp4_df["payment_method"]
        .str.contains("automatic", case=False)
        .astype(int)
    )

    # ---------------------------------------------------------
    # Compare 3 customers
    # ---------------------------------------------------------

    sample_indexes = [0, 100, 1000]

    for index in sample_indexes:

        cp4_values = cp4_df.loc[
            index,
            feature_cols
        ].tolist()

        de4_values = de4_df.loc[
            index,
            feature_cols
        ].tolist()

        assert cp4_values == de4_values, (
            f"Mismatch found at row {index}: "
            f"CP4={cp4_values}, "
            f"DE4={de4_values}"
        )

        print(
            f"PASS - Customer row {index} matches CP4"
        )
# Activity 196 - Run build_features() when this file is executed directly

if __name__ == "__main__":
    build_features(engine)
    validate_feature_logic(engine)
    validate_row_count(engine)
    validate_feature_schema(engine)
    spot_check_features(engine)