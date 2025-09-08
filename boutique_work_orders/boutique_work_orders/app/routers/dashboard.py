"""
Dashboard API router for the Boutique Work Orders Management System.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)

@router.get("/summary", response_model=schemas.DashboardSummary, summary="Master Page Summary")
async def get_dashboard_summary(
    start_date: Optional[str] = Query(None, description="Start date for delivery window (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for delivery window (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics and summary.
    
    **Purpose**: Provide a master summary page with key business metrics and order statistics
    
    **Input**: None
    
    **Output**: 
    - Total work orders count
    - Active work orders (not delivered)
    - Overdue work orders (past delivery date)
    - Orders due in 1 day (urgent attention needed)
    - Total revenue (sum of advance payments)
    - Pending payments (remaining amounts due)
    - Completed orders count
    
    **Use Case**: Main dashboard view for business overview and quick decision making
    """
    stats = crud.get_dashboard_stats(db)
    return schemas.DashboardSummary(**stats)

@router.get("/metrics/revenue", summary="Revenue Metrics")
async def get_revenue_metrics(db: Session = Depends(get_db)):
    """
    Get detailed revenue and payment metrics.
    
    **Purpose**: Financial overview of the business
    
    **Input**: None
    
    **Output**: 
    - Total revenue collected
    - Pending payments
    - Average order value
    - Payment completion rate
    """
    stats = crud.get_dashboard_stats(db)
    
    # Calculate additional metrics
    total_orders = stats["total_work_orders"]
    total_revenue = stats["total_revenue"]
    pending_payments = stats["pending_payments"]
    
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    payment_completion_rate = ((total_revenue / (total_revenue + pending_payments)) * 100) if (total_revenue + pending_payments) > 0 else 0
    
    return {
        "total_revenue": total_revenue,
        "pending_payments": pending_payments,
        "average_order_value": round(avg_order_value, 2),
        "payment_completion_rate": round(payment_completion_rate, 2),
        "total_expected_revenue": total_revenue + pending_payments
    }

@router.get("/metrics/orders", summary="Order Metrics")
async def get_order_metrics(db: Session = Depends(get_db)):
    """
    Get detailed order statistics and metrics.
    
    **Purpose**: Operational overview of order management
    
    **Input**: None
    
    **Output**: 
    - Order status distribution
    - Completion rate
    - Average processing time
    - Urgency metrics
    """
    stats = crud.get_dashboard_stats(db)
    
    total_orders = stats["total_work_orders"]
    active_orders = stats["active_work_orders"]
    completed_orders = stats["completed_orders"]
    overdue_orders = stats["overdue_work_orders"]
    due_today = stats["orders_due_in_one_day"]
    
    completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    overdue_rate = (overdue_orders / total_orders * 100) if total_orders > 0 else 0
    
    return {
        "total_orders": total_orders,
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "overdue_orders": overdue_orders,
        "orders_due_today": due_today,
        "completion_rate": round(completion_rate, 2),
        "overdue_rate": round(overdue_rate, 2),
        "on_time_delivery_rate": round(100 - overdue_rate, 2)
    }

@router.get("/alerts", summary="Dashboard Alerts")
async def get_dashboard_alerts(db: Session = Depends(get_db)):
    """
    Get important alerts and notifications for the dashboard.
    
    **Purpose**: Highlight urgent items that need immediate attention
    
    **Input**: None
    
    **Output**: 
    - Critical alerts (overdue orders)
    - Warning alerts (due today)
    - Info alerts (general notifications)
    """
    overdue_orders = crud.get_overdue_work_orders(db)
    due_today_orders = crud.get_orders_due_in_one_day(db)
    
    alerts = []
    
    # Critical alerts for overdue orders
    if overdue_orders:
        alerts.append({
            "type": "critical",
            "title": f"{len(overdue_orders)} Overdue Orders",
            "message": f"You have {len(overdue_orders)} orders that are past their delivery date",
            "count": len(overdue_orders),
            "action": "Review overdue orders immediately"
        })
    
    # Warning alerts for orders due today
    if due_today_orders:
        alerts.append({
            "type": "warning",
            "title": f"{len(due_today_orders)} Orders Due Today",
            "message": f"You have {len(due_today_orders)} orders due within 24 hours",
            "count": len(due_today_orders),
            "action": "Prepare for delivery"
        })
    
    # Info alert if no urgent items
    if not overdue_orders and not due_today_orders:
        alerts.append({
            "type": "info",
            "title": "All Orders On Track",
            "message": "No overdue orders or urgent deliveries",
            "count": 0,
            "action": "Continue normal operations"
        })
    
    return {
        "alerts": alerts,
        "total_alerts": len([a for a in alerts if a["type"] in ["critical", "warning"]]),
        "critical_count": len([a for a in alerts if a["type"] == "critical"]),
        "warning_count": len([a for a in alerts if a["type"] == "warning"])
    }

@router.get("/recent-activity", summary="Recent Activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """
    Get recent activity and updates.
    
    **Purpose**: Show latest changes and activities in the system
    
    **Input**: None
    
    **Output**: Recent work orders and client activities
    """
    # Get recent work orders (last 10)
    recent_orders = crud.get_work_orders(db, skip=0, limit=10)
    
    # Get recent clients (last 5)
    recent_clients = crud.get_clients(db, skip=0, limit=5)
    
    return {
        "recent_orders": [
            {
                "id": order.id,
                "client_name": order.client.name,
                "status": order.status.value,
                "expected_delivery": order.expected_delivery_date,
                "created_at": order.created_at
            }
            for order in recent_orders
        ],
        "recent_clients": [
            {
                "id": client.id,
                "name": client.name,
                "mobile": client.mobile_number,
                "created_at": client.created_at
            }
            for client in recent_clients
        ]
    }
