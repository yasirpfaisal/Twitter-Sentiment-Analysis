# collector.py
import time
import pandas as pd
from ntscraper import Nitter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from db_manager import init_db, save_tweet

# --- CONFIGURATION ---
SEARCH_TERM = "Apple"  # Brand or Topic to track
TWEETS_TO_SCRAPE = 20  # Number of tweets to grab per batch
POLL_INTERVAL = 30     # Wait time (seconds) between scrapes to be polite

# Initialize VADER
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    """Calculates compound score and label."""
    score = analyzer.polarity_scores(text)['compound']
    if score >= 0.05:
        label = 'Positive'
    elif score <= -0.05:
        label = 'Negative'
    else:
        label = 'Neutral'
    return score, label

def run_collector():
    print(f"🚀 Starting Collector for term: '{SEARCH_TERM}'")
    scraper = Nitter(log_level=1, skip_instance_check=False)
    init_db()

    while True:
        try:
            print(f"\n🔎 Scraping recent tweets for '{SEARCH_TERM}'...")
            
            # Scrape tweets
            scraped_data = scraper.get_tweets(SEARCH_TERM, mode='term', number=TWEETS_TO_SCRAPE)
            
            tweets = scraped_data.get('tweets', [])
            
            new_count = 0
            
            for t in tweets:
                # Extract relevant fields
                text = t['text']
                
                # Calculate Sentiment IMMEDIATELY (ETL)
                polarity, label = get_sentiment(text)
                
                # Prepare data object
                tweet_obj = {
                    'id_str': str(t['link'].split('/')[-1]), # Extract ID from link
                    'text': text,
                    'created_at': t['date'], # Nitter format is usually parseable
                    'user_location': t['user']['location'] if t['user']['location'] else "Unknown",
                    'polarity': polarity,
                    'sentiment_label': label
                }
                
                # Save to SQLite
                if save_tweet(tweet_obj):
                    new_count += 1
            
            print(f"✅ Saved {new_count} new tweets.")
            print(f"💤 Sleeping for {POLL_INTERVAL} seconds...")
            time.sleep(POLL_INTERVAL)

        except Exception as e:
            print(f"⚠️ Error during scraping: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_collector()