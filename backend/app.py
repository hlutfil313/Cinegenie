from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from utils.tmdb_client import TMDBClient
from models.recommender import MovieRecommender
from models.user import User
from models.ai_recommender import AIRecommender
import os
from dotenv import load_dotenv
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check if API key is loaded
api_key = os.getenv('TMDB_API_KEY')
if not api_key:
    logger.error("TMDB_API_KEY not found in environment variables!")
else:
    logger.info("TMDB_API_KEY loaded successfully")

app = Flask(__name__, 
    static_folder='../static',
    template_folder='..'
)
CORS(app)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize clients
try:
    user_model = User()  # Initialize User model first
    tmdb_client = TMDBClient(api_key)  # Pass the api_key to TMDBClient
    recommender = MovieRecommender(tmdb_client)
    ai_recommender = AIRecommender(recommender)
    logger.info("Clients initialized successfully")
except Exception as e:
    logger.error(f"Error initializing clients: {str(e)}")
    raise  # Re-raise the exception to prevent the app from starting with uninitialized clients

# Register endpoint
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not all([email, password, name]):
            return jsonify({
                "success": False,
                "error": "All fields are required"
            }), 400

        if user_model.create_user(email, password, name):
            return jsonify({
                "success": True,
                "message": "User registered successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Email already exists"
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                "success": False,
                "error": "Email and password are required"
            }), 400

        user = user_model.verify_user(email, password)
        if user:
            session['user'] = user
            return jsonify({
                "success": True,
                "user": user
            })
        else:
            return jsonify({
                "success": False,
                "error": "Invalid email or password"
            }), 401

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Logout endpoint
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })

# Check authentication status
@app.route('/api/auth/status')
def auth_status():
    user = session.get('user')
    return jsonify({
        "success": True,
        "authenticated": bool(user),
        "user": user
    })

# Serve HTML pages
@app.route('/')
def index():
    return send_from_directory('..', 'index.html')

@app.route('/homepage')
def homepage():
    return send_from_directory('..', 'homepage.html')

@app.route('/trending')
def trending():
    return send_from_directory('..', 'trending.html')

@app.route('/new-releases')
def new_releases():
    return send_from_directory('..', 'new-releases.html')

@app.route('/recommendation')
def recommendation():
    return send_from_directory('..', 'recommendation.html')

@app.route('/my_list')
def my_list():
    return send_from_directory('..', 'my_list.html')

@app.route('/movie-details')
def movie_details():
    return send_from_directory('..', 'movie-details.html')

@app.route('/search')
def search_page():
    return send_from_directory('..', 'search.html')

# API endpoints
@app.route('/api/health')
def health_check():
    """Health check endpoint that also verifies TMDB API connection"""
    try:
        # Try to fetch one movie to verify API connection
        test_movie = tmdb_client.get_popular_movies(page=1)
        return jsonify({
            "status": "healthy",
            "tmdb_connection": "ok" if test_movie else "error",
            "api_key_loaded": bool(api_key)
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "api_key_loaded": bool(api_key)
        }), 500

@app.route('/api/movie-of-the-day')
def get_movie_of_the_day():
    try:
        movie = tmdb_client.get_movie_of_the_day()
        if movie:
            return jsonify({
                'success': True,
                'movie': movie
            })
        return jsonify({
            'success': False,
            'error': 'No movie of the day available'
        }), 404
    except Exception as e:
        logger.error(f"Error getting movie of the day: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting movie of the day'
        }), 500

@app.route('/api/popular')
def get_popular():
    try:
        movies = tmdb_client.get_popular_movies()
        return jsonify({
            'success': True,
            'movies': movies
        })
    except Exception as e:
        logger.error(f"Error getting popular movies: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting popular movies'
        }), 500

@app.route('/api/new-releases')
def get_new_releases():
    try:
        movies = tmdb_client.get_new_releases()
        return jsonify({
            'success': True,
            'movies': movies
        })
    except Exception as e:
        logger.error(f"Error getting new releases: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting new releases'
        }), 500

@app.route('/api/search')
def search_movies():
    query = request.args.get('q', '')
    if not query:
        return jsonify({
            'success': False,
            'error': 'No search query provided'
        }), 400
    
    try:
        movies = tmdb_client.search_movies(query)
        return jsonify({
            'success': True,
            'movies': movies
        })
    except Exception as e:
        logger.error(f"Error searching movies: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error searching movies'
        }), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        mood = data.get('mood')
        genre = data.get('genre')
        
        if not any([movie_id, mood, genre]):
            return jsonify({
                'success': False,
                'error': 'No recommendation criteria provided'
            }), 400
        
        recommender = MovieRecommender(tmdb_client)
        recommendations = recommender.get_recommendations(movie_id, mood, genre)
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting recommendations'
        }), 500

