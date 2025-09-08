# Boutique Work Orders Management System

A FastAPI-based backend application for managing work orders in a boutique business.

## Features

- **Client Management**: Store and manage client information
- **Work Order Management**: Create, edit, and track work orders
- **Billing System**: Handle advance payments, estimates, and due amounts
- **Status Tracking**: Track order progress from placement to delivery
- **Priority Management**: Sort orders by delivery dates and urgency
- **Query System**: Advanced filtering and search capabilities
- **Master Dashboard**: Summary statistics and overdue tracking

## Project Structure

```
boutique_work_orders/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration and session management
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic models for request/response
│   ├── crud.py              # Database operations
│   └── routers/
│       ├── __init__.py
│       ├── work_orders.py   # Work order endpoints
│       ├── clients.py       # Client management endpoints
│       └── dashboard.py     # Dashboard and summary endpoints
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
├── setup.py                # Setup script
└── run_server.py           # Server startup script
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

#### Option 1: Automated Setup (Recommended)

1. **Setup Virtual Environment**
   ```bash
   # Double-click or run:
   setup_venv.bat
   ```

2. **Run the Application**
   ```bash
   # Double-click or run:
   run_with_venv.bat
   ```

#### Option 2: Manual Setup

1. **Clone or download the project**
   ```bash
   cd boutique_work_orders
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv C:\Users\kvs\Desktop\venv_boutique
   C:\Users\kvs\Desktop\venv_boutique\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run_server.py
   ```

#### Access the Application
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- API Base URL: http://localhost:8000
- Admin Panel: Available in API docs under "admin" section

## API Endpoints

### Work Order Management

#### A) Create Work Order
- **POST** `/work-orders/`
- Creates a new work order with client and billing information
- **Input**: Client details, delivery date, billing info
- **Output**: Created work order with assigned ID

#### B) Get Client Summary
- **GET** `/clients/summary/{client_id}`
- **GET** `/clients/summary/mobile/{mobile_number}`
- Retrieve all work orders for a specific client
- **Input**: Client ID or Mobile Number
- **Output**: Client info and associated work orders

#### C) Get Priority List
- **GET** `/work-orders/priority`
- **Query Parameters**: 
  - `sort_order`: "asc" or "desc" (default: "asc")
- Sorted list of work orders by delivery date
- **Output**: Work orders sorted by expected delivery date

#### D) Filter Orders
- **GET** `/work-orders/filter`
- **Query Parameters**:
  - `delivery_date`: Filter by specific delivery date
  - `delivery_window_start`: Start of delivery window
  - `delivery_window_end`: End of delivery window
  - `overdue_only`: Boolean to show only overdue orders
- **Output**: Filtered list of work orders

#### E) Master Page Summary
- **GET** `/dashboard/summary`
- Comprehensive dashboard statistics
- **Output**: 
  - Total work orders
  - Active work orders
  - Overdue work orders
  - Orders due in 1 day

### Additional Endpoints

- **GET** `/work-orders/` - List all work orders
- **GET** `/work-orders/{order_id}` - Get specific work order
- **PUT** `/work-orders/{order_id}` - Update work order
- **DELETE** `/work-orders/{order_id}` - Delete work order
- **GET** `/clients/` - List all clients
- **POST** `/clients/` - Create new client

## Data Models

### Work Order Status Enum
- `Order Placed`
- `Started`
- `Finished`
- `Delivered - Fully Paid`
- `Delivered – Payment Pending`

### Client Information
- Client ID (auto-generated)
- Mobile Number (10 digits, validated)
- Email (optional, validated)
- Name and other details

### Work Order Details
- Order Date (auto-captured)
- Expected Delivery Date (DD/MM/YYYY HH.MM AM/PM)
- Status tracking
- Billing information (advance, estimate, actual, due status)

## Database

The application uses SQLite database (`boutique_orders.db`) which will be created automatically on first run. The database includes:

- **clients** table: Client information
- **work_orders** table: Work order details and billing info

## Testing

The application includes sample data creation for testing purposes. When you first run the application, it will create sample clients and work orders to demonstrate functionality.

## Frontend Integration

This backend is designed to be frontend-agnostic and can be easily integrated with:
- React/Vue.js/Angular applications
- Mobile applications
- Desktop applications
- Any system that can consume REST APIs

The comprehensive API documentation available at `/docs` provides all necessary information for frontend integration.

## Development

### Adding New Features
1. Add new models in `models.py`
2. Create corresponding Pydantic schemas in `schemas.py`
3. Implement CRUD operations in `crud.py`
4. Add API endpoints in appropriate router files
5. Update documentation

### Database Migrations
For production use, consider implementing Alembic for database migrations:
```bash
pip install alembic
alembic init alembic
```

## Production Deployment

For production deployment:
1. Use a production WSGI server like Gunicorn
2. Configure environment variables for database and security
3. Set up proper logging
4. Implement authentication and authorization
5. Use PostgreSQL or MySQL instead of SQLite for better performance

## Support

For issues or questions, refer to the FastAPI documentation: https://fastapi.tiangolo.com/
