# db_manager.py
import sqlite3
from datetime import datetime

DB_NAME = "data/tweets.db"

def init_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create table matching your dashboard requirements
    c.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id_str TEXT PRIMARY KEY,
            text TEXT,
            created_at TIMESTAMP,
            user_location TEXT,
            polarity REAL,
            sentiment_label TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_NAME}")

def save_tweet(tweet_data):
    """Saves a single tweet dictionary to the DB."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT OR IGNORE INTO tweets (id_str, text, created_at, user_location, polarity, sentiment_label)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            tweet_data['id_str'],
            tweet_data['text'],
            tweet_data['created_at'],
            tweet_data['user_location'],
            tweet_data['polarity'],
            tweet_data['sentiment_label']
        ))
        conn.commit()
        return True # Success
    except Exception as e:
        print(f"Error saving tweet: {e}")
        return False
    finally:
        conn.close()