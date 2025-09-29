#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Add the backend directory to the path
sys.path.append('/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vendingapp.settings')
django.setup()

from django.urls import reverse
from django.test import RequestFactory
from core.views import AdvancedDemandAnalyticsView

def test_url_resolution():
    print("Testing URL resolution...")
    
    # Test URL reverse
    try:
        url = reverse('advanced-demand-analytics')
        print(f"[OK] URL reverse successful: {url}")
    except Exception as e:
        print(f"[FAIL] URL reverse failed: {e}")
    
    # Test view class exists
    try:
        view_class = AdvancedDemandAnalyticsView
        print(f"[OK] View class exists: {view_class.__name__}")
    except Exception as e:
        print(f"[FAIL] View class error: {e}")
    
    # Test request handling
    try:
        factory = RequestFactory()
        request = factory.get('/api/analytics/advanced-demand/')
        
        view = AdvancedDemandAnalyticsView.as_view()
        print(f"[OK] View instance created successfully")
        
        # Note: We can't actually call the view without proper authentication setup
        # but we can verify it exists and is callable
        
    except Exception as e:
        print(f"[FAIL] Request handling error: {e}")

if __name__ == '__main__':
    test_url_resolution()
