"""
Admin endpoints for database management and system operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/admin", tags=["admin"])

@router.delete("/reset-database", response_model=schemas.MessageResponse)
def reset_database(db: Session = Depends(get_db)):
    """
    Delete all data from the database (master reset).
    
    **WARNING**: This will permanently delete:
    - All work orders
    - All clients
    - All related data
    
    Use with caution - this action cannot be undone!
    """
    try:
        # Delete all work orders first (due to foreign key constraints)
        work_orders_deleted = db.query(models.WorkOrder).count()
        db.query(models.WorkOrder).delete()
        
        # Delete all clients
        clients_deleted = db.query(models.Client).count()
        db.query(models.Client).delete()
        
        # Commit the changes
        db.commit()
        
        return schemas.MessageResponse(
            message=f"Database reset successful. Deleted {work_orders_deleted} work orders and {clients_deleted} clients.",
            success=True
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database reset failed: {str(e)}")

@router.delete("/delete-all-work-orders", response_model=schemas.MessageResponse)
def delete_all_work_orders(db: Session = Depends(get_db)):
    """
    Delete all work orders from the database.
    
    **Note**: This will keep all clients but remove all their work orders.
    """
    try:
        count = db.query(models.WorkOrder).count()
        db.query(models.WorkOrder).delete()
        db.commit()
        
        return schemas.MessageResponse(
            message=f"Successfully deleted {count} work orders.",
            success=True
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete work orders: {str(e)}")

@router.delete("/delete-all-clients", response_model=schemas.MessageResponse)
def delete_all_clients(db: Session = Depends(get_db)):
    """
    Delete all clients from the database.
    
    **WARNING**: This will also delete all associated work orders due to foreign key constraints.
    """
    try:
        # Count before deletion
        work_orders_count = db.query(models.WorkOrder).count()
        clients_count = db.query(models.Client).count()
        
        # Delete work orders first
        db.query(models.WorkOrder).delete()
        # Delete clients
        db.query(models.Client).delete()
        
        db.commit()
        
        return schemas.MessageResponse(
            message=f"Successfully deleted {clients_count} clients and {work_orders_count} associated work orders.",
            success=True
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete clients: {str(e)}")

@router.get("/database-stats")
def get_database_stats(db: Session = Depends(get_db)):
    """
    Get current database statistics.
    
    Returns counts of all records in the database.
    """
    try:
        total_clients = db.query(models.Client).count()
        total_work_orders = db.query(models.WorkOrder).count()
        
        # Get status breakdown
        status_breakdown = {}
        for status in models.OrderStatus:
            count = db.query(models.WorkOrder).filter(models.WorkOrder.status == status).count()
            status_breakdown[status.value] = count
        
        return {
            "total_clients": total_clients,
            "total_work_orders": total_work_orders,
            "status_breakdown": status_breakdown,
            "database_file": "boutique_orders.db"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")