@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        
        if not movie_id:
            return jsonify({
                'success': False,
                'error': 'Movie ID is required'
            }), 400
            
        # Get movie details from TMDB
        movie = tmdb_client.get_movie_details(movie_id)
        if not movie:
            return jsonify({
                'success': False,
                'error': 'Movie not found'
            }), 404
            
        # Store in session for now (we can add database storage later)
        watchlist = session.get('watchlist', [])
        if not any(m['id'] == movie_id for m in watchlist):
            watchlist.append({
                'id': movie['id'],
                'title': movie['title'],
                'poster_path': movie['poster_path'],
                'release_date': movie['release_date'],
                'overview': movie['overview'],
                'vote_average': movie['vote_average']
            })
            session['watchlist'] = watchlist
            
        return jsonify({
            'success': True,
            'message': 'Movie added to watchlist'
        })
    except Exception as e:
        logger.error(f"Error adding to watchlist: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    try:
        data = request.get_json()
        movie_id = data.get('movie_id')
        
        if not movie_id:
            return jsonify({
                'success': False,
                'error': 'Movie ID is required'
            }), 400
            
        watchlist = session.get('watchlist', [])
        watchlist = [m for m in watchlist if m['id'] != movie_id]
        session['watchlist'] = watchlist
        
        return jsonify({
            'success': True,
            'message': 'Movie removed from watchlist'
        })
    except Exception as e:
        logger.error(f"Error removing from watchlist: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    try:
        watchlist = session.get('watchlist', [])
        return jsonify({
            'success': True,
            'movies': watchlist
        })
    except Exception as e:
        logger.error(f"Error getting watchlist: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/mood/<mood>')
def get_mood_recommendations(mood):
    try:
        recommender = MovieRecommender(tmdb_client)
        movies = recommender.get_mood_recommendations(mood)
        
        return jsonify({
            'success': True,
            'movies': movies
        })
    except Exception as e:
        logger.error(f"Error getting mood recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting mood recommendations'
        }), 500

@app.route('/api/recommendations/genre/<genre>')
def get_genre_recommendations(genre):
    try:
        recommender = MovieRecommender(tmdb_client)
        movies = recommender.get_genre_recommendations(genre)
        
        return jsonify({
            'success': True,
            'movies': movies
        })
    except Exception as e:
        logger.error(f"Error getting genre recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting genre recommendations'
        }), 500

@app.route('/api/trending')
def get_trending():
    try:
        movies = tmdb_client.get_trending_movies()
        return jsonify({
            'success': True,
            'movies': movies
        })
    except Exception as e:
        logger.error(f"Error getting trending movies: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error getting trending movies'
        }), 500

@app.route('/api/movie/<int:movie_id>')
def get_movie_details(movie_id):
    try:
        if not movie_id:
            return jsonify({
                'success': False,
                'error': 'Movie ID is required'
            }), 400

        movie = tmdb_client.get_movie_details(movie_id)
        if movie:
            return jsonify({
                'success': True,
                'movie': movie
            })
        return jsonify({
            'success': False,
            'error': 'Movie not found'
        }), 404
    except Exception as e:
        logger.error(f"Error getting movie details: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/ai', methods=['POST'])
def get_ai_recommendations():
    try:
        logger.info("AI recommendations endpoint called")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        preferences = data.get('preferences', {})
        mood = preferences.get('mood')
        genres = preferences.get('genres', [])
        
        logger.info(f"Processing preferences - mood: {mood}, genres: {genres}")
        
        # If both mood and genres are provided, prioritize mood
        if mood:
            logger.info(f"Getting recommendations for mood: {mood}")
            recommendations = recommender.get_recommendations(mood=mood)
        elif genres:
            # Take the first genre if multiple are provided
            logger.info(f"Getting recommendations for genre: {genres[0]}")
            recommendations = recommender.get_recommendations(genre=genres[0])
        else:
            # If no preferences provided, return popular movies
            logger.info("No preferences provided, getting popular movies")
            recommendations = recommender.get_recommendations()
        
        logger.info(f"Found {len(recommendations) if recommendations else 0} recommendations")
        
        if not recommendations:
            logger.warning("No recommendations found")
            return jsonify({
                'success': False,
                'error': 'No recommendations found. Try different preferences.',
                'debug_info': {
                    'mood': mood,
                    'genres': genres,
                    'recommender_initialized': recommender is not None
                }
            }), 404
        
        return jsonify({
            'success': True,
            'movies': recommendations,
            'debug_info': {
                'mood': mood,
                'genres': genres,
                'count': len(recommendations)
            }
        })
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error getting AI recommendations: {str(e)}',
            'debug_info': {
                'exception_type': type(e).__name__,
                'exception_message': str(e)
            }
        }), 500

@app.route('/api/recommendations/chat-recommendations', methods=['POST'])
def chat_recommendations():
    try:
        logger.info("Chat recommendations endpoint called")
        data = request.get_json()
        logger.info(f"Received chat data: {data}")
        
        user_input = data.get('user_input')
        if not user_input:
            logger.warning("No user_input provided")
            return jsonify({
                'success': False,
                'error': 'user_input is required'
            }), 400
        
        logger.info(f"Processing user input: {user_input}")
        
        # Check if AI recommender is properly initialized
        if not hasattr(ai_recommender, 'model'):
            logger.error("AI recommender model not initialized - missing GOOGLE_API_KEY")
            return jsonify({
                'success': False,
                'error': 'AI service not available. Please check configuration.',
                'debug_info': {
                    'ai_recommender_initialized': hasattr(ai_recommender, 'model'),
                    'google_api_key_loaded': bool(os.getenv('GOOGLE_API_KEY'))
                }
            }), 503
        
        # Call the async Gemini AI recommender
        logger.info("Calling AI recommender...")
        recommendations = asyncio.run(ai_recommender.get_chat_recommendations(user_input))
        
        logger.info(f"AI recommender returned {len(recommendations) if recommendations else 0} recommendations")
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'debug_info': {
                'user_input': user_input,
                'recommendations_count': len(recommendations) if recommendations else 0
            }
        })
    except Exception as e:
        logger.error(f"Error in chat recommendations: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error in chat recommendations: {str(e)}',
            'debug_info': {
                'exception_type': type(e).__name__,
                'exception_message': str(e),
                'ai_recommender_initialized': hasattr(ai_recommender, 'model') if 'ai_recommender' in locals() else False,
                'google_api_key_loaded': bool(os.getenv('GOOGLE_API_KEY'))
            }
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 