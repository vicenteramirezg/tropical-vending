#!/usr/bin/env python
import os
import sys
import django
import requests

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

# Test different endpoints
BASE_URL = 'http://localhost:8000/api'

endpoints_to_test = [
    '/locations/',  # Working ViewSet
    '/machines/',   # Working ViewSet  
    '/profile/',    # Working APIView
    '/dashboard/',  # Analytics APIView
    '/analytics/stock-levels/',  # Analytics APIView
    '/analytics/demand/',  # Analytics APIView
    '/analytics/revenue-profit/',  # Analytics APIView
    '/analytics/advanced-demand/',  # Failing APIView
]

def test_endpoints():
    print("Testing endpoints without authentication...")
    print("-" * 80)
    
    # Headers that match what the frontend would send
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    
    for endpoint in endpoints_to_test:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"{endpoint:<35} -> HTTP {response.status_code}")
            
            # If 404, that means the URL pattern isn't found
            if response.status_code == 404:
                print(f"  *** 404 ERROR - URL pattern not found! ***")
            elif response.status_code == 401:
                print(f"  -> Authentication required (expected)")
            elif response.status_code == 200:
                print(f"  -> Success (no auth required)")
            elif response.status_code == 400:
                print(f"  -> Bad Request - checking response content...")
                try:
                    print(f"      Response: {response.text[:200]}...")
                except:
                    print(f"      Could not decode response")
            else:
                print(f"  -> Unexpected status: {response.status_code}")
                try:
                    print(f"      Response: {response.text[:200]}...")
                except:
                    print(f"      Could not decode response")
                
        except requests.exceptions.RequestException as e:
            print(f"{endpoint:<35} -> ERROR: {str(e)}")
    
    print("-" * 80)

if __name__ == '__main__':
    test_endpoints()
