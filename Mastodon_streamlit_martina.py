import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from copy import deepcopy


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df_follower = load_data(path="./df_status_follower_v1.csv")
df_follower_copy = deepcopy(df_follower)

# Data cleaning for graph status vs followers
df_follower_unique = df_follower.drop_duplicates(subset=['user_name'], keep='first')
top_follower_count = df_follower_unique.sort_values(ascending=False, by = "followers_count").head(10).reset_index()[["user_name", "followers_count"]]
top_status_count = df_follower_unique.sort_values(ascending=False, by = "status_count").head(10).reset_index()[["user_name", "status_count"]]
df_follower_unique_rel = df_follower_unique
condition_1 = df_follower_unique_rel["followers_count"] >= 10000000
condition_2 = df_follower_unique_rel["status_count"] >= 1200000
condition = condition_1 + condition_2
df_follower_unique_rel['text'] = df_follower_unique_rel['user_name'].where(condition, '')
df_follower_unique_rel_label = df_follower_unique_rel[df_follower_unique_rel['text'].str.strip() != ""]
df_follower_unique_rel_label["type"] = ["Media outlet", "Media outlet", "Media outlet", "Media outlet", "Sports club/platform","Media outlet","Media outlet","Sports club/platform", "Sports club/platform"]
df_follower_unique_rel_label["type"] = df_follower_unique_rel_label["type"].astype("category")
color_mapping = {
    "Media outlet": "orange",
    "Sports club/platform": "green",
}
df_follower_unique_rel_label["color"] = df_follower_unique_rel_label["type"].map(color_mapping)
types = df_follower_unique_rel_label["type"].unique()



fig_1 = go.Figure()
fig_1.add_trace(
    go.Scatter(
        x=df_follower_unique_rel["followers_count"], 
        y=df_follower_unique_rel["status_count"], 
        text=df_follower_unique_rel["user_name"],
        mode="markers",
        showlegend=False)
        )

for type_ in types:
    filtered_data = df_follower_unique_rel_label[df_follower_unique_rel_label["type"] == type_]
    fig_1.add_trace(
      go.Scatter(
          x=filtered_data["followers_count"], 
          y=filtered_data["status_count"], 
          text=filtered_data["text"], 
          marker=dict(size=8, color=color_mapping[type_]),
          name = type_,
          textposition="top center",
          mode="markers+text")
        )


fig_1.update_layout(
    xaxis_title="Followers count",
    yaxis_title="Status count", 
    title = "How often do you need to post in order to get many followers?"
)

st.plotly_chart(fig_1)


# Data cleaning for boxplots
df_follower_many = df_follower_unique[df_follower_unique["followers_count"] >= 1000].sort_values(ascending=False, by = "followers_count")
top_80_percent = int(len(df_follower_unique) * 0.8)
df_follower_regular = df_follower_unique.sort_values(ascending=False, by = "followers_count")
df_follower_regular = df_follower_regular.tail(top_80_percent)
df_status_regular = df_follower_unique.sort_values(ascending=False, by = "status_count")
df_status_regular = df_status_regular.tail(top_80_percent)

fig = make_subplots(
    rows=1, cols=2, 
    subplot_titles=("Number of followers", "Number of status updates"), 
    shared_yaxes=False  
)

fig2 = go.Box(
    x=df_follower_regular["followers_count"],
    marker=dict(color="green"),
    showlegend=False
)

fig3 = go.Box(
    x=df_status_regular["status_count"],
    marker=dict(color="royalblue"),
    showlegend=False
)

fig.add_trace(fig2, row=1, col=1)  
fig.add_trace(fig3, row=1, col=2)  

fig.update_layout(
    title="How many followers do regular users of Mastodon have? How often do they post?",
    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    yaxis2=dict(showticklabels=False, showgrid=False, zeroline=False),
)
st.plotly_chart(fig)


#Data cleaning for development over time
df_follower_unique["created_at"] = pd.to_datetime(df_follower_unique["created_at"])
df_follower_unique = df_follower_unique[df_follower_unique["created_at"] >= "2016-03-16"]
follower_count_monthly = df_follower_unique.groupby(pd.Grouper(key="created_at", freq="M")).count()
follower_count_monthly = follower_count_monthly.iloc[:, [0]].rename(columns={follower_count_monthly.columns[0]: "number_new_users"})

fig = px.line(follower_count_monthly, x=follower_count_monthly.index, y= "number_new_users")

fig.update_layout(
    title="How did the popularity of Mastodon evolve?",
    yaxis_title="Number of New Users",
    xaxis_title="",
    showlegend=False
)

fig.add_annotation(
    x="2022-10-27",  
    y= 470,       
    text="Musk buys Twitter", 
    showarrow=True, 
    arrowhead=2,    
    ax = 0,            
    ay= -40,          
    arrowwidth=2,    
    arrowcolor="black"  
)


fig.add_annotation(
    x="2024-11-05",  
    y= 170,       
    text="US elections", 
    showarrow=True, 
    arrowhead=2,    
    ax = 0,            
    ay= -40,          
    arrowwidth=2,    
    arrowcolor="black"  
)

fig.add_annotation(
    x="2016-03-16",  
    y= 50,       
    text="Launch of Mastodon", 
    showarrow=True, 
    arrowhead=2,    
    ax= -10,            
    ay= -70,          
    arrowwidth=2,    
    arrowcolor="black"  
)

st.plotly_chart(fig)


# Load data for trends

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df_trend = load_data(path="./df_trends.csv")
df_trend_copy = deepcopy(df_trend)


fig = go.Figure()
for trend in df_trend['trend_name']:
    trend_data = df_trend[df_trend['trend_name'] == trend].drop(columns=['trend_name']).values.flatten()
    
    fig.add_trace(go.Scatter(
        x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 
        y=trend_data,  
        mode='lines+markers', 
        name=trend  
    ))


fig.update_layout(
    title="How long do trends last in Mastodon?",
    yaxis_title="Count",
    legend_title="Trend",
    showlegend=True,
    yaxis=dict(showticklabels=False),  
    xaxis=dict(tickmode='array', tickvals=list(range(7)), ticktext=["1 day", "2 days", "3 days", "4 days", "5 days", "6 days", "7 days"])
)

st.plotly_chart(fig)
