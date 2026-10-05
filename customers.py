from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Customer
from ..schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


# ============================================================
# CREATE CUSTOMER
# POST /customers
# ============================================================

@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        # Check duplicate email
        existing_customer = (
            db.query(Customer)
            .filter(Customer.email == customer_data.email)
            .first()
        )

        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Customer email already exists.",
            )

        new_customer = Customer(
            customer_name=customer_data.customer_name,
            email=customer_data.email,
            phone_number=customer_data.phone_number,
            address=customer_data.address,
            city=customer_data.city,
        )

        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        return new_customer

    except HTTPException:
        raise

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer email already exists.",
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating customer.",
        )


# ============================================================
# GET ALL CUSTOMERS
# GET /customers
# ============================================================

@router.get(
    "",
    response_model=list[CustomerResponse],
    status_code=status.HTTP_200_OK,
)
def get_customers(
    db: Session = Depends(get_db),
):
    try:
        customers = (
            db.query(Customer)
            .order_by(Customer.customer_id)
            .all()
        )

        return customers

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching customers.",
        )


# ============================================================
# GET CUSTOMER BY ID
# GET /customers/{customer_id}
# ============================================================

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        customer = (
            db.query(Customer)
            .filter(Customer.customer_id == customer_id)
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )

        return customer

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching customer.",
        )


# ============================================================
# UPDATE CUSTOMER
# PUT /customers/{customer_id}
# ============================================================

@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
):
    try:
        customer = (
            db.query(Customer)
            .filter(Customer.customer_id == customer_id)
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )

        # Check duplicate email if email is being changed
        if customer_data.email is not None:
            existing_customer = (
                db.query(Customer)
                .filter(
                    Customer.email == customer_data.email,
                    Customer.customer_id != customer_id,
                )
                .first()
            )

            if existing_customer:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another customer already uses this email.",
                )

            customer.email = customer_data.email

        if customer_data.customer_name is not None:
            customer.customer_name = customer_data.customer_name

        if customer_data.phone_number is not None:
            customer.phone_number = customer_data.phone_number

        if customer_data.address is not None:
            customer.address = customer_data.address

        if customer_data.city is not None:
            customer.city = customer_data.city

        db.commit()
        db.refresh(customer)

        return customer

    except HTTPException:
        raise

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer email already exists.",
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating customer.",
        )


# ============================================================
# DELETE CUSTOMER
# DELETE /customers/{customer_id}
# ============================================================

@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        customer = (
            db.query(Customer)
            .filter(Customer.customer_id == customer_id)
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found.",
            )

        db.delete(customer)
        db.commit()

        return None

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting customer.",
        )