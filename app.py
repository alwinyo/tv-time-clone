import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="My TV Time", layout="centered")
st.title("📺 My TV Time")

# 1. Credentials & Configuration
TMDB_KEY = st.secrets["TMDB_KEY"]
BIN_KEY = st.secrets["JSONBIN_KEY"]
BIN_ID = st.secrets["JSONBIN_ID"]
BIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

headers = {
    "X-Master-Key": BIN_KEY,
    "Content-Type": "application/json"
}

# Get current date string (YYYY-MM-DD) for air-date validation
TODAY = datetime.today().strftime('%Y-%m-%d')

# 2. Database Core Operations
def load_db():
    res = requests.get(BIN_URL, headers=headers)
    if res.status_code == 200:
        data = res.json().get("record", {})
        if "shows" not in data: data["shows"] = []
        if "movies" not in data: data["movies"] = []
        return data
    else:
        st.error("Failed to sync with cloud storage.")
        return {"shows": [], "movies": []}

def save_db():
    requests.put(BIN_URL, json=st.session_state.db, headers=headers)

if "db" not in st.session_state:
    st.session_state.db = load_db()

# Helper function for quick-logging from the dashboard
def quick_watch_episode(show_id, ep_code):
    for s in st.session_state.db["shows"]:
        if s["id"] == show_id:
            if ep_code not in s["watched_episodes"]:
                s["watched_episodes"].append(ep_code)
                save_db()
                st.toast(f"Marked {ep_code} as watched!")
                st.rerun()

# 3. SMART DASHBOARD: "UP NEXT"
st.subheader("🔥 Up Next to Watch")
up_next_count = 0

if not st.session_state.db["shows"]:
    st.caption("Add shows below to populate your dashboard.")
else:
    for show in st.session_state.db["shows"]:
        # Pull live show structure
        d_url = f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}"
        details = requests.get(d_url).json()
        
        found_next = False
        watched_set = set(show.get("watched_episodes", []))
        
        # Scan seasons chronologically
        seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
        for s_info in seasons:
            if found_next: break
            s_num = s_info["season_number"]
            
            s_url = f"https://api.themoviedb.org/3/tv/{show['id']}/season/{s_num}?api_key={TMDB_KEY}"
            s_data = requests.get(s_url).json()
            
            for ep in s_data.get("episodes", []):
                ep_num = ep["episode_number"]
                ep_code = f"S{s_num}E{ep_num}"
                air_date = ep.get("air_date", "")
                
                # If this episode is unwatched AND has already aired, it is "Up Next"
                if ep_code not in watched_set:
                    if air_date and air_date <= TODAY:
                        up_next_count += 1
                        found_next = True
                        
                        # UI Card layout for Up Next item
                        with st.container(border=True):
                            c1, c2 = st.columns([1, 4])
                            if ep.get("still_path"):
                                c1.image(f"https://image.tmdb.org/t/p/w185{ep['still_path']}")
                            elif details.get("poster_path"):
                                c1.image(f"https://image.tmdb.org/t/p/w92{details['poster_path']}")
                                
                            with c2:
                                st.markdown(f"**{show['name']}** — {ep_code}")
                                st.markdown(f"*{ep.get('name', 'Untitled Episode')}*")
                                if ep.get("overview"):
                                    st.caption(ep["overview"][:120] + "...")
                                
                                # Quick action button directly on dashboard
                                st.button(
                                    "Mark Watched", 
                                    key=f"next_{show['id']}_{ep_code}",
                                    on_click=quick_watch_episode,
                                    args=(show['id'], ep_code)
                                )
                    break # Stop evaluating this show once the true next item is handled

    if up_next_count == 0:
        st.info("🎉 You are completely caught up on all your active shows!")

# 4. MULTI-RESULT SEARCH SECTION
st.divider()
st.subheader("🔍 Global Search & Discover")
search_type = st.radio("Category", ["TV Shows", "Movies"], horizontal=True)
search_query = st.text_input("Enter title:")

if search_query:
    endpoint = "tv" if search_type == "TV Shows" else "movie"
    url = f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_KEY}&query={search_query}"
    res = requests.get(url).json()
    
    # CHANGED: Now pulls all 20 results instead of slicing to 5
    results = res.get("results", []) 
    
    if not results:
        st.warning("No matches found.")
    else:
        st.caption(f"Showing {len(results)} matches. Tap a card to inspect details and add to library.")
        for item in results:
            item_id = item["id"]
            title = item["name"] if search_type == "TV Shows" else item["title"]
            date_label = item.get("first_air_date", "N/A") if search_type == "TV Shows" else item.get("release_date", "N/A")
            
            with st.expander(f"🎬 {title} ({date_label[:4] if date_label else 'N/A'})"):
                col1, col2 = st.columns([1, 2])
                if item.get("poster_path"):
                    col1.image(f"https://image.tmdb.org/t/p/w154{item['poster_path']}")
                
                with col2:
                    st.markdown(f"### {title}")
                    st.markdown(f"**Release/Air Date:** {date_label}")
                    st.markdown(f"**Community Rating:** ⭐ {item.get('vote_average', 0.0)}/10")
                    st.write(item.get("overview", "No synopsis available."))
                    
                    if search_type == "TV Shows":
                        already_added = any(s["id"] == item_id for s in st.session_state.db["shows"])
                        if not already_added:
                            if st.button("Add to Library", key=f"add_tv_{item_id}"):
                                st.session_state.db["shows"].append({"id": item_id, "name": title, "watched_episodes": []})
                                save_db()
                                st.success("Added to TV collection!")
                                st.rerun()
                        else:
                            st.info("Already tracking this series.")
                    else:
                        already_added = any(m["id"] == item_id for m in st.session_state.db["movies"])
                        if not already_added:
                            if st.button("Add to Library", key=f"add_mov_{item_id}"):
                                st.session_state.db["movies"].append({"id": item_id, "name": title, "watched": False})
                                save_db()
                                st.success("Added to Movie collection!")
                                st.rerun()
                        else:
                            st.info("Already tracking this movie.")

