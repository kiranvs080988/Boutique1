"""
Work Orders API router for the Boutique Work Orders Management System.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app import crud, schemas, models

router = APIRouter(
    prefix="/work-orders",
    tags=["work-orders"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.WorkOrder, summary="Create Work Order")
async def create_work_order(
    work_order: schemas.WorkOrderCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new work order with client and billing information.
    
    **Purpose**: Creates a new work order for a client (existing or new)
    
    **Input**: 
    - Client details (if new client) or client_id (if existing)
    - Expected delivery date and time
    - Order description and notes
    - Billing information (advance, estimate, actual amount)
    - Status (defaults to "Order Placed")
    
    **Output**: Created work order with assigned ID and client information
    """
    try:
        return crud.create_work_order(db=db, work_order=work_order)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.WorkOrder], summary="List All Work Orders")
async def read_work_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all work orders with pagination.
    
    **Purpose**: Get a paginated list of all work orders
    
    **Input**: Optional skip and limit parameters for pagination
    
    **Output**: List of work orders with client information
    """
    work_orders = crud.get_work_orders(db, skip=skip, limit=limit)
    return work_orders

@router.get("/{order_id}", response_model=schemas.WorkOrder, summary="Get Work Order by ID")
async def read_work_order(order_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific work order by its ID.
    
    **Purpose**: Get detailed information about a specific work order
    
    **Input**: Work order ID
    
    **Output**: Complete work order details with client information
    """
    db_work_order = crud.get_work_order(db, order_id=order_id)
    if db_work_order is None:
        raise HTTPException(status_code=404, detail="Work order not found")
    return db_work_order

@router.put("/{order_id}", response_model=schemas.WorkOrder, summary="Update Work Order")
async def update_work_order(
    order_id: int,
    work_order_update: schemas.WorkOrderUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing work order.
    
    **Purpose**: Modify work order details, status, or billing information
    
    **Input**: 
    - Work order ID
    - Updated fields (delivery date, status, billing info, etc.)
    
    **Output**: Updated work order with new information
    """
    db_work_order = crud.update_work_order(db, order_id=order_id, work_order_update=work_order_update)
    if db_work_order is None:
        raise HTTPException(status_code=404, detail="Work order not found")
    return db_work_order

@router.delete("/{order_id}", response_model=schemas.MessageResponse, summary="Delete Work Order")
async def delete_work_order(order_id: int, db: Session = Depends(get_db)):
    """
    Delete a work order.
    
    **Purpose**: Remove a work order from the system
    
    **Input**: Work order ID
    
    **Output**: Success/failure message
    """
    success = crud.delete_work_order(db, order_id=order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Work order not found")
    return schemas.MessageResponse(message=f"Work order {order_id} deleted successfully")

@router.get("/priority/list", response_model=schemas.PriorityOrderResponse, summary="Get Priority List")
async def get_priority_work_orders(
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: 'asc' or 'desc'"),
    db: Session = Depends(get_db)
):
    """
    Get work orders sorted by expected delivery date for priority management.
    
    **Purpose**: Retrieve work orders prioritized by delivery date to help manage urgent orders
    
    **Input**: 
    - sort_order: "asc" for earliest first, "desc" for latest first
    
    **Output**: 
    - List of work orders sorted by expected delivery date
    - Sort order used
    - Total count of orders
    """
    work_orders = crud.get_priority_work_orders(db, sort_order=sort_order)
    return schemas.PriorityOrderResponse(
        work_orders=work_orders,
        sort_order=sort_order,
        total_count=len(work_orders)
    )

@router.get("/filter/advanced", response_model=List[schemas.WorkOrder], summary="Filter Orders")
async def filter_work_orders(
    delivery_date: Optional[datetime] = Query(None, description="Filter by specific delivery date"),
    delivery_window_start: Optional[datetime] = Query(None, description="Start of delivery window"),
    delivery_window_end: Optional[datetime] = Query(None, description="End of delivery window"),
    overdue_only: bool = Query(False, description="Show only overdue orders"),
    status: Optional[models.OrderStatus] = Query(None, description="Filter by order status"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    db: Session = Depends(get_db)
):
    """
    Filter work orders based on various criteria.
    
    **Purpose**: Advanced filtering to find specific orders based on delivery dates, status, or client
    
    **Input**: 
    - delivery_date: Specific date to filter by
    - delivery_window_start/end: Date range for delivery window
    - overdue_only: Boolean to show only overdue orders
    - status: Filter by specific order status
    - client_id: Filter by specific client
    
    **Output**: List of work orders matching the filter criteria
    """
    filters = schemas.WorkOrderFilter(
        delivery_date=delivery_date,
        delivery_window_start=delivery_window_start,
        delivery_window_end=delivery_window_end,
        overdue_only=overdue_only,
        status=status,
        client_id=client_id
    )
    return crud.get_filtered_work_orders(db, filters=filters)

@router.get("/status/overdue", response_model=List[schemas.WorkOrder], summary="Get Overdue Orders")
async def get_overdue_orders(db: Session = Depends(get_db)):
    """
    Get all overdue work orders.
    
    **Purpose**: Quickly identify orders that are past their expected delivery date
    
    **Input**: None
    
    **Output**: List of overdue work orders (past delivery date and not delivered)
    """
    return crud.get_overdue_work_orders(db)

@router.get("/status/due-today", response_model=List[schemas.WorkOrder], summary="Get Orders Due Today")
async def get_orders_due_today(db: Session = Depends(get_db)):
    """
    Get work orders due within 24 hours.
    
    **Purpose**: Identify orders that need immediate attention (due within 1 day)
    
    **Input**: None
    
    **Output**: List of work orders due within the next 24 hours
    """
    return crud.get_orders_due_in_one_day(db)

@router.get("/status/active", response_model=List[schemas.WorkOrder], summary="Get Active Orders")
async def get_active_orders(db: Session = Depends(get_db)):
    """
    Get all active (non-delivered) work orders.
    
    **Purpose**: View all orders currently in progress (not yet delivered)
    
    **Input**: None
    
    **Output**: List of active work orders (status not "Delivered")
    """
    return crud.get_active_work_orders(db)
