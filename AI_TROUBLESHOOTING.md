# AI Recommendation Troubleshooting Guide

## Common Issues and Solutions

### 1. "AI service not available" Error

**Problem**: The AI chat feature is not working and shows "AI service not available"

**Solution**: 
- You need to set up a Google API key for Gemini AI
- Get your API key from: https://makersuite.google.com/app/apikey
- Set the environment variable: `GOOGLE_API_KEY=your_api_key_here`

### 2. "No recommendations found" Error

**Problem**: The system can't find movie recommendations

**Possible Causes**:
- TMDB API key is missing or invalid
- Network connectivity issues
- Invalid genre/mood parameters

**Solution**:
- Check if TMDB_API_KEY is set correctly
- Verify internet connection
- Try different mood/genre selections

### 3. Chat Recommendations Not Working

**Problem**: The chat interface doesn't respond to user input

**Debug Steps**:
1. Check browser console for JavaScript errors
2. Check server logs for backend errors
3. Verify both TMDB_API_KEY and GOOGLE_API_KEY are set

### 4. Environment Variables Setup

Create a `.env` file in the backend directory with:

```
TMDB_API_KEY=your_tmdb_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

### 5. API Key Sources

- **TMDB API Key**: https://www.themoviedb.org/settings/api
- **Google API Key**: https://makersuite.google.com/app/apikey

### 6. Testing the Setup

1. Start the server: `python backend/app.py`
2. Check the logs for initialization messages
3. Look for these success messages:
   - "TMDB_API_KEY loaded successfully"
   - "GOOGLE_API_KEY loaded successfully"
   - "Successfully initialized Gemini model"

### 7. Fallback Behavior

If AI features are unavailable, the system will:
- Show popular movies instead of AI recommendations
- Display helpful error messages
- Continue to work with mood/genre-based recommendations

### 8. Debug Information

The system now provides detailed debug information in:
- Server logs (check console output)
- Browser console (press F12 to open developer tools)
- API responses (check Network tab in developer tools)

### 9. Common Error Messages

- `"GOOGLE_API_KEY not found"` → Set up Google API key
- `"TMDB_API_KEY not found"` → Set up TMDB API key
- `"No recommendations found"` → Try different preferences
- `"AI service not available"` → Check Google API key configuration

### 10. Getting Help

If you're still having issues:
1. Check the server logs for detailed error messages
2. Verify all API keys are correctly set
3. Test with simple requests first (e.g., "action movies")
4. Check browser console for frontend errors 