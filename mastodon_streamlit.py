import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
import time




@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

mastodon_df_raw = load_data(path="./mastodon_data_raw.csv")
mastodon_df = deepcopy(mastodon_df_raw)

plotly_df_raw = load_data(path="./mastodon_data.csv")
df = deepcopy(plotly_df_raw)
df= df.drop(columns=['Post Time'])

df_follower = load_data(path="./df_status_follower_v1.csv")
df_follower_copy = deepcopy(df_follower)

df_trend = load_data(path="./df_trends.csv")
df_trend_copy = deepcopy(df_trend)


#displays "mastodon" with logo
st.markdown("""
    <div style="text-align: center;">
        <a href="https://mastodon.social/" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/4/48/Mastodon_Logotype_%28Simple%29.svg" 
                 alt="Mastodon Logo" style="width: 100px; height: auto;">
        </a>
    </div>
    <h1 style='text-align: center;'>
        <a href='https://mastodon.social/' target='_blank' style='text-decoration: none; color: white;'>Mastodon</a>
    </h1>
""", unsafe_allow_html=True)

# Define button options
#INPUT MARTINAS PART HERE
options = ["Introduction", "Engagement", "MARTINA", "Conclusions", "Next Steps"]

# Initialize session state for selected button if it doesn't exist
if "selected_button" not in st.session_state:
    st.session_state["selected_button"] = None

# Custom CSS for button styling
st.markdown("""
    <style>
    .custom-button {
        display: inline-block;
        background-color: rgba(0, 0, 0, 0.1);
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        margin: 5px;
    }
    .custom-button:hover {
        background-color: rgba(0, 0, 0, 0.4);
    }
    .custom-button.selected {
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        transform: scale(1.05);
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 10px;
    }
    </style>
""", unsafe_allow_html=True)

#Render buttons horizontally using st.columns
cols = st.columns(len(options))
for i, option in enumerate(options):
    with cols[i]:
        is_selected = st.session_state["selected_button"] == option
        button_style = "custom-button selected" if is_selected else "custom-button"
        if st.button(option, key=option):
            st.session_state["selected_button"] = option


# Display content based on the selected button
#INPUT MARTINAS PART HERE
if st.session_state.get("selected_button") == "Introduction":
    st.markdown("<h2 style='text-align: center;'>What is it? 🤔</h2>", unsafe_allow_html=True)
    image_url = "https://cloudfront-us-east-1.images.arcpublishing.com/bostonglobe/OSNVLQ7JQGX4NYJNCJAUKOSYJE.jpg"
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("HINT"):
        placeholder = st.empty()
        placeholder.image(image_url, use_container_width=True)
        time.sleep(7)
        placeholder.empty()
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("Here we introduce the context and objectives.")


