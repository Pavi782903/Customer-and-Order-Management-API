from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, condecimal, constr


# ============================================================
# CUSTOMER SCHEMAS
# ============================================================

class CustomerCreate(BaseModel):
    customer_name: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    phone_number: str | None = Field(
        default=None,
        max_length=20,
    )

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )


class CustomerUpdate(BaseModel):
    customer_name: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ) | None = None

    email: EmailStr | None = None

    phone_number: str | None = Field(
        default=None,
        max_length=20,
    )

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: int
    customer_name: str
    email: EmailStr
    phone_number: str | None
    address: str | None
    city: str | None
    created_date: datetime


# ============================================================
# ORDER SCHEMAS
# ============================================================

OrderStatus = Literal[
    "Pending",
    "Confirmed",
    "Shipped",
    "Delivered",
    "Cancelled",
]


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)

    product_name: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=150,
    )

    quantity: int = Field(gt=0)

    unit_price: condecimal(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    order_status: OrderStatus = "Pending"


class OrderUpdate(BaseModel):
    customer_id: int | None = Field(
        default=None,
        gt=0,
    )

    product_name: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=150,
    ) | None = None

    quantity: int | None = Field(
        default=None,
        gt=0,
    )

    unit_price: condecimal(
        gt=0,
        max_digits=12,
        decimal_places=2,
    ) | None = None

    order_status: OrderStatus | None = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    customer_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_amount: Decimal
    order_status: OrderStatus
    order_date: datetime