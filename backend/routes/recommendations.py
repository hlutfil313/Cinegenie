from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from models.ai_recommender import AIRecommender
from models.recommender import MovieRecommender
from utils.tmdb_client import TMDBClient
from datetime import datetime
import pytz

router = APIRouter()

# Initialize the recommenders
tmdb_client = TMDBClient()
movie_recommender = MovieRecommender(tmdb_client)
ai_recommender = AIRecommender(movie_recommender)

@router.post("/chat-recommendations")
async def get_chat_recommendations(user_input: str):
    """
    Get movie recommendations based on natural language input
    """
    try:
        recommendations = await ai_recommender.get_chat_recommendations(user_input)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contextual-recommendations")
async def get_contextual_recommendations(context: Dict[str, Any]):
    """
    Get movie recommendations based on contextual factors
    """
    try:
        # Add current time and date if not provided
        if 'time_of_day' not in context:
            current_time = datetime.now(pytz.UTC)
            context['time_of_day'] = current_time.strftime('%H:%M')
        
        recommendations = await ai_recommender.get_contextual_recommendations(context)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/social-recommendations/{user_id}")
async def get_social_recommendations(user_id: str, social_context: Dict[str, Any]):
    """
    Get movie recommendations based on social and cultural context
    """
    try:
        recommendations = await ai_recommender.get_social_recommendations(user_id, social_context)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep existing routes
@router.get("/mood/{mood}")
async def get_mood_recommendations(mood: str):
    """
    Get movie recommendations based on mood
    """
    try:
        recommendations = movie_recommender.get_recommendations(mood=mood)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genre/{genre}")
async def get_genre_recommendations(genre: str):
    """
    Get movie recommendations based on genre
    """
    try:
        recommendations = movie_recommender.get_recommendations(genre=genre)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{movie_id}")
async def get_similar_movies(movie_id: int):
    """
    Get similar movies based on a movie ID
    """
    try:
        recommendations = movie_recommender.get_recommendations(movie_id=movie_id)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 