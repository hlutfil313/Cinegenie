#!/usr/bin/env python3
"""
Test script to check specific API endpoints
"""

import requests
import json

def test_api_endpoint(url, data=None, method='GET'):
    """Test a specific API endpoint"""
    try:
        if method == 'POST':
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        else:
            response = requests.get(url)
        
        print(f"Testing {method} {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', 'N/A')}")
            if 'debug_info' in result:
                print(f"Debug info: {result['debug_info']}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
                if 'debug_info' in error_data:
                    print(f"Debug info: {error_data['debug_info']}")
            except:
                print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Test all relevant API endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing CineGenie API Endpoints")
    print("=" * 40)
    
    # Test health check
    print("\n1. Health Check")
    test_api_endpoint(f"{base_url}/api/health")
    
    # Test popular movies
    print("\n2. Popular Movies")
    test_api_endpoint(f"{base_url}/api/popular")
    
    # Test AI recommendations with mood
    print("\n3. AI Recommendations (Mood)")
    test_api_endpoint(
        f"{base_url}/api/recommendations/ai",
        {"preferences": {"mood": "happy"}},
        "POST"
    )
    
    # Test AI recommendations with genre
    print("\n4. AI Recommendations (Genre)")
    test_api_endpoint(
        f"{base_url}/api/recommendations/ai",
        {"preferences": {"genres": ["action"]}},
        "POST"
    )
    
    # Test chat recommendations
    print("\n5. Chat Recommendations")
    test_api_endpoint(
        f"{base_url}/api/recommendations/chat-recommendations",
        {"user_input": "I want to watch an action movie"},
        "POST"
    )
    
    # Test mood recommendations
    print("\n6. Mood Recommendations")
    test_api_endpoint(f"{base_url}/api/recommendations/mood/happy")
    
    # Test genre recommendations
    print("\n7. Genre Recommendations")
    test_api_endpoint(f"{base_url}/api/recommendations/genre/action")

if __name__ == "__main__":
    main() 