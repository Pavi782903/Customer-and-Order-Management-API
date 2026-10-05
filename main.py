from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .database import Base, engine
from .routers import customers, orders


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Customer & Order Management API",
    description=(
        "Day 6 Python Daily Assignment - "
        "Customer and Order Management API"
    ),
    version="1.0.0",
)


# ============================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Database integrity error."
        },
    )


# ============================================================
# ROUTERS
# ============================================================

app.include_router(customers.router)
app.include_router(orders.router)


# ============================================================
# ROOT API
# ============================================================

@app.get("/", tags=["Home"])
def root():
    return {
        "message": "Customer & Order Management API is running.",
        "docs": "/docs",
        "redoc": "/redoc",
    }