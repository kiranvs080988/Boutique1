"""
Test script for mobile number table search functionality.
Demonstrates the enhanced mobile search with table format and edit capabilities.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_mobile_table_search():
    """Test the new mobile table search endpoint"""
    print("🔍 Testing Mobile Table Search...")
    
    mobile_number = "7594933334"  # Using the existing client's mobile
    
    try:
        response = requests.get(f"{BASE_URL}/search/mobile/{mobile_number}/work-orders")
        
        if response.status_code == 200:
            data = response.json()
            
            if data["client_found"]:
                print(f"✅ Client found: {data['client_info']['name']}")
                print(f"   Mobile: {data['client_info']['mobile_number']}")
                print(f"   Total Work Orders: {data['total_work_orders']}")
                print(f"   Active Orders: {data['active_orders']}")
                print(f"   Overdue Orders: {data['overdue_orders']}")
                
                print(f"\n📋 TABLE DATA:")
                print("=" * 80)
                
                # Display table headers
                headers = data["table_headers"]
                header_line = " | ".join([h["label"].ljust(15) for h in headers])
                print(header_line)
                print("-" * 80)
                
                # Display table rows
                for row in data["table_data"]:
                    table_display = row["table_display"]
                    row_line = f"{table_display['id_display'].ljust(15)} | "
                    row_line += f"{table_display['description_display'][:15].ljust(15)} | "
                    row_line += f"{table_display['delivery_display'].ljust(15)} | "
                    row_line += f"{table_display['status_display'].ljust(15)} | "
                    row_line += f"{table_display['amount_display'].ljust(15)} | "
                    row_line += f"{'[Edit]'.ljust(15)}"
                    print(row_line)
                
                print("=" * 80)
                
                # Show detailed row information
                if data["table_data"]:
                    first_row = data["table_data"][0]
                    print(f"\n📝 DETAILED ROW INFO (First Work Order):")
                    print(f"   • Work Order ID: {first_row['work_order_id']}")
                    print(f"   • Description Preview: {first_row['description_preview']}")
                    print(f"   • Full Description: {first_row['full_description']}")
                    print(f"   • Status: {first_row['status']} ({first_row['status_priority']})")
                    print(f"   • Expected Delivery: {first_row['expected_delivery_date']} {first_row['expected_delivery_time']}")
                    print(f"   • Remaining Amount: ₹{first_row['remaining_amount']}")
                    print(f"   • Can Edit: {first_row['can_edit']}")
                    print(f"   • Can Update Status: {first_row['can_update_status']}")
                    print(f"   • Edit URL: {first_row['edit_url']}")
                    print(f"   • Status Update URL: {first_row['status_update_url']}")
                    
                    return first_row["work_order_id"]  # Return for further testing
                
            else:
                print(f"❌ No client found with mobile: {mobile_number}")
                return None
        else:
            print(f"❌ Request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_work_order_for_edit(mobile_number, work_order_id):
    """Test getting work order details for editing"""
    print(f"\n📝 Testing Get Work Order for Edit...")
    
    try:
        response = requests.get(f"{BASE_URL}/search/mobile/{mobile_number}/work-orders/{work_order_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data["success"]:
                print(f"✅ Work order details retrieved for editing:")
                
                client = data["client_info"]
                work_order = data["work_order"]
                status_options = data["status_options"]
                edit_caps = data["edit_capabilities"]
                
                print(f"\n👤 CLIENT INFO:")
                print(f"   • Name: {client['name']}")
                print(f"   • Mobile: {client['mobile_number']}")
                print(f"   • Email: {client['email']}")
                print(f"   • Address: {client['address']}")
                
                print(f"\n📋 WORK ORDER DETAILS:")
                print(f"   • ID: #{work_order['work_order_id']}")
                print(f"   • Description: {work_order['description']}")
                print(f"   • Notes: {work_order['notes']}")
                print(f"   • Status: {work_order['status']}")
                print(f"   • Order Date: {work_order['order_date']}")
                print(f"   • Expected Delivery: {work_order['expected_delivery_date']}")
                print(f"   • Advance Paid: ₹{work_order['advance_paid']}")
                print(f"   • Total Estimate: ₹{work_order['total_estimate']}")
                print(f"   • Actual Amount: ₹{work_order['actual_amount']}")
                print(f"   • Remaining: ₹{work_order['remaining_amount']}")
                print(f"   • Due Cleared: {work_order['due_cleared']}")
                print(f"   • Is Overdue: {work_order['is_overdue']}")
                
                print(f"\n🔄 STATUS OPTIONS:")
                print(f"   • Current: {status_options['current_status']}")
                print(f"   • Next Options: {[opt['label'] for opt in status_options['next_options']]}")
                
                print(f"\n✏️ EDIT CAPABILITIES:")
                for capability, allowed in edit_caps.items():
                    status = "✅" if allowed else "❌"
                    print(f"   • {capability.replace('_', ' ').title()}: {status}")
                
                return True
            else:
                print(f"❌ Failed to get work order: {data['error']}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_update_work_order_via_mobile(mobile_number, work_order_id):
    """Test updating work order via mobile search"""
    print(f"\n🔄 Testing Work Order Update via Mobile...")
    
    # Update data
    update_data = {
        "notes": "Updated via mobile search - test successful!",
        "actual_amount": 150.0
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/search/mobile/{mobile_number}/work-orders/{work_order_id}",
            json=update_data
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data["success"]:
                print(f"✅ Work order updated successfully!")
                print(f"   • Message: {data['message']}")
                print(f"   • Updated Fields: {data['updated_fields']}")
                
                updated_order = data["updated_order"]
                print(f"\n📋 UPDATED ORDER INFO:")
                print(f"   • ID: #{updated_order['work_order_id']}")
                print(f"   • Client: {updated_order['client_name']}")
                print(f"   • Description: {updated_order['description']}")
                print(f"   • Status: {updated_order['status']}")
                print(f"   • Remaining Amount: ₹{updated_order['remaining_amount']}")
                
                return True
            else:
                print(f"❌ Update failed: {data['error']}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_frontend_table_integration():
    """Show how frontend would integrate with the table endpoints"""
    print(f"\n💻 FRONTEND TABLE INTEGRATION DEMO")
    print("=" * 50)
    
    print("""
    Frontend Mobile Search Interface:
    
    ┌─────────────────────────────────────────────────────────┐
    │ Search by Mobile Number                                 │
    │                                                         │
    │ Mobile: [7594933334_________] [Search]                  │
    └─────────────────────────────────────────────────────────┘
    
    Results Table:
    ┌─────────────────────────────────────────────────────────┐
    │ Client: Revathy Jayanbabu (7594933334)                 │
    │ Total Orders: 1 | Active: 1 | Overdue: 1               │
    │                                                         │
    │ ┌─────┬─────────────────┬─────────────┬─────────┬─────┐ │
    │ │ ID  │ Description     │ Delivery    │ Status  │ Edit│ │
    │ ├─────┼─────────────────┼─────────────┼─────────┼─────┤ │
    │ │ #1  │ Owner...        │ 2025-09-07  │Finished │[📝] │ │
    │ └─────┴─────────────────┴─────────────┴─────────┴─────┘ │
    └─────────────────────────────────────────────────────────┘
    
    Edit Modal (when [📝] clicked):
    ┌─────────────────────────────────────────────────────────┐
    │ Edit Work Order #1                                      │
    │                                                         │
    │ Description: [Owner________________________]            │
    │ Notes:       [Owner Suit__________________]            │
    │ Status:      [Finished              ▼]                 │
    │ Delivery:    [2025-09-07] [12:57]                      │
    │ Advance:     [₹1.0_____]                               │
    │ Estimate:    [₹0.0_____]                               │
    │ Actual:      [₹100.0___]                               │
    │                                                         │
    │ [Cancel]  [Save Changes]                                │
    └─────────────────────────────────────────────────────────┘
    """)
    
    print("JavaScript Integration:")
    print("""
    // Search by mobile and get table data
    async function searchByMobile(mobile) {
        const response = await fetch(`/search/mobile/${mobile}/work-orders`);
        const data = await response.json();
        
        if (data.client_found) {
            displayTable(data.table_data, data.table_headers);
            showClientInfo(data.client_info);
        }
        return data;
    }
    
    // Get work order for editing
    async function getWorkOrderForEdit(mobile, workOrderId) {
        const response = await fetch(
            `/search/mobile/${mobile}/work-orders/${workOrderId}`
        );
        return await response.json();
    }
    
    // Update work order
    async function updateWorkOrder(mobile, workOrderId, updateData) {
        const response = await fetch(
            `/search/mobile/${mobile}/work-orders/${workOrderId}`,
            {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updateData)
            }
        );
        return await response.json();
    }
    
    // Display table with edit buttons
    function displayTable(tableData, headers) {
        tableData.forEach(row => {
            const editButton = createEditButton(row.work_order_id);
            // Add row to table with edit functionality
        });
    }
    """)

def main():
    """Run all mobile table search tests"""
    print("🎯 BOUTIQUE WORK ORDERS - MOBILE TABLE SEARCH TESTS")
    print("=" * 60)
    
    mobile_number = "7594933334"
    
    # Test 1: Mobile table search
    work_order_id = test_mobile_table_search()
    
    if work_order_id:
        # Test 2: Get work order for editing
        if test_get_work_order_for_edit(mobile_number, work_order_id):
            # Test 3: Update work order
            test_update_work_order_via_mobile(mobile_number, work_order_id)
    
    # Demo frontend integration
    demo_frontend_table_integration()
    
    print(f"\n🎉 MOBILE TABLE SEARCH TESTS COMPLETE!")
    print("=" * 60)
    print("✅ NEW FEATURES AVAILABLE:")
    print("   • GET /search/mobile/{mobile}/work-orders - Table format search")
    print("   • GET /search/mobile/{mobile}/work-orders/{id} - Get for editing")
    print("   • PUT /search/mobile/{mobile}/work-orders/{id} - Update via mobile")
    print("\n🎯 FRONTEND BENEFITS:")
    print("   • Table-ready data format")
    print("   • Built-in edit capabilities")
    print("   • Security verification (mobile ownership)")
    print("   • Status update options")
    print("   • Responsive table headers")
    print("=" * 60)

if __name__ == "__main__":
    main()
