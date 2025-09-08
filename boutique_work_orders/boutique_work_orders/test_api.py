"""
Test script to verify the Boutique Work Orders Management System API.
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test API health endpoint"""
    print("Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API is healthy - {data['clients_count']} clients, {data['orders_count']} orders")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_dashboard_summary():
    """Test dashboard summary endpoint"""
    print("\nTesting dashboard summary...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Dashboard summary retrieved:")
            print(f"  - Total orders: {data['total_work_orders']}")
            print(f"  - Active orders: {data['active_work_orders']}")
            print(f"  - Overdue orders: {data['overdue_work_orders']}")
            print(f"  - Due in 1 day: {data['orders_due_in_one_day']}")
            return True
        else:
            print(f"✗ Dashboard summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Dashboard summary error: {e}")
        return False

def test_clients_list():
    """Test clients list endpoint"""
    print("\nTesting clients list...")
    try:
        response = requests.get(f"{BASE_URL}/clients/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data)} clients")
            if data:
                print(f"  - First client: {data[0]['name']} ({data[0]['mobile_number']})")
            return True
        else:
            print(f"✗ Clients list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Clients list error: {e}")
        return False

def test_work_orders_list():
    """Test work orders list endpoint"""
    print("\nTesting work orders list...")
    try:
        response = requests.get(f"{BASE_URL}/work-orders/")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data)} work orders")
            if data:
                order = data[0]
                print(f"  - First order: ID {order['id']} - {order['description'][:50]}...")
                print(f"    Status: {order['status']}, Client: {order['client']['name']}")
            return True
        else:
            print(f"✗ Work orders list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Work orders list error: {e}")
        return False

def test_priority_orders():
    """Test priority orders endpoint"""
    print("\nTesting priority orders...")
    try:
        response = requests.get(f"{BASE_URL}/work-orders/priority/list?sort_order=asc")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved priority list with {data['total_count']} orders")
            print(f"  - Sort order: {data['sort_order']}")
            return True
        else:
            print(f"✗ Priority orders failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Priority orders error: {e}")
        return False

def test_overdue_orders():
    """Test overdue orders endpoint"""
    print("\nTesting overdue orders...")
    try:
        response = requests.get(f"{BASE_URL}/work-orders/status/overdue")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data)} overdue orders")
            return True
        else:
            print(f"✗ Overdue orders failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Overdue orders error: {e}")
        return False

def test_client_summary():
    """Test client summary by mobile number"""
    print("\nTesting client summary...")
    try:
        # First get a client
        clients_response = requests.get(f"{BASE_URL}/clients/")
        if clients_response.status_code == 200:
            clients = clients_response.json()
            if clients:
                mobile = clients[0]['mobile_number']
                response = requests.get(f"{BASE_URL}/clients/summary/mobile/{mobile}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Client summary for {data['client']['name']}:")
                    print(f"  - Total orders: {data['total_orders']}")
                    print(f"  - Active orders: {data['active_orders']}")
                    print(f"  - Amount due: ₹{data['total_amount_due']}")
                    return True
                else:
                    print(f"✗ Client summary failed: {response.status_code}")
                    return False
            else:
                print("✗ No clients found for testing")
                return False
        else:
            print(f"✗ Could not get clients: {clients_response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Client summary error: {e}")
        return False

def test_create_work_order():
    """Test creating a new work order"""
    print("\nTesting work order creation...")
    try:
        # Create a new work order with new client
        order_data = {
            "client_name": "Test Client",
            "client_mobile": "9999999999",
            "client_email": "test@example.com",
            "expected_delivery_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "description": "Test order for API verification",
            "notes": "This is a test order created by the test script",
            "advance_paid": 100.0,
            "total_estimate": 500.0
        }
        
        response = requests.post(f"{BASE_URL}/work-orders/", json=order_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Work order created successfully:")
            print(f"  - Order ID: {data['id']}")
            print(f"  - Client: {data['client']['name']}")
            print(f"  - Description: {data['description']}")
            return True
        else:
            print(f"✗ Work order creation failed: {response.status_code}")
            if response.text:
                print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Work order creation error: {e}")
        return False

def main():
    """Run all API tests"""
    print("=" * 60)
    print("Boutique Work Orders Management System - API Tests")
    print("=" * 60)
    
    tests = [
        test_api_health,
        test_dashboard_summary,
        test_clients_list,
        test_work_orders_list,
        test_priority_orders,
        test_overdue_orders,
        test_client_summary,
        test_create_work_order
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        print("\nYou can now:")
        print("  - Access the API documentation at http://localhost:8000/docs")
        print("  - Use the API endpoints in your frontend application")
        print("  - Explore the sample data created automatically")
    else:
        print("⚠️  Some tests failed. Please check the server logs.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
