from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from predict import predict_churn as predict_churn_model
from schemas import (
    CustomerResponse,
    CustomerFeatures,
    ChurnPredictionRequest,
    ErrorResponse
)

from services import (
    get_customer_by_id,
    get_churn_summary,
    get_high_risk_customers,
    get_customer_features
)

import logging
# =========================================================
# API6
# ACTIVITY 128
# Logging configuration
#
# Logging allows us to track:
# - Incoming requests
# - Important parameters
# - Response status
# - Errors
# =========================================================

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================================================
# Create API router
# =========================================================

router = APIRouter()


# =========================================================
# API1
# =========================================================
# ACTIVITY 93
# Implement GET /customer/{customer_id}
# =========================================================

@router.get(
    "/customer/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(customer_id: str):
     # =====================================================
    # ACTIVITY 128
    # Log incoming request
    # =====================================================

    logger.info(
        f"GET /customer/{customer_id} - Request received"
    )

    # Create database session
    db = SessionLocal()

    try:

        # Call the service layer
        # The SQL query is handled inside services.py
        customer = get_customer_by_id(
            db,
            customer_id
        )


        # =================================================
        # Customer not found
        #
        # ACTIVITY 93
        # Raise HTTPException(404) if not found
        # =================================================

        if customer is None:

            logger.info(
                f"GET /customer/{customer_id} - Response 404"
            )
             
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        logger.info(
            f"GET /customer/{customer_id} - Response 200"
        )
        # =================================================
        # ACTIVITY 94
        # Return the result as the CustomerResponse model
        # =================================================

        return CustomerResponse(
            customer_id=customer.customer_id,
            tenure=customer.tenure,
            contract_type=customer.contract_type,
            internet_service=customer.internet_service,
            monthly_charges=float(
                customer.monthly_charges
            ),
            churn=customer.churn
        )


    # ACTIVITY 127
    # Database error handling
    except HTTPException:
        # Preserve our intentional 404 error
        raise

    except SQLAlchemyError:

        logger.error(
            f"GET /customer/{customer_id} - Response 500"
        )

        # Database is unavailable or query failed
        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:

        # Close database session
        db.close()


# =========================================================
# API1 TESTING
# =========================================================
# ACTIVITY 96
# Test at /docs:
# Look up a known customer ID
# Example: "7590-VHVEG"
# =========================================================

'''
Example successful response:

{
    "customer_id": "7590-VHVEG",
    "tenure": 1,
    "contract_type": "Month-to-month",
    "internet_service": "DSL",
    "monthly_charges": 29.85,
    "churn": 0
}
'''


# =========================================================
# ACTIVITY 97
# Test a non-existent ID
# Confirm 404 is returned with a clear message
# =========================================================

'''
Response:

Code: 404

Response body:

{
    "detail": "Customer not found"
}
'''


# =========================================================
# API2
# ACTIVITY 98
# Churn summary endpoint
# =========================================================

@router.get("/churn/summary")
def churn_summary():

    # =====================================================
    # ACTIVITY 128
    # Log incoming request
    # =====================================================

    logger.info(
        "GET /churn/summary - Request received"
    )

    db = SessionLocal()

    try:

        result = get_churn_summary(db)

        logger.info(
            "GET /churn/summary - Response 200"
        )

        return result

    except SQLAlchemyError:

        logger.error(
            "GET /churn/summary - Response 500"
        )

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:
        db.close()


# =========================================================
# ACTIVITY 104
# Test at /docs
# Verify values match your SQL4 query results
# =========================================================

'''
Expected result from your database:

{
  "total_customers": 7043,
  "churned": 1869,
  "churn_rate": 0.2654,

  "by_contract": [
    {
      "contract_type": "Month-to-month",
      "churn_rate": 0.4271
    },
    {
      "contract_type": "One year",
      "churn_rate": 0.1127
    },
    {
      "contract_type": "Two year",
      "churn_rate": 0.0283
    }
  ],

  "by_internet_service": [
    {
      "internet_service": "DSL",
      "churn_rate": 0.1896
    },
    {
      "internet_service": "Fiber optic",
      "churn_rate": 0.4189
    },
    {
      "internet_service": "No",
      "churn_rate": 0.074
    }
  ]
}
'''


# =========================================================
# ACTIVITY 105
# Discuss:
# Why create a service layer function rather than putting
# SQL directly in the route?
# =========================================================

'''
We use a service layer to keep business logic separate
from the API route.

Reasoning:
This makes the route cleaner, and the same business logic
can be tested and reused without depending on the HTTP
endpoint.
'''


# =========================================================
# API3
# =========================================================
# ACTIVITY 106
# Add GET /customers/high-risk
#
# ACTIVITY 108
# Add optional query parameters:
# limit = maximum number of customers
# min_tenure = minimum customer tenure
# max_tenure = maximum customer tenure
# =========================================================

@router.get("/customers/high-risk")
def high_risk_customers(
    limit: int = 50,
    min_tenure: int | None = None,
    max_tenure: int | None = None
):
    # =====================================================
    # ACTIVITY 128
    # Log incoming request and parameters
    # =====================================================
    logger.info(
        f"GET /customers/high-risk - "
        f"limit={limit}, min_tenure={min_tenure}, "
        f"max_tenure={max_tenure}"
    )

    # Create database session
    db = SessionLocal()

    try:
        # =================================================
        # ACTIVITY 107
        # Query the v_high_risk_customers SQL view
        # =================================================

        results = get_high_risk_customers(
            db,
            limit,
            min_tenure,
            max_tenure
        )

        logger.info(
                    "GET /customers/high-risk - Response 200"
        )

        # Convert SQLAlchemy rows into dictionaries
        return [
            dict(row._mapping)
            for row in results
        ]

    except SQLAlchemyError:

        logger.error(
            "GET /customers/high-risk - Response 500"
        )

        # =====================================================
        # ACTIVITY 127
        # Database error handling
        # =====================================================

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:

        # Close database session
        db.close()



# =========================================================
# API4
# =========================================================
# ACTIVITY 113
# Add GET /customer/{customer_id}/features
#
# Nested path:
# /customer/{customer_id}/features
#
# This represents a sub-resource:
# customer → features
# =========================================================

@router.get(
    "/customer/{customer_id}/features",
    response_model=CustomerFeatures
)
def customer_features(customer_id: str):

    # Create database session
    db = SessionLocal()

    try:
        logger.info(
            f"GET /customer/{customer_id}/features - Request received"
        )
        # =================================================
        # ACTIVITY 114
        # Query the customer_ml_features table
        # =================================================

        features = get_customer_features(
            db,
            customer_id
        )


        # =================================================
        # ACTIVITY 116
        # Raise 404 if customer not found
        # =================================================

        if features is None:

            logger.info(
                    f"GET /customer/{customer_id}/features - Response 404"
            )

            raise HTTPException(
                status_code=404,
                detail="Customer features not found"
            )


        # =================================================
        # ACTIVITY 115
        # Return all engineered features
        # =================================================

        logger.info(
            f"GET /customer/{customer_id}/features - Response 200"
        )

        return CustomerFeatures(
            customer_id=features.customer_id,
            service_count=features.service_count,
            tenure_bucket=features.tenure_bucket,
            high_charge_flag=features.high_charge_flag,
            is_long_term_customer=features.is_long_term_customer,
            has_streaming_bundle=features.has_streaming_bundle,
            auto_pay_flag=features.auto_pay_flag,
            monthly_charges=float(
                features.monthly_charges
            ),
            total_charges=float(
                features.total_charges
            )
        )

    except HTTPException:
        # Preserve our intentional 404 error
        raise

    except SQLAlchemyError:

        # =====================================================
        # ACTIVITY 127
        # Database error handling
        # =====================================================
        logger.error(
            f"GET /customer/{customer_id}/features - Response 500"
        )

        raise HTTPException(
            status_code=500,
            detail="Database unavailable"
        )

    finally:

        # Close database session
        db.close()


# =========================================================
# API5
# =========================================================
# ACTIVITY 120
# POST /predict-churn
# =========================================================

# Task 267 — Replace the /predict-churn stub with the real trained model

# Task 267 — Replace the /predict-churn stub with a real call to the trained ML model

@router.post("/predict-churn")
def predict_churn(request: ChurnPredictionRequest):

    logger.info(
        "POST /predict-churn - Request received"
    )

    # Call the trained Decision Tree model
    result = predict_churn_model(
        tenure=request.tenure,
        monthly_charges=request.monthly_charges,
        contract_type=request.contract_type,
        service_count=request.service_count
    )

    logger.info(
        "POST /predict-churn - Response 200"
    )

    return result