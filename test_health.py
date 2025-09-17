#!/usr/bin/env python3
"""
Simple test script to check if the health endpoint works
"""

import os
import sys
from web.dashboard import WebDashboard

def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    
    try:
        # Create dashboard without environment variables
        dashboard = WebDashboard()
        
        # Create test client
        client = dashboard.app.test_client()
        
        # Test health endpoint
        response = client.get('/health')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            return True
        else:
            print("❌ Health endpoint failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False

if __name__ == "__main__":
    success = test_health_endpoint()
    sys.exit(0 if success else 1)
