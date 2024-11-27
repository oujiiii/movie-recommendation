import streamlit as st
import pickle
import requests
import pandas as pd

# Function to fetch movie posters
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    if poster_path:
        full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return full_path
    else:
        return "https://via.placeholder.com/500"  # Placeholder image if no poster is available

# Load data
movies = pickle.load(open("movies_list.pkl", 'rb'))  # Ensure movies_list.pkl includes 'genre' and 'id'
similarity = pickle.load(open("similarity.pkl", 'rb'))

# Streamlit header
st.header("Movie Recommender System")

# User input for genres
genres = movies['genre'].str.split(',').explode().dropna().unique()  # Extract unique genres
selected_genres = st.multiselect("Select genres:", genres)

# User option to show all movies or limit recommendations
show_all = st.checkbox("Show all matching movies", value=False)

# User input for number of recommendations (only shown if "Show all" is unchecked)
top_n = 5  # Default value
if not show_all:
    top_n = st.slider("Number of recommendations:", min_value=1, max_value=100, value=5)

# Function to recommend movies based on genres
def recommend_by_genres(genres, top_n=None):
    if not genres:
        return [], []  # No genres selected

    recommended_movies = []
    recommended_posters = []

    for genre in genres:
        # Filter movies matching the genre
        genre_movies = movies[movies['genre'].str.contains(genre, case=False, na=False)]
        for index, row in genre_movies.iterrows():
            movie_index = row.name  # Get the movie index in the dataset
            distances = list(enumerate(similarity[movie_index]))
            distances = sorted(distances, reverse=True, key=lambda x: x[1])[1:]  # Skip the movie itself

            # Add recommendations
            for i in distances:
                movie_title = movies.iloc[i[0]]['title']
                movie_id = movies.iloc[i[0]]['id']
                if movie_title not in recommended_movies:  # Avoid duplicates
                    recommended_movies.append(movie_title)
                    recommended_posters.append(fetch_poster(movie_id))
                    if top_n and len(recommended_movies) >= top_n:  # Stop when top_n is reached
                        break
            if top_n and len(recommended_movies) >= top_n:
                break

        if top_n and len(recommended_movies) >= top_n:
            break

    return recommended_movies, recommended_posters

# Show recommendations
if st.button("Show Recommendations"):
    if not selected_genres:
        st.write("Please select at least one genre.")
    else:
        movie_names, movie_posters = recommend_by_genres(selected_genres, None if show_all else top_n)
        if not movie_names:
            st.write("No recommendations available for the selected genres.")
        else:
            # Display recommendations
            num_cols = 5  # Number of columns to display in a row
            for i in range(0, len(movie_names), num_cols):
                cols = st.columns(num_cols)
                for idx, col in enumerate(cols):
                    if i + idx < len(movie_names):
                        with col:
                            st.text(movie_names[i + idx])
                            st.image(movie_posters[i + idx])
