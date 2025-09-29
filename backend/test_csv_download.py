#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def get_test_token():
    """Get a JWT token for testing"""
    try:
        # Use the provided credentials
        user = User.objects.get(username='vicente')
        print(f"Using existing user: {user.username}")
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return access_token
        
    except User.DoesNotExist:
        print("User 'vicente' not found")
        return None
    except Exception as e:
        print(f"Error creating token: {e}")
        return None

def test_csv_download():
    """Test CSV download functionality"""
    BASE_URL = 'http://localhost:8000/api'
    
    print("Getting JWT token...")
    token = get_test_token()
    if not token:
        print("Failed to get token")
        return
    
    print("Testing CSV download...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    
    # Test regular JSON request first
    print("\n1. Testing JSON request...")
    url = f"{BASE_URL}/analytics/advanced-demand/"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   JSON request -> HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response has {len(data.get('products', {}).get('all', []))} products")
        else:
            print(f"   Error: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test CSV request
    print("\n2. Testing CSV request...")
    try:
        params = {'format': 'csv'}
        csv_url = f"{url}?format=csv"
        print(f"   Full URL: {csv_url}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"   CSV request -> HTTP {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'text/csv' in content_type:
                print(f"   ✓ Got CSV response ({len(response.content)} bytes)")
                # Save to file for inspection
                with open('test_download.csv', 'wb') as f:
                    f.write(response.content)
                print(f"   ✓ Saved to test_download.csv")
            else:
                print(f"   ⚠ Expected CSV but got: {content_type}")
                print(f"   Response preview: {response.text[:200]}...")
        elif response.status_code == 404:
            print(f"   404 Error - URL not found")
            print(f"   This suggests the endpoint doesn't handle ?format=csv")
        else:
            print(f"   Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with direct URL construction
    print("\n3. Testing CSV with manual URL...")
    try:
        manual_csv_url = f"{BASE_URL}/analytics/advanced-demand/?format=csv"
        print(f"   Manual URL: {manual_csv_url}")
        response = requests.get(manual_csv_url, headers=headers, timeout=10)
        print(f"   Manual CSV request -> HTTP {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test the FIXED frontend approach
    print("\n4. Testing FIXED frontend approach (no trailing slash)...")
    try:
        # This is what the frontend should use now
        fixed_url = f"{BASE_URL}/analytics/advanced-demand"
        params = {'format': 'csv'}
        
        print(f"   URL: {fixed_url}")
        print(f"   Params: {params}")
        
        response = requests.get(fixed_url, headers=headers, params=params, timeout=10)
        print(f"   -> HTTP {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")
            
            if 'text/csv' in content_type:
                print(f"   [SUCCESS] Got CSV response ({len(response.content)} bytes)")
                
                # Save CSV for inspection
                with open('working_download.csv', 'wb') as f:
                    f.write(response.content)
                print(f"   [SUCCESS] Saved to working_download.csv")
                
                # Show first few lines
                csv_text = response.content.decode('utf-8')
                lines = csv_text.split('\n')[:5]
                print(f"   Preview:")
                for i, line in enumerate(lines):
                    print(f"     {i+1}: {line[:100]}...")
                    
            else:
                print(f"   [ERROR] Expected CSV but got: {content_type}")
                # Show HTML content for debugging
                print(f"   [DEBUG] Response content: {response.text[:300]}...")
        else:
            print(f"   [ERROR] HTTP {response.status_code}: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   [ERROR] Exception: {e}")

if __name__ == '__main__':
    test_csv_download()
