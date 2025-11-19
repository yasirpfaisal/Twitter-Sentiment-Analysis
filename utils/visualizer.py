import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st

class Visualizer:
    def __init__(self, df):
        self.df = df
        # consistent color map
        self.color_map = {'Positive': '#00CC96', 'Negative': '#EF553B', 'Neutral': '#636EFA'}

    def plot_sentiment_over_time(self):
        # Resample by hour or day depending on range
        df_grouped = self.df.groupby([pd.Grouper(key='created_at', freq='H'), 'sentiment_label']).size().reset_index(name='counts')
        
        fig = px.line(df_grouped, x='created_at', y='counts', color='sentiment_label',
                      title='Sentiment Trends Over Time',
                      color_discrete_map=self.color_map,
                      labels={'created_at': 'Time', 'counts': 'Tweet Volume'})
        fig.update_layout(hovermode="x unified")
        return fig

    def plot_sentiment_distribution(self):
        fig = px.donut(self.df, names='sentiment_label', 
                       title='Overall Sentiment Distribution',
                       color='sentiment_label',
                       color_discrete_map=self.color_map,
                       hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig

    def plot_top_locations(self):
        # Filter out 'Unknown' for the chart
        loc_df = self.df[self.df['location'] != 'Unknown']
        top_loc = loc_df['location'].value_counts().nlargest(10).reset_index()
        top_loc.columns = ['location', 'count']
        
        fig = px.bar(top_loc, x='count', y='location', orientation='h',
                     title='Top 10 User Locations',
                     color='count',
                     color_continuous_scale='Viridis')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        return fig

    def plot_polarity_vs_subjectivity(self):
        fig = px.scatter(self.df, x='polarity', y='subjectivity',
                         color='sentiment_label',
                         title='Polarity vs. Subjectivity',
                         color_discrete_map=self.color_map,
                         hover_data=['text'],
                         opacity=0.6)
        return fig

    def generate_wordcloud(self, sentiment_filter):
        text = " ".join(tweet for tweet in self.df[self.df['sentiment_label'] == sentiment_filter]['text'])
        
        # Generate cloud
        wc = WordCloud(width=800, height=400, background_color='#0E1117', colormap='Greens' if sentiment_filter == 'Positive' else 'Reds').generate(text)
        
        # Return matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        # Transparent background for dark mode integration
        fig.patch.set_alpha(0) 
        return fig