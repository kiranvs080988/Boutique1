"""
Demonstration of the complete search and update workflow for boutique work orders.
This shows how clients can find and update work orders without remembering IDs.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def demo_complete_workflow():
    """Demonstrate the complete workflow from search to status update"""
    
    print("🎯 BOUTIQUE WORK ORDERS - SEARCH & UPDATE WORKFLOW DEMO")
    print("=" * 60)
    
    # Scenario: Client calls and says "I'm Revathy, what's the status of my order?"
    print("\n📞 SCENARIO: Client calls asking about their order")
    print("Client: 'Hi, this is Revathy. Can you check my order status?'")
    
    # Step 1: Search by name
    print("\n🔍 STEP 1: Search by client name")
    search_response = requests.get(f"{BASE_URL}/search/work-orders", params={"query": "Revathy"})
    
    if search_response.status_code == 200:
        search_data = search_response.json()
        print(f"✅ Found {search_data['total_results']} work order(s)")
        
        if search_data['total_results'] > 0:
            work_order = search_data['results'][0]
            print(f"📋 Work Order Details:")
            print(f"   • Order ID: #{work_order['work_order_id']}")
            print(f"   • Client: {work_order['client_name']} ({work_order['client_mobile']})")
            print(f"   • Description: {work_order['description']}")
            print(f"   • Current Status: {work_order['status']}")
            print(f"   • Expected Delivery: {work_order['expected_delivery_date'][:10]}")
            print(f"   • Amount Due: ₹{work_order['remaining_amount']}")
            print(f"   • Is Overdue: {'Yes' if work_order['is_overdue'] else 'No'}")
            
            # Step 2: Quick lookup by mobile for verification
            print(f"\n🔍 STEP 2: Verify by mobile number ({work_order['client_mobile']})")
            lookup_response = requests.get(f"{BASE_URL}/search/quick-lookup", 
                                         params={"mobile": work_order['client_mobile']})
            
            if lookup_response.status_code == 200:
                lookup_data = lookup_response.json()
                client_info = lookup_data['results'][0]['client']
                print(f"✅ Client verified: {client_info['name']}")
                print(f"   • Address: {client_info['address']}")
                print(f"   • Total Orders: {len(lookup_data['results'][0]['work_orders'])}")
            
            # Step 3: Status update scenario
            print(f"\n🔄 STEP 3: Update work order status")
            current_status = work_order['status']
            
            # Determine next status in workflow
            next_status_map = {
                "Order Placed": "Started",
                "Started": "Finished", 
                "Finished": "Delivered - Fully Paid"
            }
            
            if current_status in next_status_map:
                next_status = next_status_map[current_status]
                print(f"Staff: 'Let me update your order from {current_status} to {next_status}'")
                
                # Update status
                update_response = requests.put(
                    f"{BASE_URL}/search/work-orders/{work_order['work_order_id']}/status",
                    params={"new_status": next_status}
                )
                
                if update_response.status_code == 200:
                    update_data = update_response.json()
                    print(f"✅ Status updated successfully!")
                    print(f"   • Old Status: {update_data['old_status']}")
                    print(f"   • New Status: {update_data['new_status']}")
                    print(f"   • Remaining Amount: ₹{update_data['updated_order']['remaining_amount']}")
                    
                    # Step 4: Verify the update
                    print(f"\n✅ STEP 4: Verify the update")
                    verify_response = requests.get(f"{BASE_URL}/search/work-orders", 
                                                 params={"query": "Revathy"})
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        updated_order = verify_data['results'][0]
                        print(f"✅ Update confirmed:")
                        print(f"   • Current Status: {updated_order['status']}")
                        print(f"   • Display Summary: {updated_order['display_summary']}")
                else:
                    print(f"❌ Status update failed: {update_response.status_code}")
            else:
                print(f"ℹ️  Order is already at final status: {current_status}")
    
    # Step 5: Show other search capabilities
    print(f"\n🔍 STEP 5: Other search capabilities")
    
    # Search by mobile number
    print(f"\n📱 Search by mobile number:")
    mobile_search = requests.get(f"{BASE_URL}/search/work-orders", params={"query": "7594933334"})
    if mobile_search.status_code == 200:
        mobile_data = mobile_search.json()
        print(f"✅ Found {mobile_data['total_results']} orders by mobile search")
    
    # Search by description
    print(f"\n📝 Search by description:")
    desc_search = requests.get(f"{BASE_URL}/search/work-orders", params={"query": "Owner"})
    if desc_search.status_code == 200:
        desc_data = desc_search.json()
        print(f"✅ Found {desc_data['total_results']} orders by description search")
    
    # Recent orders
    print(f"\n📅 Recent orders (last 7 days):")
    recent_response = requests.get(f"{BASE_URL}/search/recent-orders", params={"days": 7})
    if recent_response.status_code == 200:
        recent_data = recent_response.json()
        print(f"✅ Found {recent_data['total_results']} recent orders")
        for order in recent_data['results']:
            print(f"   • {order['display_summary']}")
    
    print(f"\n🎉 WORKFLOW COMPLETE!")
    print("=" * 60)
    print("✅ BENEFITS FOR BOUTIQUE BUSINESS:")
    print("   • Clients don't need to remember order IDs")
    print("   • Staff can quickly find orders by name, mobile, or description")
    print("   • Easy status updates with workflow validation")
    print("   • Multiple search options for flexibility")
    print("   • Real-time verification and confirmation")
    print("=" * 60)

def demo_frontend_integration():
    """Show how frontend would integrate with these endpoints"""
    
    print(f"\n💻 FRONTEND INTEGRATION EXAMPLE")
    print("=" * 40)
    
    print("""
    Frontend Search Form:
    ┌─────────────────────────────────────┐
    │ Search Work Orders                  │
    │                                     │
    │ Search: [Revathy____________] 🔍    │
    │                                     │
    │ Results:                            │
    │ ┌─────────────────────────────────┐ │
    │ │ ✓ Revathy Jayanbabu - Owner     │ │
    │ │   Status: Started               │ │
    │ │   Mobile: 7594933334            │ │
    │ │   Due: ₹99.0                    │ │
    │ │   [Update Status ▼] [View]      │ │
    │ └─────────────────────────────────┘ │
    └─────────────────────────────────────┘
    
    Status Update Dropdown:
    ┌─────────────────────────────────────┐
    │ Update Status for Order #1          │
    │                                     │
    │ Current: Started                    │
    │ New Status: [Finished        ▼]    │
    │                                     │
    │ [Cancel]  [Update Status]           │
    └─────────────────────────────────────┘
    """)
    
    print("JavaScript Integration Example:")
    print("""
    // Search work orders
    async function searchWorkOrders(query) {
        const response = await fetch(`/search/work-orders?query=${query}`);
        const data = await response.json();
        return data.results;
    }
    
    // Update status
    async function updateStatus(workOrderId, newStatus) {
        const response = await fetch(
            `/search/work-orders/${workOrderId}/status?new_status=${newStatus}`,
            { method: 'PUT' }
        );
        return await response.json();
    }
    
    // Quick lookup by mobile
    async function quickLookup(mobile) {
        const response = await fetch(`/search/quick-lookup?mobile=${mobile}`);
        return await response.json();
    }
    """)

if __name__ == "__main__":
    demo_complete_workflow()
    demo_frontend_integration()
