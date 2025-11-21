import pandas as pd
import sqlite3
import streamlit as st

DB_PATH = "data/tweets.db"

def load_data(file_path=None): # file_path argument kept for compatibility but unused
    try:
        # Connect to SQLite
        conn = sqlite3.connect(DB_PATH)
        
        # Read entire table into DataFrame
        query = "SELECT * FROM tweets"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return pd.DataFrame()

        # Post-processing dates
        # Nitter dates might look like "Nov 19, 2025 · 10:00 PM UTC"
        # We let pandas guess the format
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df = df.dropna(subset=['created_at'])
        
        df['date'] = df['created_at'].dt.date
        df['hour'] = df['created_at'].dt.hour
        
        # Note: Polarity and Sentiment are already in the DB!
        
        return df

    except Exception as e:
        st.error(f"Error reading database: {e}")
        return pd.DataFrame()