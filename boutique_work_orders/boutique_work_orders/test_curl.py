import requests
import json

# Test the exact curl command that was failing
url = "http://localhost:8000/work-orders/"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
data = {
    "expected_delivery_date": "2025-09-07T10:12:26.169Z",
    "description": "Weddeding",
    "notes": "string",
    "status": "Order Placed",
    "advance_paid": 0,
    "total_estimate": 0,
    "actual_amount": 0,
    "due_cleared": False,
    "client_id": 12345678,
    "client_name": "Shikha",
    "client_mobile": "1791732880",
    "client_email": "kiranvs@ymail.com",
    "client_address": "TRAE"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    if response.status_code == 200:
        print("✅ SUCCESS!")
        print(f"Response: {response.json()}")
    else:
        print("❌ FAILED!")
        print(f"Error: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
