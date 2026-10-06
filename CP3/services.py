from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# =========================================================
# API1 SERVICE
# =========================================================
# The service layer contains database queries and
# business logic separately from the API routes.
# =========================================================


# =========================================================
# ACTIVITY 93
# Customer database query
# =========================================================

def get_customer_by_id(db, customer_id):

    # SQL query
    query = text("""
        SELECT
            c.customer_id,
            f.tenure,
            dc.contract_type,
            s.internet_service,
            f.monthly_charges,
            f.churn
        FROM customers c

        JOIN fact_customer_account f
            ON c.customer_id = f.customer_id

        JOIN dim_contract dc
            ON f.contract_id = dc.contract_id

        JOIN services s
            ON c.customer_id = s.customer_id

        WHERE c.customer_id = :customer_id
    """)

    # Execute parameterised query
    # Using a parameter prevents SQL injection
    result = db.execute(
        query,
        {"customer_id": customer_id}
    )

    # Get one row
    return result.fetchone()



# =========================================================
# API2
# ACTIVITY 99
# Service layer function
# =========================================================

def get_churn_summary(db):

    try:

        # =====================================================
        # 100 Overall churn summary
        # =====================================================

        summary_query = text("""
            SELECT
                COUNT(*) AS total_customers,
                SUM(churn) AS churned,
                AVG(churn) AS churn_rate
            FROM fact_customer_account
        """)

        summary = db.execute(summary_query).fetchone()


        # =====================================================
        # 101 Churn rate by contract type
        # =====================================================

        contract_query = text("""
            SELECT
                dc.contract_type,
                AVG(f.churn) AS churn_rate
            FROM fact_customer_account f
            JOIN dim_contract dc
                ON f.contract_id = dc.contract_id
            GROUP BY dc.contract_type
        """)

        contract_results = db.execute(
            contract_query
        ).fetchall()

        by_contract = [
            {
                "contract_type": row.contract_type,
                "churn_rate": round(float(row.churn_rate), 4)
            }
            for row in contract_results
        ]


        # =====================================================
        # 102 Churn rate by internet service
        # =====================================================

        internet_query = text("""
            SELECT
                s.internet_service,
                AVG(f.churn) AS churn_rate
            FROM fact_customer_account f
            JOIN services s
                ON f.customer_id = s.customer_id
            GROUP BY s.internet_service
        """)

        internet_results = db.execute(
            internet_query
        ).fetchall()

        by_internet_service = [
            {
                "internet_service": row.internet_service,
                "churn_rate": round(float(row.churn_rate), 4)
            }
            for row in internet_results
        ]


        # =====================================================
        # 103
        # Return all of this in a single structured JSON response
        # =====================================================

        return {
            "total_customers": summary.total_customers,
            "churned": summary.churned,
            "churn_rate": round(float(summary.churn_rate), 4),
            "by_contract": by_contract,
            "by_internet_service": by_internet_service
        }
#127 db error handling
    except SQLAlchemyError:
        # Database problem occurred
        raise



# =========================================================
# API3 SERVICE
# =========================================================
# ACTIVITY 107
# Query the v_high_risk_customers SQL view
#
# ACTIVITY 108
# Support filtering using:
# limit
# min_tenure
# max_tenure
# =========================================================

def get_high_risk_customers(
    db,
    limit=50,
    min_tenure=None,
    max_tenure=None
):

    # Base query
    query = """
        SELECT *
        FROM sql6_high_risk_customers
        WHERE 1 = 1
    """

    # Parameters for the SQL query
    params = {}


    # =====================================================
    # Filter by minimum tenure
    # =====================================================

    if min_tenure is not None:

        query += """
            AND tenure >= :min_tenure
        """

        params["min_tenure"] = min_tenure


    # =====================================================
    # Filter by maximum tenure
    # =====================================================

    if max_tenure is not None:

        query += """
            AND tenure <= :max_tenure
        """

        params["max_tenure"] = max_tenure


    # =====================================================
    # Limit number of results
    # =====================================================

    query += """
        LIMIT :limit
    """

    params["limit"] = limit


    # Convert string query into SQLAlchemy text object
    query = text(query)


    # Execute parameterised query
    results = db.execute(
        query,
        params
    ).fetchall()


    return results



# =========================================================
# API4 SERVICE
# =========================================================
# ACTIVITY 114
# Query the customer_ml_features table
# for the given customer_id
# =========================================================

def get_customer_features(db, customer_id):

    query = text("""
        SELECT
            customer_id,
            service_count,
            tenure_bucket,
            high_charge_flag,
            is_long_term_customer,
            has_streaming_bundle,
            auto_pay_flag,
            monthly_charges,
            total_charges
        FROM customer_ml_features
        WHERE customer_id = :customer_id
    """)

    # Execute parameterised query
    result = db.execute(
        query,
        {"customer_id": customer_id}
    )

    # Get one customer
    return result.fetchone()