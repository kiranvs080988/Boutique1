"""
Clients API router for the Boutique Work Orders Management System.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Client, summary="Create Client")
async def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new client.
    
    **Purpose**: Add a new client to the system
    
    **Input**: 
    - Client name (required)
    - Mobile number (10 digits, required)
    - Email (optional, validated)
    - Address (optional)
    
    **Output**: Created client with assigned ID
    """
    # Check if client with this mobile number already exists
    existing_client = crud.get_client_by_mobile(db, mobile_number=client.mobile_number)
    if existing_client:
        raise HTTPException(
            status_code=400, 
            detail=f"Client with mobile number {client.mobile_number} already exists"
        )
    
    return crud.create_client(db=db, client=client)

@router.get("/", response_model=List[schemas.Client], summary="List All Clients")
async def read_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all clients with pagination.
    
    **Purpose**: Get a paginated list of all clients
    
    **Input**: Optional skip and limit parameters for pagination
    
    **Output**: List of clients
    """
    clients = crud.get_clients(db, skip=skip, limit=limit)
    return clients

@router.get("/{client_id}", response_model=schemas.Client, summary="Get Client by ID")
async def read_client(client_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific client by ID.
    
    **Purpose**: Get detailed information about a specific client
    
    **Input**: Client ID
    
    **Output**: Client details
    """
    db_client = crud.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.put("/{client_id}", response_model=schemas.Client, summary="Update Client")
async def update_client(
    client_id: int,
    client_update: schemas.ClientUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing client.
    
    **Purpose**: Modify client information
    
    **Input**: 
    - Client ID
    - Updated fields (name, mobile, email, address)
    
    **Output**: Updated client information
    """
    # If mobile number is being updated, check for duplicates
    if client_update.mobile_number:
        existing_client = crud.get_client_by_mobile(db, mobile_number=client_update.mobile_number)
        if existing_client and existing_client.id != client_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Another client with mobile number {client_update.mobile_number} already exists"
            )
    
    db_client = crud.update_client(db, client_id=client_id, client_update=client_update)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@router.delete("/{client_id}", response_model=schemas.MessageResponse, summary="Delete Client")
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    """
    Delete a client.
    
    **Purpose**: Remove a client from the system
    
    **Input**: Client ID
    
    **Output**: Success/failure message
    
    **Note**: This will also delete all associated work orders
    """
    success = crud.delete_client(db, client_id=client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return schemas.MessageResponse(message=f"Client {client_id} deleted successfully")

@router.get("/summary/{client_id}", response_model=schemas.ClientSummary, summary="Get Client Summary by ID")
async def get_client_summary(client_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive client summary with all work orders.
    
    **Purpose**: Retrieve complete client information including all associated work orders and statistics
    
    **Input**: Client ID
    
    **Output**: 
    - Client information
    - All work orders for the client
    - Summary statistics (total orders, active orders, completed orders)
    - Total amount due
    """
    summary = crud.get_client_summary(db, client_id=client_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return schemas.ClientSummary(**summary)

@router.get("/summary/mobile/{mobile_number}", response_model=schemas.ClientSummary, summary="Get Client Summary by Mobile")
async def get_client_summary_by_mobile(mobile_number: str, db: Session = Depends(get_db)):
    """
    Get comprehensive client summary by mobile number.
    
    **Purpose**: Retrieve complete client information using mobile number instead of ID
    
    **Input**: Mobile number (10 digits)
    
    **Output**: 
    - Client information
    - All work orders for the client
    - Summary statistics (total orders, active orders, completed orders)
    - Total amount due
    """
    # Validate mobile number format
    if not mobile_number.isdigit() or len(mobile_number) != 10:
        raise HTTPException(
            status_code=400, 
            detail="Mobile number must be exactly 10 digits"
        )
    
    summary = crud.get_client_summary_by_mobile(db, mobile_number=mobile_number)
    if summary is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return schemas.ClientSummary(**summary)

@router.get("/search/mobile/{mobile_number}", response_model=schemas.Client, summary="Find Client by Mobile")
async def find_client_by_mobile(mobile_number: str, db: Session = Depends(get_db)):
    """
    Find a client by mobile number.
    
    **Purpose**: Quick client lookup using mobile number
    
    **Input**: Mobile number (10 digits)
    
    **Output**: Client information
    """
    # Validate mobile number format
    if not mobile_number.isdigit() or len(mobile_number) != 10:
        raise HTTPException(
            status_code=400, 
            detail="Mobile number must be exactly 10 digits"
        )
    
    client = crud.get_client_by_mobile(db, mobile_number=mobile_number)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/{client_id}/work-orders", response_model=List[schemas.WorkOrder], summary="Get Client Work Orders")
async def get_client_work_orders(client_id: int, db: Session = Depends(get_db)):
    """
    Get all work orders for a specific client.
    
    **Purpose**: Retrieve all work orders associated with a client
    
    **Input**: Client ID
    
    **Output**: List of work orders for the client
    """
    # Verify client exists
    client = crud.get_client(db, client_id=client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    work_orders = crud.get_work_orders_by_client(db, client_id=client_id)
    return work_orders