elif st.session_state["selected_button"] == "Engagement":
        
    st.markdown("<h3 style='text-align: center;'>Is there a magic formula for engagement?</h3>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>...let´s find out!</h3>", unsafe_allow_html=True)
    #st.image("https://onemanandhisblog.com/content/images/size/w1384/2023/10/wordpress-mastodon.jpg", use_container_width=True)

    #FIRST PLOTS FAVS VS BOOSTS
    # Total posts
    total_posts = len(df)
    # Calculate posts with and without favorites
    favorites_count = len(df[df["# of Favorites"] > 0])
    without_favorites_count = total_posts - favorites_count
    # Calculate posts with and without boosts (shares)
    shared_count = len(df[df["# of Boosts"] > 0])
    without_shared_count = total_posts - shared_count
    # Prepare data for favorites donut plot
    favorites_data = {
        "Category": ["With Favorites", "Without Favorites"],
        "Count": [favorites_count, without_favorites_count],
    }
    # Prepare data for shares donut plot
    shares_data = {
        "Category": ["Shared", "Not Shared"],
        "Count": [shared_count, without_shared_count],
    }
    # Convert to DataFrames
    favorites_df = pd.DataFrame(favorites_data)
    shares_df = pd.DataFrame(shares_data)
    # Create donut plots
    favorites_donut = px.pie(
        favorites_df,
        values="Count",
        names="Category",
        title="Percentage of Posts with Favorites",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    shares_donut = px.pie(
        shares_df,
        values="Count",
        names="Category",
        title="Percentage of Posts Shared",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    # Display plots side by side
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(favorites_donut, use_container_width=True)

    with col2:
        st.plotly_chart(shares_donut, use_container_width=True)

    

    #SECOND PLOT Average Number of Shares Based on Followers Count
    bins = [0, 1000, 5000, 10000, 50000, float('inf')]  # Define ranges for followers count
    labels = ['0-1k', '1k-5k', '5k-10k', '10k-50k', '50k+']
    df['Followers_Bin'] = pd.cut(df["Users_Followers"], bins=bins, labels=labels)
    # Aggregate data by followers bins and calculate the mean of boosts
    aggregated_data = df.groupby("Followers_Bin")["# of Boosts"].mean().reset_index()
    # Create bar plot
    fig = px.bar(
        aggregated_data,
        x="Followers_Bin",
        y="# of Boosts",
        title="Average Number of Shares Based on Followers Count",
        labels={
            "Followers_Bin": "Followers Range",
            "# of Boosts": "Average Shares",
        },
        color_discrete_sequence=["#FF9347"],  
    )
    # Add axis formatting
    fig.update_layout(
        xaxis_title="Followers Range",
        yaxis_title="Average Number of Shares (Boosts)",
        template="plotly_white",
    )
    # Display the plot
    st.plotly_chart(fig)


    # Centered text ""What elements can affect the number of boosts a post receives?""
    st.markdown(
        """
        <style>
            .center-text {
                text-align: center;
                font-size: 20px;  /* Optional: Adjust font size */
                font-weight: bold; /* Optional: Make the text bold */
            }
        </style>
        <div class="center-text">
            What elements could affect the number of boosts a post receives?
        </div>
        """,
        unsafe_allow_html=True
    )

    #PLOT´S SELECTOR
    menu_options = ["Select an option", "Media Input", "Hashtags", "Mentions", "More characters"]
    selected_plot = st.selectbox(" ", menu_options)

    if selected_plot == "Media Input":
        # Filter posts with and without media
        posts_with_media = df[df["Post has Media"] == 1]
        posts_without_media = df[df["Post has Media"] == 0]
        # Calculate shared vs non-shared for posts with media
        shared_with_media = posts_with_media["# of Boosts"].sum()
        not_shared_with_media = len(posts_with_media) - shared_with_media
        # Calculate shared vs non-shared for posts without media
        shared_without_media = posts_without_media["# of Boosts"].sum()
        not_shared_without_media = len(posts_without_media) - shared_without_media
        # Prepare data for the plots
        plot_data_with_media = {
            "Category": ["Shared", "Not Shared"],
            "Count": [shared_with_media, not_shared_with_media],
        }
        plot_data_without_media = {
            "Category": ["Shared", "Not Shared"],
            "Count": [shared_without_media, not_shared_without_media],
        }
        # Convert plot data to DataFrames
        plot_df_with_media = pd.DataFrame(plot_data_with_media)
        plot_df_without_media = pd.DataFrame(plot_data_without_media)
        # Create donut plots with blue colors (keeping the original blue colors)
        fig_with_media = px.pie(
            plot_df_with_media,
            values="Count",
            names="Category",
            title="Posts with Media that Got Shared",
            hole=0.4,
            color_discrete_sequence=["#1f77b4", "#aec7e8"],  # Original blue color scheme
            labels={"Category": "Shared vs Not Shared"}  # Add custom label for clarity
        )
        fig_without_media = px.pie(
            plot_df_without_media,
            values="Count",
            names="Category",
            title="Posts without Media that Got Shared",
            hole=0.4,
            color_discrete_sequence=["#1f77b4", "#aec7e8"],  # Original blue color scheme
            labels={"Category": "Shared vs Not Shared"}  # Add custom label for clarity
        )
        # Remove default legend from both figures
        fig_with_media.update_layout(showlegend=False)
        fig_without_media.update_layout(showlegend=False)
        # Display the plots side by side using Streamlit columns
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_with_media, use_container_width=True)
        with col2:
            st.plotly_chart(fig_without_media, use_container_width=True)
        # Add custom legend centered below the plots
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <span style="background-color: #1f77b4; color: white; padding: 10px;"> </span>
            Shared
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="background-color: #aec7e8; color: black; padding: 10px;"> </span>
            Not Shared
        </div>
        """, unsafe_allow_html=True)



    if selected_plot == "Hashtags":
        
        posts_with_hashtags = df[df["Number of Hashtags (#)"] > 0]
        posts_without_hashtags = df[df["Number of Hashtags (#)"] == 0]

        # Calculate shared vs non-shared for posts with hashtags
        shared_with_hashtags = posts_with_hashtags["# of Boosts"].sum()
        not_shared_with_hashtags = len(posts_with_hashtags) - shared_with_hashtags

        # Calculate shared vs non-shared for posts without hashtags
        shared_without_hashtags = posts_without_hashtags["# of Boosts"].sum()
        not_shared_without_hashtags = len(posts_without_hashtags) - shared_without_hashtags

        # Prepare data for the plots
        plot_data_with_hashtags = {
            "Category": ["Shared", "Not Shared"],
            "Count": [shared_with_hashtags, not_shared_with_hashtags],
        }

        plot_data_without_hashtags = {
            "Category": ["Shared", "Not Shared"],
            "Count": [shared_without_hashtags, not_shared_without_hashtags],
        }

        # Convert plot data to DataFrames
        plot_df_with_hashtags = pd.DataFrame(plot_data_with_hashtags)
        plot_df_without_hashtags = pd.DataFrame(plot_data_without_hashtags)

        # Create donut plots with green colors
        fig_with_hashtags = px.pie(
            plot_df_with_hashtags,
            values='Count',
            names='Category',
            title="Posts with Hashtags that Got Shared",
            hole=0.4,
            color_discrete_sequence=["green", "lightgreen"],  # Green color for the donut chart
            labels={"Category": "Shared vs Not Shared"}  # Add custom label for clarity
        )

        fig_without_hashtags = px.pie(
            plot_df_without_hashtags,
            values='Count',
            names='Category',
            title="Posts without Hashtags that Got Shared",
            hole=0.4,
            color_discrete_sequence=["green", "lightgreen"],  # Green color for the donut chart
            labels={"Category": "Shared vs Not Shared"}  # Add custom label for clarity
        )

        # Remove default legend from both figures
        fig_with_hashtags.update_layout(showlegend=False)
        fig_without_hashtags.update_layout(showlegend=False)

        # Display the plots side by side using Streamlit columns
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig_with_hashtags, use_container_width=True)

        with col2:
            st.plotly_chart(fig_without_hashtags, use_container_width=True)

        # Add custom legend centered below the plots
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <span style="background-color: green; color: white; padding: 10px;"> </span>
            Shared
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="background-color: lightgreen; color: black; padding: 10px;"> </span>
            Not Shared
        </div>
        """, unsafe_allow_html=True)

        
    
    if selected_plot == "Mentions":
        # Filter posts with and without mentions
        posts_with_mentions = df[df["Number of Mentions (@)"] > 0]
        posts_without_mentions = df[df["Number of Mentions (@)"] == 0]
        
        # Calculate shared vs non-shared for posts with mentions
        shared_with_mentions = posts_with_mentions["# of Boosts"].sum()
        not_shared_with_mentions = len(posts_with_mentions) - shared_with_mentions
        
        # Calculate shared vs non-shared for posts without mentions
        shared_without_mentions = posts_without_mentions["# of Boosts"].sum()
        not_shared_without_mentions = len(posts_without_mentions) - shared_without_mentions
        
        # Prepare data for the plots
        plot_data_with_mentions = {
            "Category": ["Shared", "Not Shared"],
            "Count": [shared_with_mentions, not_shared_with_mentions],
        }
        plot_data_without_mentions = {
            "Category": ["Shared", "Not Shared"],
            "Count": [shared_without_mentions, not_shared_without_mentions],
        }
        
        # Convert plot data to DataFrames
        plot_df_with_mentions = pd.DataFrame(plot_data_with_mentions)
        plot_df_without_mentions = pd.DataFrame(plot_data_without_mentions)
        
        # Create donut plots with a different color scheme (choose new colors)
        fig_with_mentions = px.pie(
            plot_df_with_mentions,
            values="Count",
            names="Category",
            title="Posts with Mentions that Got Shared",
            hole=0.4,
            color_discrete_sequence=["#f1c40f", "#f39c12"],  # Bright Yellow and Warm Yellow
            labels={"Category": "Shared vs Not Shared"}  # Add custom label for clarity
        )
        
        fig_without_mentions = px.pie(
            plot_df_without_mentions,
            values="Count",
            names="Category",
            title="Posts without Mentions that Got Shared",
            hole=0.4,
            color_discrete_sequence=["#f1c40f", "#f39c12"],  # Bright Yellow and Warm Yellow
            labels={"Category": "Shared vs Not Shared"}  # Add custom label for clarity
        )
        
        # Remove default legend from both figures
        fig_with_mentions.update_layout(showlegend=False)
        fig_without_mentions.update_layout(showlegend=False)
        
        # Display the plots side by side using Streamlit columns
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_with_mentions, use_container_width=True)
        with col2:
            st.plotly_chart(fig_without_mentions, use_container_width=True)
        
        # Add custom legend centered below the plots
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <span style="background-color: #f1c40f; color: white; padding: 10px;"> </span>
            Shared
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="background-color: #f39c12; color: black; padding: 10px;"> </span>
            Not Shared
        </div>
        """, unsafe_allow_html=True)

    
    
    if selected_plot == "More characters":
        print()

        # Set a threshold for character count (e.g., 100 characters)
        char_threshold = 100

        # Filter posts based on character count
        posts_with_more_chars = df[df["Post_Length"] > char_threshold]
        posts_with_fewer_chars = df[df["Post_Length"] <= char_threshold]

        # Calculate shared vs non-shared for posts with more characters
        shared_with_more_chars = posts_with_more_chars["# of Boosts"].sum()
        not_shared_with_more_chars = len(posts_with_more_chars) - shared_with_more_chars

        # Calculate shared vs non-shared for posts with fewer characters
        shared_with_fewer_chars = posts_with_fewer_chars["# of Boosts"].sum()
        not_shared_with_fewer_chars = len(posts_with_fewer_chars) - shared_with_fewer_chars

        # Prepare data for the plots
        plot_data_with_more_chars = {
            "Category": ["Shared", "Not Shared"],
            "Count": [shared_with_more_chars, not_shared_with_more_chars],
        }
        
        plot_data_with_fewer_chars = {
            "Category": ["Shared", "Not Shared"],
            "Count": [shared_with_fewer_chars, not_shared_with_fewer_chars],
        }

        # Convert plot data to DataFrames
        plot_df_with_more_chars = pd.DataFrame(plot_data_with_more_chars)
        plot_df_with_fewer_chars = pd.DataFrame(plot_data_with_fewer_chars)

        # Create donut plots
        fig_with_more_chars = px.pie(
            plot_df_with_more_chars,
            values='Count',
            names='Category',
            title="Posts with More Characters that Got Shared",
            hole=0.4,
            color_discrete_sequence=["#6e44ad", "#9b59b6"],  # Purple tones (Dark Purple and Light Purple)
            labels={"Category": "Shared vs Not Shared"}  # Add custom label for clarity
        )

        fig_with_fewer_chars = px.pie(
            plot_df_with_fewer_chars,
            values='Count',
            names='Category',
            title="Posts with Fewer Characters that Got Shared",
            hole=0.4,
            color_discrete_sequence=["#6e44ad", "#9b59b6"],  # Purple tones (Dark Purple and Light Purple)
            labels={"Category": "Shared vs Not Shared"}  # Add custom label for clarity
        )

        # Remove default legend from both figures
        fig_with_more_chars.update_layout(showlegend=False)
        fig_with_fewer_chars.update_layout(showlegend=False)

        # Display the plots side by side using Streamlit columns
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig_with_more_chars, use_container_width=True)

        with col2:
            st.plotly_chart(fig_with_fewer_chars, use_container_width=True)

        # Add custom legend centered below the plots
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <span style="background-color: #6e44ad; color: white; padding: 10px;"> </span>
            Shared
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <span style="background-color: #9b59b6; color: black; padding: 10px;"> </span>
            Not Shared
        </div>
        """, unsafe_allow_html=True)


