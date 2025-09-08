"""
Main FastAPI application for the Boutique Work Orders Management System.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import create_tables, get_db
from app.routers import work_orders, clients, dashboard, admin, status, search
from app import crud, schemas, models

# Create FastAPI application
app = FastAPI(
    title="Boutique Work Orders Management System",
    description="""
    A comprehensive FastAPI backend for managing work orders in a boutique business.
    
    ## Features
    
    * **Client Management**: Store and manage client information with mobile number validation
    * **Work Order Management**: Create, edit, and track work orders with status progression
    * **Billing System**: Handle advance payments, estimates, and due amounts
    * **Priority Management**: Sort orders by delivery dates and urgency
    * **Advanced Filtering**: Query orders by date ranges, status, and client
    * **Dashboard Analytics**: Comprehensive business metrics and alerts
    
    ## API Sections
    
    * **Work Orders**: Complete CRUD operations and advanced querying
    * **Clients**: Client management and summary reports
    * **Dashboard**: Business analytics and summary statistics
    
    ## Status Workflow
    
    1. **Order Placed** → 2. **Started** → 3. **Finished** → 4. **Delivered - Fully Paid** / **Delivered – Payment Pending**
    
    ## Quick Start
    
    1. Create a client or use existing client ID
    2. Create work orders with delivery dates and billing info
    3. Track progress through status updates
    4. Monitor dashboard for overdue orders and business metrics
    """,
    version="1.0.0",
    contact={
        "name": "Boutique Work Orders API",
        "email": "support@boutique-orders.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(work_orders.router)
app.include_router(clients.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(status.router)
app.include_router(search.router)

@app.on_event("startup")
async def startup_event():
    """
    Initialize database and create sample data on startup.
    """
    # Create database tables
    create_tables()
    
    # Create sample data for testing (only if database is empty)
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        # Check if we already have data
        existing_clients = crud.get_clients(db, limit=1)
        if not existing_clients:
            await create_sample_data(db)
    finally:
        db.close()

async def create_sample_data(db: Session):
    """
    Create sample clients and work orders for testing purposes.
    """
    print("Creating sample data for testing...")
    
    # Sample clients
    sample_clients = [
        {
            "name": "Priya Sharma",
            "mobile_number": "9876543210",
            "email": "priya.sharma@email.com",
            "address": "123 MG Road, Bangalore"
        },
        {
            "name": "Rajesh Kumar",
            "mobile_number": "9876543211",
            "email": "rajesh.kumar@email.com",
            "address": "456 Park Street, Mumbai"
        },
        {
            "name": "Anita Desai",
            "mobile_number": "9876543212",
            "email": "anita.desai@email.com",
            "address": "789 Brigade Road, Bangalore"
        },
        {
            "name": "Vikram Singh",
            "mobile_number": "9876543213",
            "address": "321 Connaught Place, Delhi"
        },
        {
            "name": "Meera Patel",
            "mobile_number": "9876543214",
            "email": "meera.patel@email.com",
            "address": "654 Commercial Street, Bangalore"
        }
    ]
    
    created_clients = []
    for client_data in sample_clients:
        client = crud.create_client(db, schemas.ClientCreate(**client_data))
        created_clients.append(client)
    
    # Sample work orders with various statuses and dates
    base_date = datetime.now()
    sample_orders = [
        {
            "client_id": created_clients[0].id,
            "expected_delivery_date": base_date + timedelta(days=2),
            "description": "Custom saree blouse with intricate embroidery",
            "notes": "Gold thread work, size 36",
            "status": models.OrderStatus.STARTED,
            "advance_paid": 500.0,
            "total_estimate": 1200.0,
            "actual_amount": 0.0,
            "due_cleared": False
        },
        {
            "client_id": created_clients[1].id,
            "expected_delivery_date": base_date + timedelta(days=1),
            "description": "Lehenga alteration and fitting",
            "notes": "Reduce length by 2 inches, adjust waist",
            "status": models.OrderStatus.FINISHED,
            "advance_paid": 300.0,
            "total_estimate": 800.0,
            "actual_amount": 750.0,
            "due_cleared": False
        },
        {
            "client_id": created_clients[2].id,
            "expected_delivery_date": base_date - timedelta(days=1),  # Overdue
            "description": "Wedding dress with beadwork",
            "notes": "Pearl and crystal beading, urgent order",
            "status": models.OrderStatus.STARTED,
            "advance_paid": 1000.0,
            "total_estimate": 2500.0,
            "actual_amount": 0.0,
            "due_cleared": False
        },
        {
            "client_id": created_clients[3].id,
            "expected_delivery_date": base_date + timedelta(days=5),
            "description": "Kurta set with matching dupatta",
            "notes": "Cotton fabric, machine embroidery",
            "status": models.OrderStatus.ORDER_PLACED,
            "advance_paid": 200.0,
            "total_estimate": 600.0,
            "actual_amount": 0.0,
            "due_cleared": False
        },
        {
            "client_id": created_clients[4].id,
            "expected_delivery_date": base_date - timedelta(days=3),  # Delivered
            "description": "Saree blouse and petticoat",
            "notes": "Simple design, cotton lining",
            "status": models.OrderStatus.DELIVERED_FULLY_PAID,
            "advance_paid": 400.0,
            "total_estimate": 400.0,
            "actual_amount": 400.0,
            "due_cleared": True
        },
        {
            "client_id": created_clients[0].id,
            "expected_delivery_date": base_date + timedelta(hours=12),  # Due today
            "description": "Quick hem adjustment",
            "notes": "Simple hem for party dress",
            "status": models.OrderStatus.FINISHED,
            "advance_paid": 100.0,
            "total_estimate": 150.0,
            "actual_amount": 150.0,
            "due_cleared": False
        },
        {
            "client_id": created_clients[2].id,
            "expected_delivery_date": base_date + timedelta(days=7),
            "description": "Designer gown with hand embroidery",
            "notes": "Silk fabric, French knots and sequins",
            "status": models.OrderStatus.ORDER_PLACED,
            "advance_paid": 800.0,
            "total_estimate": 3000.0,
            "actual_amount": 0.0,
            "due_cleared": False
        }
    ]
    
    for order_data in sample_orders:
        # Create work order using the existing client
        work_order_create = schemas.WorkOrderCreate(
            client_id=order_data["client_id"],
            expected_delivery_date=order_data["expected_delivery_date"],
            description=order_data["description"],
            notes=order_data["notes"],
            status=order_data["status"],
            advance_paid=order_data["advance_paid"],
            total_estimate=order_data["total_estimate"],
            actual_amount=order_data["actual_amount"],
            due_cleared=order_data["due_cleared"]
        )
        crud.create_work_order(db, work_order_create)
    
    print(f"Created {len(created_clients)} sample clients and {len(sample_orders)} sample work orders")

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to Boutique Work Orders Management System API",
        "version": "1.0.0",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "status": "active",
        "features": [
            "Client Management",
            "Work Order Tracking", 
            "Billing System",
            "Priority Management",
            "Dashboard Analytics",
            "Advanced Filtering"
        ]
    }

@app.get("/health", tags=["health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API and database connectivity.
    """
    try:
        # Test database connection
        client_count = db.query(models.Client).count()
        order_count = db.query(models.WorkOrder).count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database": "connected",
            "clients_count": client_count,
            "orders_count": order_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(),
            "database": "disconnected",
            "error": str(e)
        }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Resource not found",
        "detail": "The requested resource could not be found",
        "status_code": 404
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred",
        "status_code": 500
    }
