import streamlit as st
import requests

st.title("📺 TV Time Clone")

# 1. Credentials
TMDB_KEY = st.secrets["TMDB_KEY"]
BIN_KEY = st.secrets["JSONBIN_KEY"]
BIN_ID = st.secrets["JSONBIN_ID"]
BIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

headers = {
    "X-Master-Key": BIN_KEY,
    "Content-Type": "application/json"
}

# 2. Database Functions (Now with Error Catching!)
def load_db():
    res = requests.get(BIN_URL, headers=headers)
    if res.status_code == 200:
        return res.json().get("record", {"shows": []})
    else:
        st.error(f"Could not load database! Error: {res.text}")
        return {"shows": []}

def save_db():
    res = requests.put(BIN_URL, json=st.session_state.db, headers=headers)
    if res.status_code != 200:
        st.error(f"Could not save! Error: {res.text}")

if "db" not in st.session_state:
    st.session_state.db = load_db()

# 3. Search & Add Section
st.subheader("🔍 Add a Show")
search_query = st.text_input("Search TMDB:")

if search_query:
    url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_KEY}&query={search_query}"
    res = requests.get(url).json()
    
    if res.get("results"):
        top = res["results"][0]
        show_id = top["id"]
        
        st.write(f"**{top['name']}**")
        st.caption(top["overview"])
        
        # Check if already added
        already_added = any(s["id"] == show_id for s in st.session_state.db.get("shows", []))
        
        if not already_added:
            if st.button("Add to Library"):
                # Upgraded format to hold detailed episode tracking
                st.session_state.db["shows"].append({
                    "id": show_id,
                    "name": top["name"],
                    "watched_episodes": [] # Will store unique episode codes like "S1E1"
                })
                save_db()
                st.success("Added!")
                st.rerun()
        else:
            st.success("Already in your library!")

# 4. Library & Episode Tracking Section
st.divider()
st.subheader("📋 My Library")

# Callback function to handle checkbox clicks instantly
def toggle_episode(show_id, ep_code):
    chk_key = f"chk_{show_id}_{ep_code}"
    is_checked = st.session_state[chk_key]
    
    for show in st.session_state.db["shows"]:
        if show["id"] == show_id:
            if is_checked and ep_code not in show["watched_episodes"]:
                show["watched_episodes"].append(ep_code)
            elif not is_checked and ep_code in show["watched_episodes"]:
                show["watched_episodes"].remove(ep_code)
            save_db() # Instantly save to cloud when tapped
            break

if not st.session_state.db.get("shows"):
    st.info("Your library is empty. Add a show above!")
else:
    for show in st.session_state.db["shows"]:
        # Expandable box for each show to save screen space on your phone
        with st.expander(f"📺 {show['name']}"):
            
            # Fetch show details (to get the list of seasons)
            details_url = f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}"
            details = requests.get(details_url).json()
            
            # Filter out "Specials" (Season 0)
            seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
            
            if not seasons:
                st.write("No season data available.")
                continue
            
            # Pick a season from a dropdown
            season_numbers = [s["season_number"] for s in seasons]
            sel_season = st.selectbox("Season", season_numbers, key=f"sel_{show['id']}")
            
            # Fetch specific episode details for that season
            season_url = f"https://api.themoviedb.org/3/tv/{show['id']}/season/{sel_season}?api_key={TMDB_KEY}"
            season_data = requests.get(season_url).json()
            
            st.write("---")
            
            # List all episodes
            for ep in season_data.get("episodes", []):
                ep_num = ep["episode_number"]
                ep_code = f"S{sel_season}E{ep_num}"
                ep_name = ep.get("name", "Episode")
                air_date = ep.get("air_date", "Unknown Date")
                
                # Check Watch Status
                watched_list = show.get("watched_episodes", [])
                is_watched = ep_code in watched_list
                
                # The Watched Checkbox
                st.checkbox(
                    f"**E{ep_num}:** {ep_name} *(Aired: {air_date})*",
                    value=is_watched,
                    key=f"chk_{show['id']}_{ep_code}",
                    on_change=toggle_episode,
                    args=(show['id'], ep_code) # Passes info so the app knows exactly which episode to save
                )
                
                # Short description under the checkbox
                if ep.get("overview"):
                    st.caption(ep["overview"])
