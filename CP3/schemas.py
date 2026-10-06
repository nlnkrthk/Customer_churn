from pydantic import BaseModel,Field


# =========================================================
# ACTIVITY 92
# Pydantic response model
# =========================================================

class CustomerResponse(BaseModel):

    customer_id: str
    tenure: int
    contract_type: str
    internet_service: str
    monthly_charges: float
    churn: int



# =========================================================
# API4
# =========================================================
# ACTIVITY 117
# Pydantic response model for customer ML features
# =========================================================

class CustomerFeatures(BaseModel):

    customer_id: str
    service_count: int
    tenure_bucket: str
    high_charge_flag: int
    is_long_term_customer: int
    has_streaming_bundle: int
    auto_pay_flag: int
    monthly_charges: float
    total_charges: float


# =========================================================
# API5
# =========================================================
# ACTIVITY 119
# Pydantic request model for churn prediction
# =========================================================


# =========================================================
# API6
# =========================================================
# ACTIVITY 125
# Add field-level Pydantic validators to ChurnPredictionRequest: tenure must be >= 0 and <= 100; monthly_charges must be > 0
# =========================================================

class ChurnPredictionRequest(BaseModel):

    # Customer's tenure in months
    # Must be between 0 and 100
    tenure: int = Field(
        ge=0,
        le=100,
        description="Customer tenure in months"
    )

    # Customer's monthly charges
    # Must be greater than 0
    monthly_charges: float = Field(
        gt=0,
        description="Customer monthly charges"
    )

    # Type of contract
    contract_type: str

    # Number of services used by the customer
    service_count: int



# ACTIVITY 126
# Consistent error response model
#
# All API errors will eventually use this structure:
#
# {
#     "detail": "Customer not found",
#     "status_code": 404
# }
#
# This gives the frontend a consistent format for handling
# errors from different API endpoints.
# =========================================================

class ErrorResponse(BaseModel):

    # Description of the error
    detail: str

    # HTTP status code associated with the error
    status_code: int


class ChurnPredictionRequest(BaseModel):
    tenure: int
    monthly_charges: float
    contract_type: str
    service_count: int