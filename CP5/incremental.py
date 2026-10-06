# Activity 213 - Implement incremental upsert logic for customers
# File: incremental.py

import pandas as pd
from sqlalchemy import create_engine, text


# MySQL connection
engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecomdb"
)


def upsert_customers(engine, df):
    """
    Insert new customers and update existing customers.
    """

    inserted = 0
    updated = 0
    unchanged = 0

    with engine.begin() as connection:

        for _, row in df.iterrows():

            customer_id = row["customer_id"]

            # Check whether customer already exists
            result = connection.execute(
                text("""
                    SELECT
                    c.gender,
                    c.senior_citizen,
                    c.partner,
                    c.dependents,
                    f.tenure
                FROM customers c
                JOIN fact_customer_account f
                    ON c.customer_id = f.customer_id
                WHERE c.customer_id = :customer_id
                """),
                {
                    "customer_id": customer_id
                }
            ).fetchone()

            # ----------------------------------------
            # CASE 1: NEW CUSTOMER
            # ----------------------------------------

            if result is None:

                connection.execute(
                    text("""
                        INSERT INTO customers
                        (
                            customer_id,
                            gender,
                            senior_citizen,
                            partner,
                            dependents
                        )
                        VALUES
                        (
                            :customer_id,
                            :gender,
                            :senior_citizen,
                            :partner,
                            :dependents
                        )
                    """),
                    {
                        "customer_id": customer_id,
                        "gender": row["gender"],
                        "senior_citizen": row["senior_citizen"],
                        "partner": row["partner"],
                        "dependents": row["dependents"]
                    }
                )

                inserted += 1

            else:

                # Existing database values
                existing_values = (
                    result.gender,
                    result.senior_citizen,
                    result.partner,
                    result.dependents,
                    result.tenure
                )

                # Incoming CSV values
                incoming_values = (
                    row["gender"],
                    row["senior_citizen"],
                    row["partner"],
                    row["dependents"],
                    row["tenure"]
                )

                # ----------------------------------------
                # CASE 2: EXISTING CUSTOMER WITH CHANGES
                # ----------------------------------------

                if existing_values != incoming_values:

                    connection.execute(
                    text("""
                        UPDATE customers c
                        JOIN fact_customer_account f
                            ON c.customer_id = f.customer_id
                        SET
                            c.gender = :gender,
                            c.senior_citizen = :senior_citizen,
                            c.partner = :partner,
                            c.dependents = :dependents,
                            f.tenure = :tenure
                        WHERE c.customer_id = :customer_id
                    """),
                    {
                        "customer_id": customer_id,
                        "gender": row["gender"],
                        "senior_citizen": row["senior_citizen"],
                        "partner": row["partner"],
                        "dependents": row["dependents"],
                        "tenure": row["tenure"]
                    }
                )

                    updated += 1

                # ----------------------------------------
                # CASE 3: EXISTING CUSTOMER, NO CHANGE
                # ----------------------------------------

                else:

                    unchanged += 1

    return inserted, updated, unchanged

def log_pipeline_run(
    engine,
    file_name,
    inserted,
    updated,
    unchanged
):
    """
    Record the result of one incremental pipeline run.
    """

    with engine.begin() as connection:

        connection.execute(
            text("""
                INSERT INTO pipeline_run_log
                (
                    file_name,
                    rows_inserted,
                    rows_updated,
                    rows_unchanged
                )
                VALUES
                (
                    :file_name,
                    :inserted,
                    :updated,
                    :unchanged
                )
            """),
            {
                "file_name": file_name,
                "inserted": inserted,
                "updated": updated,
                "unchanged": unchanged
            }
        )

    print("Pipeline run logged successfully.")


if __name__ == "__main__":

    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    print(f"Rows read: {len(df)}")

    inserted, updated, unchanged = upsert_customers(
        engine,
        df
    )

    print("========================================")
    print("INCREMENTAL LOAD RESULT")
    print("========================================")
    print(f"Inserted  : {inserted}")
    print(f"Updated   : {updated}")
    print(f"Unchanged : {unchanged}")
    print("========================================")

    # Log this pipeline run
    log_pipeline_run(
        engine,
        "customer_cleaned.csv",
        inserted,
        updated,
        unchanged
    )