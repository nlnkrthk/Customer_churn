import os

from dotenv import load_dotenv
from fastapi import Header, HTTPException


# =========================================================
# ACTIVITY 131
# Load environment variables from .env
# =========================================================

load_dotenv()

API_KEY = os.getenv("API_KEY")



def verify_api_key(
    x_api_key: str | None = Header(default=None)
):

    if x_api_key != API_KEY:

        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    return True