import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'cinegenie.db')
        self.init_db()

    def init_db(self):
        """Initialize the database and create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def create_user(self, email, password, name):
        """Create a new user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hash the password
            hashed_password = generate_password_hash(password)
            
            cursor.execute(
                'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
                (email, hashed_password, name)
            )
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def verify_user(self, email, password):
        """Verify user credentials."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user[2], password):
                return {
                    'id': user[0],
                    'email': user[1],
                    'name': user[3]
                }
            return None
        finally:
            conn.close()

    def get_user_by_email(self, email):
        """Get user by email."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'email': user[1],
                    'name': user[3]
                }
            return None
        finally:
            conn.close() 