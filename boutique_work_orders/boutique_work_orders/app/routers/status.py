"""
Status management endpoints for work order status workflow.
"""

from fastapi import APIRouter
from typing import List, Dict
from app import models

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/options")
def get_status_options():
    """
    Get all available work order status options for frontend dropdown.
    
    Returns a list of status options with their display names and values,
    ordered according to the workflow progression.
    
    **Workflow Order:**
    1. Order Placed → 2. Started → 3. Finished → 4. Delivered - Fully Paid / Delivered – Payment Pending
    
    **Returns:**
    - List of status objects with 'value' and 'label' fields
    - Ordered by workflow progression
    - Compatible with frontend dropdown components
    """
    status_options = [
        {
            "value": models.OrderStatus.ORDER_PLACED.value,
            "label": "Order Placed",
            "order": 1,
            "description": "Initial status when order is first created"
        },
        {
            "value": models.OrderStatus.STARTED.value,
            "label": "Started", 
            "order": 2,
            "description": "Work has begun on the order"
        },
        {
            "value": models.OrderStatus.FINISHED.value,
            "label": "Finished",
            "order": 3,
            "description": "Work is completed, ready for delivery"
        },
        {
            "value": models.OrderStatus.DELIVERED_FULLY_PAID.value,
            "label": "Delivered - Fully Paid",
            "order": 4,
            "description": "Order delivered and payment completed"
        },
        {
            "value": models.OrderStatus.DELIVERED_PAYMENT_PENDING.value,
            "label": "Delivered – Payment Pending",
            "order": 4,
            "description": "Order delivered but payment still pending"
        }
    ]
    
    return status_options

@router.get("/workflow")
def get_status_workflow():
    """
    Get the complete status workflow information.
    
    Returns detailed workflow information including:
    - Status progression rules
    - Valid transitions
    - Workflow stages
    
    **Returns:**
    - Complete workflow structure
    - Transition rules
    - Stage descriptions
    """
    workflow = {
        "stages": [
            {
                "stage": 1,
                "name": "Order Placement",
                "statuses": ["Order Placed"],
                "description": "Initial order creation and confirmation"
            },
            {
                "stage": 2, 
                "name": "Work in Progress",
                "statuses": ["Started"],
                "description": "Active work being performed on the order"
            },
            {
                "stage": 3,
                "name": "Work Completed", 
                "statuses": ["Finished"],
                "description": "Work completed, ready for delivery"
            },
            {
                "stage": 4,
                "name": "Delivered",
                "statuses": ["Delivered - Fully Paid", "Delivered – Payment Pending"],
                "description": "Order delivered to customer"
            }
        ],
        "transitions": {
            "Order Placed": ["Started"],
            "Started": ["Finished"],
            "Finished": ["Delivered - Fully Paid", "Delivered – Payment Pending"],
            "Delivered - Fully Paid": [],  # Final state
            "Delivered – Payment Pending": ["Delivered - Fully Paid"]  # Can update payment status
        },
        "final_states": ["Delivered - Fully Paid"],
        "active_states": ["Order Placed", "Started", "Finished", "Delivered – Payment Pending"]
    }
    
    return workflow

@router.get("/next-options/{current_status}")
def get_next_status_options(current_status: str):
    """
    Get valid next status options based on current status.
    
    **Parameters:**
    - current_status: Current work order status
    
    **Returns:**
    - List of valid next status options
    - Empty list if no valid transitions available
    
    **Example:**
    - Current: "Order Placed" → Next: ["Started"]
    - Current: "Finished" → Next: ["Delivered - Fully Paid", "Delivered – Payment Pending"]
    """
    workflow_transitions = {
        "Order Placed": [
            {
                "value": models.OrderStatus.STARTED.value,
                "label": "Started",
                "description": "Begin work on the order"
            }
        ],
        "Started": [
            {
                "value": models.OrderStatus.FINISHED.value,
                "label": "Finished", 
                "description": "Mark work as completed"
            }
        ],
        "Finished": [
            {
                "value": models.OrderStatus.DELIVERED_FULLY_PAID.value,
                "label": "Delivered - Fully Paid",
                "description": "Order delivered with full payment"
            },
            {
                "value": models.OrderStatus.DELIVERED_PAYMENT_PENDING.value,
                "label": "Delivered – Payment Pending",
                "description": "Order delivered but payment pending"
            }
        ],
        "Delivered – Payment Pending": [
            {
                "value": models.OrderStatus.DELIVERED_FULLY_PAID.value,
                "label": "Delivered - Fully Paid",
                "description": "Update to fully paid status"
            }
        ],
        "Delivered - Fully Paid": []  # Final state, no transitions
    }
    
    return workflow_transitions.get(current_status, [])

@router.get("/validation/{status}")
def validate_status(status: str):
    """
    Validate if a status value is valid.
    
    **Parameters:**
    - status: Status value to validate
    
    **Returns:**
    - Validation result with status information
    """
    valid_statuses = [status.value for status in models.OrderStatus]
    
    is_valid = status in valid_statuses
    
    result = {
        "status": status,
        "is_valid": is_valid,
        "valid_statuses": valid_statuses
    }
    
    if is_valid:
        # Find the status enum and get additional info
        for status_enum in models.OrderStatus:
            if status_enum.value == status:
                result["display_name"] = status_enum.value
                result["is_final"] = status_enum in [
                    models.OrderStatus.DELIVERED_FULLY_PAID
                ]
                result["is_active"] = status_enum not in [
                    models.OrderStatus.DELIVERED_FULLY_PAID,
                    models.OrderStatus.DELIVERED_PAYMENT_PENDING
                ]
                break
    
    return result
