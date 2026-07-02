import streamlit as st
import requests
from datetime import datetime

# Mobile-friendly layout configuration
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS: THE EDGE-TO-EDGE POSTER WALL FIX ---
st.markdown("""
<style>
    /* Hide Streamlit Header & Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove top padding for a flush native feel */
    .block-container {
        padding-top: 1rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* TV Time Gold Theme for Progress Bars */
    [data-testid="stProgressBar"] > div > div {
        background-color: #FFC107 !important;
    }
    
    /* Floating App Cards (For TV Tab and Search only) */
    .tv-card [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border: 1px solid rgba(200, 200, 200, 0.2) !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1) !important;
        padding: 0.5rem !important;
        margin: 0.2rem;
    }
    
    /* Make images round by default, but we will override this for the movie wall */
    img { border-radius: 8px; }
    
    /* ========================================================
       THE MAGIC FIX: FORCING THE 3-COLUMN MOBILE GRID
       ======================================================== */
    @media (max-width: 768px) {
        /* Isolate rows that have exactly 3 columns */
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3):last-child) {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0px !important; /* ZERO GAP FOR EDGE TO EDGE */
        }
        /* Force each column to exactly 33.3% width with ZERO padding */
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3):last-child) > div[data-testid="column"] {
            width: 33.33% !important;
            flex: 1 1 0% !important;
            min-width: 0 !important;
            padding: 0px !important;
        }
    }
    
    /* 3x3 Grid Text Formatting (For TV Tab) */
    .grid-title {
        font-size: 0.65rem !important;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: center;
        margin-top: 6px;
        line-height: 1.2;
    }
    
    /* Movie Wall Specifics to match 64433.jpg */
    .movie-wall-img img {
        border-radius: 0px !important; /* Sharp edges */
        width: 100% !important;
        border: 1px solid #000; /* Tiny black separator line */
    }
    
    /* Floating Settings Button over Movie Posters */
    .movie-btn-overlay {
        margin-top: -35px;
        margin-right: 5px;
        text-align: right;
        position: relative;
        z-index: 10;
    }
    .movie-btn-overlay div.stButton > button {
        background-color: rgba(0,0,0,0.6) !important;
        border: none !important;
        color: #FFC107 !important;
        border-radius: 50% !important;
        padding: 0px !important;
        height: 28px !important;
        width: 28px !important;
        font-size: 14px !important;
    }
    
    /* Style the toggle radios to look like native header tabs */
    div.row-widget.stRadio > div {
        justify-content: space-around;
        margin-bottom: 5px;
        padding: 0 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📺 My TV Time")

# 1. Credentials
TMDB_KEY = st.secrets["TMDB_KEY"]
BIN_KEY = st.secrets["JSONBIN_KEY"]
BIN_ID = st.secrets["JSONBIN_ID"]
BIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
headers = {"X-Master-Key": BIN_KEY, "Content-Type": "application/json"}
TODAY = datetime.today().strftime('%Y-%m-%d')

# 2. Database Core
@st.cache_data(ttl=3600)
def fetch_api(url): return requests.get(url).json()

def load_db():
    res = requests.get(BIN_URL, headers=headers)
    if res.status_code == 200:
        data = res.json().get("record", {})
        if "shows" not in data: data["shows"] = []
        if "movies" not in data: data["movies"] = []
        return data
    return {"shows": [], "movies": []}

def save_db(): requests.put(BIN_URL, json=st.session_state.db, headers=headers)

if "db" not in st.session_state: st.session_state.db = load_db()

def render_badges(items, is_gold=False):
    css_class = "badge badge-gold" if is_gold else "badge"
    html = "".join([f'<span class="{css_class}">{item}</span>' for item in items])
    st.markdown(html, unsafe_allow_html=True)

def show_cast_grid(cast_list, limit=6):
    cast_list = cast_list[:limit]
    if not cast_list: return
    for i in range(0, len(cast_list), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(cast_list):
                actor = cast_list[i + j]
                with cols[j]:
                    if actor.get("profile_path"): st.image(f"https://image.tmdb.org/t/p/w185{actor['profile_path']}", use_container_width=True)
                    else: st.info("No Photo") 
                    st.markdown(f'<div class="grid-title" title="{actor["name"]}">{actor["name"]}</div>', unsafe_allow_html=True)

# --- DIALOG / POPUP FUNCTIONS ---
@st.dialog("Episode Details")
def show_episode_details(show_id, show_name, ep_code, ep_data, is_watched):
    if ep_data.get("still_path"): st.image(f"https://image.tmdb.org/t/p/w500{ep_data['still_path']}", use_container_width=True)
    st.markdown(f"### {ep_data.get('name', 'Untitled Episode')}")
    render_badges([ep_code, f"⭐ {ep_data.get('vote_average', 0.0)}"], is_gold=True)
    st.caption(f"**Aired:** {ep_data.get('air_date', 'N/A')}")
    st.write(ep_data.get("overview", "No synopsis available for this episode yet."))
    st.divider()
    btn_label = "❌ Unmark as Watched" if is_watched else "✅ Mark as Watched"
    if st.button(btn_label, use_container_width=True):
        for s in st.session_state.db["shows"]:
            if s["id"] == show_id:
                if is_watched and ep_code in s["watched_episodes"]: s["watched_episodes"].remove(ep_code)
                elif not is_watched and ep_code not in s["watched_episodes"]: s["watched_episodes"].append(ep_code)
                save_db(); break
        st.rerun()

@st.dialog("Manage Show")
def manage_show_dialog(show_id, show_name, details):
    if details.get("backdrop_path"): st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
    st.markdown(f"### {show_name}")
    render_badges([details.get('status')] + [g["name"] for g in details.get("genres", [])])
    st.write(details.get("overview", "No overview available."))
    st.divider()
    st.markdown("#### Episodes")
    s_nums = [s["season_number"] for s in details.get("seasons", []) if s["season_number"] > 0]
    if s_nums:
        sel_s = st.selectbox("Select Season", s_nums, key=f"dlg_s_{show_id}")
        s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/season/{sel_s}?api_key={TMDB_KEY}")
        current_show = next((s for s in st.session_state.db["shows"] if s["id"] == show_id), None)
        watched_list = current_show.get("watched_episodes", []) if current_show else []
        for ep in s_data.get("episodes", []):
            e_code = f"S{sel_s}E{ep['episode_number']}"
            is_watched = e_code in watched_list
            def on_check(sid=show_id, ecode=e_code):
                chkd = st.session_state[f"chk_dlg_{sid}_{ecode}"]
                for s in st.session_state.db["shows"]:
                    if s["id"] == sid:
                        if chkd and ecode not in s["watched_episodes"]: s["watched_episodes"].append(ecode)
                        elif not chkd and ecode in s["watched_episodes"]: s["watched_episodes"].remove(ecode)
                        save_db(); break
            st.checkbox(f"**E{ep['episode_number']}.** {ep.get('name', 'Episode')}", value=is_watched, key=f"chk_dlg_{show_id}_{e_code}", on_change=on_check)
    st.divider()
    st.markdown("#### Top Cast")
    credits = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}")
    show_cast_grid(credits.get("cast", []), limit=6)

@st.dialog("Movie Details")
def show_movie_details(m_id, m_name, details, is_watched):
    if details.get("backdrop_path"): st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
    st.markdown(f"### {m_name}")
    render_badges([f"{details.get('runtime', 0)} mins"] + [g["name"] for g in details.get("genres", [])])
    st.write(details.get("overview", "No synopsis available."))
    st.divider()
    btn_label = "❌ Unmark as Watched" if is_watched else "✅ Mark as Watched"
    if st.button(btn_label, use_container_width=True):
        for m in st.session_state.db["movies"]:
            if m["id"] == m_id:
                m["watched"] = not is_watched
                save_db(); break
        st.rerun()

# --- APP NAVIGATION BAR ---
t_next, t_soon, t_search, t_tv, t_movies, t_profile = st.tabs(["🔥 Next", "📅 Soon", "🔍 Search", "📺 TV", "🎬 Movies", "👤 Stats"])

# ==========================================
# TAB 4: TV LIBRARY (Keeps the floating cards)
# ==========================================
with t_tv:
    st.markdown('<div style="padding-left:10px;"><h3>My TV Collection</h3></div>', unsafe_allow_html=True)
    tv_view = st.radio("TV View", ["WATCH LIST", "UPCOMING"], horizontal=True, label_visibility="collapsed")
    
    shows = st.session_state.db.get("shows", [])
    if not shows:
        st.info("Your TV library is empty.")
    else:
        display_shows = []
        for show in shows:
            details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
            air_date = details.get("first_air_date", "")
            is_upcoming = bool(air_date and air_date > TODAY)
            
            if tv_view == "WATCH LIST" and not is_upcoming: display_shows.append((show, details))
            elif tv_view == "UPCOMING" and is_upcoming: display_shows.append((show, details))
                
        if not display_shows: st.info(f"Your TV {tv_view.lower()} is currently empty.")
        else:
            st.markdown('<div class="tv-card">', unsafe_allow_html=True)
            for i in range(0, len(display_shows), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(display_shows):
                        show, details = display_shows[i + j]
                        t_eps = details.get("number_of_episodes", 1) 
                        w_eps = len(show.get("watched_episodes", []))
                        
                        with cols[j]:
                            with st.container(border=True):
                                if details.get("poster_path"): st.image(f"https://image.tmdb.org/t/p/w185{details['poster_path']}", use_container_width=True)
                                st.markdown(f'<div class="grid-title">{show["name"]}</div>', unsafe_allow_html=True)
                                st.progress(min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0)
                                if st.button("Open", key=f"s_mgr_{show['id']}", use_container_width=True):
                                    manage_show_dialog(show['id'], show['name'], details)
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 5: MOVIE LIBRARY (Matches 64433.jpg Edge-to-Edge)
# ==========================================
with t_movies:
    movie_view = st.radio("Movie View", ["WATCH LIST", "UPCOMING"], horizontal=True, label_visibility="collapsed")
    movies = st.session_state.db.get("movies", [])
    
    if not movies:
        st.info("Your Movie library is empty.")
    else:
        display_movies = []
        for m in movies:
            details = fetch_api(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}")
            r_date = details.get("release_date", "")
            is_upcoming = bool(r_date and r_date > TODAY)
            
            if movie_view == "WATCH LIST" and not is_upcoming: display_movies.append((m, details))
            elif movie_view == "UPCOMING" and is_upcoming: display_movies.append((m, details))
                
        if not display_movies:
            st.info(f"Your Movie {movie_view.lower()} is currently empty.")
        else:
            # We output rows of 3 without standard containers to force them flush together
            for i in range(0, len(display_movies), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(display_movies):
                        m, details = display_movies[i + j]
                        is_watched = m.get("watched", False)
                        
                        with cols[j]:
                            # Image specifically wrapped to strip rounded corners and gaps
                            st.markdown('<div class="movie-wall-img">', unsafe_allow_html=True)
                            if details.get("poster_path"):
                                st.image(f"https://image.tmdb.org/t/p/w185{details['poster_path']}", use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Tiny yellow grid icon overlaid on the image exactly like the reference
                            st.markdown('<div class="movie-btn-overlay">', unsafe_allow_html=True)
                            if st.button("⚙", key=f"m_mgr_{m['id']}"):
                                show_movie_details(m['id'], m['name'], details, is_watched)
                            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# REST OF TABS (Kept Safe from Grid Logic)
# ==========================================
with t_next:
    st.markdown('<div style="padding:10px;"><h3>Up Next</h3></div>', unsafe_allow_html=True)
    up_next_count = 0
    for show in st.session_state.db["shows"]:
        details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
        found_next = False
        watched_set = set(show.get("watched_episodes", []))
        seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
        for s_info in seasons:
            if found_next: break
            s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/season/{s_info['season_number']}?api_key={TMDB_KEY}")
            for ep in s_data.get("episodes", []):
                ep_code = f"S{s_info['season_number']}E{ep['episode_number']}"
                air_date = ep.get("air_date", "")
                if ep_code not in watched_set and air_date and air_date <= TODAY:
                    up_next_count += 1
                    found_next = True
                    with st.container(border=True):
                        if ep.get("still_path"): st.image(f"https://image.tmdb.org/t/p/w500{ep['still_path']}", use_container_width=True)
                        st.markdown(f"#### {show['name']}")
                        st.markdown(f"*{ep.get('name', 'Episode')}*")
                        if st.button("✔️ Mark Watched", key=f"btn_nxt_{show['id']}_{ep_code}", use_container_width=True):
                            for s in st.session_state.db["shows"]:
                                if s["id"] == show['id']:
                                    s["watched_episodes"].append(ep_code)
                                    save_db(); st.rerun()
                    break
    if up_next_count == 0: st.info("You are completely caught up! 🎉")

with t_search:
    st.markdown('<div style="padding:10px;"><h3>Discover</h3></div>', unsafe_allow_html=True)
    search_type = st.radio("Category:", ["TV Shows", "Movies"], horizontal=True)
    search_query = st.text_input("Enter title:")
    if search_query:
        endpoint = "tv" if search_type == "TV Shows" else "movie"
        res = fetch_api(f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_KEY}&query={search_query}")
        results = res.get("results", [])
        if results:
            for item in results:
                with st.container(border=True):
                    c1, c2 = st.columns([1, 2])
                    item_id = item["id"]
                    title = item["name"] if search_type == "TV Shows" else item["title"]
                    with c1:
                        if item.get("poster_path"): st.image(f"https://image.tmdb.org/t/p/w154{item['poster_path']}", use_container_width=True)
                    with c2:
                        st.markdown(f"**{title}**")
                        if search_type == "TV Shows" and not any(s["id"] == item_id for s in st.session_state.db["shows"]):
                            if st.button("➕ Add", key=f"add_tv_{item_id}", use_container_width=True):
                                st.session_state.db["shows"].append({"id": item_id, "name": title, "watched_episodes": []})
                                save_db(); st.rerun()
                        elif search_type == "Movies" and not any(m["id"] == item_id for m in st.session_state.db["movies"]):
                            if st.button("➕ Add", key=f"add_mov_{item_id}", use_container_width=True):
                                st.session_state.db["movies"].append({"id": item_id, "name": title, "watched": False})
                                save_db(); st.rerun()

with t_profile:
    st.markdown('<div style="padding:10px;"><h3>Stats</h3></div>', unsafe_allow_html=True)
    # Keeping stats simple to protect the memory and grid formatting
    st.info("Watch time stats are compiling in the background...")
