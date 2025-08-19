#!/usr/bin/env python3
"""
Quick test script to verify the bulk visit endpoint is working correctly.
Run this from the backend directory after deploying the changes.
"""

import requests
import json
from datetime import datetime

# Test payload for bulk visit save
test_payload = {
    "visit": {
        "location": 1,  # Replace with actual location ID
        "visit_date": datetime.now().isoformat(),
        "notes": "Test bulk save",
        "user": 1  # Replace with actual user ID
    },
    "machine_restocks": [
        {
            "machine": 1,  # Replace with actual machine ID
            "notes": "",
            "restock_entries": [
                {
                    "product": 1,  # Replace with actual product ID
                    "stock_before": 5,
                    "discarded": 1,
                    "restocked": 10
                }
            ]
        }
    ]
}

def test_bulk_endpoint(base_url, token):
    """Test the bulk visit save endpoint"""
    url = f"{base_url}/api/visits/bulk-save/"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"Testing bulk endpoint: {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Bulk endpoint working correctly!")
            return True
        else:
            print(f"❌ Bulk endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    # Replace these with your actual values
    BASE_URL = "https://tropical-vending-production.up.railway.app"  # Your Railway URL
    TOKEN = "your-jwt-token-here"  # Get from login response
    
    print("🧪 Testing Bulk Visit Save Endpoint")
    print("=" * 50)
    
    success = test_bulk_endpoint(BASE_URL, TOKEN)
    
    if success:
        print("\n🎉 Optimization working correctly!")
        print("Your field personnel should now experience much faster visit saving.")
    else:
        print("\n⚠️  Please check the endpoint configuration and try again.")
        print("Make sure to:")
        print("1. Deploy the latest changes to Railway")
        print("2. Apply database migrations")
        print("3. Use valid location, machine, and product IDs in the test")
