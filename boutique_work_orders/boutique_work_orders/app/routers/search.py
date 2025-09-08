"""
Search and lookup endpoints for finding work orders without knowing IDs.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List, Optional
from app.database import get_db
from app import models, schemas, crud

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/work-orders")
def search_work_orders(
    query: str = Query(..., description="Search term (client name, mobile, description, or notes)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Search for work orders by client name, mobile number, description, or notes.
    
    **Perfect for frontend search functionality when clients don't remember IDs.**
    
    **Parameters:**
    - query: Search term to look for in client name, mobile, description, or notes
    - status: Optional status filter
    - limit: Maximum number of results (default: 20)
    
    **Returns:**
    - List of matching work orders with complete client information
    - Each result includes work order ID for easy selection and editing
    
    **Example Usage:**
    - Search by client name: "Priya"
    - Search by mobile: "9876543210" 
    - Search by description: "saree"
    - Search by notes: "urgent"
    """
    
    # Build the search query
    search_term = f"%{query.lower()}%"
    
    # Join with client table and search across multiple fields
    query_builder = db.query(models.WorkOrder).options(joinedload(models.WorkOrder.client)).join(models.Client)
    
    # Search in multiple fields
    search_conditions = or_(
        func.lower(models.Client.name).like(search_term),
        func.lower(models.Client.mobile_number).like(search_term),
        func.lower(models.WorkOrder.description).like(search_term),
        func.lower(models.WorkOrder.notes).like(search_term)
    )
    
    query_builder = query_builder.filter(search_conditions)
    
    # Apply status filter if provided
    if status:
        query_builder = query_builder.filter(models.WorkOrder.status == status)
    
    # Order by most recent first
    query_builder = query_builder.order_by(models.WorkOrder.created_at.desc())
    
    # Apply limit
    results = query_builder.limit(limit).all()
    
    # Format results for easy frontend consumption
    formatted_results = []
    for work_order in results:
        formatted_results.append({
            "work_order_id": work_order.id,
            "client_id": work_order.client_id,
            "client_name": work_order.client.name,
            "client_mobile": work_order.client.mobile_number,
            "description": work_order.description,
            "notes": work_order.notes,
            "status": work_order.status.value,
            "expected_delivery_date": work_order.expected_delivery_date,
            "order_date": work_order.order_date,
            "advance_paid": work_order.advance_paid,
            "total_estimate": work_order.total_estimate,
            "actual_amount": work_order.actual_amount,
            "due_cleared": work_order.due_cleared,
            "remaining_amount": work_order.remaining_amount,
            "is_overdue": work_order.is_overdue,
            "is_active": work_order.is_active,
            # Add display-friendly summary for easy selection
            "display_summary": f"{work_order.client.name} - {work_order.description[:50]}{'...' if len(work_order.description) > 50 else ''} ({work_order.status.value})",
            "search_match_reason": "Multiple field match"  # Could be enhanced to show which field matched
        })
    
    return {
        "query": query,
        "total_results": len(formatted_results),
        "results": formatted_results
    }