elif st.session_state["selected_button"] == "MARTINA":
    st.write("Analyze THINGS.")
    
elif st.session_state["selected_button"] == "Conclusions":
    #st.header("Are there any correlationships?")
    fig = px.imshow(df.corr(), text_auto=True, aspect="auto", color_continuous_scale='Viridis')
    fig.update_layout(title="Are there any correlationships?",  # Title added here
                    #title_x=0.5,  # Center the title
                    title_font=dict(size=24, family="Arial", color="white"))  # Optional styling for the title
    st.plotly_chart(fig)





    # Define the gif link
    gifslink = """
    <div style="width:100%;height:0;padding-bottom:72%;position:relative;">
        <iframe src="https://giphy.com/embed/Khi4ihXtrDpfnlZIXh" width="100%" height="100%" style="position:absolute" frameBorder="0" class="giphy-embed" allowFullScreen></iframe>
    </div>
    <p><a href="https://giphy.com/gifs/fallontonight-work-hard-whoopi-goldberg-Khi4ihXtrDpfnlZIXh">via GIPHY</a></p>
    """
    # Create a placeholder to show the gif
    placeholder = st.empty()
    # Display the button
    if st.button("So, here is the answer..."):
        # Show the gif in the placeholder
        placeholder.markdown(gifslink, unsafe_allow_html=True)
        # Wait for 8 seconds
        time.sleep(8)
        # Clear the gif after 8 seconds
        placeholder.empty()

elif st.session_state["selected_button"] == "Next Steps":
    st.header("Future improvements and analyses:")
    st.write("- Greater Data Mining")
    st.write("- Large Language Models (LLM)")
    st.write("- Natural Language Processing (NLP)")
    # URLs
    image_url = "https://www.shutterstock.com/image-vector/coming-soon-on-dark-background-600nw-2364512887.jpg"
    gif_url = "https://giphy.com/embed/esR1eKgmOnxWKR627f"
    # Create a placeholder for the image and gif
    image_placeholder = st.empty()
    gif_placeholder = st.empty()
    # Show the image as a clickable "button"
    image = image_placeholder.image(image_url,  use_container_width =True)
    # Add a click event on the image
    if st.button('.'):
        # Hide the image and show the GIF
        image_placeholder.empty()
        gif_placeholder.markdown(f'<iframe src="{gif_url}" width="100%" height="400" frameBorder="0" class="giphy-embed" allowFullScreen></iframe>', unsafe_allow_html=True)
        # Wait for 5 seconds
        time.sleep(5)
        # Hide the GIF and show the image again
        gif_placeholder.empty()
        image_placeholder.image(image_url,  use_container_width =True)




#else:
#    st.write("Select an option above to get started.")
#
#
#
#
#
#
#
#