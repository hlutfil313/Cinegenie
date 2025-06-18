import os
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from models.recommender import MovieRecommender

logger = logging.getLogger(__name__)

class AIRecommender:
    def __init__(self, movie_recommender: MovieRecommender):
        """Initialize AI recommender with movie recommender"""
        self.movie_recommender = movie_recommender
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in environment variables!")
            logger.error("Please set GOOGLE_API_KEY environment variable to use AI features")
            self.model = None
            return
        else:
            logger.info("GOOGLE_API_KEY loaded successfully")
            logger.debug(f"API Key length: {len(api_key)}")
        
        try:
            genai.configure(api_key=api_key)
            # List available models for debugging
            models = genai.list_models()
            available_models = [model.name for model in models]
            logger.info(f"Available models: {available_models}")
            
            # Use gemini-1.5-flash as recommended
            model_name = 'models/gemini-1.5-flash'
            if model_name not in available_models:
                logger.warning(f"Recommended model {model_name} not found, using first available model")
                model_name = available_models[0] if available_models else None
                if not model_name:
                    raise Exception("No available models found")
            
            logger.info(f"Using model: {model_name}")
            self.model = genai.GenerativeModel(model_name)
            logger.info("Successfully initialized Gemini model")
        except Exception as e:
            logger.error(f"Error initializing Gemini: {str(e)}")
            logger.error("AI features will be disabled. Please check your GOOGLE_API_KEY")
            self.model = None

    async def get_chat_recommendations(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Get movie recommendations based on natural language input using Gemini AI
        """
        # Check if AI model is available
        if not self.model:
            logger.warning("AI model not available, providing fallback recommendations")
            fallback_movies = self.movie_recommender.get_popular_movies()
            if fallback_movies:
                fallback_movies.insert(0, {
                    "message": "AI service is currently unavailable. Here are some popular movies you might enjoy."
                })
            return fallback_movies
        
        prompt = f"""You are a movie recommendation expert. Based on the following user request, 
        identify the key elements for movie recommendations. Respond in this exact format:
        GENRES: [list of genres, separated by commas]
        YEAR: [specific year or year range, or "any" if not specified]
        MOOD: [mood if specified, or "any"]
        
        For example:
        - For "horror comedy movies" -> GENRES: horror, comedy
        - For "90s movies" -> YEAR: 1990-1999
        - For "romantic comedies from 2000s" -> GENRES: romance, comedy, YEAR: 2000-2009
        
        User request: {user_input}"""
        
        try:
            logger.info(f"Processing user request: {user_input}")
            response = self.model.generate_content(prompt)
            analysis = response.text.strip()
            logger.info(f"AI analysis: {analysis}")
            
            # Parse the analysis
            genres = []
            year_range = None
            mood = None
            
            for line in analysis.split('\n'):
                if line.startswith('GENRES:'):
                    genres = [g.strip().lower() for g in line.replace('GENRES:', '').split(',')]
                elif line.startswith('YEAR:'):
                    year_str = line.replace('YEAR:', '').strip()
                    if year_str != 'any':
                        if '-' in year_str:
                            start_year, end_year = map(int, year_str.split('-'))
                            year_range = (start_year, end_year)
                        else:
                            year = int(year_str)
                            year_range = (year, year)
                elif line.startswith('MOOD:'):
                    mood = line.replace('MOOD:', '').strip().lower()
            
            logger.info(f"Parsed genres: {genres}, year range: {year_range}, mood: {mood}")
            
            # Get recommendations based on the analysis
            try:
                recommendations = []
                
                # If we have a mood, get movies for that mood
                if mood and mood != 'any':
                    # Use the mood-based recommendations method
                    mood_movies = self.movie_recommender.get_recommendations(mood=mood)
                    if mood_movies:
                        recommendations.extend(mood_movies)
                
                # If we have specific genres, get movies for those genres
                elif genres and genres[0] != 'any':
                    for genre in genres:
                        genre_movies = self.movie_recommender.get_recommendations(genre=genre)
                        if genre_movies:
                            recommendations.extend(genre_movies)
                
                # If no specific criteria, get popular movies
                if not recommendations:
                    recommendations = self.movie_recommender.get_popular_movies()
                
                # Filter by year if specified
                if year_range and recommendations:
                    recommendations = [
                        movie for movie in recommendations
                        if movie.get('release_date') and 
                        year_range[0] <= int(movie['release_date'][:4]) <= year_range[1]
                    ]
                
                if not recommendations:
                    logger.warning("No recommendations found matching all criteria")
                    popular_movies = self.movie_recommender.get_popular_movies()
                    if popular_movies:
                        popular_movies.insert(0, {
                            "message": f"I couldn't find movies matching your specific criteria. Here are some popular movies you might enjoy."
                        })
                    return popular_movies
                
                # Add a message explaining the recommendation
                message_parts = []
                if genres and genres[0] != 'any':
                    message_parts.append(f"{', '.join(g.title() for g in genres)} movies")
                if year_range:
                    if year_range[0] == year_range[1]:
                        message_parts.append(f"from {year_range[0]}")
                    else:
                        message_parts.append(f"from {year_range[0]}-{year_range[1]}")
                if mood and mood != 'any':
                    message_parts.append(f"with a {mood} mood")
                
                message = f"Based on your request for '{user_input}', I've selected {', '.join(message_parts)} that might interest you."
                recommendations.insert(0, {"message": message})
                
                return recommendations
                
            except Exception as e:
                logger.error(f"Error getting recommendations: {str(e)}")
                popular_movies = self.movie_recommender.get_popular_movies()
                if popular_movies:
                    popular_movies.insert(0, {
                        "message": "I encountered an issue finding specific recommendations. Here are some popular movies you might enjoy."
                    })
                return popular_movies
            
        except Exception as e:
            logger.error(f"Error in AI recommendation process: {str(e)}")
            popular_movies = self.movie_recommender.get_popular_movies()
            if popular_movies:
                popular_movies.insert(0, {
                    "message": "I encountered an issue processing your request. Here are some popular movies you might enjoy."
                })
            return popular_movies
    
    def _process_ai_analysis(self, analysis: str) -> List[Dict[str, Any]]:
        """
        Process the AI analysis to extract key preferences and get recommendations
        """
        try:
            # Extract the primary genre/type from the analysis
            prompt = f"""Based on this analysis, what is the SINGLE most relevant movie genre that would best match the user's preferences?
            Choose from these exact genre names: Action, Adventure, Animation, Comedy, Crime, Documentary, 
            Drama, Family, Fantasy, History, Horror, Music, Mystery, Romance, Science Fiction, TV Movie, 
            Thriller, War, Western.
            
            Only respond with the genre name, nothing else.
            
            Analysis: {analysis}"""
            
            response = self.model.generate_content(prompt)
            primary_genre = response.text.strip().lower()
            logger.info(f"Primary genre identified: {primary_genre}")
            
            try:
                # Get recommendations based on the primary genre
                recommendations = self.movie_recommender.get_recommendations(genre=primary_genre)
                
                if not recommendations or len(recommendations) == 0:
                    logger.warning(f"No recommendations found for genre: {primary_genre}")
                    popular_movies = self.movie_recommender.get_popular_movies()
                    if popular_movies:
                        popular_movies.insert(0, {
                            "message": f"I couldn't find specific {primary_genre.title()} movies, but here are some popular movies you might enjoy."
                        })
                    return popular_movies
                
                # Add a message explaining the recommendation
                recommendations.insert(0, {
                    "message": f"Based on your preferences, I've selected {primary_genre.title()} movies that might interest you."
                })
                
                return recommendations
                
            except Exception as e:
                logger.error(f"Error getting genre recommendations: {str(e)}")
                popular_movies = self.movie_recommender.get_popular_movies()
                if popular_movies:
                    popular_movies.insert(0, {
                        "message": "I encountered an issue finding specific recommendations. Here are some popular movies you might enjoy."
                    })
                return popular_movies
            
        except Exception as e:
            logger.error(f"Error in AI analysis process: {str(e)}")
            popular_movies = self.movie_recommender.get_popular_movies()
            if popular_movies:
                popular_movies.insert(0, {
                    "message": "I encountered an issue processing your request. Here are some popular movies you might enjoy."
                })
            return popular_movies
    
    async def get_contextual_recommendations(
        self,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on various contextual factors
        """
        prompt = f"""Analyze the following context and provide movie recommendations:
        - Time of day: {context.get('time_of_day')}
        - Weather: {context.get('weather')}
        - Season: {context.get('season')}
        - User's mood: {context.get('mood')}
        - Previous watch history: {context.get('watch_history')}
        
        Please provide recommendations that would be suitable for this context.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._process_ai_analysis(response.text)
            
        except Exception as e:
            print(f"Error getting contextual recommendations: {str(e)}")
            return self.movie_recommender.get_popular_movies()
    
    async def get_social_recommendations(
        self,
        user_id: str,
        social_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations based on social and cultural context
        """
        prompt = f"""Based on the following social context, provide movie recommendations:
        - User's cultural background: {social_context.get('cultural_background')}
        - User's interests: {social_context.get('interests')}
        - Trending in user's social circle: {social_context.get('trending')}
        - User's age group: {social_context.get('age_group')}
        
        Please provide recommendations that would be culturally relevant and socially engaging.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._process_ai_analysis(response.text)
            
        except Exception as e:
            print(f"Error getting social recommendations: {str(e)}")
            return self.movie_recommender.get_popular_movies() 