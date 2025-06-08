from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import func

# Create a base class for our models
Base = declarative_base()


# Define a mixin for audit columns
class AuditMixin:
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        onupdate=func.now(),
    )
    created_by = Column(String, nullable=False, default="app_service")
    updated_by = Column(String, nullable=False, default="app_service")


# Define an enum for order status
class OrderStatus(PyEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    PICKED_UP = "PICKED_UP"
    CANCELLED = "CANCELLED"


# Define an enum for order status
class PaymentMethod(PyEnum):
    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"
    OTHERS = "OTHERS"


# Model for storing menu items
class MenuItem(Base, AuditMixin):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)

    def __repr__(self):
        return f"MenuItem(name={self.name}, price={self.price}, active={self.active})"


# Model for managing customer related information
class Customer(Base, AuditMixin):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)

    orders = relationship("Order", backref="customer")

    def __repr__(self):
        return f"Customer(name={self.name}, phone_number={self.phone_number})"


# Model to manage the orders of various customers
class Order(Base, AuditMixin):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)

    order_items = relationship("OrderItem", backref="order")

    def __repr__(self):
        return f"Order(customer_id={self.customer_id}, total_cost={self.total_cost}, status={self.status})"


# Model to manage the order items
class OrderItem(Base, AuditMixin):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    menu_item = relationship("MenuItem", backref="order_items")

    def __repr__(self):
        return f"OrderItem(order_id={self.order_id}, menu_item_id={self.menu_item_id}, quantity={self.quantity})"


# Model to manage the payment transactions
class PaymentTransaction(Base, AuditMixin):
    __tablename__ = "payment_transactions"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    amount = Column(Float, nullable=False)
    payment_method = Column(
        Enum(PaymentMethod), default=PaymentMethod.CASH, nullable=False
    )
    paid = Column(Boolean, default=False, nullable=False)

    order = relationship("Order", backref="payment_transactions")

    def __repr__(self):
        return f"PaymentTransaction(order_id={self.order_id}, amount={self.amount}, payment_method={self.payment_method})"


# # Create an engine to connect to the database
# engine = create_engine('postgresql://user:password@host:port/dbname')

# # Create a session maker
# Session = sessionmaker(bind=engine)

# # Create the tables in the database
# Base.metadata.create_all(engine)