@router.get("/clients")
def search_clients(
    query: str = Query(..., description="Search term (name, mobile, email, or address)"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Search for clients by name, mobile number, email, or address.
    
    **Parameters:**
    - query: Search term to look for in client fields
    - limit: Maximum number of results (default: 20)
    
    **Returns:**
    - List of matching clients with their work order counts
    """
    
    search_term = f"%{query.lower()}%"
    
    # Search across client fields
    search_conditions = or_(
        func.lower(models.Client.name).like(search_term),
        func.lower(models.Client.mobile_number).like(search_term),
        func.lower(models.Client.email).like(search_term),
        func.lower(models.Client.address).like(search_term)
    )
    
    clients = db.query(models.Client).filter(search_conditions).limit(limit).all()
    
    # Add work order counts for each client
    results = []
    for client in clients:
        work_order_count = db.query(models.WorkOrder).filter(models.WorkOrder.client_id == client.id).count()
        active_orders = db.query(models.WorkOrder).filter(
            and_(
                models.WorkOrder.client_id == client.id,
                models.WorkOrder.status.notin_([
                    models.OrderStatus.DELIVERED_FULLY_PAID,
                    models.OrderStatus.DELIVERED_PAYMENT_PENDING
                ])
            )
        ).count()
        
        results.append({
            "client_id": client.id,
            "name": client.name,
            "mobile_number": client.mobile_number,
            "email": client.email,
            "address": client.address,
            "total_orders": work_order_count,
            "active_orders": active_orders,
            "display_summary": f"{client.name} ({client.mobile_number}) - {work_order_count} orders"
        })
    
    return {
        "query": query,
        "total_results": len(results),
        "results": results
    }

@router.get("/quick-lookup")
def quick_lookup(
    mobile: Optional[str] = Query(None, description="Mobile number"),
    name: Optional[str] = Query(None, description="Client name (partial match)"),
    db: Session = Depends(get_db)
):
    """
    Quick lookup for work orders by mobile number or client name.
    
    **Perfect for quick searches when client calls or visits.**
    
    **Parameters:**
    - mobile: Client mobile number (exact or partial match)
    - name: Client name (partial match)
    
    **Returns:**
    - All work orders for matching clients
    - Organized by client with work order details
    """
    
    if not mobile and not name:
        return {"error": "Please provide either mobile number or client name"}
    
    # Build client search conditions
    conditions = []
    if mobile:
        conditions.append(func.lower(models.Client.mobile_number).like(f"%{mobile.lower()}%"))
    if name:
        conditions.append(func.lower(models.Client.name).like(f"%{name.lower()}%"))
    
    # Find matching clients
    clients = db.query(models.Client).filter(or_(*conditions)).all()
    
    if not clients:
        return {
            "message": "No clients found matching the search criteria",
            "results": []
        }
    
    # Get work orders for each client
    results = []
    for client in clients:
        work_orders = db.query(models.WorkOrder).options(joinedload(models.WorkOrder.client)).filter(
            models.WorkOrder.client_id == client.id
        ).order_by(models.WorkOrder.created_at.desc()).all()
        
        client_result = {
            "client": {
                "client_id": client.id,
                "name": client.name,
                "mobile_number": client.mobile_number,
                "email": client.email,
                "address": client.address
            },
            "work_orders": []
        }
        
        for wo in work_orders:
            client_result["work_orders"].append({
                "work_order_id": wo.id,
                "description": wo.description,
                "status": wo.status.value,
                "expected_delivery_date": wo.expected_delivery_date,
                "order_date": wo.order_date,
                "advance_paid": wo.advance_paid,
                "total_estimate": wo.total_estimate,
                "actual_amount": wo.actual_amount,
                "remaining_amount": wo.remaining_amount,
                "is_overdue": wo.is_overdue,
                "is_active": wo.is_active,
                "display_summary": f"#{wo.id} - {wo.description[:40]}{'...' if len(wo.description) > 40 else ''} ({wo.status.value})"
            })
        
        results.append(client_result)
    
    return {
        "search_criteria": {"mobile": mobile, "name": name},
        "total_clients": len(results),
        "results": results
    }

@router.put("/work-orders/{work_order_id}/status")
def update_work_order_status(
    work_order_id: int,
    new_status: str = Query(..., description="New status value"),
    db: Session = Depends(get_db)
):
    """
    Update work order status after finding it through search.
    
    **Perfect for updating status after selecting from search results.**
    
    **Parameters:**
    - work_order_id: Work order ID (from search results)
    - new_status: New status value
    
    **Returns:**
    - Updated work order with new status
    """
    
    # Validate status
    valid_statuses = [status.value for status in models.OrderStatus]
    if new_status not in valid_statuses:
        return {
            "error": f"Invalid status. Valid options: {valid_statuses}"
        }
    
    # Get work order
    work_order = crud.get_work_order(db, work_order_id)
    if not work_order:
        return {"error": f"Work order {work_order_id} not found"}
    
    # Update status
    old_status = work_order.status.value
    update_data = schemas.WorkOrderUpdate(status=new_status)
    updated_order = crud.update_work_order(db, work_order_id, update_data)
    
    return {
        "message": f"Status updated from '{old_status}' to '{new_status}'",
        "work_order_id": work_order_id,
        "old_status": old_status,
        "new_status": new_status,
        "updated_order": {
            "work_order_id": updated_order.id,
            "client_name": updated_order.client.name,
            "description": updated_order.description,
            "status": updated_order.status.value,
            "remaining_amount": updated_order.remaining_amount,
            "is_overdue": updated_order.is_overdue
        }
    }

@router.get("/recent-orders")
def get_recent_orders(
    days: int = Query(7, description="Number of days to look back"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Get recent work orders for quick access.
    
    **Parameters:**
    - days: Number of days to look back (default: 7)
    - limit: Maximum number of results (default: 50)
    
    **Returns:**
    - Recent work orders with client information
    """
    
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_orders = db.query(models.WorkOrder).options(joinedload(models.WorkOrder.client)).filter(
        models.WorkOrder.created_at >= cutoff_date
    ).order_by(models.WorkOrder.created_at.desc()).limit(limit).all()
    
    results = []
    for wo in recent_orders:
        results.append({
            "work_order_id": wo.id,
            "client_name": wo.client.name,
            "client_mobile": wo.client.mobile_number,
            "description": wo.description,
            "status": wo.status.value,
            "order_date": wo.order_date,
            "expected_delivery_date": wo.expected_delivery_date,
            "is_overdue": wo.is_overdue,
            "is_active": wo.is_active,
            "display_summary": f"#{wo.id} - {wo.client.name} - {wo.description[:30]}{'...' if len(wo.description) > 30 else ''}"
        })
    
    return {
        "days_back": days,
        "total_results": len(results),
        "results": results
    }

@router.get("/mobile/{mobile_number}/work-orders")
def search_by_mobile_table_format(
    mobile_number: str,
    db: Session = Depends(get_db)
):
    """
    Search work orders by mobile number and return in table-friendly format.
    
    **Enhanced for complete frontend integration:**
    - Shows existing work orders with edit options
    - Provides "Add New Work Order" option for existing clients
    - Provides "Create New Client" option if mobile not found
    
    **Parameters:**
    - mobile_number: Client mobile number (exact or partial match)
    
    **Returns:**
    - Table-ready work orders data with edit capabilities
    - Frontend action options (add work order, create client)
    """
    
    # Find client by mobile number (exact or partial match)
    client = db.query(models.Client).filter(
        func.lower(models.Client.mobile_number).like(f"%{mobile_number.lower()}%")
    ).first()
    
    if not client:
        # No client found - provide create new client option
        return {
            "mobile_number": mobile_number,
            "client_found": False,
            "message": f"No client found with mobile number: {mobile_number}",
            "table_data": [],
            "frontend_actions": {
                "can_create_client": True,
                "can_add_work_order": False,
                "create_client_url": "/clients/",
                "create_client_data": {
                    "mobile_number": mobile_number,
                    "name": "",
                    "email": "",
                    "address": ""
                }
            },
            "suggested_workflow": [
                "1. Create new client profile with this mobile number",
                "2. Add work order details",
                "3. Set delivery date and billing information"
            ]
        }
    
    # Get all work orders for this client
    work_orders = db.query(models.WorkOrder).options(joinedload(models.WorkOrder.client)).filter(
        models.WorkOrder.client_id == client.id
    ).order_by(models.WorkOrder.created_at.desc()).all()
    
    # Format for table display
    table_data = []
    for wo in work_orders:
        # Create description preview (first 40 characters)
        description_preview = wo.description[:40] + "..." if len(wo.description) > 40 else wo.description
        
        # Format delivery date for display
        delivery_date_str = wo.expected_delivery_date.strftime("%Y-%m-%d") if wo.expected_delivery_date else "Not set"
        delivery_time_str = wo.expected_delivery_date.strftime("%H:%M") if wo.expected_delivery_date else ""
        
        # Determine status color/priority for frontend
        status_priority = {
            "Order Placed": "info",
            "Started": "warning", 
            "Finished": "success",
            "Delivered - Fully Paid": "success",
            "Delivered – Payment Pending": "warning"
        }.get(wo.status.value, "secondary")
        
        table_row = {
            "work_order_id": wo.id,
            "description_preview": description_preview,
            "full_description": wo.description,
            "expected_delivery_date": delivery_date_str,
            "expected_delivery_time": delivery_time_str,
            "status": wo.status.value,
            "status_priority": status_priority,
            "order_date": wo.order_date.strftime("%Y-%m-%d") if wo.order_date else "",
            "advance_paid": wo.advance_paid,
            "total_estimate": wo.total_estimate,
            "actual_amount": wo.actual_amount,
            "remaining_amount": wo.remaining_amount,
            "due_cleared": wo.due_cleared,
            "is_overdue": wo.is_overdue,
            "is_active": wo.is_active,
            "notes": wo.notes or "",
            # Edit capabilities
            "edit_url": f"/search/mobile/{mobile_number}/work-orders/{wo.id}",
            "status_update_url": f"/search/work-orders/{wo.id}/status",
            "can_edit": True,
            "can_update_status": wo.is_active,
            # Display formatting
            "table_display": {
                "id_display": f"#{wo.id}",
                "description_display": description_preview,
                "delivery_display": f"{delivery_date_str} {delivery_time_str}".strip(),
                "status_display": wo.status.value,
                "amount_display": f"₹{wo.remaining_amount}" if wo.remaining_amount > 0 else "Paid",
                "overdue_indicator": "🔴" if wo.is_overdue else "🟢"
            }
        }
        
        table_data.append(table_row)
    
    return {
        "mobile_number": mobile_number,
        "client_found": True,
        "client_info": {
            "client_id": client.id,
            "name": client.name,
            "mobile_number": client.mobile_number,
            "email": client.email,
            "address": client.address
        },
        "total_work_orders": len(table_data),
        "active_orders": len([wo for wo in table_data if wo["is_active"]]),
        "overdue_orders": len([wo for wo in table_data if wo["is_overdue"]]),
        "table_data": table_data,
        "table_headers": [
            {"key": "work_order_id", "label": "ID", "sortable": True},
            {"key": "description_preview", "label": "Description", "sortable": False},
            {"key": "expected_delivery_date", "label": "Expected Delivery", "sortable": True},
            {"key": "status", "label": "Status", "sortable": True},
            {"key": "remaining_amount", "label": "Amount Due", "sortable": True},
            {"key": "actions", "label": "Actions", "sortable": False}
        ],
        "frontend_actions": {
            "can_create_client": False,
            "can_add_work_order": True,
            "add_work_order_url": f"/search/mobile/{mobile_number}/work-orders/new",
            "add_work_order_data": {
                "client_id": client.id,
                "mobile_number": client.mobile_number,
                "client_name": client.name
            }
        }
    }

@router.post("/mobile/{mobile_number}/work-orders/new")
def create_work_order_for_mobile(
    mobile_number: str,
    work_order: schemas.WorkOrderCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new work order for an existing client found by mobile number.
    
    **Perfect for adding new work orders to existing clients.**
    
    **Parameters:**
    - mobile_number: Client mobile number
    - work_order: Work order creation data
    
    **Returns:**
    - Created work order with client information
    """
    
    # Find client by mobile number
    client = db.query(models.Client).filter(
        func.lower(models.Client.mobile_number).like(f"%{mobile_number.lower()}%")
    ).first()
    
    if not client:
        return {
            "success": False,
            "error": f"No client found with mobile number: {mobile_number}",
            "suggestion": "Create client first, then add work order"
        }
    
    # Ensure client_id matches the found client
    work_order.client_id = client.id
    
    # Create the work order
    created_order = crud.create_work_order(db, work_order)
    
    if created_order:
        return {
            "success": True,
            "message": f"Work order created successfully for {client.name}",
            "work_order": {
                "work_order_id": created_order.id,
                "client_name": client.name,
                "mobile_number": client.mobile_number,
                "description": created_order.description,
                "status": created_order.status.value,
                "expected_delivery_date": created_order.expected_delivery_date,
                "advance_paid": created_order.advance_paid,
                "total_estimate": created_order.total_estimate
            },
            "next_actions": [
                f"View all orders: /search/mobile/{mobile_number}/work-orders",
                f"Edit this order: /search/mobile/{mobile_number}/work-orders/{created_order.id}"
            ]
        }
    else:
        return {
            "success": False,
            "error": "Failed to create work order"
        }

@router.put("/mobile/{mobile_number}/work-orders/{work_order_id}")
def update_work_order_by_mobile(
    mobile_number: str,
    work_order_id: int,
    work_order_update: schemas.WorkOrderUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific work order found via mobile number search.
    
    **Perfect for editing work orders after mobile search.**
    
    **Parameters:**
    - mobile_number: Client mobile number (for verification)
    - work_order_id: Work order ID to update
    - work_order_update: Updated work order data
    
    **Returns:**
    - Updated work order information
    - Success/error status
    
    **Security:**
    - Verifies that the work order belongs to the client with given mobile number
    """
    
    # Find client by mobile number
    client = db.query(models.Client).filter(
        func.lower(models.Client.mobile_number).like(f"%{mobile_number.lower()}%")
    ).first()
    
    if not client:
        return {
            "success": False,
            "error": f"No client found with mobile number: {mobile_number}",
            "work_order_id": work_order_id
        }
    
    # Get work order and verify it belongs to this client
    work_order = crud.get_work_order(db, work_order_id)
    if not work_order:
        return {
            "success": False,
            "error": f"Work order {work_order_id} not found",
            "work_order_id": work_order_id
        }
    
    if work_order.client_id != client.id:
        return {
            "success": False,
            "error": f"Work order {work_order_id} does not belong to client with mobile {mobile_number}",
            "work_order_id": work_order_id
        }
    
    # Update the work order
    updated_order = crud.update_work_order(db, work_order_id, work_order_update)
    
    if updated_order:
        return {
            "success": True,
            "message": f"Work order {work_order_id} updated successfully",
            "work_order_id": work_order_id,
            "updated_fields": work_order_update.dict(exclude_unset=True),
            "updated_order": {
                "work_order_id": updated_order.id,
                "client_name": updated_order.client.name,
                "description": updated_order.description,
                "status": updated_order.status.value,
                "expected_delivery_date": updated_order.expected_delivery_date,
                "remaining_amount": updated_order.remaining_amount,
                "is_overdue": updated_order.is_overdue,
                "is_active": updated_order.is_active
            }
        }
    else:
        return {
            "success": False,
            "error": f"Failed to update work order {work_order_id}",
            "work_order_id": work_order_id
        }

@router.get("/mobile/{mobile_number}/work-orders/{work_order_id}")
def get_work_order_by_mobile(
    mobile_number: str,
    work_order_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed work order information for editing via mobile number search.
    
    **Perfect for populating edit forms after mobile search.**
    
    **Parameters:**
    - mobile_number: Client mobile number (for verification)
    - work_order_id: Work order ID to retrieve
    
    **Returns:**
    - Complete work order details for editing
    - Client information
    - Available status options
    """
    
    # Find client by mobile number
    client = db.query(models.Client).filter(
        func.lower(models.Client.mobile_number).like(f"%{mobile_number.lower()}%")
    ).first()
    
    if not client:
        return {
            "success": False,
            "error": f"No client found with mobile number: {mobile_number}"
        }
    
    # Get work order and verify it belongs to this client
    work_order = crud.get_work_order(db, work_order_id)
    if not work_order:
        return {
            "success": False,
            "error": f"Work order {work_order_id} not found"
        }
    
    if work_order.client_id != client.id:
        return {
            "success": False,
            "error": f"Work order {work_order_id} does not belong to client with mobile {mobile_number}"
        }
    
    # Get available status options for dropdown
    from app.routers.status import get_next_status_options
    next_status_options = get_next_status_options(work_order.status.value)
    
    return {
        "success": True,
        "client_info": {
            "client_id": client.id,
            "name": client.name,
            "mobile_number": client.mobile_number,
            "email": client.email,
            "address": client.address
        },
        "work_order": {
            "work_order_id": work_order.id,
            "description": work_order.description,
            "notes": work_order.notes,
            "status": work_order.status.value,
            "order_date": work_order.order_date,
            "expected_delivery_date": work_order.expected_delivery_date,
            "advance_paid": work_order.advance_paid,
            "total_estimate": work_order.total_estimate,
            "actual_amount": work_order.actual_amount,
            "due_cleared": work_order.due_cleared,
            "remaining_amount": work_order.remaining_amount,
            "is_overdue": work_order.is_overdue,
            "is_active": work_order.is_active
        },
        "status_options": {
            "current_status": work_order.status.value,
            "next_options": next_status_options,
            "all_options": [
                {"value": "Order Placed", "label": "Order Placed"},
                {"value": "Started", "label": "Started"},
                {"value": "Finished", "label": "Finished"},
                {"value": "Delivered - Fully Paid", "label": "Delivered - Fully Paid"},
                {"value": "Delivered – Payment Pending", "label": "Delivered – Payment Pending"}
            ]
        },
        "edit_capabilities": {
            "can_edit_description": True,
            "can_edit_notes": True,
            "can_edit_delivery_date": work_order.is_active,
            "can_edit_amounts": True,
            "can_update_status": work_order.is_active,
            "can_mark_due_cleared": not work_order.due_cleared
        }
    }
