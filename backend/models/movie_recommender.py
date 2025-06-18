from typing import List, Dict, Any
from utils.tmdb_client import TMDBClient
import logging

logger = logging.getLogger(__name__)

class MovieRecommender:
    def __init__(self, tmdb_client: TMDBClient):
        """Initialize the movie recommender with TMDB client"""
        if tmdb_client is None:
            raise ValueError("tmdb_client must be provided to MovieRecommender. This is required for mood and genre mapping.")
        self.tmdb_client = tmdb_client
        self.genre_mapping = tmdb_client.genre_mapping
        self.mood_mapping = tmdb_client.mood_mapping
        self.user_model = None

    def get_recommendations(self, genre: str = None, mood: str = None, year: int = None) -> List[Dict[str, Any]]:
        """Get movie recommendations based on genre, mood, or year"""
        try:
            if genre:
                genre_id = self.genre_mapping.get(genre.lower())
                if not genre_id:
                    logger.warning(f"Invalid genre: {genre}")
                    return []
                return self.tmdb_client.get_movies_by_genre(genre_id)
            elif mood:
                mood_genres = self.mood_mapping.get(mood.lower())
                if not mood_genres:
                    logger.warning(f"Invalid mood: {mood}")
                    return []
                # Get movies for each genre in the mood and combine them
                all_movies = []
                for genre_id in mood_genres:
                    movies = self.tmdb_client.get_movies_by_genre(genre_id)
                    all_movies.extend(movies)
                return all_movies
            elif year:
                return self.tmdb_client.get_movies_by_year(year)
            else:
                return self.tmdb_client.get_popular_movies()
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

    def get_popular_movies(self) -> List[Dict[str, Any]]:
        """Get popular movies"""
        try:
            return self.tmdb_client.get_popular_movies()
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            return []

    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific movie"""
        try:
            return self.tmdb_client.get_movie_details(movie_id)
        except Exception as e:
            logger.error(f"Error getting movie details: {str(e)}")
            return {} 