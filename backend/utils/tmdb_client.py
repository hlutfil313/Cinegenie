from tmdbv3api import TMDb, Movie
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

class TMDBClient:
    def __init__(self, api_key: str):
        """Initialize TMDB client with API key"""
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.genre_mapping = {
            'action': 28,
            'adventure': 12,
            'animation': 16,
            'comedy': 35,
            'crime': 80,
            'documentary': 99,
            'drama': 18,
            'family': 10751,
            'fantasy': 14,
            'history': 36,
            'horror': 27,
            'music': 10402,
            'mystery': 9648,
            'romance': 10749,
            'science fiction': 878,
            'tv movie': 10770,
            'thriller': 53,
            'war': 10752,
            'western': 37
        }
        self.mood_mapping = {
            'feel-good': [35, 10751],  # Comedy, Family
            'uplifting': [18, 10751],  # Drama, Family
            'heartwarming': [10749, 10751],  # Romance, Family
            'nostalgic': [18, 10751],  # Drama, Family
            'exciting': [28, 12, 53],  # Action, Adventure, Thriller
            'relaxing': [18, 10749],  # Drama, Romance
            'thought-provoking': [18, 9648],  # Drama, Mystery
            'scary': [27, 53],  # Horror, Thriller
            'romantic': [10749],  # Romance
            'funny': [35],  # Comedy
            'adventurous': [12, 28],  # Adventure, Action
            'mysterious': [9648, 53],  # Mystery, Thriller
            'dramatic': [18],  # Drama
            'fantastical': [14, 12],  # Fantasy, Adventure
            'historical': [36, 18],  # History, Drama
            'suspenseful': [53, 9648],  # Thriller, Mystery
            'emotional': [18, 10749],  # Drama, Romance
            'inspiring': [18, 10751],  # Drama, Family
            'dark': [27, 53, 80],  # Horror, Thriller, Crime
            'lighthearted': [35, 10751]  # Comedy, Family
        }
        self.tmdb = TMDb()
        self.tmdb.api_key = self.api_key
        self.tmdb.language = 'en-US'
        self.movie_api = Movie()
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        
        if not self.api_key:
            logger.error("TMDB API key not found in environment variables")
            raise ValueError("TMDB API key not found")
        
        logger.info(f"TMDB client initialized with API key: {self.api_key[:5]}...")

    def _make_request(self, endpoint, params=None):
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            logger.debug(f"Making request to: {url}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return None

    def search_movies(self, query):
        logger.info(f"Searching for movies with query: {query}")
        data = self._make_request('search/movie', {'query': query})
        
        if not data or 'results' not in data:
            logger.error(f"No results found for query: {query}")
            return []
        
        movies = []
        for movie in data['results']:
            movie_data = self.get_movie_details(movie['id'])
            if movie_data:
                movies.append(movie_data)
        
        logger.info(f"Found {len(movies)} movies for query: {query}")
        return movies

    def get_movie_details(self, movie_id):
        logger.info(f"Getting details for movie ID: {movie_id}")
        try:
            data = self._make_request(f'movie/{movie_id}', {
                'append_to_response': 'credits'
            })
            
            if not data:
                logger.error(f"No data found for movie ID: {movie_id}")
                return None
            
            # Get cast information
            cast = []
            if 'credits' in data and 'cast' in data['credits']:
                for actor in data['credits']['cast'][:5]:  # Get top 5 cast members
                    cast.append({
                        'name': actor['name'],
                        'character': actor['character'],
                        'profile_path': actor['profile_path'] if actor['profile_path'] else None
                    })
            
            return {
                'id': data['id'],
                'title': data['title'],
                'overview': data['overview'],
                'poster_path': data.get('poster_path'),  # Return just the path
                'release_date': data.get('release_date'),
                'vote_average': data.get('vote_average'),
                'runtime': data.get('runtime', 0),
                'genres': [genre['name'] for genre in data.get('genres', [])],
                'credits': {
                    'cast': cast
                }
            }
        except Exception as e:
            logger.error(f"Error getting movie details: {str(e)}")
            return None

    def get_popular_movies(self):
        logger.info("Getting popular movies")
        data = self._make_request('movie/popular')
        
        if not data or 'results' not in data:
            logger.error("No popular movies found")
            return []
        
        movies = []
        for movie in data['results']:
            movie_data = self.get_movie_details(movie['id'])
            if movie_data:
                movies.append(movie_data)
        
        logger.info(f"Found {len(movies)} popular movies")
        return movies

    def get_trending_movies(self, time_window='day'):
        logger.info(f"Getting trending movies for time window: {time_window}")
        data = self._make_request(f'trending/movie/{time_window}')
        
        if not data or 'results' not in data:
            logger.error(f"No trending movies found for time window: {time_window}")
            return []
        
        movies = []
        for movie in data['results']:
            movie_data = self.get_movie_details(movie['id'])
            if movie_data:
                movies.append(movie_data)
        
        logger.info(f"Found {len(movies)} trending movies")
        return movies

    def get_new_releases(self):
        """Get new movie releases from TMDB."""
        try:
            print("Fetching new releases")
            results = self.movie_api.upcoming()
            movies = [{
                'id': movie.id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_path': movie.poster_path,
                'release_date': movie.release_date,
                'vote_average': movie.vote_average
            } for movie in results]
            print(f"Found {len(movies)} new releases")
            return movies
        except Exception as e:
            print(f"Error fetching new releases: {str(e)}")
            return []

    def get_similar_movies(self, movie_id):
        logger.info(f"Getting similar movies for movie ID: {movie_id}")
        data = self._make_request(f'movie/{movie_id}/similar')
        
        if not data or 'results' not in data:
            logger.error(f"No similar movies found for movie ID: {movie_id}")
            return []
        
        movies = []
        for movie in data['results'][:5]:  # Limit to 5 similar movies
            movie_data = self.get_movie_details(movie['id'])
            if movie_data:
                movies.append(movie_data)
        
        logger.info(f"Found {len(movies)} similar movies")
        return movies

    def get_movies_by_genre(self, genre_id, page=1):
        logger.info(f"Getting movies for genre ID: {genre_id}")
        try:
            data = self._make_request('discover/movie', {
                'with_genres': genre_id,
                'page': page,
                'sort_by': 'popularity.desc'
            })
            
            if not data or 'results' not in data:
                logger.error(f"No movies found for genre ID: {genre_id}")
                return []
            
            movies = []
            for movie in data['results'][:10]:  # Limit to 10 movies
                try:
                    # Get genre names from genre IDs
                    genre_names = []
                    for gid in movie.get('genre_ids', []):
                        for name, id in self.genre_mapping.items():
                            if id == gid:
                                genre_names.append(name.title())
                                break
                    
                    movie_data = {
                        'id': movie['id'],
                        'title': movie['title'],
                        'overview': movie['overview'],
                        'poster_path': movie.get('poster_path'),
                        'release_date': movie.get('release_date'),
                        'vote_average': movie.get('vote_average', 0),
                        'genres': genre_names
                    }
                    movies.append(movie_data)
                except Exception as e:
                    logger.error(f"Error processing movie data: {str(e)}")
                    continue
            
            logger.info(f"Found {len(movies)} movies for genre ID: {genre_id}")
            return movies
            
        except Exception as e:
            logger.error(f"Error getting movies by genre: {str(e)}")
            return []

    def get_movie_of_the_day(self):
        logger.info("Getting movie of the day")
        popular_movies = self.get_popular_movies()
        if not popular_movies:
            logger.error("No popular movies available for movie of the day")
            return None
        
        # Get the first movie from popular movies
        movie = popular_movies[0]
        logger.info(f"Selected movie of the day: {movie['title']}")
        return movie

    def get_movies_by_mood(self, mood):
        """Get movies based on mood using genre combinations."""
        logger.info(f"Getting movies for mood: {mood}")
        
        if mood not in self.mood_mapping:
            logger.error(f"Invalid mood: {mood}")
            return []
        
        genre_ids = self.mood_mapping[mood]
        movies = []
        
        for genre_id in genre_ids:
            data = self._make_request('discover/movie', {
                'with_genres': genre_id,
                'sort_by': 'popularity.desc',
                'page': 1
            })
            
            if data and 'results' in data:
                for movie in data['results']:
                    movie_data = self.get_movie_details(movie['id'])
                    if movie_data and movie_data not in movies:
                        movies.append(movie_data)
        
        # Sort by popularity and limit to 10 movies
        movies = sorted(movies, key=lambda x: x.get('vote_average', 0), reverse=True)[:10]
        logger.info(f"Found {len(movies)} movies for mood: {mood}")
        return movies

    def get_movies_by_genre_name(self, genre_name):
        """Get movies by genre name."""
        logger.info(f"Getting movies for genre: {genre_name}")
        
        genre_id = self.genre_mapping.get(genre_name.lower())
        if not genre_id:
            logger.error(f"Invalid genre: {genre_name}")
            return []
        
        return self.get_movies_by_genre(genre_id) 