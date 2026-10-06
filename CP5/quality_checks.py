import pandas as pd
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def enforce_quality_gates(results):
    """
    Activities 226 and 227

    CRITICAL failure:
        Stop the pipeline by raising an exception.

    WARNING failure:
        Log a warning but allow the pipeline to continue.
    """

    critical_failures = []

    for result in results:

        check_name = result["check_name"]
        status = result["status"]
        severity = result.get("severity", "CRITICAL")

        # ----------------------------------------
        # CHECK PASSED
        # ----------------------------------------

        if status == "PASS":
            print(
                f"PASS - {check_name} "
                f"[{severity}]"
            )

        # ----------------------------------------
        # CHECK FAILED
        # ----------------------------------------

        else:

            if severity == "CRITICAL":

                print(
                    f"FAIL - {check_name} "
                    f"[CRITICAL]"
                )

                critical_failures.append(check_name)

            elif severity == "WARNING":

                logging.warning(
                    f"WARNING - {check_name} failed. "
                    f"Pipeline will continue."
                )

    # ----------------------------------------
    # ACTIVITY 226
    # STOP PIPELINE IF CRITICAL CHECK FAILS
    # ----------------------------------------

    if critical_failures:

        raise Exception(
            "CRITICAL DATA QUALITY CHECK FAILED. "
            f"Pipeline stopped. Failed checks: "
            f"{critical_failures}"
        )

    print("All critical quality checks passed.")

# --------------------------------------------------
# 1. NULL RATE CHECK
# --------------------------------------------------

def check_null_rate(df, col, threshold):
    """
    Check whether the null percentage of a column
    is within the allowed threshold.

    threshold is given as a percentage.

    Example:
        threshold = 0
        means no NULL values are allowed.
    """

    null_rate = df[col].isna().mean() * 100

    passed = null_rate <= threshold

    return {
        "check_name": f"null_rate_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": round(null_rate, 4),
        "threshold": threshold,
        "severity": "CRITICAL"
    }


# --------------------------------------------------
# 2. VALUE RANGE CHECK
# --------------------------------------------------

def check_value_range(df, col, min_value, max_value):
    """
    Check whether all values in a column are
    inside the allowed range.
    """

    invalid_count = (
        (df[col] < min_value) |
        (df[col] > max_value)
    ).sum()

    passed = invalid_count == 0

    return {
        "check_name": f"value_range_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": int(invalid_count),
        "threshold": f"{min_value} to {max_value}",
        "severity": "CRITICAL"
    }


# --------------------------------------------------
# 3. ALLOWED VALUES CHECK
# --------------------------------------------------

def check_allowed_values(df, col, allowed_set):
    """
    Check that every value in a column belongs
    to the allowed set.
    """

    invalid_count = (
        ~df[col].isin(allowed_set)
    ).sum()

    passed = invalid_count == 0

    return {
        "check_name": f"allowed_values_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": int(invalid_count),
        "threshold": list(allowed_set),
        "severity": "CRITICAL"
    }


# --------------------------------------------------
# 4. ROW COUNT CHECK
# --------------------------------------------------

def check_row_count(df, expected_min):
    """
    Check that the dataset contains at least
    the expected minimum number of rows.
    """

    actual_count = len(df)

    passed = actual_count >= expected_min

    return {
        "check_name": "row_count",
        "status": "PASS" if passed else "FAIL",
        "value_found": actual_count,
        "threshold": expected_min,
        "severity": "CRITICAL"
    }


# --------------------------------------------------
# 5. DUPLICATE CHECK
# --------------------------------------------------

def check_no_duplicates(df, key_col):
    """
    Check that the key column contains no duplicates.
    """

    duplicate_count = df[key_col].duplicated().sum()

    passed = duplicate_count == 0

    return {
        "check_name": f"duplicates_{key_col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": int(duplicate_count),
        "threshold": 0,
        "severity": "CRITICAL"
    }


# --------------------------------------------------
# 6. CHURN DISTRIBUTION CHECK
# --------------------------------------------------

def check_churn_distribution(df):
    """
    Check the distribution of churn values.

    Expected churn values:
        0 = No
        1 = Yes
    """

    churn_counts = df["churn"].value_counts().to_dict()

    invalid_values = [
        value
        for value in churn_counts
        if value not in [0, 1]
    ]

    passed = len(invalid_values) == 0

    return {
        "check_name": "churn_distribution",
        "status": "PASS" if passed else "FAIL",
        "value_found": churn_counts,
        "threshold": "Only 0 and 1 allowed",
        "severity": "CRITICAL"
    }


# --------------------------------------------------
# RUN QUALITY CHECKS
# --------------------------------------------------

if __name__ == "__main__":

    # Read the cleaned data
    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        "mysql+pymysql://root:root@localhost/telecomdb"
    )

    print(f"Rows read: {len(df)}")

    results = []

    # --------------------------------------------------
    # 220. NULL CHECKS
    # --------------------------------------------------

    results.append(
        check_null_rate(
            df,
            "monthly_charges",
            0
        )
    )

    results.append(
        check_null_rate(
            df,
            "tenure",
            0
        )
    )

    # --------------------------------------------------
    # 221. VALUE RANGE CHECKS
    # --------------------------------------------------

    results.append(
        check_value_range(
            df,
            "tenure",
            0,
            100
        )
    )

    results.append(
        check_value_range(
            df,
            "monthly_charges",
            0.000001,
            float("inf")
        )
    )

    # --------------------------------------------------
    # 222. ALLOWED CONTRACT VALUES
    # --------------------------------------------------

    results.append(
        check_allowed_values(
            df,
            "contract",
            {
                "Month-to-month",
                "One year",
                "Two year"
            }
        )
    )

    # --------------------------------------------------
    # 223. ROW COUNT
    # --------------------------------------------------

    results.append(
        check_row_count(
            df,
            7000
        )
    )

    # --------------------------------------------------
    # 224. DUPLICATE CUSTOMER IDs
    # --------------------------------------------------

    results.append(
        check_no_duplicates(
            df,
            "customer_id"
        )
    )

    # --------------------------------------------------
    # CHURN CHECK
    # --------------------------------------------------

    results.append(
        check_churn_distribution(df)
    )

    # --------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("DATA QUALITY CHECKS")
    print("=" * 60)

    for result in results:

        print(
            f"{result['check_name']:30} : "
            f"{result['status']} "
            f"(value={result['value_found']}, "
            f"threshold={result['threshold']})"
        )
    print("=" * 60)
    # --------------------------------------------------
    # 225. WRITE QUALITY REPORT
    # --------------------------------------------------

    with open("quality_report.json", "w") as file:

        json.dump(
            results,
            file,
            indent=4,
            default=str
        )

    print()
    print("Quality report written to quality_report.json")

        # --------------------------------------------------
    # 226 + 227. ENFORCE QUALITY GATES
    # --------------------------------------------------

    enforce_quality_gates(results)
    