import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# Mobile-friendly layout configuration
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")

# Force clear session memory
if st.button("🔄 Refresh Data from Cloud"):
    del st.session_state.db
    st.rerun()

# --- CUSTOM CSS: SMART MOBILE GRID & APP STYLING ---
st.markdown("""
<style>
    /* Hide Streamlit Header & Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }
    
    img {
        border-radius: 8px !important;
    }
    
    [data-testid="stProgressBar"] > div > div {
        background-color: #FFC107 !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border: 1px solid rgba(200, 200, 200, 0.2) !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1) !important;
        padding: 0.5rem !important;
    }
    
    div.stButton > button {
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.2s;
        padding: 2px 5px !important;
        font-size: 0.75rem !important;
    }
    div.stButton > button:active {
        transform: scale(0.95);
    }
    
    button[kind="primary"] {
        background-color: #FFC107 !important;
        color: #000 !important;
        border: none !important;
    }
    button[kind="secondary"] {
        background-color: #222 !important;
        color: #ccc !important;
        border: 1px solid #444 !important;
    }
    
    .ep-toggle-btn div.stButton > button {
        background: transparent !important;
        border: none !important;
        color: #888 !important;
        font-size: 0.9rem !important;
        padding: 0 !important;
        margin-top: 6px !important; 
        box-shadow: none !important;
    }
    
    .hist-toggle-btn div.stButton > button {
        background: transparent !important;
        border: none !important;
        color: #888 !important;
        font-size: 1.1rem !important;
        padding: 0 !important;
        margin-top: 15px !important;
        box-shadow: none !important;
    }
    
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3):last-child) {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 4px !important; 
        }
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3):last-child) > div[data-testid="column"] {
            width: 33.33% !important;
            flex: 1 1 0% !important;
            min-width: 0 !important;
            padding: 0 !important;
        }
    }
    
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
    
    .badge {
        display: inline-block;
        background-color: #333333;
        color: #FFFFFF;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 6px;
    }
    .badge-gold {
        background-color: #FFC107;
        color: #000000;
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
        if "history" not in data: data["history"] = []
        return data
    return {"shows": [], "movies": [], "history": []}

def save_db():
    requests.put(BIN_URL, json=st.session_state.db, headers=headers)

if "db" not in st.session_state:
    st.session_state.db = load_db()

# --- HELPERS ---
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
                    encoded_name = actor['name'].replace(" ", "+")
                    imdb_url = f"https://www.imdb.com/find/?q={encoded_name}"
                    img_url = f"https://image.tmdb.org/t/p/w185{actor['profile_path']}" if actor.get("profile_path") else "https://via.placeholder.com/185x278/222222/888888?text=No+Photo"
                    html = f'<a href="{imdb_url}" target="_blank" style="text-decoration:none; color:inherit;"><img src="{img_url}" style="width:100%; border-radius:8px; display:block;"><div class="grid-title">{actor["name"]}</div></a>'
                    st.markdown(html, unsafe_allow_html=True)

# --- DIALOG / POPUP FUNCTIONS ---
@st.dialog("Episode Details")
def show_episode_details(show_id, show_name, ep_code, ep_data, is_watched):
    if ep_data.get("still_path"): st.image(f"https://image.tmdb.org/t/p/w500{ep_data['still_path']}", use_container_width=True)
    st.markdown(f"### {ep_data.get('name', 'Untitled Episode')}")
    render_badges([ep_code, f"⭐ {ep_data.get('vote_average', 0.0)}"], is_gold=True)
    st.caption(f"**Aired:** {ep_data.get('air_date', 'N/A')}")
    st.write(ep_data.get("overview", "No synopsis available for this episode yet."))
    
    st.divider()
    st.markdown("#### Series Regulars")
    credits = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}")
    show_cast_grid(credits.get("cast", []), limit=6)
    
    st.divider()
    btn_label = "❌ Unmark as Watched" if is_watched else "✅ Mark as Watched"
    if st.button(btn_label, use_container_width=True):
        for s in st.session_state.db["shows"]:
            if s["id"] == show_id:
                if is_watched and ep_code in s["watched_episodes"]: 
                    s["watched_episodes"].remove(ep_code)
                    st.session_state.db["history"] = [h for h in st.session_state.db.get("history", []) if not (h["type"]=="tv" and h["id"]==show_id and h["detail"]==ep_code)]
                elif not is_watched and ep_code not in s["watched_episodes"]: 
                    s["watched_episodes"].append(ep_code)
                    st.session_state.db.setdefault("history", []).append({"type": "tv", "id": show_id, "title": show_name, "detail": ep_code, "watched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                save_db(); break
        st.rerun()

@st.dialog("Manage Show")
def manage_show_dialog(show_id, show_name, details):
    if details.get("backdrop_path"): st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
    st.markdown(f"### {show_name}")
    
    genres = [g["name"] for g in details.get("genres", [])]
    render_badges([details.get('status')] + genres)
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
            info_key = f"view_info_{show_id}_{e_code}"
            
            def on_check(sid=show_id, sname=show_name, ecode=e_code):
                chkd = st.session_state[f"chk_dlg_{sid}_{ecode}"]
                for s in st.session_state.db["shows"]:
                    if s["id"] == sid:
                        if chkd and ecode not in s["watched_episodes"]: 
                            s["watched_episodes"].append(ecode)
                            st.session_state.db.setdefault("history", []).append({"type": "tv", "id": sid, "title": sname, "detail": ecode, "watched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                        elif not chkd and ecode in s["watched_episodes"]: 
                            s["watched_episodes"].remove(ecode)
                            st.session_state.db["history"] = [h for h in st.session_state.db.get("history", []) if not (h["type"]=="tv" and h["id"]==sid and h["detail"]==ecode)]
                        save_db(); break
            
            ep_col1, ep_col2 = st.columns([6, 1])
            with ep_col1:
                st.checkbox(f"**E{ep['episode_number']}.** {ep.get('name', 'Episode')}", value=is_watched, key=f"chk_dlg_{show_id}_{e_code}", on_change=on_check)
            with ep_col2:
                st.markdown('<div class="ep-toggle-btn">', unsafe_allow_html=True)
                def toggle_info(k=info_key): st.session_state[k] = not st.session_state.get(k, False)
                is_open = st.session_state.get(info_key, False)
                st.button("▲" if is_open else "▼", key=f"btn_i_{show_id}_{e_code}", on_click=toggle_info)
                st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.get(info_key, False):
                with st.container(border=True):
                    if ep.get("still_path"): st.image(f"https://image.tmdb.org/t/p/w500{ep['still_path']}", use_container_width=True)
                    st.caption(f"⭐ {ep.get('vote_average', 0.0)} | **Aired:** {ep.get('air_date', 'N/A')}")
                    st.write(ep.get("overview", "No synopsis available."))

    st.divider()
    st.markdown("#### Top Cast")
    credits = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}")
    show_cast_grid(credits.get("cast", []), limit=6)

@st.dialog("Movie Details")
def show_movie_details(m_id, m_name, details, is_watched):
    if details.get("backdrop_path"): st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
    st.markdown(f"### {m_name}")
    
    genres = [g["name"] for g in details.get("genres", [])]
    render_badges([f"{details.get('runtime', 0)} mins"] + genres)
    st.write(details.get("overview", "No synopsis available."))
    
    st.divider()
    st.markdown("#### Top Cast")
    credits = fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}/credits?api_key={TMDB_KEY}")
    show_cast_grid(credits.get("cast", []), limit=6)
    
    st.divider()
    btn_label = "❌ Unmark as Watched" if is_watched else "✅ Mark as Watched"
    if st.button(btn_label, use_container_width=True):
        for m in st.session_state.db["movies"]:
            if m["id"] == m_id:
                m["watched"] = not is_watched
                if m["watched"]:
                    st.session_state.db.setdefault("history", []).append({"type": "movie", "id": m_id, "title": m_name, "detail": "", "watched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                else:
                    st.session_state.db["history"] = [h for h in st.session_state.db.get("history", []) if not (h["type"]=="movie" and h["id"]==m_id)]
                save_db(); break
        st.rerun()

# --- APP NAVIGATION BAR ---
t_next, t_soon, t_search, t_tv, t_movies, t_profile = st.tabs(["🔥 Next", "📅 Soon", "🔍 Search", "📺 TV", "🎬 Movies", "👤 Profile"])

# ==========================================
# TAB 1: UP NEXT DASHBOARD (WITH SORTING)
# ==========================================
with t_next:
    st.markdown("### Up Next to Watch")
    next_sort = st.selectbox("Sort Library by:", ["Recently Added", "Alphabetical", "Release Date"], key="sort_next")
    
    up_next_items = []
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
                    up_next_items.append({"show": show, "details": details, "ep": ep, "ep_code": ep_code, "air_date": air_date})
                    found_next = True; break

    if next_sort == "Alphabetical": up_next_items.sort(key=lambda x: x["show"]["name"].lower())
    elif next_sort == "Release Date": up_next_items.sort(key=lambda x: x["air_date"] or "1900-01-01")

    if not up_next_items: st.info("You are completely caught up! 🎉")
    else:
        for item in up_next_items:
            show, details, ep, ep_code = item["show"], item["details"], item["ep"], item["ep_code"]
            with st.container(border=True):
                if ep.get("still_path"): st.image(f"https://image.tmdb.org/t/p/w500{ep['still_path']}", use_container_width=True)
                elif details.get("backdrop_path"): st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
                st.markdown(f"#### {show['name']}")
                render_badges([ep_code, "Up Next"], is_gold=True)
                st.markdown(f"*{ep.get('name', 'Episode')}*")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("ℹ️ Info", key=f"info_next_{show['id']}_{ep_code}", use_container_width=True):
                        show_episode_details(show['id'], show['name'], ep_code, ep, is_watched=False)
                with c2:
                    def fast_watch(sid=show['id'], sname=show['name'], ecode=ep_code):
                        for s in st.session_state.db["shows"]:
                            if s["id"] == sid:
                                s["watched_episodes"].append(ecode)
                                st.session_state.db.setdefault("history", []).append({"type": "tv", "id": sid, "title": sname, "detail": ecode, "watched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                                save_db(); st.toast("Watched! ✅"); break
                    st.button("✔️ Watched", key=f"btn_next_{show['id']}_{ep_code}", on_click=fast_watch, use_container_width=True)

# ==========================================
# TAB 2: UPCOMING CALENDAR
# ==========================================
with t_soon:
    st.markdown("### Upcoming Episodes")
    upcoming_count = 0
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
                if ep_code not in watched_set and air_date and air_date > TODAY:
                    upcoming_count += 1; found_next = True
                    days_left = (datetime.strptime(air_date, '%Y-%m-%d') - datetime.today()).days
                    with st.container(border=True):
                        if ep.get("still_path"): st.image(f"https://image.tmdb.org/t/p/w500{ep['still_path']}", use_container_width=True)
                        elif details.get("backdrop_path"): st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
                        st.markdown(f"#### {show['name']}")
                        render_badges([ep_code, f"In {days_left} days"], is_gold=False)
                        st.markdown(f"*{ep.get('name', 'Episode')}*")
                        st.caption(f"Air Date: {air_date}")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("ℹ️ Info", key=f"info_soon_{show['id']}_{ep_code}", use_container_width=True):
                                show_episode_details(show['id'], show['name'], ep_code, ep, is_watched=False)
                        with c2:
                            def fast_watch_soon(sid=show['id'], sname=show['name'], ecode=ep_code):
                                for s in st.session_state.db["shows"]:
                                    if s["id"] == sid:
                                        s["watched_episodes"].append(ecode)
                                        st.session_state.db.setdefault("history", []).append({"type": "tv", "id": sid, "title": sname, "detail": ecode, "watched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                                        save_db(); st.toast("Watched! ✅"); break
                            st.button("✔️ Watched", key=f"btn_soon_{show['id']}_{ep_code}", on_click=fast_watch_soon, use_container_width=True)
                    break
    if upcoming_count == 0: st.info("No upcoming episodes scheduled yet.")

# ==========================================
# TAB 3: GLOBAL SEARCH 
# ==========================================
with t_search:
    st.markdown("### Discover")
    search_type = st.radio("Category:", ["TV Shows", "Movies"], horizontal=True)
    search_query = st.text_input("Enter title to search:")

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
                        render_badges([f"⭐ {item.get('vote_average', 0.0)}"])
                        if search_type == "TV Shows":
                            if not any(s["id"] == item_id for s in st.session_state.db["shows"]):
                                if st.button("➕ Add", key=f"add_tv_{item_id}", use_container_width=True):
                                    st.session_state.db["shows"].append({"id": item_id, "name": title, "watched_episodes": []})
                                    save_db(); st.toast("Added!"); st.rerun()
                            else: st.button("✔️ Added", key=f"dsbl_tv_{item_id}", disabled=True, use_container_width=True)
                        else:
                            if not any(m["id"] == item_id for m in st.session_state.db["movies"]):
                                if st.button("➕ Add", key=f"add_mov_{item_id}", use_container_width=True):
                                    st.session_state.db["movies"].append({"id": item_id, "name": title, "watched": False})
                                    save_db(); st.toast("Added!"); st.rerun()
                            else: st.button("✔️ Added", key=f"dsbl_mov_{item_id}", disabled=True, use_container_width=True)

# ==========================================
# TAB 4: TV LIBRARY 
# ==========================================
with t_tv:
    st.markdown("### My TV Collection")
    if "tv_tab" not in st.session_state: st.session_state.tv_tab = "WATCHLIST"
        
    c1, c2, c3 = st.columns(3)
    if c1.button("Watchlist", type="primary" if st.session_state.tv_tab == "WATCHLIST" else "secondary", use_container_width=True, key="tv_wl"): st.session_state.tv_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.tv_tab == "UPCOMING" else "secondary", use_container_width=True, key="tv_up"): st.session_state.tv_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.tv_tab == "WATCHED" else "secondary", use_container_width=True, key="tv_wd"): st.session_state.tv_tab = "WATCHED"; st.rerun()
        
    tv_sort = st.selectbox("Sort Library by:", ["Recently Added", "Alphabetical", "Release Date"], key="sort_tv")
    st.divider()
    
    shows = st.session_state.db.get("shows", [])
    if not shows: st.info("Your TV library is empty.")
    else:
        display_shows = []
        for show in shows:
            details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
            air_date = details.get("first_air_date", "")
            t_eps = details.get("number_of_episodes", 1) 
            w_eps = len(show.get("watched_episodes", []))
            is_upcoming = bool(air_date and air_date > TODAY)
            is_completed = (w_eps >= t_eps and t_eps > 0)
            
            if st.session_state.tv_tab == "WATCHED" and is_completed: display_shows.append((show, details, t_eps, w_eps))
            elif st.session_state.tv_tab == "UPCOMING" and is_upcoming and not is_completed: display_shows.append((show, details, t_eps, w_eps))
            elif st.session_state.tv_tab == "WATCHLIST" and not is_upcoming and not is_completed: display_shows.append((show, details, t_eps, w_eps))
                
        if tv_sort == "Alphabetical": display_shows.sort(key=lambda x: x[0]['name'].lower())
        elif tv_sort == "Release Date": display_shows.sort(key=lambda x: x[1].get('first_air_date', '1900-01-01') or '1900-01-01', reverse=True)
                
        if not display_shows: st.info(f"Your {st.session_state.tv_tab.lower()} is empty.")
        else:
            for i in range(0, len(display_shows), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(display_shows):
                        show, details, t_eps, w_eps = display_shows[i + j]
                        with cols[j]:
                            with st.container(border=True):
                                if details.get("poster_path"): st.image(f"https://image.tmdb.org/t/p/w185{details['poster_path']}", use_container_width=True)
                                st.markdown(f'<div class="grid-title" title="{show["name"]}">{show["name"]}</div>', unsafe_allow_html=True)
                                st.progress(min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0)
                                if st.button("DETAILS", key=f"s_mgr_{show['id']}", use_container_width=True): manage_show_dialog(show['id'], show['name'], details)

# ==========================================
# TAB 5: MOVIE LIBRARY 
# ==========================================
with t_movies:
    st.markdown("""<style>.movie-wall-btn div.stButton > button { border: none !important; background-color: transparent !important; color: #aaa !important; font-size: 0.7rem !important; padding: 0 !important; margin-top: 2px !important; margin-bottom: 5px !important; text-transform: uppercase; letter-spacing: 1px; }.movie-poster-sharp img { border-radius: 0px !important; }</style>""", unsafe_allow_html=True)
    st.markdown("### My Movies")
    if "mov_tab" not in st.session_state: st.session_state.mov_tab = "WATCHLIST"
        
    c1, c2, c3 = st.columns(3)
    if c1.button("Watchlist", type="primary" if st.session_state.mov_tab == "WATCHLIST" else "secondary", use_container_width=True, key="m_wl"): st.session_state.mov_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.mov_tab == "UPCOMING" else "secondary", use_container_width=True, key="m_up"): st.session_state.mov_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.mov_tab == "WATCHED" else "secondary", use_container_width=True, key="m_wd"): st.session_state.mov_tab = "WATCHED"; st.rerun()
        
    mov_sort = st.selectbox("Sort Library by:", ["Recently Added", "Alphabetical", "Release Date"], key="sort_mov")
    st.divider()
    
    movies = st.session_state.db.get("movies", [])
    if not movies: st.info("Your Movie library is empty.")
    else:
        display_movies = []
        for m in movies:
            details = fetch_api(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}")
            r_date = details.get("release_date", "")
            is_watched = m.get("watched", False)
            is_upcoming = bool(r_date and r_date > TODAY)
            
            if st.session_state.mov_tab == "WATCHED" and is_watched: display_movies.append((m, details, is_watched))
            elif st.session_state.mov_tab == "UPCOMING" and is_upcoming and not is_watched: display_movies.append((m, details, is_watched))
            elif st.session_state.mov_tab == "WATCHLIST" and not is_upcoming and not is_watched: display_movies.append((m, details, is_watched))
                
        if mov_sort == "Alphabetical": display_movies.sort(key=lambda x: x[0]['name'].lower())
        elif mov_sort == "Release Date": display_movies.sort(key=lambda x: x[1].get('release_date', '1900-01-01') or '1900-01-01', reverse=True)
                
        if not display_movies: st.info(f"Your {st.session_state.mov_tab.lower()} is empty.")
        else:
            for i in range(0, len(display_movies), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(display_movies):
                        m, details, is_watched = display_movies[i + j]
                        st.markdown('<div class="movie-poster-sharp">', unsafe_allow_html=True)
                        if details.get("poster_path"): st.image(f"https://image.tmdb.org/t/p/w185{details['poster_path']}", use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                        if st.button("DETAILS", key=f"m_mgr_{m['id']}", use_container_width=True): show_movie_details(m['id'], m['name'], details, is_watched)
                        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 6: PROFILE & LIVE DATA IMPORT ENGINE
# ==========================================
with t_profile:
    st.markdown("### Lifetime Stats")
    history = st.session_state.db.get("history", [])
    
    total_tv_mins = 0
    total_episodes_watched = len([h for h in history if h["type"] == "tv"])
    total_movies_watched = len([h for h in history if h["type"] == "movie"])
    
    # Fast estimations for lifetime totals
    for show in st.session_state.db["shows"]:
        total_tv_mins += (len(show.get("watched_episodes", [])) * 45)
    total_mov_mins = total_movies_watched * 110
    
    total_mins = total_tv_mins + total_mov_mins
    months = total_mins // 43800
    days = (total_mins % 43800) // 1440
    hours = (total_mins % 1440) // 60
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Months", f"{months}")
        col2.metric("Days", f"{days}")
        col3.metric("Hours", f"{hours}")
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.metric("Episodes", total_episodes_watched)
        c2.metric("Movies", total_movies_watched)
        
    st.divider()
    
    # --- LIVE METRIC MONTHLY BAR CHART ---
    st.markdown("### 📊 Watch Activity")
    if history:
        monthly_data = {}
        for h in history:
            try:
                dt = datetime.strptime(h["watched_at"][:19], '%Y-%m-%d %H:%M:%S')
            except:
                dt = datetime.strptime(h["watched_at"][:10], '%Y-%m-%d')
            month_key = dt.strftime('%Y-%m')
            if month_key not in monthly_data: monthly_data[month_key] = {"Series": 0, "Movies": 0}
            if h["type"] == "tv": monthly_data[month_key]["Series"] += 1
            else: monthly_data[month_key]["Movies"] += 1
        
        df = pd.DataFrame.from_dict(monthly_data, orient='index').sort_index()
        df.index = pd.to_datetime(df.index).strftime('%b %Y')
        st.bar_chart(df, color=["#FFC107", "#555555"])

    st.divider()
    
    # --- MONTHLY WATCH HISTORY JOURNAL ---
    st.markdown("### 📜 Watch History Journal")
    h_tv, h_mov = st.tabs(["📺 Series", "🎬 Movies"])
    history_sorted = sorted(history, key=lambda x: x["watched_at"], reverse=True)
    
    with h_tv:
        tv_hist = [h for h in history_sorted if h["type"] == "tv"]
        if not tv_hist: st.info("No series history loaded.")
        else:
            grouped_tv = {}
            for item in tv_hist:
                try: dt = datetime.strptime(item["watched_at"][:19], '%Y-%m-%d %H:%M:%S')
                except: dt = datetime.strptime(item["watched_at"][:10], '%Y-%m-%d')
                grouped_tv.setdefault(dt.strftime('%B %Y'), []).append((item, dt))
            
            for month_str, items in grouped_tv.items():
                st.markdown(f"#### {month_str}")
                for item, dt in items:
                    info_key = f"hist_info_tv_{item['id']}_{item['detail']}_{item['watched_at']}"
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([5, 4, 1])
                        with c1: st.markdown(f"**{item['title']}** \n\n*{item['detail']}*")
                        with c2: st.caption(dt.strftime('%b %d • %I:%M %p'))
                        with c3:
                            st.markdown('<div class="hist-toggle-btn">', unsafe_allow_html=True)
                            def t_info(k=info_key): st.session_state[k] = not st.session_state.get(k, False)
                            is_open = st.session_state.get(info_key, False)
                            st.button("▲" if is_open else "▼", key=f"btn_{info_key}", on_click=t_info)
                            st.markdown('</div>', unsafe_allow_html=True)
                    if is_open:
                        try:
                            s_part, e_part = item["detail"].split("E")
                            ep_data = fetch_api(f"https://api.themoviedb.org/3/tv/{item['id']}/season/{s_part.replace('S','')}/episode/{e_num}?api_key={TMDB_KEY}")
                        except: ep_data = {}
                        with st.container(border=True):
                            if ep_data.get("still_path"): st.image(f"https://image.tmdb.org/t/p/w500{ep_data['still_path']}", use_container_width=True)
                            st.write(ep_data.get("overview", "Synced successfully from export ledger."))
                    
    with h_mov:
        mov_hist = [h for h in history_sorted if h["type"] == "movie"]
        if not mov_hist: st.info("No movie history loaded.")
        else:
            grouped_mov = {}
            for item in mov_hist:
                try: dt = datetime.strptime(item["watched_at"][:19], '%Y-%m-%d %H:%M:%S')
                except: dt = datetime.strptime(item["watched_at"][:10], '%Y-%m-%d')
                grouped_mov.setdefault(dt.strftime('%B %Y'), []).append((item, dt))
                
            for month_str, items in grouped_mov.items():
                st.markdown(f"#### {month_str}")
                for item, dt in items:
                    info_key = f"hist_info_mov_{item['id']}_{item['watched_at']}"
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([5, 4, 1])
                        with c1: st.markdown(f"**{item['title']}**")
                        with c2: st.caption(dt.strftime('%b %d • %I:%M %p'))
                        with c3:
                            st.markdown('<div class="hist-toggle-btn">', unsafe_allow_html=True)
                            def m_info(k=info_key): st.session_state[k] = not st.session_state.get(k, False)
                            is_open = st.session_state.get(info_key, False)
                            st.button("▲" if is_open else "▼", key=f"btn_{info_key}", on_click=m_info)
                            st.markdown('</div>', unsafe_allow_html=True)
                    if is_open:
                        details = fetch_api(f"https://api.themoviedb.org/3/movie/{item['id']}?api_key={TMDB_KEY}")
                        with st.container(border=True):
                            if details.get("backdrop_path"): st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
                            st.write(details.get("overview", "Synced successfully from export ledger."))

    # ==========================================
    # DATA IMPORT UTILITY PANEL (BATCHED VERSION)
    # ==========================================
    st.divider()
    with st.expander("📥 TV Time Data Migrator", expanded=False):
        st.caption("Upload your official TV Time backup files.")
        m_file = st.file_uploader("Upload tvtime-movies JSON", type=["json"])
        s_file = st.file_uploader("Upload tvtime-series JSON", type=["json"])
        
        status_log = st.empty()
        
        if m_file and s_file:
            if st.button("🚀 WIPE DATABASE AND IMPORT NOW", type="primary", use_container_width=True):
                try:
                    status_log.info("Starting processing...")
                    
                    # Process in a single pass to build the structure
                    movies_raw = json.load(m_file)
                    series_raw = json.load(s_file)
                    
                    final_db = {"shows": [], "movies": [], "history": []}
                    fallback_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d 12:00:00')
                    
                    # 1. Process Movies
                    for movie in movies_raw:
                        imdb = movie.get("id", {}).get("imdb")
                        if imdb:
                            res = fetch_api(f"https://api.themoviedb.org/3/find/{imdb}?api_key={TMDB_KEY}&external_source=imdb_id")
                            if res.get("movie_results"):
                                tid = res["movie_results"][0]["id"]
                                title = movie.get("title", "Movie")
                                watched = movie.get("is_watched", False)
                                final_db["movies"].append({"id": tid, "name": title, "watched": watched})
                                if watched:
                                    w_at = movie.get("watched_at", fallback_date).replace("T", " ").replace("Z", "")[:19]
                                    final_db["history"].append({"type": "movie", "id": tid, "title": title, "detail": "", "watched_at": w_at})
                    
                    # 2. Process Series
                    for show in series_raw:
                        tvdb = show.get("id", {}).get("tvdb")
                        if tvdb:
                            res = fetch_api(f"https://api.themoviedb.org/3/find/{tvdb}?api_key={TMDB_KEY}&external_source=tvdb_id")
                            if res.get("tv_results"):
                                tid = res["tv_results"][0]["id"]
                                w_eps = []
                                for season in show.get("seasons", []):
                                    s_num = season.get("number", 0)
                                    if s_num == 0: continue
                                    for ep in season.get("episodes", []):
                                        if ep.get("is_watched"):
                                            ecode = f"S{s_num}E{ep.get('number')}"
                                            w_eps.append(ecode)
                                            w_at = ep.get("watched_at") or fallback_date
                                            final_db["history"].append({"type": "tv", "id": tid, "title": show.get("title", "Show"), "detail": ecode, "watched_at": w_at[:19]})
                                final_db["shows"].append({"id": tid, "name": show.get("title"), "watched_episodes": w_eps})

                    # 3. BATCHED UPLOAD (CHUNKED)
                    status_log.info("Data processed! Syncing to Cloud...")
                    
                    # Split history into chunks to avoid 413 error
                    chunk_size = 50 
                    hist_data = final_db.pop("history")
                    
                    # Upload base structure first
                    requests.put(BIN_URL, json=final_db, headers=headers)
                    
                    # Upload history in chunks
                    for i in range(0, len(hist_data), chunk_size):
                        chunk = hist_data[i:i+chunk_size]
                        # This patch adds to the existing history array
                        requests.patch(f"{BIN_URL}/record/history", json=chunk, headers={**headers, "Content-Type": "application/json"})
                    
                    st.session_state.db = {**final_db, "history": hist_data}
                    st.success("✅ Success! Your data has been synced in batches.")
                    st.rerun()
                        
                except Exception as e:
                    st.error(f"Migration error: {e}")
