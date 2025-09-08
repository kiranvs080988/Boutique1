"""
Test script for status endpoints - workflow and dropdown functionality.
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_status_options():
    """Test getting status options for dropdown"""
    print("Testing status options...")
    try:
        response = requests.get(f"{BASE_URL}/status/options")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status options retrieved:")
            for option in data:
                print(f"  - {option['label']} (value: {option['value']}, order: {option['order']})")
            return True
        else:
            print(f"✗ Status options failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Status options error: {e}")
        return False

def test_status_workflow():
    """Test getting complete workflow information"""
    print("\nTesting status workflow...")
    try:
        response = requests.get(f"{BASE_URL}/status/workflow")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status workflow retrieved:")
            print(f"  - Stages: {len(data['stages'])}")
            for stage in data['stages']:
                print(f"    Stage {stage['stage']}: {stage['name']} - {stage['statuses']}")
            print(f"  - Final states: {data['final_states']}")
            print(f"  - Active states: {data['active_states']}")
            return True
        else:
            print(f"✗ Status workflow failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Status workflow error: {e}")
        return False

def test_next_options():
    """Test getting next status options"""
    print("\nTesting next status options...")
    test_cases = [
        "Order Placed",
        "Started", 
        "Finished",
        "Delivered – Payment Pending",
        "Delivered - Fully Paid"
    ]
    
    success_count = 0
    for status in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/status/next-options/{status}")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Next options for '{status}': {len(data)} options")
                for option in data:
                    print(f"    → {option['label']}")
                success_count += 1
            else:
                print(f"✗ Next options for '{status}' failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Next options for '{status}' error: {e}")
    
    return success_count == len(test_cases)

def test_status_validation():
    """Test status validation"""
    print("\nTesting status validation...")
    test_cases = [
        ("Order Placed", True),
        ("Started", True),
        ("Invalid Status", False),
        ("Delivered - Fully Paid", True)
    ]
    
    success_count = 0
    for status, expected_valid in test_cases:
        try:
            response = requests.get(f"{BASE_URL}/status/validation/{status}")
            if response.status_code == 200:
                data = response.json()
                is_valid = data['is_valid']
                if is_valid == expected_valid:
                    print(f"✓ Validation for '{status}': {is_valid} (expected: {expected_valid})")
                    success_count += 1
                else:
                    print(f"✗ Validation for '{status}': {is_valid} (expected: {expected_valid})")
            else:
                print(f"✗ Validation for '{status}' failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Validation for '{status}' error: {e}")
    
    return success_count == len(test_cases)

def main():
    """Run all status endpoint tests"""
    print("=" * 60)
    print("Boutique Work Orders - Status Endpoints Tests")
    print("=" * 60)
    
    tests = [
        ("Status Options (Dropdown)", test_status_options),
        ("Status Workflow", test_status_workflow),
        ("Next Status Options", test_next_options),
        ("Status Validation", test_status_validation)
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
    print(f"Status Tests Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All status tests passed! Frontend dropdown integration ready.")
        print("\nStatus endpoints available:")
        print("  - GET /status/options - Status dropdown options")
        print("  - GET /status/workflow - Complete workflow information")
        print("  - GET /status/next-options/{current_status} - Valid next statuses")
        print("  - GET /status/validation/{status} - Status validation")
        print("\nWorkflow Order:")
        print("  1. Order Placed → 2. Started → 3. Finished → 4. Delivered")
    else:
        print("⚠️  Some status tests failed. Please check the server logs.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
