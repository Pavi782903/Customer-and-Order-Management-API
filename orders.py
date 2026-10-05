from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Customer, Order
from ..schemas import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def calculate_total_amount(
    quantity: int,
    unit_price: Decimal,
) -> Decimal:
    total = Decimal(quantity) * Decimal(unit_price)

    return total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


# ============================================================
# CREATE ORDER
# POST /orders
# ============================================================

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
):
    try:
        # Check whether customer exists
        customer = (
            db.query(Customer)
            .filter(Customer.customer_id == order_data.customer_id)
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Customer with ID "
                    f"{order_data.customer_id} does not exist."
                ),
            )

        # Automatically calculate total amount
        total_amount = calculate_total_amount(
            order_data.quantity,
            order_data.unit_price,
        )

        new_order = Order(
            customer_id=order_data.customer_id,
            product_name=order_data.product_name,
            quantity=order_data.quantity,
            unit_price=order_data.unit_price,
            total_amount=total_amount,
            order_status=order_data.order_status,
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return new_order

    except HTTPException:
        raise

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create order because of invalid data.",
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating order.",
        )


# ============================================================
# GET ALL ORDERS
# GET /orders
# ============================================================

@router.get(
    "",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
)
def get_orders(
    db: Session = Depends(get_db),
):
    try:
        orders = (
            db.query(Order)
            .order_by(Order.order_id)
            .all()
        )

        return orders

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching orders.",
        )


# ============================================================
# GET ORDER BY ID
# GET /orders/{order_id}
# ============================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    try:
        order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found.",
            )

        return order

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching order.",
        )


# ============================================================
# UPDATE ORDER
# PUT /orders/{order_id}
# ============================================================

@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
):
    try:
        # Find order
        order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found.",
            )

        # Update customer
        if order_data.customer_id is not None:
            customer = (
                db.query(Customer)
                .filter(
                    Customer.customer_id
                    == order_data.customer_id
                )
                .first()
            )

            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Customer with ID "
                        f"{order_data.customer_id} does not exist."
                    ),
                )

            order.customer_id = order_data.customer_id

        # Update product
        if order_data.product_name is not None:
            order.product_name = order_data.product_name

        # Update quantity
        if order_data.quantity is not None:
            order.quantity = order_data.quantity

        # Update unit price
        if order_data.unit_price is not None:
            order.unit_price = order_data.unit_price

        # Update status
        if order_data.order_status is not None:
            order.order_status = order_data.order_status

        # Always recalculate total after update
        order.total_amount = calculate_total_amount(
            order.quantity,
            order.unit_price,
        )

        db.commit()
        db.refresh(order)

        return order

    except HTTPException:
        raise

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update order because of invalid data.",
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating order.",
        )


# ============================================================
# DELETE ORDER
# DELETE /orders/{order_id}
# ============================================================

@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    try:
        order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found.",
            )

        db.delete(order)
        db.commit()

        return None

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting order.",
        )