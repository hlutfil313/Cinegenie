// API endpoints
const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
const recommendationsContainer = document.getElementById('recommendations');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadPopularMovies();
    setupEventListeners();
});

function setupEventListeners() {
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 500));
    }
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API Functions
async function searchMovies(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        return data.results;
    } catch (error) {
        console.error('Error searching movies:', error);
        return [];
    }
}

async function getRecommendations(movieId) {
    try {
        const response = await fetch(`${API_BASE_URL}/recommendations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ movie_id: movieId }),
        });
        const data = await response.json();
        return data.recommendations;
    } catch (error) {
        console.error('Error getting recommendations:', error);
        return [];
    }
}

async function loadPopularMovies() {
    try {
        const response = await fetch(`${API_BASE_URL}/popular`);
        const data = await response.json();
        displayMovies(data.results, 'popular-movies');
    } catch (error) {
        console.error('Error loading popular movies:', error);
    }
}

// UI Functions
function displayMovies(movies, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = movies.map(movie => `
        <div class="movie-card" data-movie-id="${movie.id}">
            <img src="${movie.poster_path || 'placeholder.jpg'}" alt="${movie.title}">
            <h3>${movie.title}</h3>
            <p>${movie.overview.substring(0, 100)}...</p>
            <div class="movie-rating">⭐ ${movie.vote_average.toFixed(1)}</div>
        </div>
    `).join('');

    // Add click event listeners to movie cards
    container.querySelectorAll('.movie-card').forEach(card => {
        card.addEventListener('click', () => {
            const movieId = card.dataset.movieId;
            showMovieDetails(movieId);
        });
    });
}

async function handleSearch(event) {
    const query = event.target.value.trim();
    if (query.length < 2) {
        searchResults.innerHTML = '';
        return;
    }

    const results = await searchMovies(query);
    displayMovies(results, 'search-results');
}

async function showMovieDetails(movieId) {
    const recommendations = await getRecommendations(movieId);
    displayMovies(recommendations, 'recommendations');
}

// Add to My List functionality
function addToMyList(movieId) {
    let myList = JSON.parse(localStorage.getItem('myList') || '[]');
    if (!myList.includes(movieId)) {
        myList.push(movieId);
        localStorage.setItem('myList', JSON.stringify(myList));
        showNotification('Movie added to your list!');
    }
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
} 