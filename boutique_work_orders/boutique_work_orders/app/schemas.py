"""
Pydantic schemas for request and response models in the Boutique Work Orders system.
"""

from pydantic import BaseModel, validator, Field, model_validator
from datetime import datetime
from typing import Optional, List
from app.models import OrderStatus

# Base schemas
class ClientBase(BaseModel):
    """Base schema for client data"""
    name: str = Field(..., min_length=1, max_length=100, description="Client's full name")
    mobile_number: str = Field(..., pattern=r'^\d{10}$', description="10-digit mobile number")
    email: Optional[str] = Field(None, description="Client's email address (optional)")
    address: Optional[str] = Field(None, max_length=500, description="Client's address")

class ClientCreate(ClientBase):
    """Schema for creating a new client"""
    pass

class ClientUpdate(BaseModel):
    """Schema for updating client information"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    mobile_number: Optional[str] = Field(None, pattern=r'^\d{10}$')
    email: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)

class Client(ClientBase):
    """Schema for client response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Work Order schemas
class WorkOrderBase(BaseModel):
    """Base schema for work order data"""
    expected_delivery_date: datetime = Field(..., description="Expected delivery date and time")
    description: Optional[str] = Field(None, max_length=1000, description="Order description")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    status: OrderStatus = Field(OrderStatus.ORDER_PLACED, description="Current order status")
    advance_paid: float = Field(0.0, ge=0, description="Advance amount paid")
    total_estimate: float = Field(0.0, ge=0, description="Total estimated cost")
    actual_amount: float = Field(0.0, ge=0, description="Actual final amount")
    due_cleared: bool = Field(False, description="Whether all dues are cleared")

class WorkOrderCreate(WorkOrderBase):
    """Schema for creating a new work order"""
    client_id: Optional[int] = Field(None, description="Existing client ID (if client exists)")
    # Client information (if creating new client)
    client_name: Optional[str] = Field(None, min_length=1, max_length=100)
    client_mobile: Optional[str] = Field(None, pattern=r'^\d{10}$')
    client_email: Optional[str] = None
    client_address: Optional[str] = Field(None, max_length=500)

    @model_validator(mode='after')
    def validate_client_info(self):
        """Ensure either client_id or client details are provided"""
        if self.client_id is None:
            # Check if client details are provided
            if not self.client_name or not self.client_mobile:
                raise ValueError('Either client_id or both client_name and client_mobile must be provided')
        return self

class WorkOrderUpdate(BaseModel):
    """Schema for updating work order information"""
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[OrderStatus] = None
    advance_paid: Optional[float] = Field(None, ge=0)
    total_estimate: Optional[float] = Field(None, ge=0)
    actual_amount: Optional[float] = Field(None, ge=0)
    due_cleared: Optional[bool] = None

class WorkOrder(WorkOrderBase):
    """Schema for work order response"""
    id: int
    client_id: int
    order_date: datetime
    actual_delivery_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed properties
    is_overdue: bool
    due_in_one_day: bool
    is_active: bool
    remaining_amount: float
    
    # Related client information
    client: Client

    class Config:
        from_attributes = True

# Client summary schemas
class ClientSummary(BaseModel):
    """Schema for client summary with work orders"""
    client: Client
    work_orders: List[WorkOrder]
    total_orders: int
    active_orders: int
    completed_orders: int
    total_amount_due: float

# Dashboard schemas
class DashboardSummary(BaseModel):
    """Schema for dashboard summary statistics"""
    total_work_orders: int
    active_work_orders: int
    overdue_work_orders: int
    orders_due_in_one_day: int
    total_revenue: float
    pending_payments: float
    completed_orders: int

# Filter schemas
class WorkOrderFilter(BaseModel):
    """Schema for filtering work orders"""
    delivery_date: Optional[datetime] = Field(None, description="Filter by specific delivery date")
    delivery_window_start: Optional[datetime] = Field(None, description="Start of delivery window")
    delivery_window_end: Optional[datetime] = Field(None, description="End of delivery window")
    overdue_only: Optional[bool] = Field(False, description="Show only overdue orders")
    status: Optional[OrderStatus] = Field(None, description="Filter by order status")
    client_id: Optional[int] = Field(None, description="Filter by client ID")

# Response schemas
class MessageResponse(BaseModel):
    """Generic message response schema"""
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    success: bool = False

# Priority list schema
class PriorityOrderResponse(BaseModel):
    """Schema for priority-sorted work orders"""
    work_orders: List[WorkOrder]
    sort_order: str
    total_count: int
