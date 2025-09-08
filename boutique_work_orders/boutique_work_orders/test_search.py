"""
Test script for search endpoints - finding work orders without knowing IDs.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_search_work_orders():
    """Test searching work orders by various criteria"""
    print("Testing work order search...")
    
    test_cases = [
        ("Priya", "Search by client name"),
        ("saree", "Search by description"),
        ("9876543210", "Search by mobile number"),
        ("urgent", "Search by notes"),
        ("embroidery", "Search by description keyword")
    ]
    
    success_count = 0
    for query, description in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/search/work-orders", params={"query": query})
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {description}: Found {data['total_results']} results")
                if data['total_results'] > 0:
                    first_result = data['results'][0]
                    print(f"    → {first_result['display_summary']}")
                success_count += 1
            else:
                print(f"✗ {description} failed: {response.status_code}")
        except Exception as e:
            print(f"✗ {description} error: {e}")
    
    return success_count == len(test_cases)

def test_quick_lookup():
    """Test quick lookup functionality"""
    print("\nTesting quick lookup...")
    
    test_cases = [
        ({"mobile": "9876543210"}, "Lookup by mobile"),
        ({"name": "Priya"}, "Lookup by name"),
        ({"mobile": "987654", "name": "Sharma"}, "Lookup by mobile and name")
    ]
    
    success_count = 0
    for params, description in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/search/quick-lookup", params=params)
            if response.status_code == 200:
                data = response.json()
                if "results" in data:
                    print(f"✓ {description}: Found {data['total_clients']} clients")
                    for client_result in data['results']:
                        client = client_result['client']
                        orders_count = len(client_result['work_orders'])
                        print(f"    → {client['name']} ({client['mobile_number']}) - {orders_count} orders")
                    success_count += 1
                else:
                    print(f"✓ {description}: {data.get('message', 'No results')}")
                    success_count += 1
            else:
                print(f"✗ {description} failed: {response.status_code}")
        except Exception as e:
            print(f"✗ {description} error: {e}")
    
    return success_count == len(test_cases)

def test_status_update():
    """Test updating work order status after search"""
    print("\nTesting status update after search...")
    
    try:
        # First, search for a work order
        response = requests.get(f"{BASE_URL}/search/work-orders", params={"query": "Priya"})
        if response.status_code == 200:
            data = response.json()
            if data['total_results'] > 0:
                work_order = data['results'][0]
                work_order_id = work_order['work_order_id']
                current_status = work_order['status']
                
                print(f"Found work order #{work_order_id} with status: {current_status}")
                
                # Determine next valid status
                next_status = None
                if current_status == "Order Placed":
                    next_status = "Started"
                elif current_status == "Started":
                    next_status = "Finished"
                elif current_status == "Finished":
                    next_status = "Delivered - Fully Paid"
                
                if next_status:
                    # Update status
                    update_response = requests.put(
                        f"{BASE_URL}/search/work-orders/{work_order_id}/status",
                        params={"new_status": next_status}
                    )
                    
                    if update_response.status_code == 200:
                        update_data = update_response.json()
                        print(f"✓ Status updated: {update_data['old_status']} → {update_data['new_status']}")
                        return True
                    else:
                        print(f"✗ Status update failed: {update_response.status_code}")
                        return False
                else:
                    print(f"✓ Work order already at final status: {current_status}")
                    return True
            else:
                print("✗ No work orders found for status update test")
                return False
        else:
            print(f"✗ Search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Status update error: {e}")
        return False

def test_recent_orders():
    """Test getting recent orders"""
    print("\nTesting recent orders...")
    
    try:
        response = requests.get(f"{BASE_URL}/search/recent-orders", params={"days": 30})
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Recent orders: Found {data['total_results']} orders in last {data['days_back']} days")
            for order in data['results'][:3]:  # Show first 3
                print(f"    → {order['display_summary']}")
            return True
        else:
            print(f"✗ Recent orders failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Recent orders error: {e}")
        return False

def test_client_search():
    """Test client search functionality"""
    print("\nTesting client search...")
    
    try:
        response = requests.get(f"{BASE_URL}/search/clients", params={"query": "Sharma"})
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Client search: Found {data['total_results']} clients")
            for client in data['results']:
                print(f"    → {client['display_summary']}")
            return True
        else:
            print(f"✗ Client search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Client search error: {e}")
        return False

def main():
    """Run all search endpoint tests"""
    print("=" * 60)
    print("Boutique Work Orders - Search & Lookup Tests")
    print("=" * 60)
    
    tests = [
        ("Work Order Search", test_search_work_orders),
        ("Quick Lookup", test_quick_lookup),
        ("Status Update", test_status_update),
        ("Recent Orders", test_recent_orders),
        ("Client Search", test_client_search)
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
    print(f"Search Tests Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All search tests passed! Frontend search integration ready.")
        print("\nSearch endpoints available:")
        print("  - GET /search/work-orders - Search work orders by any field")
        print("  - GET /search/quick-lookup - Quick lookup by mobile/name")
        print("  - PUT /search/work-orders/{id}/status - Update status after search")
        print("  - GET /search/recent-orders - Get recent work orders")
        print("  - GET /search/clients - Search clients by any field")
        print("\nFrontend Integration:")
        print("  1. User searches by name/mobile/description")
        print("  2. System shows matching work orders with display summaries")
        print("  3. User selects the right work order from results")
        print("  4. System allows status update (e.g., Started → Delivered - Fully Paid)")
    else:
        print("⚠️  Some search tests failed. Please check the server logs.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
