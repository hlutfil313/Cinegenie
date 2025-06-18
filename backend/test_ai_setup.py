#!/usr/bin/env python3
"""
Test script to diagnose AI recommendation setup issues
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are set correctly"""
    print("=== Environment Variables Test ===")
    
    # Load .env file if it exists
    load_dotenv()
    
    # Check TMDB API key
    tmdb_key = os.getenv('TMDB_API_KEY')
    if tmdb_key:
        print(f"✅ TMDB_API_KEY: Found (length: {len(tmdb_key)})")
    else:
        print("❌ TMDB_API_KEY: Not found")
    
    # Check Google API key
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key:
        print(f"✅ GOOGLE_API_KEY: Found (length: {len(google_key)})")
    else:
        print("❌ GOOGLE_API_KEY: Not found")
    
    return bool(tmdb_key), bool(google_key)

def test_tmdb_connection():
    """Test TMDB API connection"""
    print("\n=== TMDB API Connection Test ===")
    
    try:
        from utils.tmdb_client import TMDBClient
        api_key = os.getenv('TMDB_API_KEY')
        if not api_key:
            print("❌ Cannot test TMDB - no API key")
            return False
        
        client = TMDBClient(api_key)
        movies = client.get_popular_movies()
        
        if movies and len(movies) > 0:
            print(f"✅ TMDB API: Connected successfully (got {len(movies)} movies)")
            return True
        else:
            print("❌ TMDB API: No movies returned")
            return False
            
    except Exception as e:
        print(f"❌ TMDB API: Error - {str(e)}")
        return False

def test_ai_setup():
    """Test AI recommender setup"""
    print("\n=== AI Recommender Setup Test ===")
    
    try:
        from models.ai_recommender import AIRecommender
        from models.movie_recommender import MovieRecommender
        from utils.tmdb_client import TMDBClient
        
        api_key = os.getenv('TMDB_API_KEY')
        if not api_key:
            print("❌ Cannot test AI - no TMDB API key")
            return False
        
        tmdb_client = TMDBClient(api_key)
        movie_recommender = MovieRecommender(tmdb_client)
        ai_recommender = AIRecommender(movie_recommender)
        
        if hasattr(ai_recommender, 'model') and ai_recommender.model:
            print("✅ AI Recommender: Initialized successfully")
            return True
        else:
            print("❌ AI Recommender: Model not available (check GOOGLE_API_KEY)")
            return False
            
    except Exception as e:
        print(f"❌ AI Recommender: Error - {str(e)}")
        return False

def main():
    """Run all tests"""
    print("CineGenie AI Setup Diagnostic Tool")
    print("=" * 40)
    
    # Test environment variables
    tmdb_ok, google_ok = test_environment()
    
    # Test TMDB connection
    tmdb_connected = test_tmdb_connection()
    
    # Test AI setup
    ai_ok = test_ai_setup()
    
    # Summary
    print("\n=== Summary ===")
    if tmdb_ok and tmdb_connected:
        print("✅ TMDB: Working correctly")
    else:
        print("❌ TMDB: Issues detected")
    
    if google_ok and ai_ok:
        print("✅ AI Features: Working correctly")
    else:
        print("❌ AI Features: Issues detected")
    
    if not google_ok:
        print("\nTo fix AI issues:")
        print("1. Get a Google API key from: https://makersuite.google.com/app/apikey")
        print("2. Set GOOGLE_API_KEY environment variable")
        print("3. Restart the application")
    
    if not tmdb_ok:
        print("\nTo fix TMDB issues:")
        print("1. Get a TMDB API key from: https://www.themoviedb.org/settings/api")
        print("2. Set TMDB_API_KEY environment variable")
        print("3. Restart the application")

if __name__ == "__main__":
    main() 