# 5. DETAILED LIBRARY VIEWS (With Deep Meta-Data)
st.divider()
tab_tv, tab_movies = st.tabs(["📺 TV Collection", "🎬 Movie Collection"])

with tab_tv:
    if not st.session_state.db["shows"]:
        st.info("Your TV library is currently empty.")
    else:
        for show in st.session_state.db["shows"]:
            # Query advanced metadata directly from show profile
            d_url = f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}"
            details = requests.get(d_url).json()
            
            total_eps = details.get("number_of_episodes", 0)
            watched_eps = len(show.get("watched_episodes", []))
            progress_val = (watched_eps / total_eps) if total_eps > 0 else 0.0
            
            genres = ", ".join([g["name"] for g in details.get("genres", [])])
            networks = ", ".join([n["name"] for n in details.get("networks", [])])
            
            with st.expander(f"📺 {show['name']} ({watched_eps}/{total_eps})"):
                c1, c2 = st.columns([1, 2])
                if details.get("poster_path"):
                    c1.image(f"https://image.tmdb.org/t/p/w185{details['poster_path']}")
                
                with c2:
                    st.markdown(f"### {show['name']}")
                    st.markdown(f"**Genres:** {genres}")
                    st.markdown(f"**Network:** {networks}")
                    st.markdown(f"**Status:** {details.get('status', 'Unknown')}")
                    st.markdown(f"**Total Seasons:** {details.get('number_of_seasons', 0)}")
                    st.progress(min(progress_val, 1.0))
                
                st.markdown("#### Episode Breakdown")
                seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
                if seasons:
                    s_nums = [s["season_number"] for s in seasons]
                    selected_s = st.selectbox("Select Season Focus", s_nums, key=f"lib_s_{show['id']}")
                    
                    s_url = f"https://api.themoviedb.org/3/tv/{show['id']}/season/{selected_s}?api_key={TMDB_KEY}"
                    s_data = requests.get(s_url).json()
                    
                    for ep in s_data.get("episodes", []):
                        e_num = ep["episode_number"]
                        e_code = f"S{selected_s}E{e_num}"
                        is_checked = e_code in show.get("watched_episodes", [])
                        
                        # Checkbox with callback architecture
                        def on_check_change(sid=show['id'], ecode=e_code):
                            k = f"chk_lib_{sid}_{ecode}"
                            checked = st.session_state[k]
                            for s in st.session_state.db["shows"]:
                                if s["id"] == sid:
                                    if checked and ecode not in s["watched_episodes"]: s["watched_episodes"].append(ecode)
                                    elif not checked and ecode in s["watched_episodes"]: s["watched_episodes"].remove(ecode)
                                    save_db()
                                    break
                        
                        st.checkbox(
                            f"**E{e_num}:** {ep.get('name', 'Episode')}",
                            value=is_checked,
                            key=f"chk_lib_{show['id']}_{e_code}",
                            on_change=on_check_change
                        )
                        # Embedded per-episode details
                        st.markdown(f"   *Air Date: {ep.get('air_date', 'N/A')} | ⭐️ Rating: {ep.get('vote_average', 0.0)}/10*")
                        if ep.get("overview"):
                            st.caption(f"   {ep['overview']}")
                        st.write("")

with tab_movies:
    if not st.session_state.db["movies"]:
        st.info("Your Movie library is currently empty.")
    else:
        for m in st.session_state.db["movies"]:
            m_url = f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}"
            details = requests.get(m_url).json()
            
            genres = ", ".join([g["name"] for g in details.get("genres", [])])
            runtime = details.get("runtime", 0)
            
            with st.expander(f"🎬 {m['name']} " + ("✅ (Watched)" if m.get("watched") else "⏳ (Plan to Watch)")):
                c1, c2 = st.columns([1, 2])
                if details.get("poster_path"):
                    c1.image(f"https://image.tmdb.org/t/p/w185{details['poster_path']}")
                
                with c2:
                    st.markdown(f"### {m['name']}")
                    st.markdown(f"**Genres:** {genres}")
                    st.markdown(f"**Runtime:** {runtime} mins")
                    st.markdown(f"**Tagline:** *{details.get('tagline', '')}*")
                    st.write(details.get("overview", ""))
                    
                    def on_movie_change(mid=m['id']):
                        k = f"chk_mov_lib_{mid}"
                        checked = st.session_state[k]
                        for mov in st.session_state.db["movies"]:
                            if mov["id"] == mid:
                                mov["watched"] = checked
                                save_db()
                                break
                    
                    st.checkbox("Mark Movie as Watched", value=m.get("watched", False), key=f"chk_mov_lib_{m['id']}", on_change=on_movie_change)
