"""
SQLAlchemy database models for the Boutique Work Orders system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class OrderStatus(enum.Enum):
    """Enumeration for work order status"""
    ORDER_PLACED = "Order Placed"
    STARTED = "Started"
    FINISHED = "Finished"
    DELIVERED_FULLY_PAID = "Delivered - Fully Paid"
    DELIVERED_PAYMENT_PENDING = "Delivered – Payment Pending"

class Client(Base):
    """
    Client model to store customer information.
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    mobile_number = Column(String(10), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with work orders
    work_orders = relationship("WorkOrder", back_populates="client")

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', mobile='{self.mobile_number}')>"

class WorkOrder(Base):
    """
    Work Order model to store order details and billing information.
    """
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Client relationship
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Order details
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    expected_delivery_date = Column(DateTime(timezone=True), nullable=False)
    actual_delivery_date = Column(DateTime(timezone=True), nullable=True)
    
    # Order description and details
    description = Column(String(1000), nullable=True)
    notes = Column(String(1000), nullable=True)
    
    # Status tracking
    status = Column(Enum(OrderStatus), default=OrderStatus.ORDER_PLACED, nullable=False)
    
    # Billing information
    advance_paid = Column(Float, default=0.0, nullable=False)
    total_estimate = Column(Float, default=0.0, nullable=False)
    actual_amount = Column(Float, default=0.0, nullable=False)
    due_cleared = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with client
    client = relationship("Client", back_populates="work_orders")

    def __repr__(self):
        return f"<WorkOrder(id={self.id}, client_id={self.client_id}, status='{self.status.value}')>"

    @property
    def is_overdue(self):
        """Check if the order is overdue based on expected delivery date"""
        from datetime import datetime
        return self.expected_delivery_date < datetime.now() and self.status not in [
            OrderStatus.DELIVERED_FULLY_PAID, 
            OrderStatus.DELIVERED_PAYMENT_PENDING
        ]

    @property
    def due_in_one_day(self):
        """Check if the order is due within 24 hours"""
        from datetime import datetime, timedelta
        tomorrow = datetime.now() + timedelta(days=1)
        return (self.expected_delivery_date <= tomorrow and 
                self.expected_delivery_date >= datetime.now() and 
                self.status not in [OrderStatus.DELIVERED_FULLY_PAID, OrderStatus.DELIVERED_PAYMENT_PENDING])

    @property
    def is_active(self):
        """Check if the order is active (not delivered)"""
        return self.status not in [OrderStatus.DELIVERED_FULLY_PAID, OrderStatus.DELIVERED_PAYMENT_PENDING]

    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        if self.actual_amount > 0:
            return max(0, self.actual_amount - self.advance_paid)
        else:
            return max(0, self.total_estimate - self.advance_paid)
