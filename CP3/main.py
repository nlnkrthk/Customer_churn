from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse

from routers import router
from auth import verify_api_key

# TASK 136: Configure CORS for the React frontend

from fastapi.middleware.cors import CORSMiddleware

# =========================================================
# ACTIVITY 90
# Create FastAPI application
# =========================================================

app = FastAPI()

# TASK 136: Configure CORS for the React frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =========================================================
# Register API routes
# =========================================================
# main.py is now responsible for starting the FastAPI
# application and connecting the router.
#
# The actual endpoint code is kept in routers.py.
# =========================================================

app.include_router(
    router,
    dependencies=[Depends(verify_api_key)]
)


# =========================================================
# API6
# ACTIVITY 129
# Global 404 handler
#========================================================

@app.exception_handler(404)
async def not_found_handler(
    request: Request,
    exc
):

    return JSONResponse(
        status_code=404,
        content={
            "detail": "Route not found",
            "status_code": 404
        }
    )