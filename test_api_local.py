#!/usr/bin/env python3
"""
Test script to verify API endpoints work correctly
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
BASE_URL = "http://127.0.0.1:5000/api"

def test_endpoint(endpoint, description):
    """Test an API endpoint and print results"""
    print(f"\n🔍 Testing {description}...")
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                if 'movies' in data:
                    print(f"✅ Success! Found {len(data['movies'])} movies")
                    if data['movies']:
                        print(f"   First movie: {data['movies'][0].get('title', 'Unknown')}")
                elif 'movie' in data:
                    print(f"✅ Success! Movie: {data['movie'].get('title', 'Unknown')}")
                else:
                    print("✅ Success!")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("🚀 Testing CineGenie API Endpoints")
    print("=" * 50)
    
    # Test environment variables
    print("\n🔧 Environment Variables:")
    tmdb_key = os.getenv('TMDB_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    print(f"TMDB_API_KEY: {'✅ Set' if tmdb_key else '❌ Missing'}")
    print(f"GOOGLE_API_KEY: {'✅ Set' if google_key else '❌ Missing'}")
    
    # Test endpoints
    test_endpoint("health", "Health Check")
    test_endpoint("popular", "Popular Movies")
    test_endpoint("new-releases", "New Releases")
    test_endpoint("movie-of-the-day", "Movie of the Day")
    test_endpoint("trending", "Trending Movies")
    
    print("\n" + "=" * 50)
    print("🏁 Testing Complete!")

if __name__ == "__main__":
    main() 