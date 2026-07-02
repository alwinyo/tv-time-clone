import streamlit as st
import requests

st.title("📺 My TV Time Clone")

# 1. Pull hidden keys from Streamlit Secrets
TMDB_KEY = st.secrets["TMDB_KEY"]
BIN_KEY = st.secrets["JSONBIN_KEY"]
BIN_ID = st.secrets["JSONBIN_ID"]
BIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

headers = {
    "X-Master-Key": BIN_KEY,
    "Content-Type": "application/json"
}

# 2. Database Functions
def load_watchlist():
    response = requests.get(BIN_URL, headers=headers)
    if response.status_code == 200:
        return response.json()["record"]
    return []

def save_watchlist(data):
    requests.put(BIN_URL, json=data, headers=headers)

# 3. App Logic - Initialize the list
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# --- SEARCH SECTION ---
st.subheader("🔍 Search & Add")
search_query = st.text_input("Find a TV Show:")

if search_query:
    url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_KEY}&query={search_query}"
    response = requests.get(url).json()
    
    if response.get("results"):
        top_show = response["results"][0]
        show_name = top_show["name"]
        show_id = top_show["id"]
        
        st.write(f"**{show_name}**")
        st.write(top_show["overview"])
        
        if st.button("Add to Watchlist"):
            # Check if it's already in the list to prevent duplicates
            if not any(show["id"] == show_id for show in st.session_state.watchlist):
                st.session_state.watchlist.append({
                    "name": show_name,
                    "id": show_id,
                    "episodes_watched": 0
                })
                save_watchlist(st.session_state.watchlist)
                st.success(f"Added {show_name}!")
            else:
                st.warning("This show is already in your watchlist.")

# --- WATCHLIST SECTION ---
st.divider()
st.subheader("📋 My Watchlist")

if not st.session_state.watchlist:
    st.write("Your watchlist is empty. Search above to add some shows!")
else:
    for show in st.session_state.watchlist:
        st.write(f"**{show['name']}** — Episodes Watched: {show['episodes_watched']}")
        
        # The +1 Button
        if st.button(f"+1 Episode", key=f"add_{show['id']}"):
            show["episodes_watched"] += 1
            save_watchlist(st.session_state.watchlist)
            st.rerun()
