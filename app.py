import streamlit as st
import requests

st.title("📺 My TV Time")

# 1. Credentials
TMDB_KEY = st.secrets["TMDB_KEY"]
BIN_KEY = st.secrets["JSONBIN_KEY"]
BIN_ID = st.secrets["JSONBIN_ID"]
BIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

headers = {
    "X-Master-Key": BIN_KEY,
    "Content-Type": "application/json"
}

# 2. Database Functions (Auto-updates old formats)
def load_db():
    res = requests.get(BIN_URL, headers=headers)
    if res.status_code == 200:
        data = res.json().get("record", {})
        # Ensure both categories exist in your cloud db
        if "shows" not in data: data["shows"] = []
        if "movies" not in data: data["movies"] = []
        return data
    else:
        st.error(f"Could not load database! {res.text}")
        return {"shows": [], "movies": []}

def save_db():
    requests.put(BIN_URL, json=st.session_state.db, headers=headers)

if "db" not in st.session_state:
    st.session_state.db = load_db()

# 3. Search & Add Section
st.subheader("🔍 Add to Library")
search_type = st.radio("What are you looking for?", ["TV Show", "Movie"], horizontal=True)
search_query = st.text_input("Search TMDB:")

if search_query:
    if search_type == "TV Show":
        url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_KEY}&query={search_query}"
        res = requests.get(url).json()
        
        if res.get("results"):
            top = res["results"][0]
            col1, col2 = st.columns([1, 3]) # Splits screen for poster and text
            if top.get("poster_path"):
                col1.image(f"https://image.tmdb.org/t/p/w92{top['poster_path']}")
            
            col2.write(f"**{top['name']}**")
            col2.caption(top["overview"][:100] + "...")
            
            if not any(s["id"] == top["id"] for s in st.session_state.db["shows"]):
                if col2.button("Add TV Show"):
                    st.session_state.db["shows"].append({"id": top["id"], "name": top["name"], "watched_episodes": []})
                    save_db()
                    st.success("Added!")
                    st.rerun()
            else:
                col2.success("Already in Library!")

    else: # Movie Search
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={search_query}"
        res = requests.get(url).json()
        
        if res.get("results"):
            top = res["results"][0]
            col1, col2 = st.columns([1, 3])
            if top.get("poster_path"):
                col1.image(f"https://image.tmdb.org/t/p/w92{top['poster_path']}")
            
            col2.write(f"**{top['title']}**")
            col2.caption(top["overview"][:100] + "...")
            
            if not any(m["id"] == top["id"] for m in st.session_state.db["movies"]):
                if col2.button("Add Movie"):
                    st.session_state.db["movies"].append({"id": top["id"], "name": top["title"], "watched": False})
                    save_db()
                    st.success("Added!")
                    st.rerun()
            else:
                col2.success("Already in Library!")

# 4. Library Sections (Using Tabs)
st.divider()
tab_tv, tab_movies = st.tabs(["📺 TV Shows", "🎬 Movies"])

# --- TV SHOWS TAB ---
with tab_tv:
    def toggle_ep(show_id, ep_code):
        chk_key = f"chk_{show_id}_{ep_code}"
        is_checked = st.session_state[chk_key]
        for s in st.session_state.db["shows"]:
            if s["id"] == show_id:
                if is_checked and ep_code not in s["watched_episodes"]:
                    s["watched_episodes"].append(ep_code)
                elif not is_checked and ep_code in s["watched_episodes"]:
                    s["watched_episodes"].remove(ep_code)
                save_db()
                break

    if not st.session_state.db["shows"]:
        st.info("No TV shows added yet.")
    else:
        watching = []
        finished = []
        
        # Calculate progress and categorize
        for show in st.session_state.db["shows"]:
            details_url = f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}"
            details = requests.get(details_url).json()
            show["details"] = details 
            
            total_eps = details.get("number_of_episodes", 1)
            watched_eps = len(show.get("watched_episodes", []))
            
            if watched_eps >= total_eps and total_eps > 0:
                finished.append(show)
            else:
                watching.append(show)

        def render_shows(show_list):
            for show in show_list:
                details = show["details"]
                total_eps = details.get("number_of_episodes", 1)
                watched_eps = len(show.get("watched_episodes", []))
                
                # Math for the progress bar
                progress_math = watched_eps / total_eps if total_eps > 0 else 0.0
                progress_cap = min(progress_math, 1.0) 
                
                with st.expander(f"📺 {show['name']} ({watched_eps}/{total_eps})"):
                    col1, col2 = st.columns([1, 2])
                    if details.get("poster_path"):
                        col1.image(f"https://image.tmdb.org/t/p/w154{details['poster_path']}")
                    
                    col2.write(f"**Completion:** {int(progress_cap*100)}%")
                    col2.progress(progress_cap)
                    
                    seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
                    if seasons:
                        season_numbers = [s["season_number"] for s in seasons]
                        sel_season = st.selectbox("Season", season_numbers, key=f"sel_{show['id']}")
                        
                        season_url = f"https://api.themoviedb.org/3/tv/{show['id']}/season/{sel_season}?api_key={TMDB_KEY}"
                        season_data = requests.get(season_url).json()
                        
                        st.write("---")
                        for ep in season_data.get("episodes", []):
                            ep_num = ep["episode_number"]
                            ep_code = f"S{sel_season}E{ep_num}"
                            is_watched = ep_code in show.get("watched_episodes", [])
                            
                            st.checkbox(
                                f"**E{ep_num}:** {ep.get('name', 'Episode')}",
                                value=is_watched,
                                key=f"chk_{show['id']}_{ep_code}",
                                on_change=toggle_ep,
                                args=(show['id'], ep_code)
                            )

        if watching:
            st.subheader("Currently Watching")
            render_shows(watching)
        if finished:
            st.subheader("Finished")
            render_shows(finished)

# --- MOVIES TAB ---
with tab_movies:
    def toggle_movie(movie_id):
        chk_key = f"mov_{movie_id}"
        is_checked = st.session_state[chk_key]
        for m in st.session_state.db["movies"]:
            if m["id"] == movie_id:
                m["watched"] = is_checked
                save_db()
                break

    if not st.session_state.db["movies"]:
        st.info("No movies added yet.")
    else:
        to_watch = [m for m in st.session_state.db["movies"] if not m.get("watched")]
        watched = [m for m in st.session_state.db["movies"] if m.get("watched")]
        
        def render_movies(movie_list):
            for m in movie_list:
                details_url = f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}"
                details = requests.get(details_url).json()
                
                col1, col2 = st.columns([1, 4])
                if details.get("poster_path"):
                    col1.image(f"https://image.tmdb.org/t/p/w92{details['poster_path']}")
                
                with col2:
                    st.write(f"**{m['name']}**")
                    st.checkbox("Watched", value=m.get("watched", False), key=f"mov_{m['id']}", on_change=toggle_movie, args=(m['id'],))
                    st.write("---")

        if to_watch:
            st.subheader("Plan to Watch")
            render_movies(to_watch)
        if watched:
            st.subheader("Watched")
            render_movies(watched)
