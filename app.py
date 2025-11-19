import streamlit as st
from utils.data_loader import load_data
from utils.visualizer import Visualizer

# --- Page Config ---
st.set_page_config(page_title="Twitter Sentiment Dashboard", page_icon="🐦", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .metric-card { background-color: #262730; border-radius: 10px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
DATA_PATH = 'data/sample_data.csv'
full_df = load_data(DATA_PATH)

if full_df.empty:
    st.stop()

# --- Sidebar ---
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date Range", (full_df['date'].min(), full_df['date'].max()))
locations = st.sidebar.multiselect("Locations", options=full_df['user_location'].unique())

# --- Filtering Logic ---
start, end = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (date_range[0], date_range[0])
filtered_df = full_df[(full_df['date'] >= start) & (full_df['date'] <= end)]

if locations:
    filtered_df = filtered_df[filtered_df['user_location'].isin(locations)]

viz = Visualizer(filtered_df)

# --- Main Dashboard ---
st.title("🐦 Real-Time Sentiment Tracker")

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Tweets", f"{len(filtered_df):,}")
with col2:
    # Average Polarity (-1 to 1)
    avg_pol = filtered_df['polarity'].mean()
    st.metric("Avg Polarity", f"{avg_pol:.3f}")
with col3:
    # Positive Percentage
    pos_count = len(filtered_df[filtered_df['sentiment_label'] == 'Positive'])
    pos_pct = (pos_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("Positive %", f"{pos_pct:.1f}%")
with col4:
    # Negative Percentage
    neg_count = len(filtered_df[filtered_df['sentiment_label'] == 'Negative'])
    neg_pct = (neg_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("Negative %", f"{neg_pct:.1f}%")

st.markdown("---")

# Charts
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🗺️ Location & Text", "📝 Raw Data"])

with tab1:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.plotly_chart(viz.plot_sentiment_over_time(), use_container_width=True)
    with c2:
        st.plotly_chart(viz.plot_sentiment_distribution(), use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(viz.plot_top_locations(), use_container_width=True)
    with c2:
        st.subheader("Word Cloud Analysis")
        sent_type = st.radio("Select Sentiment", ["Positive", "Negative", "Neutral"], horizontal=True)
        wc_fig = viz.generate_wordcloud(sent_type)
        if wc_fig:
            st.pyplot(wc_fig)
        else:
            st.warning("No tweets found for this sentiment category.")

with tab3:
    st.dataframe(filtered_df[['created_at', 'text', 'sentiment_label', 'polarity', 'user_location']], use_container_width=True)