import time
import pandas as pd
import random
import sqlite3
from datetime import datetime
from db_manager import init_db, save_tweet

# --- CONFIGURATION ---
SOURCE_FILE = "data/sample_data.csv"
POLL_INTERVAL_MIN = 2  # Min seconds between tweets
POLL_INTERVAL_MAX = 6  # Max seconds between tweets

def load_sample_tweets():
    """Loads the static CSV to use as a source of 'real' text."""
    try:
        df = pd.read_csv(SOURCE_FILE)
        # Filter for valid text
        tweets = df['text'].dropna().tolist()
        # Also get locations if available to keep it realistic
        locations = df['user_location'].dropna().tolist()
        return tweets, locations
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return [], []

def generate_mock_tweet(tweet_text_pool, location_pool):
    """Creates a tweet object that LOOKS like it just came from the API."""
    
    # Pick a random tweet text from your historical data
    text = random.choice(tweet_text_pool)
    
    # 50% chance to have a location
    location = random.choice(location_pool) if (location_pool and random.random() > 0.5) else "Unknown"
    
    # SIMULATE VADER SCORING
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)['compound']
    
    if score >= 0.05:
        label = 'Positive'
    elif score <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'

    # --- FIX IS HERE BELOW ---
    # We ensure both numbers are 19 digits long so start < end
    random_id = random.randint(1000000000000000000, 9999999999999999999)

    return {
        'id_str': str(random_id), 
        'text': text,
        'created_at': datetime.now(), # <--- KEY: timestamp is NOW
        'user_location': location,
        'polarity': score,
        'sentiment_label': label
    }

def run_simulator():
    print("🚀 Starting Twitter Stream Simulator...")
    print("   (Using sample_data.csv to generate 'live' events)")
    
    init_db()
    tweets, locations = load_sample_tweets()
    
    if not tweets:
        print("⚠️ No tweets found in CSV. Exiting.")
        return

    while True:
        try:
            # 1. Generate a "New" Tweet
            fake_tweet = generate_mock_tweet(tweets, locations)
            
            # 2. Save it to the Database
            save_tweet(fake_tweet)
            
            # 3. Log it
            print(f"✅ [LIVE SIM] New Tweet at {fake_tweet['created_at'].strftime('%H:%M:%S')}: {fake_tweet['sentiment_label']} ({fake_tweet['polarity']:.2f})")
            
            # 4. Wait a random amount of time (Simulating irregular traffic)
            sleep_time = random.randint(POLL_INTERVAL_MIN, POLL_INTERVAL_MAX)
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("\n🛑 Simulator stopped.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    run_simulator()