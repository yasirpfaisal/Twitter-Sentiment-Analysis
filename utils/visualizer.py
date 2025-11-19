import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd

class Visualizer:
    def __init__(self, df):
        self.df = df
        self.color_map = {'Positive': '#00CC96', 'Negative': '#EF553B', 'Neutral': '#636EFA'}

    def plot_sentiment_over_time(self):
        df_grouped = self.df.groupby([pd.Grouper(key='created_at', freq='H'), 'sentiment_label']).size().reset_index(name='counts')
        
        fig = px.line(df_grouped, x='created_at', y='counts', color='sentiment_label',
                      title='Sentiment Volume Over Time (Hourly)',
                      color_discrete_map=self.color_map)
        fig.update_layout(hovermode="x unified", xaxis_title="Time", yaxis_title="Tweet Count")
        return fig

    def plot_sentiment_distribution(self):
        fig = px.donut(self.df, names='sentiment_label', 
                       title='Sentiment Breakdown',
                       color='sentiment_label',
                       color_discrete_map=self.color_map,
                       hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig

    def plot_top_locations(self):
        # Uses 'user_location' instead of 'location'
        loc_df = self.df[self.df['user_location'] != 'Unknown']
        top_loc = loc_df['user_location'].value_counts().nlargest(10).reset_index()
        top_loc.columns = ['user_location', 'count']
        
        fig = px.bar(top_loc, x='count', y='user_location', orientation='h',
                     title='Top User Locations',
                     color='count',
                     color_continuous_scale='Viridis')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        return fig

    def generate_wordcloud(self, sentiment_filter):
        subset = self.df[self.df['sentiment_label'] == sentiment_filter]
        if subset.empty: return None
            
        text = " ".join(str(t) for t in subset['text'])
        colormap = 'Greens' if sentiment_filter == 'Positive' else 'Reds'
        if sentiment_filter == 'Neutral': colormap = 'Blues'
            
        wc = WordCloud(width=800, height=400, background_color='#0E1117', colormap=colormap).generate(text)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        fig.patch.set_alpha(0)
        return fig