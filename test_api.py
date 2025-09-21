#!/usr/bin/env python3
"""
Test script to verify the Flask backend is working correctly
"""

import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

def test_api_endpoints():
    """Test all Flask API endpoints"""
    print("🧪 Testing Flask API endpoints...")
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Health check: FAILED (Error: {e})")
    
    # Test status endpoint
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Status endpoint: PASSED")
            data = response.json()
            print(f"   Last update: {data.get('last_update', 'None')}")
            print(f"   Scheduler running: {data.get('scheduler_running', False)}")
        else:
            print(f"❌ Status endpoint: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Status endpoint: FAILED (Error: {e})")
    
    # Test home endpoint
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Home endpoint: PASSED")
            data = response.json()
            print(f"   API Version: {data.get('version', 'Unknown')}")
        else:
            print(f"❌ Home endpoint: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Home endpoint: FAILED (Error: {e})")
    
    # Test earnings endpoint
    try:
        response = requests.get(f"{BASE_URL}/earnings", timeout=5)
        if response.status_code == 200:
            print("✅ Earnings endpoint: PASSED")
            data = response.json()
            print(f"   Total companies: {data.get('total_companies', 0)}")
        elif response.status_code == 404:
            print("⚠️  Earnings endpoint: No data available yet (expected for first run)")
        else:
            print(f"❌ Earnings endpoint: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Earnings endpoint: FAILED (Error: {e})")
    
    # Test sentiment endpoint
    try:
        response = requests.get(f"{BASE_URL}/sentiment", timeout=5)
        if response.status_code == 200:
            print("✅ Sentiment endpoint: PASSED")
            data = response.json()
            print(f"   Total companies analyzed: {data.get('total_companies_analyzed', 0)}")
        elif response.status_code == 404:
            print("⚠️  Sentiment endpoint: No data available yet (expected for first run)")
        else:
            print(f"❌ Sentiment endpoint: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Sentiment endpoint: FAILED (Error: {e})")

def test_manual_update():
    """Test manual update trigger"""
    print("\n🔄 Testing manual update trigger...")
    
    try:
        response = requests.post(f"{BASE_URL}/update", timeout=10)
        if response.status_code == 200:
            print("✅ Manual update trigger: PASSED")
            print("   Update triggered successfully")
        elif response.status_code == 409:
            print("⚠️  Manual update trigger: Update already in progress")
        else:
            print(f"❌ Manual update trigger: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Manual update trigger: FAILED (Error: {e})")

if __name__ == "__main__":
    print("🚀 Starting Flask Backend API Tests")
    print("="*50)
    
    # Wait a moment for server to start
    print("⏳ Waiting for Flask server to start...")
    time.sleep(3)
    
    # Run tests
    test_api_endpoints()
    test_manual_update()
    
    print("\n" + "="*50)
    print("✅ Flask Backend Tests Complete!")
    print("\n📚 API Documentation:")
    print("  - GET  /          - API information")
    print("  - GET  /status    - Update status")
    print("  - GET  /health    - Health check")
    print("  - GET  /earnings  - Current earnings data")
    print("  - GET  /sentiment - Sentiment analysis results")
    print("  - GET  /companies - Companies with sentiment scores")
    print("  - GET  /logs      - Recent log entries")
    print("  - POST /update    - Trigger manual update")
    print("\n🌐 Flask server should be running at http://127.0.0.1:5000")