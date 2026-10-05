from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint,
)

from sqlalchemy.orm import relationship

from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    customer_name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    phone_number = Column(
        String(20),
        nullable=True,
    )

    address = Column(
        String(255),
        nullable=True,
    )

    city = Column(
        String(100),
        nullable=True,
    )

    created_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # One customer can have many orders
    orders = relationship(
        "Order",
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_name = Column(
        String(150),
        nullable=False,
    )

    quantity = Column(
        Integer,
        nullable=False,
    )

    unit_price = Column(
        Numeric(12, 2),
        nullable=False,
    )

    total_amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    order_status = Column(
        String(20),
        nullable=False,
        default="Pending",
    )

    order_date = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship with customer
    customer = relationship(
        "Customer",
        back_populates="orders",
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_quantity_positive",
        ),
        CheckConstraint(
            "unit_price > 0",
            name="check_unit_price_positive",
        ),
        CheckConstraint(
            "order_status IN ('Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled')",
            name="check_order_status",
        ),
    )