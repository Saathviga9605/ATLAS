# Sample API Test Script
# Run with: python test_api.py

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_query_pan_logs():
    """Test RAG query about PAN in logs"""
    print("\n🔍 Testing RAG Query: PAN in logs...")
    
    payload = {
        "question": "Is PAN allowed in application logs?",
        "top_k": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/regulations/query",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_query_cvv_storage():
    """Test RAG query about CVV storage"""
    print("\n🔍 Testing RAG Query: CVV storage...")
    
    payload = {
        "question": "Can I store CVV values in the database?",
        "top_k": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/regulations/query",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_obligations():
    """Test get obligations endpoint"""
    print("\n🔍 Testing Get Obligations (CRITICAL only)...")
    
    response = requests.get(
        f"{BASE_URL}/regulations/obligations",
        params={"severity": "CRITICAL"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total obligations: {data['total']}")
    
    if data['obligations']:
        print(f"\nSample obligation:")
        print(json.dumps(data['obligations'][0], indent=2))

def test_statistics():
    """Test statistics endpoint"""
    print("\n🔍 Testing Statistics...")
    
    response = requests.get(f"{BASE_URL}/regulations/statistics")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_all():
    """Run all tests"""
    print("="*60)
    print("🚀 Running Regulatory Intelligence API Tests")
    print("="*60)
    
    try:
        test_health()
        test_query_pan_logs()
        test_query_cvv_storage()
        test_get_obligations()
        test_statistics()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    test_all()
