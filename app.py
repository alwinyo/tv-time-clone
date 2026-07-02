import streamlit as st
import requests
from datetime import datetime

# Mobile-friendly, dark-mode native layout
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS: TRUE TV TIME UI ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        max-width: 600px; /* Forces phone-like width on desktop */
    }
    img {
        border-radius: 8px; /* Smooth corners for all posters/stills */
    }
    /* Style the tabs to look like the top nav in TV Time */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: space-evenly;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 1. Credentials
TMDB_KEY = st.secrets["TMDB_KEY"]
BIN_KEY = st.secrets["JSONBIN_KEY"]
BIN_ID = st.secrets["JSONBIN_ID"]
BIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
headers = {"X-Master-Key": BIN_KEY, "Content-Type": "application/json"}
TODAY = datetime.today().strftime('%Y-%m-%d')

# 2. Performance Caching
@st.cache_data(ttl=3600)
def fetch_api(url):
    return requests.get(url).json()

# 3. Database Core Operations
def load_db():
    res = requests.get(BIN_URL, headers=headers)
    if res.status_code == 200:
        data = res.json().get("record", {})
        if "shows" not in data: data["shows"] = []
        if "movies" not in data: data["movies"] = []
        return data
    return {"shows": [], "movies": []}

def save_db():
    requests.put(BIN_URL, json=st.session_state.db, headers=headers)

if "db" not in st.session_state:
    st.session_state.db = load_db()

# Main Navigation (Bottom Nav simulation)
nav_shows, nav_movies, nav_search, nav_profile = st.tabs(["📺 Shows", "🎬 Movies", "🔍 Explore", "👤 Profile"])

# ==========================================
# 📺 SHOWS TAB (WATCH LIST & UPCOMING)
# ==========================================
with nav_shows:
    tab_watchlist, tab_upcoming, tab_library = st.tabs(["WATCH LIST", "UPCOMING", "LIBRARY"])
    
    # 1. WATCH LIST (Matches Screenshot 3)
    with tab_watchlist:
        st.write("") # Spacer
        count = 0
        for show in st.session_state.db["shows"]:
            details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
            watched_set = set(show.get("watched_episodes", []))
            found_next = False
            
            seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
            for s_info in seasons:
                if found_next: break
                s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/season/{s_info['season_number']}?api_key={TMDB_KEY}")
                
                for ep in s_data.get("episodes", []):
                    s_num = s_info['season_number']
                    e_num = ep['episode_number']
                    ep_code = f"S{s_num}E{e_num}"
                    air_date = ep.get("air_date", "")
                    
                    if ep_code not in watched_set and air_date and air_date <= TODAY:
                        count += 1
                        found_next = True
                        
                        # THE TV TIME HORIZONTAL CARD
                        with st.container(border=True):
                            # Using vertical_alignment="center" perfectly aligns the text and checkmark
                            c1, c2, c3 = st.columns([1.5, 3, 1], vertical_alignment="center")
                            with c1:
                                if ep.get("still_path"):
                                    st.image(f"https://image.tmdb.org/t/p/w300{ep['still_path']}", use_container_width=True)
                                elif details.get("backdrop_path"):
                                    st.image(f"https://image.tmdb.org/t/p/w300{details['backdrop_path']}", use_container_width=True)
                            with c2:
                                st.markdown(f"<span style='font-size:11px; color:#888; font-weight:bold; letter-spacing:1px;'>{show['name'].upper()} &gt;</span>", unsafe_allow_html=True)
                                st.markdown(f"**S{s_num:02d} | E{e_num:02d}**")
                                st.caption(ep.get("name", "Episode"))
                            with c3:
                                def mark_watched(sid=show['id'], ecode=ep_code):
                                    for s in st.session_state.db["shows"]:
                                        if s["id"] == sid:
                                            s["watched_episodes"].append(ecode)
                                            save_db(); break
                                # Big circular-style checkmark button
                                st.button("✔️", key=f"chk_{show['id']}_{ep_code}", on_click=mark_watched, use_container_width=True)
                        break
        
        if count == 0:
            st.info("You're all caught up!")

    # 2. UPCOMING EPISODES
    with tab_upcoming:
        st.write("")
        count = 0
        for show in st.session_state.db["shows"]:
            details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
            watched_set = set(show.get("watched_episodes", []))
            found_next = False
            
            seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
            for s_info in seasons:
                if found_next: break
                s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/season/{s_info['season_number']}?api_key={TMDB_KEY}")
                
                for ep in s_data.get("episodes", []):
                    s_num = s_info['season_number']
                    e_num = ep['episode_number']
                    ep_code = f"S{s_num}E{e_num}"
                    air_date = ep.get("air_date", "")
                    
                    if ep_code not in watched_set and air_date and air_date > TODAY:
                        count += 1
                        found_next = True
                        air_date_obj = datetime.strptime(air_date, '%Y-%m-%d')
                        days_left = (air_date_obj - datetime.today()).days
                        
                        with st.container(border=True):
                            c1, c2 = st.columns([1.5, 4], vertical_alignment="center")
                            with c1:
                                if details.get("poster_path"): st.image(f"https://image.tmdb.org/t/p/w154{details['poster_path']}")
                            with c2:
                                st.markdown(f"**{show['name']}**")
                                st.markdown(f"S{s_num:02d} | E{e_num:02d} airs in **{days_left} days**")
                                st.caption(f"Airs: {air_date}")
                        break
        if count == 0:
            st.info("No upcoming episodes scheduled yet.")
            
    # 3. SHOWS LIBRARY (GRID)
    with tab_library:
        st.write("")
        cols = st.columns(3)
        for idx, show in enumerate(st.session_state.db["shows"]):
            details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
            with cols[idx % 3]:
                if details.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w342{details['poster_path']}", use_container_width=True)
                st.button("Info", key=f"btn_s_lib_{show['id']}", use_container_width=True)

