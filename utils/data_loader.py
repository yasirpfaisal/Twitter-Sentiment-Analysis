import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def load_data(file_path):
    """
    Loads CSV data, handles missing values, and parses dates.
    Cached to improve performance on large datasets.
    """
    try:
        # Load data
        df = pd.read_csv(file_path)

        # Validate required columns
        required_columns = ['text', 'created_at', 'location', 'polarity', 'subjectivity', 'sentiment']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            st.error(f"Missing columns in CSV: {missing}")
            return pd.DataFrame()

        # Date parsing
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # Drop rows with invalid dates
        df = df.dropna(subset=['created_at'])

        # Extract time features
        df['hour'] = df['created_at'].dt.hour
        df['date'] = df['created_at'].dt.date
        
        # Handle missing locations
        df['location'] = df['location'].fillna("Unknown")

        # Ensure sentiment is mapped correctly for readability
        sentiment_map = {-1: 'Negative', 0: 'Neutral', 1: 'Positive'}
        # Check if sentiment is numeric or string, adjust accordingly
        if pd.api.types.is_numeric_dtype(df['sentiment']):
             df['sentiment_label'] = df['sentiment'].map(sentiment_map)
        else:
             df['sentiment_label'] = df['sentiment'] # Assume it's already labelled

        return df

    except FileNotFoundError:
        st.error(f"File not found at {file_path}. Please ensure data exists.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()