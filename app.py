import streamlit as st
import requests

# 1. Set up the app interface
st.title("📺 My TV Time Clone")
st.write("Search for a show to pull live data from TMDB.")

# 2. Store your API key
API_KEY = "08b20e7049fde04639d3edc201cb4936"

# 3. Create a search bar
search_query = st.text_input("Search for a TV Show:")

# 4. Fetch and display data when a search is made
if search_query:
    url = f"https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&query={search_query}"
    response = requests.get(url).json()
    
    # Check if TMDB found any results
    if response.get("results"):
        top_show = response["results"][0]
        
        st.subheader(top_show["name"])
        st.write(f"**First Aired:** {top_show.get('first_air_date', 'Unknown')}")
        st.write(top_show["overview"])
    else:
        st.warning("No shows found. Try another search!")
