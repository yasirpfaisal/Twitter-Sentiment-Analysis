import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def load_data(file_path):
    try:
        # Load the CSV
        df = pd.read_csv(file_path)
        
        # 1. Check for the columns that ACTUALLY exist in your file
        required_cols = ['text', 'created_at', 'polarity', 'user_location']
        if not all(col in df.columns for col in required_cols):
            st.error(f"The CSV file is missing one of these columns: {required_cols}")
            st.write("Columns found:", df.columns.tolist())
            return pd.DataFrame()

        # 2. Parse Dates
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df = df.dropna(subset=['created_at'])
        
        df['date'] = df['created_at'].dt.date
        df['hour'] = df['created_at'].dt.hour

        # 3. Handle Location (Fill missing values)
        df['user_location'] = df['user_location'].fillna("Unknown")

        # 4. Map Polarity integers (-1, 0, 1) to Sentiment Labels
        # Your data has -1, 0, 1. We map them directly.
        sentiment_map = {
            -1: 'Negative',
            0: 'Neutral',
            1: 'Positive'
        }
        df['sentiment_label'] = df['polarity'].map(sentiment_map)
        
        # Handle any polarity values that might not be -1, 0, or 1
        df['sentiment_label'] = df['sentiment_label'].fillna('Neutral')

        return df

    except Exception as e:
        st.error(f"Error processing data: {e}")
        return pd.DataFrame()