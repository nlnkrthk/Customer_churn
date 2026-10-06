# Activity 190 - Import CustomerCleaner from CP1 and prepare the cleaning stage

import importlib.util
import pandas as pd
from sqlalchemy import create_engine


# Full path to the existing CustomerCleaner file
cleaner_path = r"D:\training\python\CUSTOMER RETENTION INTELLIGENCE SYSTEM\CP1\customer_cleaner.py"

# Create a module specification from the file
spec = importlib.util.spec_from_file_location(
    "customer_cleaner",
    cleaner_path
)

# Create the module
customer_cleaner = importlib.util.module_from_spec(spec)

# Execute the module
spec.loader.exec_module(customer_cleaner)

# Get the CustomerCleaner class
CustomerCleaner = customer_cleaner.CustomerCleaner

print("CustomerCleaner imported successfully")


# Activity 190 - Write clean_staging(): read staging, reuse CustomerCleaner, write cleaned_customers

engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecomdb"
)


def clean_staging(engine):

    # Read raw data from the staging table
    df = pd.read_sql(
        "SELECT * FROM stg_customer_raw",
        engine
    )

    print("Rows read from staging:", len(df))

    # Create CustomerCleaner using the staging DataFrame
    cleaner = CustomerCleaner(df)

    # Run the existing CP1 cleaning pipeline
    cleaned_df = cleaner.clean()

    # Write cleaned data to cleaned_customers
    cleaned_df.to_sql(
        "cleaned_customers",
        engine,
        if_exists="replace",
        index=False
    )

    print("Rows written to cleaned_customers:", len(cleaned_df))

    return len(cleaned_df)


# Activity 191 - Write build_curated_tables(): populate dim_contract, dim_payment, customers, and fact_customer_account

# Activity 191 - Write build_curated_tables(): populate dim_contract, dim_payment, customers, and fact_customer_account

def build_curated_tables(engine):

    # Read cleaned data
    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    print("Rows read from cleaned_customers:", len(df))


    # ---------------------------------------------------------
    # 1. Clear child table first
    # ---------------------------------------------------------

    with engine.begin() as connection:

        connection.exec_driver_sql(
            "DELETE FROM fact_customer_account"
        )

    print("fact_customer_account cleared")


    # ---------------------------------------------------------
    # 2. Clear dimension tables
    # ---------------------------------------------------------

    with engine.begin() as connection:

        connection.exec_driver_sql(
            "DELETE FROM dim_contract"
        )

        connection.exec_driver_sql(
            "DELETE FROM dim_payment"
        )

    print("Dimension tables cleared")


    # ---------------------------------------------------------
    # 3. Populate dim_contract
    # ---------------------------------------------------------

    contracts = df[["contract"]].drop_duplicates()

    with engine.begin() as connection:

        for contract in contracts["contract"]:

            connection.exec_driver_sql(
                """
                INSERT INTO dim_contract (contract_type)
                VALUES (%s)
                """,
                (contract,)
            )

    print("dim_contract populated:", len(contracts))


    # ---------------------------------------------------------
    # 4. Populate dim_payment
    # ---------------------------------------------------------

    payments = df[["payment_method"]].drop_duplicates()

    with engine.begin() as connection:

        for payment in payments["payment_method"]:

            connection.exec_driver_sql(
                """
                INSERT INTO dim_payment (payment_method)
                VALUES (%s)
                """,
                (payment,)
            )

    print("dim_payment populated:", len(payments))


    # ---------------------------------------------------------
    # 5. Refresh customers table
    # ---------------------------------------------------------

    # Activity 191 - Populate customers without deleting existing parent rows

    customers = df[
        [
            "customer_id",
            "gender",
            "senior_citizen",
            "partner",
            "dependents"
        ]
    ].copy()

    with engine.begin() as connection:

        for _, row in customers.iterrows():

            connection.exec_driver_sql(
                """
                UPDATE customers
                SET
                    gender = %s,
                    senior_citizen = %s,
                    partner = %s,
                    dependents = %s
                WHERE customer_id = %s
                """,
                (
                    row["gender"],
                    row["senior_citizen"],
                    row["partner"],
                    row["dependents"],
                    row["customer_id"]
                )
            )

    print("customers updated:", len(customers))


    # ---------------------------------------------------------
    # 6. Read dimension IDs
    # ---------------------------------------------------------

    contract_lookup = pd.read_sql(
        "SELECT contract_id, contract_type FROM dim_contract",
        engine
    )

    payment_lookup = pd.read_sql(
        "SELECT payment_id, payment_method FROM dim_payment",
        engine
    )


    # ---------------------------------------------------------
    # 7. Add foreign keys to customer data
    # ---------------------------------------------------------

    df = df.merge(
        contract_lookup,
        left_on="contract",
        right_on="contract_type",
        how="left"
    )

    df = df.merge(
        payment_lookup,
        on="payment_method",
        how="left"
    )


    # ---------------------------------------------------------
    # 8. Build fact table
    # ---------------------------------------------------------

    fact = df[
        [
            "customer_id",
            "tenure",
            "monthly_charges",
            "total_charges",
            "churn",
            "contract_id",
            "payment_id"
        ]
    ].copy()


    # Insert into existing fact table
    fact.to_sql(
        "fact_customer_account",
        engine,
        if_exists="append",
        index=False
    )

    print(
        "fact_customer_account populated:",
        len(fact)
    )


