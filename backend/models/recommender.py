import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from tmdbv3api import TMDb, Movie, Keyword
import os
from dotenv import load_dotenv
from utils.tmdb_client import TMDBClient

load_dotenv()

class MovieRecommender:
    def __init__(self, tmdb_client):
        self.tmdb_client = tmdb_client
        self.tmdb = TMDb()
        self.tmdb.api_key = os.getenv('TMDB_API_KEY')
        self.movie_api = Movie()
        self.keyword_api = Keyword()
        self.movies_df = None
        self.tfidf_matrix = None
        self.vectorizer = None
        
        self.mood_keywords = {
            'happy': ['comedy', 'feel-good', 'uplifting', 'family', 'adventure'],
            'sad': ['drama', 'emotional', 'tragedy', 'romance', 'melodrama'],
            'excited': ['action', 'adventure', 'thriller', 'sci-fi', 'fantasy'],
            'romantic': ['romance', 'drama', 'comedy', 'feel-good', 'romantic comedy'],
            'scared': ['horror', 'thriller', 'suspense', 'mystery', 'psychological'],
            'inspired': ['drama', 'biography', 'sports', 'documentary', 'inspirational'],
            'relaxed': ['comedy', 'animation', 'family', 'feel-good', 'light']
        }
        
        self.genre_mapping = {
            'action': 28,
            'comedy': 35,
            'drama': 18,
            'horror': 27,
            'romance': 10749,
            'sci-fi': 878,
            'thriller': 53
        }
        
    def fetch_movie_data(self, limit=1000):
        """Fetch movie data from TMDB and prepare it for recommendations"""
        movies = []
        
        # Fetch popular movies
        popular_movies = self.movie_api.popular()
        for movie in popular_movies:
            try:
                # Get detailed movie info
                details = self.movie_api.details(movie.id)
                
                # Get keywords
                keywords = self.movie_api.keywords(movie.id)
                keyword_names = [k.name for k in keywords.keywords]
                
                # Combine features for content-based filtering
                features = ' '.join([
                    ' '.join([g.name for g in details.genres]),
                    ' '.join(keyword_names),
                    details.overview
                ])
                
                movies.append({
                    'id': movie.id,
                    'title': movie.title,
                    'features': features,
                    'genres': [g.name for g in details.genres],
                    'keywords': keyword_names,
                    'overview': details.overview,
                    'poster_path': f"https://image.tmdb.org/t/p/w500{movie.poster_path}" if movie.poster_path else None,
                    'vote_average': movie.vote_average,
                    'release_date': movie.release_date,
                    'runtime': details.runtime
                })
            except Exception as e:
                print(f"Error fetching details for movie {movie.id}: {str(e)}")
                continue
                
            if len(movies) >= limit:
                break
                
        self.movies_df = pd.DataFrame(movies)
        return self.movies_df
        
    def prepare_recommender(self):
        """Prepare the TF-IDF matrix for recommendations"""
        if self.movies_df is None:
            self.fetch_movie_data()
            
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        
        # Create TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(self.movies_df['features'])
        
    def get_recommendations(self, movie_id=None, mood=None, genre=None):
        """Get movie recommendations based on movie ID, mood, or genre."""
        try:
            if movie_id:
                return self.tmdb_client.get_similar_movies(movie_id)
            elif mood:
                # Get mood-based recommendations
                mood_genres = {
                    'happy': [35, 10751],  # Comedy, Family
                    'sad': [18, 10749],    # Drama, Romance
                    'excited': [28, 12],   # Action, Adventure
                    'romantic': [10749, 35], # Romance, Comedy
                    'scared': [27, 53],    # Horror, Thriller
                    'inspired': [18, 99],  # Drama, Documentary
                    'relaxed': [35, 16]    # Comedy, Animation
                }
                
                if mood not in mood_genres:
                    return self.tmdb_client.get_popular_movies()
                
                movies = []
                for genre_id in mood_genres[mood]:
                    genre_movies = self.tmdb_client.get_movies_by_genre(genre_id)
                    movies.extend(genre_movies)
                
                # Remove duplicates and sort by popularity
                unique_movies = {movie['id']: movie for movie in movies}.values()
                sorted_movies = sorted(unique_movies, key=lambda x: x.get('vote_average', 0), reverse=True)
                return list(sorted_movies)[:10]
                
            elif genre:
                # Get genre-based recommendations
                genre_id = self.genre_mapping.get(genre.lower())
                if not genre_id:
                    return self.tmdb_client.get_popular_movies()
                
                movies = self.tmdb_client.get_movies_by_genre(genre_id)
                return movies[:10]
            else:
                # If no parameters provided, return popular movies
                return self.tmdb_client.get_popular_movies()
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            # Return popular movies as fallback
            return self.tmdb_client.get_popular_movies()

    def _get_content_based_recommendations(self, movie_id):
        """Get recommendations based on movie content similarity"""
        try:
            # Get the target movie details
            target_movie = self.tmdb_client.get_movie_details(movie_id)
            if not target_movie:
                return self._get_popular_movies()

            # Get similar movies from TMDB
            similar_movies = self.tmdb_client.get_similar_movies(movie_id)
            return similar_movies[:10]  # Return top 10 similar movies
        except Exception as e:
            print(f"Error in content-based recommendations: {str(e)}")
            return self._get_popular_movies()

    def _get_mood_based_recommendations(self, mood):
        """Get recommendations based on mood"""
        try:
            if mood not in self.mood_keywords:
                return self._get_popular_movies()

            # Map mood to TMDB genre IDs
            mood_genres = {
                'happy': [35, 10751],  # Comedy, Family
                'sad': [18, 10749],    # Drama, Romance
                'excited': [28, 12],   # Action, Adventure
                'romantic': [10749, 35], # Romance, Comedy
                'scared': [27, 53],    # Horror, Thriller
                'inspired': [18, 99],  # Drama, Documentary
                'relaxed': [35, 16]    # Comedy, Animation
            }

            # Get movies using TMDB discover API
            movies = []
            for genre_id in mood_genres.get(mood, []):
                genre_movies = self.tmdb_client.get_movies_by_genre(genre_id)
                movies.extend(genre_movies)

            # Remove duplicates and sort by popularity
            unique_movies = {movie['id']: movie for movie in movies}.values()
            sorted_movies = sorted(unique_movies, key=lambda x: x.get('vote_average', 0), reverse=True)

            return list(sorted_movies)[:10]  # Return top 10 mood-based movies
        except Exception as e:
            print(f"Error in mood-based recommendations: {str(e)}")
            return self._get_popular_movies()

    def _get_genre_based_recommendations(self, genre):
        """Get recommendations based on genre"""
        try:
            if genre not in self.genre_mapping:
                return self._get_popular_movies()

            # Get movies by genre from TMDB
            genre_id = self.genre_mapping[genre]
            movies = self.tmdb_client.get_movies_by_genre(genre_id)
            return movies[:10]  # Return top 10 genre-based movies
        except Exception as e:
            print(f"Error in genre-based recommendations: {str(e)}")
            return self._get_popular_movies()

    def _get_popular_movies(self):
        """Get popular movies as fallback"""
        try:
            return self.tmdb_client.get_popular_movies()[:10]
        except Exception as e:
            print(f"Error getting popular movies: {str(e)}")
            return []
        
    def get_mood_recommendations(self, mood, n_recommendations=5):
        """Get movie recommendations based on mood"""
        if self.tfidf_matrix is None:
            self.prepare_recommender()
            
        # Mood to keyword mapping
        mood_keywords = {
            'happy': ['comedy', 'feel-good', 'uplifting', 'funny', 'light-hearted'],
            'sad': ['drama', 'emotional', 'touching', 'heartfelt', 'melancholy'],
            'excited': ['action', 'adventure', 'thriller', 'suspense', 'exciting'],
            'romantic': ['romance', 'love', 'romantic', 'passion', 'relationship'],
            'scared': ['horror', 'scary', 'frightening', 'terrifying', 'suspense']
        }
        
        if mood not in mood_keywords:
            return []
            
        # Create a query string from mood keywords
        query = ' '.join(mood_keywords[mood])
        
        # Transform query to TF-IDF
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(
            query_vector,
            self.tfidf_matrix
        ).flatten()
        
        # Get indices of most similar movies
        similar_indices = similarity_scores.argsort()[::-1][:n_recommendations]
        
        # Get recommended movies
        recommendations = self.movies_df.iloc[similar_indices].to_dict('records')
        
        return recommendations
        
    def get_quiz_recommendations(self, preferences, n_recommendations=5):
        """Get movie recommendations based on quiz answers"""
        if self.tfidf_matrix is None:
            self.prepare_recommender()
            
        # Filter movies based on preferences
        filtered_movies = self.movies_df.copy()
        
        # Filter by genre
        if preferences.get('genre'):
            filtered_movies = filtered_movies[
                filtered_movies['genres'].apply(
                    lambda x: preferences['genre'].lower() in [g.lower() for g in x]
                )
            ]
            
        # Filter by mood
        if preferences.get('mood'):
            mood_keywords = {
                'happy': ['comedy', 'feel-good', 'uplifting'],
                'sad': ['drama', 'emotional', 'touching'],
                'excited': ['action', 'adventure', 'thriller'],
                'relaxed': ['comedy', 'drama', 'feel-good'],
                'thrilled': ['action', 'thriller', 'suspense']
            }
            
            if preferences['mood'] in mood_keywords:
                mood_terms = mood_keywords[preferences['mood']]
                filtered_movies = filtered_movies[
                    filtered_movies['keywords'].apply(
                        lambda x: any(term in [k.lower() for k in x] for term in mood_terms)
                    )
                ]
                
        # Filter by length
        if preferences.get('length'):
            if preferences['length'] == 'Short (< 90 min)':
                filtered_movies = filtered_movies[filtered_movies['runtime'] < 90]
            elif preferences['length'] == 'Medium (90-120 min)':
                filtered_movies = filtered_movies[
                    (filtered_movies['runtime'] >= 90) & 
                    (filtered_movies['runtime'] <= 120)
                ]
            elif preferences['length'] == 'Long (> 120 min)':
                filtered_movies = filtered_movies[filtered_movies['runtime'] > 120]
                
        # If no movies match the filters, return popular movies
        if len(filtered_movies) == 0:
            return self.movies_df.nlargest(n_recommendations, 'vote_average').to_dict('records')
            
        # Sort by rating and get top recommendations
        recommendations = filtered_movies.nlargest(n_recommendations, 'vote_average').to_dict('records')
        
        return recommendations

    def get_popular_movies(self):
        """Get popular movies as fallback"""
        try:
            return self.tmdb_client.get_popular_movies()[:10]
        except Exception as e:
            print(f"Error getting popular movies: {str(e)}")
            return [] 