"""
CRUD (Create, Read, Update, Delete) operations for the Boutique Work Orders system.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional
from app import models, schemas

# Client CRUD operations
def get_client(db: Session, client_id: int) -> Optional[models.Client]:
    """Get a client by ID"""
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_client_by_mobile(db: Session, mobile_number: str) -> Optional[models.Client]:
    """Get a client by mobile number"""
    return db.query(models.Client).filter(models.Client.mobile_number == mobile_number).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[models.Client]:
    """Get all clients with pagination"""
    return db.query(models.Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: schemas.ClientCreate) -> models.Client:
    """Create a new client"""
    db_client = models.Client(
        name=client.name,
        mobile_number=client.mobile_number,
        email=client.email,
        address=client.address
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: int, client_update: schemas.ClientUpdate) -> Optional[models.Client]:
    """Update an existing client"""
    db_client = get_client(db, client_id)
    if db_client:
        update_data = client_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_client, field, value)
        db.commit()
        db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: int) -> bool:
    """Delete a client"""
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
        return True
    return False

# Work Order CRUD operations
def get_work_order(db: Session, order_id: int) -> Optional[models.WorkOrder]:
    """Get a work order by ID"""
    return db.query(models.WorkOrder).options(joinedload(models.WorkOrder.client)).filter(models.WorkOrder.id == order_id).first()

def get_work_orders(db: Session, skip: int = 0, limit: int = 100) -> List[models.WorkOrder]:
    """Get all work orders with pagination"""
    return db.query(models.WorkOrder).options(joinedload(models.WorkOrder.client)).offset(skip).limit(limit).all()

def create_work_order(db: Session, work_order: schemas.WorkOrderCreate) -> models.WorkOrder:
    """Create a new work order"""
    # Handle client creation or retrieval
    if work_order.client_id:
        # Check if the provided client_id exists
        existing_client = get_client(db, work_order.client_id)
        if existing_client:
            client_id = work_order.client_id
        else:
            # Client ID doesn't exist, create new client with provided details
            if work_order.client_name and work_order.client_mobile:
                client_data = schemas.ClientCreate(
                    name=work_order.client_name,
                    mobile_number=work_order.client_mobile,
                    email=work_order.client_email,
                    address=work_order.client_address
                )
                # Check if client with this mobile already exists
                existing_mobile_client = get_client_by_mobile(db, work_order.client_mobile)
                if existing_mobile_client:
                    client_id = existing_mobile_client.id
                else:
                    new_client = create_client(db, client_data)
                    client_id = new_client.id
            else:
                raise ValueError(f"Client ID {work_order.client_id} does not exist and insufficient client details provided")
    else:
        # Create new client
        client_data = schemas.ClientCreate(
            name=work_order.client_name,
            mobile_number=work_order.client_mobile,
            email=work_order.client_email,
            address=work_order.client_address
        )
        # Check if client with this mobile already exists
        existing_client = get_client_by_mobile(db, work_order.client_mobile)
        if existing_client:
            client_id = existing_client.id
        else:
            new_client = create_client(db, client_data)
            client_id = new_client.id

    # Create work order
    db_work_order = models.WorkOrder(
        client_id=client_id,
        expected_delivery_date=work_order.expected_delivery_date,
        description=work_order.description,
        notes=work_order.notes,
        status=work_order.status,
        advance_paid=work_order.advance_paid,
        total_estimate=work_order.total_estimate,
        actual_amount=work_order.actual_amount,
        due_cleared=work_order.due_cleared
    )
    db.add(db_work_order)
    db.commit()
    db.refresh(db_work_order)
    # Return the work order with client relationship loaded
    return get_work_order(db, db_work_order.id)

def update_work_order(db: Session, order_id: int, work_order_update: schemas.WorkOrderUpdate) -> Optional[models.WorkOrder]:
    """Update an existing work order"""
    db_work_order = get_work_order(db, order_id)
    if db_work_order:
        update_data = work_order_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_work_order, field, value)
        db.commit()
        db.refresh(db_work_order)
    return db_work_order

def delete_work_order(db: Session, order_id: int) -> bool:
    """Delete a work order"""
    db_work_order = get_work_order(db, order_id)
    if db_work_order:
        db.delete(db_work_order)
        db.commit()
        return True
    return False

# Advanced query operations
def get_work_orders_by_client(db: Session, client_id: int) -> List[models.WorkOrder]:
    """Get all work orders for a specific client"""
    return db.query(models.WorkOrder).filter(models.WorkOrder.client_id == client_id).all()

def get_work_orders_by_mobile(db: Session, mobile_number: str) -> List[models.WorkOrder]:
    """Get all work orders for a client by mobile number"""
    client = get_client_by_mobile(db, mobile_number)
    if client:
        return get_work_orders_by_client(db, client.id)
    return []

def get_priority_work_orders(db: Session, sort_order: str = "asc") -> List[models.WorkOrder]:
    """Get work orders sorted by expected delivery date"""
    query = db.query(models.WorkOrder).options(joinedload(models.WorkOrder.client))
    if sort_order.lower() == "desc":
        query = query.order_by(models.WorkOrder.expected_delivery_date.desc())
    else:
        query = query.order_by(models.WorkOrder.expected_delivery_date.asc())
    return query.all()

def get_filtered_work_orders(db: Session, filters: schemas.WorkOrderFilter) -> List[models.WorkOrder]:
    """Get work orders based on various filters"""
    query = db.query(models.WorkOrder)
    
    # Filter by specific delivery date
    if filters.delivery_date:
        start_of_day = filters.delivery_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        query = query.filter(
            and_(
                models.WorkOrder.expected_delivery_date >= start_of_day,
                models.WorkOrder.expected_delivery_date < end_of_day
            )
        )
    
    # Filter by delivery window
    if filters.delivery_window_start:
        query = query.filter(models.WorkOrder.expected_delivery_date >= filters.delivery_window_start)
    
    if filters.delivery_window_end:
        query = query.filter(models.WorkOrder.expected_delivery_date <= filters.delivery_window_end)
    
    # Filter by status
    if filters.status:
        query = query.filter(models.WorkOrder.status == filters.status)
    
    # Filter by client
    if filters.client_id:
        query = query.filter(models.WorkOrder.client_id == filters.client_id)
    
    # Filter overdue orders
    if filters.overdue_only:
        now = datetime.now()
        query = query.filter(
            and_(
                models.WorkOrder.expected_delivery_date < now,
                models.WorkOrder.status.notin_([
                    models.OrderStatus.DELIVERED_FULLY_PAID,
                    models.OrderStatus.DELIVERED_PAYMENT_PENDING
                ])
            )
        )
    
    return query.all()

def get_overdue_work_orders(db: Session) -> List[models.WorkOrder]:
    """Get all overdue work orders"""
    now = datetime.now()
    return db.query(models.WorkOrder).options(joinedload(models.WorkOrder.client)).filter(
        and_(
            models.WorkOrder.expected_delivery_date < now,
            models.WorkOrder.status.notin_([
                models.OrderStatus.DELIVERED_FULLY_PAID,
                models.OrderStatus.DELIVERED_PAYMENT_PENDING
            ])
        )
    ).all()

def get_orders_due_in_one_day(db: Session) -> List[models.WorkOrder]:
    """Get orders due within 24 hours"""
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    return db.query(models.WorkOrder).filter(
        and_(
            models.WorkOrder.expected_delivery_date >= now,
            models.WorkOrder.expected_delivery_date <= tomorrow,
            models.WorkOrder.status.notin_([
                models.OrderStatus.DELIVERED_FULLY_PAID,
                models.OrderStatus.DELIVERED_PAYMENT_PENDING
            ])
        )
    ).all()

def get_active_work_orders(db: Session) -> List[models.WorkOrder]:
    """Get all active (non-delivered) work orders"""
    return db.query(models.WorkOrder).filter(
        models.WorkOrder.status.notin_([
            models.OrderStatus.DELIVERED_FULLY_PAID,
            models.OrderStatus.DELIVERED_PAYMENT_PENDING
        ])
    ).all()

# Dashboard statistics
def get_dashboard_stats(db: Session) -> dict:
    """Get comprehensive dashboard statistics"""
    total_orders = db.query(models.WorkOrder).count()
    
    active_orders = db.query(models.WorkOrder).filter(
        models.WorkOrder.status.notin_([
            models.OrderStatus.DELIVERED_FULLY_PAID,
            models.OrderStatus.DELIVERED_PAYMENT_PENDING
        ])
    ).count()
    
    overdue_orders = len(get_overdue_work_orders(db))
    orders_due_today = len(get_orders_due_in_one_day(db))
    
    completed_orders = db.query(models.WorkOrder).filter(
        models.WorkOrder.status.in_([
            models.OrderStatus.DELIVERED_FULLY_PAID,
            models.OrderStatus.DELIVERED_PAYMENT_PENDING
        ])
    ).count()
    
    # Calculate revenue and pending payments
    total_revenue = db.query(func.sum(models.WorkOrder.advance_paid)).scalar() or 0
    
    # Calculate pending payments (orders that are not fully paid)
    pending_orders = db.query(models.WorkOrder).filter(
        models.WorkOrder.due_cleared == False
    ).all()
    
    pending_payments = 0
    for order in pending_orders:
        # Use actual_amount if available, otherwise use total_estimate
        amount_due = order.actual_amount if order.actual_amount > 0 else order.total_estimate
        remaining = max(0, amount_due - order.advance_paid)
        pending_payments += remaining
    
    return {
        "total_work_orders": total_orders,
        "active_work_orders": active_orders,
        "overdue_work_orders": overdue_orders,
        "orders_due_in_one_day": orders_due_today,
        "completed_orders": completed_orders,
        "total_revenue": total_revenue,
        "pending_payments": pending_payments
    }

def get_client_summary(db: Session, client_id: int) -> Optional[dict]:
    """Get comprehensive client summary"""
    client = get_client(db, client_id)
    if not client:
        return None
    
    work_orders = get_work_orders_by_client(db, client_id)
    active_orders = [wo for wo in work_orders if wo.is_active]
    completed_orders = [wo for wo in work_orders if not wo.is_active]
    
    total_amount_due = sum(wo.remaining_amount for wo in work_orders if not wo.due_cleared)
    
    return {
        "client": client,
        "work_orders": work_orders,
        "total_orders": len(work_orders),
        "active_orders": len(active_orders),
        "completed_orders": len(completed_orders),
        "total_amount_due": total_amount_due
    }

def get_client_summary_by_mobile(db: Session, mobile_number: str) -> Optional[dict]:
    """Get comprehensive client summary by mobile number"""
    client = get_client_by_mobile(db, mobile_number)
    if not client:
        return None
    return get_client_summary(db, client.id)