# ==========================================
# 🎬 MOVIES TAB (PURE POSTER GRID) - Matches Screenshot 4
# ==========================================
@st.dialog("Movie Actions")
def movie_action_dialog(m_id, m_name, is_watched):
    st.markdown(f"### {m_name}")
    btn_lbl = "❌ Remove from Watched" if is_watched else "✅ Mark as Watched"
    if st.button(btn_lbl, use_container_width=True):
        for m in st.session_state.db["movies"]:
            if m["id"] == m_id:
                m["watched"] = not is_watched
                save_db(); st.rerun()

with nav_movies:
    st.write("")
    if not st.session_state.db["movies"]:
        st.info("No movies added yet.")
    
    # 3-Column pure poster grid
    cols = st.columns(3)
    for idx, m in enumerate(st.session_state.db["movies"]):
        details = fetch_api(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}")
        with cols[idx % 3]:
            if details.get("poster_path"):
                st.image(f"https://image.tmdb.org/t/p/w342{details['poster_path']}", use_container_width=True)
            # A tiny button under the poster to manage it, keeping it visually clean
            if st.button(m['name'][:12] + "..", key=f"grid_m_{m['id']}", use_container_width=True):
                movie_action_dialog(m['id'], m['name'], m.get("watched", False))

# ==========================================
# 🔍 EXPLORE TAB
# ==========================================
with nav_search:
    st.write("")
    search_type = st.radio("Search for:", ["TV Shows", "Movies"], horizontal=True, label_visibility="collapsed")
    search_query = st.text_input("Enter title...", placeholder="Search TMDB...")

    if search_query:
        endpoint = "tv" if search_type == "TV Shows" else "movie"
        res = fetch_api(f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_KEY}&query={search_query}")
        results = res.get("results", [])
        
        if results:
            cols = st.columns(3)
            for idx, item in enumerate(results):
                with cols[idx % 3]:
                    item_id = item["id"]
                    title = item["name"] if search_type == "TV Shows" else item["title"]
                    
                    if item.get("poster_path"): 
                        st.image(f"https://image.tmdb.org/t/p/w342{item['poster_path']}", use_container_width=True)
                    
                    if search_type == "TV Shows":
                        if not any(s["id"] == item_id for s in st.session_state.db["shows"]):
                            if st.button("➕ Add", key=f"add_tv_{item_id}", use_container_width=True):
                                st.session_state.db["shows"].append({"id": item_id, "name": title, "watched_episodes": []})
                                save_db(); st.rerun()
                        else:
                            st.button("✔️ Added", key=f"dsbl_tv_{item_id}", disabled=True, use_container_width=True)
                    else:
                        if not any(m["id"] == item_id for m in st.session_state.db["movies"]):
                            if st.button("➕ Add", key=f"add_mov_{item_id}", use_container_width=True):
                                st.session_state.db["movies"].append({"id": item_id, "name": title, "watched": False})
                                save_db(); st.rerun()
                        else:
                            st.button("✔️ Added", key=f"dsbl_mov_{item_id}", disabled=True, use_container_width=True)

# ==========================================
# 👤 PROFILE TAB
# ==========================================
with nav_profile:
    st.markdown("## My TV Time Stats")
    
    eps_watched = sum([len(s.get("watched_episodes", [])) for s in st.session_state.db["shows"]])
    movs_watched = sum([1 for m in st.session_state.db["movies"] if m.get("watched", False)])
    
    c1, c2 = st.columns(2)
    with c1:
        st.container(border=True).metric("Episodes Watched", eps_watched)
    with c2:
        st.container(border=True).metric("Movies Watched", movs_watched)
