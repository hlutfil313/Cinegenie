# CineGenie - AI-Powered Movie Recommendation System

CineGenie is a modern web application that provides personalized movie recommendations using AI and machine learning. The application uses the TMDB (The Movie Database) API to fetch movie data and implements a content-based recommendation system.

## Features

- 🎬 Movie search and discovery
- 🤖 AI-powered movie recommendations
- 📱 Responsive design
- 💾 Save movies to your personal list
- ⭐ Movie ratings and reviews
- 🎨 Modern and intuitive UI

## Tech Stack

- Frontend: HTML5, CSS3, JavaScript
- Backend: Python (Flask)
- Machine Learning: scikit-learn
- Movie Data: TMDB API
- Database: Local Storage (for user preferences)

## Prerequisites

- Python 3.8 or higher
- Node.js (for development)
- TMDB API key

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cinegenie.git
cd cinegenie
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your TMDB API key:
```
TMDB_API_KEY=your_api_key_here
```

5. Start the backend server:
```bash
python backend/app.py
```

6. Open `index.html` in your web browser or use a local server:
```bash
python -m http.server 8000
```

## Project Structure

```
cinegenie/
├── backend/
│   ├── api/
│   ├── models/
│   ├── utils/
│   └── app.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── index.html
├── recommendation.html
├── my_list.html
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TMDB for providing the movie database API
- scikit-learn for the machine learning capabilities
- All contributors who have helped shape this project 