# Activity 192 - Add row count check: cleaned_customers must equal stg_customer_raw

def check_row_count(engine):

    # Get row count from staging table
    staging_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM stg_customer_raw",
        engine
    ).iloc[0]["count"]

    # Get row count from cleaned table
    cleaned_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM cleaned_customers",
        engine
    ).iloc[0]["count"]

    # Compare the two row counts
    assert staging_count == cleaned_count, (
        f"Row count mismatch: "
        f"staging={staging_count}, "
        f"cleaned={cleaned_count}"
    )

    print(
        f"PASS - Row count check: "
        f"staging={staging_count}, "
        f"cleaned={cleaned_count}"
    )

# Activity 193 - Add data quality assertions for NULLs and churn values

def check_data_quality(engine):

    # Read cleaned customer data
    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    # ---------------------------------------------------------
    # Check 1: customer_id must not contain NULL values
    # ---------------------------------------------------------

    null_customer_id = df["customer_id"].isna().sum()

    assert null_customer_id == 0, (
        f"customer_id contains {null_customer_id} NULL values"
    )

    print(
        f"PASS - customer_id NULL check: {null_customer_id} NULLs"
    )


    # ---------------------------------------------------------
    # Check 2: monthly_charges must not contain NULL values
    # ---------------------------------------------------------

    null_monthly_charges = df["monthly_charges"].isna().sum()

    assert null_monthly_charges == 0, (
        f"monthly_charges contains {null_monthly_charges} NULL values"
    )

    print(
        f"PASS - monthly_charges NULL check: "
        f"{null_monthly_charges} NULLs"
    )


    # ---------------------------------------------------------
    # Check 3: churn must contain only 0 or 1
    # ---------------------------------------------------------

    invalid_churn = (
        ~df["churn"].isin([0, 1])
    ).sum()

    assert invalid_churn == 0, (
        f"churn contains {invalid_churn} invalid values"
    )

    print(
        f"PASS - churn value check: "
        f"{invalid_churn} invalid values"
    )

# Activity 194 - Write a simple quality report with PASS/FAIL and counts

def quality_report(engine):

    # Read staging and cleaned data
    staging_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM stg_customer_raw",
        engine
    ).iloc[0]["count"]

    cleaned_count = pd.read_sql(
        "SELECT COUNT(*) AS count FROM cleaned_customers",
        engine
    ).iloc[0]["count"]

    # Count NULL customer IDs
    null_customer_id = pd.read_sql(
        """
        SELECT COUNT(*) AS count
        FROM cleaned_customers
        WHERE customer_id IS NULL
        """,
        engine
    ).iloc[0]["count"]

    # Count NULL monthly charges
    null_monthly_charges = pd.read_sql(
        """
        SELECT COUNT(*) AS count
        FROM cleaned_customers
        WHERE monthly_charges IS NULL
        """,
        engine
    ).iloc[0]["count"]

    # Count invalid churn values
    invalid_churn = pd.read_sql(
        """
        SELECT COUNT(*) AS count
        FROM cleaned_customers
        WHERE churn NOT IN (0, 1)
           OR churn IS NULL
        """,
        engine
    ).iloc[0]["count"]

    # Determine PASS / FAIL
    row_count_status = (
        "PASS" if staging_count == cleaned_count else "FAIL"
    )

    customer_id_status = (
        "PASS" if null_customer_id == 0 else "FAIL"
    )

    monthly_charges_status = (
        "PASS" if null_monthly_charges == 0 else "FAIL"
    )

    churn_status = (
        "PASS" if invalid_churn == 0 else "FAIL"
    )

    # Print quality report
    print()
    print("=" * 50)
    print("              DATA QUALITY REPORT")
    print("=" * 50)

    print(
        f"Row count check       : {row_count_status} "
        f"(staging={staging_count}, cleaned={cleaned_count})"
    )

    print(
        f"customer_id NULL check: {customer_id_status} "
        f"(NULLs={null_customer_id})"
    )

    print(
        f"monthly_charges NULL  : {monthly_charges_status} "
        f"(NULLs={null_monthly_charges})"
    )

    print(
        f"churn value check     : {churn_status} "
        f"(invalid={invalid_churn})"
    )

    print("=" * 50)


# Activity 195 - Verify all DE3 curated tables are populated

def verify_curated_tables(engine):

    tables = [
        "cleaned_customers",
        "dim_contract",
        "dim_payment",
        "customers",
        "fact_customer_account"
    ]

    print()
    print("=" * 50)
    print("        DE3 FINAL TABLE VERIFICATION")
    print("=" * 50)

    for table in tables:

        result = pd.read_sql(
            f"SELECT COUNT(*) AS count FROM {table}",
            engine
        )

        count = result.iloc[0]["count"]

        if count > 0:
            print(f"{table:<25} : PASS ({count} rows)")
        else:
            print(f"{table:<25} : FAIL (0 rows)")

    print("=" * 50)
# Activity 190 - Run clean_staging() when this file is executed directly

# Activity 191 - Run cleaning stage followed by curated table build

if __name__ == "__main__":
    clean_staging(engine)
    build_curated_tables(engine)
    check_row_count(engine)
    check_data_quality(engine)
    quality_report(engine)
    verify_curated_tables(engine)