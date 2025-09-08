"""
Test script for admin endpoints - database management functionality.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_database_stats():
    """Test getting database statistics"""
    print("Testing database stats...")
    try:
        response = requests.get(f"{BASE_URL}/admin/database-stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Database stats retrieved:")
            print(f"  - Total clients: {data['total_clients']}")
            print(f"  - Total work orders: {data['total_work_orders']}")
            print(f"  - Status breakdown: {data['status_breakdown']}")
            return True
        else:
            print(f"✗ Database stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Database stats error: {e}")
        return False

def test_reset_database():
    """Test resetting the entire database"""
    print("\nTesting database reset...")
    try:
        response = requests.delete(f"{BASE_URL}/admin/reset-database")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Database reset successful:")
            print(f"  - Message: {data['message']}")
            return True
        else:
            print(f"✗ Database reset failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Database reset error: {e}")
        return False

def test_delete_work_orders():
    """Test deleting all work orders"""
    print("\nTesting delete all work orders...")
    try:
        response = requests.delete(f"{BASE_URL}/admin/delete-all-work-orders")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Work orders deletion successful:")
            print(f"  - Message: {data['message']}")
            return True
        else:
            print(f"✗ Work orders deletion failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Work orders deletion error: {e}")
        return False

def test_delete_clients():
    """Test deleting all clients"""
    print("\nTesting delete all clients...")
    try:
        response = requests.delete(f"{BASE_URL}/admin/delete-all-clients")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Clients deletion successful:")
            print(f"  - Message: {data['message']}")
            return True
        else:
            print(f"✗ Clients deletion failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Clients deletion error: {e}")
        return False

def create_test_data():
    """Create some test data to verify deletion works"""
    print("\nCreating test data...")
    
    # Create a test client
    client_data = {
        "name": "Test Admin Client",
        "mobile_number": "9999999999",
        "email": "admin@test.com",
        "address": "Test Address"
    }
    
    try:
        client_response = requests.post(f"{BASE_URL}/clients/", json=client_data)
        if client_response.status_code == 200:
            client = client_response.json()
            print(f"✓ Test client created: ID {client['id']}")
            
            # Create a test work order
            order_data = {
                "client_id": client['id'],
                "expected_delivery_date": "2025-09-10T10:00:00Z",
                "description": "Test admin order",
                "notes": "Created for admin testing",
                "status": "Order Placed",
                "advance_paid": 100,
                "total_estimate": 500,
                "actual_amount": 0,
                "due_cleared": False
            }
            
            order_response = requests.post(f"{BASE_URL}/work-orders/", json=order_data)
            if order_response.status_code == 200:
                order = order_response.json()
                print(f"✓ Test work order created: ID {order['id']}")
                return True
            else:
                print(f"✗ Test work order creation failed: {order_response.status_code}")
                return False
        else:
            print(f"✗ Test client creation failed: {client_response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Test data creation error: {e}")
        return False

def main():
    """Run all admin endpoint tests"""
    print("=" * 60)
    print("Boutique Work Orders - Admin Endpoints Tests")
    print("=" * 60)
    
    tests = [
        ("Initial Database Stats", test_database_stats),
        ("Create Test Data", create_test_data),
        ("Database Stats After Creation", test_database_stats),
        ("Delete All Work Orders", test_delete_work_orders),
        ("Database Stats After Work Orders Deletion", test_database_stats),
        ("Create Test Data Again", create_test_data),
        ("Delete All Clients", test_delete_clients),
        ("Database Stats After Clients Deletion", test_database_stats),
        ("Create Test Data Again", create_test_data),
        ("Reset Entire Database", test_reset_database),
        ("Final Database Stats", test_database_stats)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"Admin Tests Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All admin tests passed! Database management is working correctly.")
        print("\nAdmin endpoints available:")
        print("  - GET /admin/database-stats - View database statistics")
        print("  - DELETE /admin/reset-database - Reset entire database")
        print("  - DELETE /admin/delete-all-work-orders - Delete all work orders")
        print("  - DELETE /admin/delete-all-clients - Delete all clients")
    else:
        print("⚠️  Some admin tests failed. Please check the server logs.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
