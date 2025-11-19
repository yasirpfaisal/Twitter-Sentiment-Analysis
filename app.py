import streamlit as st
import pandas as pd
import time
from utils.data_loader import load_data
from utils.visualizer import Visualizer

# Page Config
st.set_page_config(
    page_title="Twitter Sentiment Engine",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Handling for Custom Styling ---
st.markdown("""
<style>
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1DA1F2;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar & Controls ---
st.sidebar.title("🔧 Dashboard Controls")
st.sidebar.markdown("---")

# Load Data
DATA_PATH = 'data/sample_data.csv'
full_df = load_data(DATA_PATH)

if full_df.empty:
    st.stop() # Stop execution if data fails to load

# Sidebar Filters
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(full_df['date'].min(), full_df['date'].max()),
    min_value=full_df['date'].min(),
    max_value=full_df['date'].max()
)

location_filter = st.sidebar.multiselect(
    "Filter by Location",
    options=full_df['location'].unique(),
    default=[]
)

# Filter Logic
start_date, end_date = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (date_range[0], date_range[0])
filtered_df = full_df[
    (full_df['date'] >= start_date) & 
    (full_df['date'] <= end_date)
]

if location_filter:
    filtered_df = filtered_df[filtered_df['location'].isin(location_filter)]

# Initialize Visualizer with filtered data
viz = Visualizer(filtered_df)

# --- Main Layout ---

st.title("🐦 Real-Time Twitter Sentiment Analysis")
st.markdown(f"Analyzing **{len(filtered_df)}** tweets from **{start_date}** to **{end_date}**")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Tweets", f"{len(filtered_df):,}")
with col2:
    avg_pol = filtered_df['polarity'].mean()
    st.metric("Avg Polarity", f"{avg_pol:.2f}", delta="Positive" if avg_pol > 0 else "Negative")
with col3:
    pos_pct = (filtered_df['sentiment_label'] == 'Positive').mean() * 100
    st.metric("Positive Sentiment", f"{pos_pct:.1f}%")
with col4:
    subjectivity = filtered_df['subjectivity'].mean()
    st.metric("Avg Subjectivity", f"{subjectivity:.2f}")

st.markdown("---")

# Tabbed Layout for Visualizations
tab1, tab2, tab3 = st.tabs(["📈 Temporal & Distribution", "🗺️ Geography & NLP", "📊 Raw Data & Export"])

with tab1:
    row1_col1, row1_col2 = st.columns([2, 1])
    
    with row1_col1:
        st.plotly_chart(viz.plot_sentiment_over_time(), use_container_width=True)
    
    with row1_col2:
        st.plotly_chart(viz.plot_sentiment_distribution(), use_container_width=True)
        
    st.plotly_chart(viz.plot_polarity_vs_subjectivity(), use_container_width=True)

with tab2:
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.plotly_chart(viz.plot_top_locations(), use_container_width=True)
        
    with row2_col2:
        st.subheader("☁️ Sentiment Word Clouds")
        wc_type = st.radio("Select Sentiment", ["Positive", "Negative"], horizontal=True)
        try:
            st.pyplot(viz.generate_wordcloud(wc_type))
        except ValueError:
            st.info("Not enough text data to generate word cloud for this selection.")

with tab3:
    st.dataframe(filtered_df[['created_at', 'text', 'sentiment_label', 'location', 'polarity']], use_container_width=True)
    
    # Export Button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name='sentiment_analysis_export.csv',
        mime='text/csv',
    )

# --- Auto-Refresh Simulation (Optional) ---
if st.sidebar.checkbox("Simulate Real-Time Feeds"):
    st.sidebar.warning("Simulating live updates...")
    time.sleep(2)
    st.rerun()