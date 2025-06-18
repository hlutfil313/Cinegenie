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

// Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/sw.js')
      .then(registration => {
        console.log('ServiceWorker registration successful:', registration.scope);
      })
      .catch(error => {
        console.log('ServiceWorker registration failed:', error);
      });
  });
}

// PWA Installation prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  // Show install button if available
  const installButton = document.getElementById('installButton');
  if (installButton) {
    installButton.style.display = 'block';
    installButton.addEventListener('click', () => {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted the install prompt');
        } else {
          console.log('User dismissed the install prompt');
        }
        deferredPrompt = null;
        installButton.style.display = 'none';
      });
    });
  }
});

// Mobile navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    // Create mobile menu button
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const mobileMenuBtn = document.createElement('button');
        mobileMenuBtn.className = 'mobile-menu-btn';
        mobileMenuBtn.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        mobileMenuBtn.setAttribute('aria-label', 'Toggle mobile menu');
        
        // Insert mobile menu button before nav-links
        const navLinks = navbar.querySelector('.nav-links');
        if (navLinks) {
            navbar.insertBefore(mobileMenuBtn, navLinks);
            
            // Add mobile menu functionality
            mobileMenuBtn.addEventListener('click', function() {
                navLinks.classList.toggle('mobile-active');
                mobileMenuBtn.classList.toggle('active');
            });
            
            // Close mobile menu when clicking on a link
            navLinks.addEventListener('click', function(e) {
                if (e.target.tagName === 'A') {
                    navLinks.classList.remove('mobile-active');
                    mobileMenuBtn.classList.remove('active');
                }
            });
            
            // Close mobile menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!navbar.contains(e.target)) {
                    navLinks.classList.remove('mobile-active');
                    mobileMenuBtn.classList.remove('active');
                }
            });
        }
    }
    
    // Add touch gestures for mobile
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            const navLinks = document.querySelector('.nav-links');
            const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
            
            if (diff > 0 && navLinks.classList.contains('mobile-active')) {
                // Swipe left - close menu
                navLinks.classList.remove('mobile-active');
                mobileMenuBtn.classList.remove('active');
            } else if (diff < 0 && !navLinks.classList.contains('mobile-active')) {
                // Swipe right - open menu
                navLinks.classList.add('mobile-active');
                mobileMenuBtn.classList.add('active');
            }
        }
    }
    
    // Optimize images for mobile
    const movieCards = document.querySelectorAll('.movie-card img');
    movieCards.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });
        
        img.addEventListener('error', function() {
            this.src = '/static/images/no-poster.svg';
        });
    });
    
    // Add lazy loading for better mobile performance
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Optimize chat interface for mobile
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        // Auto-resize chat input
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        // Focus chat input when tapping on chat container
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.addEventListener('click', function(e) {
                if (e.target === this) {
                    chatInput.focus();
                }
            });
        }
    }
    
    // Add pull-to-refresh functionality for mobile
    let startY = 0;
    let currentY = 0;
    let pullDistance = 0;
    const pullThreshold = 100;
    
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
        }
    });
    
    document.addEventListener('touchmove', function(e) {
        if (window.scrollY === 0 && startY > 0) {
            currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;
            
            if (pullDistance > 0) {
                e.preventDefault();
                document.body.style.transform = `translateY(${Math.min(pullDistance * 0.5, pullThreshold)}px)`;
            }
        }
    });
    
    document.addEventListener('touchend', function() {
        if (pullDistance > pullThreshold) {
            // Trigger refresh
            window.location.reload();
        }
        
        // Reset
        document.body.style.transform = '';
        startY = 0;
        pullDistance = 0;
    });
}); 