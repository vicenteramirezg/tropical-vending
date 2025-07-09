#!/usr/bin/env python3
"""
Test script to verify the wholesale purchase API endpoint works correctly
after the serializer fix.
"""

import requests
import json
from datetime import datetime

def test_wholesale_purchase_api():
    """Test the wholesale purchase API endpoint"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/wholesale-purchases/"
    
    # First, let's get available products and suppliers
    try:
        products_response = requests.get(f"{base_url}/api/products/")
        suppliers_response = requests.get(f"{base_url}/api/suppliers/")
        
        if products_response.status_code == 200 and suppliers_response.status_code == 200:
            products = products_response.json()
            suppliers = suppliers_response.json()
            
            if products and suppliers:
                product_id = products[0]['id']
                supplier_id = suppliers[0]['id']
                
                print(f"Using product ID: {product_id}")
                print(f"Using supplier ID: {supplier_id}")
                
                # Test data that previously caused the error
                test_data = {
                    'product': product_id,
                    'supplier': supplier_id,
                    'quantity': 10,
                    'cost_per_unit': '1.50',
                    'purchase_date': datetime.now().isoformat(),
                    'notes': 'API test purchase'
                }
                
                print(f"Sending test data: {json.dumps(test_data, indent=2)}")
                
                # Make the POST request
                response = requests.post(
                    endpoint, 
                    json=test_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"Response status: {response.status_code}")
                print(f"Response data: {json.dumps(response.json(), indent=2)}")
                
                if response.status_code == 201:
                    print("✅ API test successful!")
                    
                    # Clean up - delete the test purchase
                    purchase_id = response.json()['id']
                    delete_response = requests.delete(f"{endpoint}{purchase_id}/")
                    if delete_response.status_code == 204:
                        print("✅ Test purchase cleaned up")
                    
                    return True
                else:
                    print(f"❌ API test failed with status {response.status_code}")
                    return False
            else:
                print("❌ No products or suppliers found for testing")
                return False
        else:
            print(f"❌ Failed to get products or suppliers: {products_response.status_code}, {suppliers_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        return False

if __name__ == "__main__":
    print("Testing wholesale purchase API endpoint...\n")
    success = test_wholesale_purchase_api()
    
    if success:
        print("\n🎉 API test completed successfully!")
    else:
        print("\n❌ API test failed. Please check the output above.") 