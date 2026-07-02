import streamlit as st
import requests
import pandas as pd
import json
import time
import re
from datetime import datetime, timedelta

# Mobile-friendly layout configuration
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS: SMART MOBILE GRID & APP STYLING ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    img { border-radius: 8px !important; }
    [data-testid="stProgressBar"] > div > div { background-color: #FFC107 !important; }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important; border: 1px solid rgba(200, 200, 200, 0.2) !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1) !important; padding: 0.5rem !important;
    }
    
    div.stButton > button {
        border-radius: 20px; font-weight: 600; transition: all 0.2s;
        padding: 2px 5px !important; font-size: 0.75rem !important;
    }
    div.stButton > button:active { transform: scale(0.95); }
    
    button[kind="primary"] { background-color: #FFC107 !important; color: #000 !important; border: none !important; }
    button[kind="secondary"] { background-color: #222 !important; color: #ccc !important; border: 1px solid #444 !important; }
    
    .ep-toggle-btn div.stButton > button, .hist-toggle-btn div.stButton > button {
        background: transparent !important; border: none !important; color: #888 !important; box-shadow: none !important;
    }
    .ep-toggle-btn div.stButton > button { font-size: 0.9rem !important; padding: 0 !important; margin-top: 6px !important; }
    .hist-toggle-btn div.stButton > button { font-size: 1.1rem !important; padding: 0 !important; margin-top: 15px !important; }
    .ep-toggle-btn div.stButton > button:active, .hist-toggle-btn div.stButton > button:active { color: #FFC107 !important; transform: none !important; }
    
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3):last-child) {
            flex-direction: row !important; flex-wrap: nowrap !important; gap: 4px !important; 
        }
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3):last-child) > div[data-testid="column"] {
            width: 33.33% !important; flex: 1 1 0% !important; min-width: 0 !important; padding: 0 !important;
        }
    }
    
    .grid-title {
        font-size: 0.65rem !important; font-weight: 700; white-space: nowrap; overflow: hidden;
        text-overflow: ellipsis; text-align: center; margin-top: 6px; line-height: 1.2;
    }
    
    .badge {
        display: inline-block; background-color: #333333; color: #FFFFFF; padding: 3px 8px;
        border-radius: 12px; font-size: 0.7rem; font-weight: 600; margin-right: 4px; margin-bottom: 6px;
    }
    .badge-gold { background-color: #FFC107; color: #000000; }
</style>
""", unsafe_allow_html=True)

st.title("📺 My TV Time")

# --- CREDENTIALS & DB ---
TMDB_KEY = st.secrets["TMDB_KEY"]
BIN_KEY = st.secrets["JSONBIN_KEY"]
BIN_ID = st.secrets["JSONBIN_ID"]
BIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
headers = {"X-Master-Key": BIN_KEY, "Content-Type": "application/json"}
TODAY = datetime.today().strftime('%Y-%m-%d')

@st.cache_data(ttl=3600)
def fetch_api(url):
    try:
        return requests.get(url, timeout=5).json()
    except: return {}

def fetch_robust(url):
    for _ in range(3):
        try:
            r = requests.get(url, timeout=5).json()
            if r.get("status_code") in [25, 9]:
                time.sleep(1)
                continue
            return r
        except: time.sleep(1)
    return {}

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

def parse_tvtime_date(d_str):
    if not d_str: return "2000-01-01 12:00:00"
    try:
        dt = datetime.strptime(d_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        try:
            dt = datetime.strptime(d_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except: return "2000-01-01 12:00:00"

# --- DIALOGS ---
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
    guest_stars = ep_data.get("guest_stars", [])
    if guest_stars:
        st.markdown("#### Guest Stars")
        show_cast_grid(guest_stars, limit=6)
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
    
    providers = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/watch/providers?api_key={TMDB_KEY}")
    if "AE" in providers.get("results", {}):
        streams = providers["results"]["AE"].get("flatrate", [])
        if streams:
            p_names = ", ".join([p["provider_name"] for p in streams])
            st.info(f"📱 **Streaming locally:** {p_names}")
            
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
# TAB 1: UP NEXT DASHBOARD
# ==========================================
with t_next:
    st.markdown("### Up Next to Watch")
    next_sort = st.selectbox("Sort by:", ["Release Date", "Alphabetical", "Recently Added"], key="sort_next")
    up_next_items = []
    
    for show in st.session_state.db["shows"]:
        w_eps = len(show.get("watched_episodes", []))
        t_eps = show.get("total_episodes", 1)
        if w_eps >= t_eps and t_eps > 0: continue
        
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
        w_eps = len(show.get("watched_episodes", []))
        t_eps = show.get("total_episodes", 1)
        if w_eps >= t_eps and t_eps > 0: continue
        
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
                    upcoming_count += 1
                    found_next = True
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
                                    details = fetch_api(f"https://api.themoviedb.org/3/tv/{item_id}?api_key={TMDB_KEY}")
                                    st.session_state.db["shows"].append({
                                        "id": item_id, "name": title, "watched_episodes": [],
                                        "poster_path": details.get("poster_path", ""), "first_air_date": details.get("first_air_date", ""),
                                        "total_episodes": details.get("number_of_episodes", 1)
                                    })
                                    save_db(); st.toast("Added!"); st.rerun()
                            else: st.button("✔️ Added", key=f"dsbl_tv_{item_id}", disabled=True, use_container_width=True)
                        else:
                            if not any(m["id"] == item_id for m in st.session_state.db["movies"]):
                                if st.button("➕ Add", key=f"add_mov_{item_id}", use_container_width=True):
                                    details = fetch_api(f"https://api.themoviedb.org/3/movie/{item_id}?api_key={TMDB_KEY}")
                                    st.session_state.db["movies"].append({
                                        "id": item_id, "name": title, "watched": False,
                                        "poster_path": details.get("poster_path", ""), "release_date": details.get("release_date", ""),
                                        "runtime": details.get("runtime", 0)
                                    })
                                    save_db(); st.toast("Added!"); st.rerun()
                            else: st.button("✔️ Added", key=f"dsbl_mov_{item_id}", disabled=True, use_container_width=True)

# ==========================================
# TAB 4: TV LIBRARY (CACHED FROM DB)
# ==========================================
with t_tv:
    st.markdown("### My TV Collection")
    if "tv_tab" not in st.session_state: st.session_state.tv_tab = "WATCHLIST"
        
    c1, c2, c3 = st.columns(3)
    if c1.button("Watchlist", type="primary" if st.session_state.tv_tab == "WATCHLIST" else "secondary", use_container_width=True, key="tv_wl"):
        st.session_state.tv_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.tv_tab == "UPCOMING" else "secondary", use_container_width=True, key="tv_up"):
        st.session_state.tv_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.tv_tab == "WATCHED" else "secondary", use_container_width=True, key="tv_wd"):
        st.session_state.tv_tab = "WATCHED"; st.rerun()
        
    tv_sort = st.selectbox("Sort Library by:", ["Recently Added", "Alphabetical", "Release Date"], key="sort_tv")
    st.divider()
    
    shows = st.session_state.db.get("shows", [])
    if not shows: st.info("Your TV library is empty.")
    else:
        display_shows = []
        for show in shows:
            air_date = show.get("first_air_date", "")
            t_eps = show.get("total_episodes", 1) 
            w_eps = len(show.get("watched_episodes", []))
            
            is_upcoming = bool(air_date and air_date > TODAY)
            is_completed = (w_eps >= t_eps and t_eps > 0)
            
            if st.session_state.tv_tab == "WATCHED" and is_completed: display_shows.append((show, t_eps, w_eps))
            elif st.session_state.tv_tab == "UPCOMING" and is_upcoming and not is_completed: display_shows.append((show, t_eps, w_eps))
            elif st.session_state.tv_tab == "WATCHLIST" and not is_upcoming and not is_completed: display_shows.append((show, t_eps, w_eps))
                
        if tv_sort == "Alphabetical": display_shows.sort(key=lambda x: x[0]['name'].lower())
        elif tv_sort == "Release Date": display_shows.sort(key=lambda x: x[0].get('first_air_date', '1900-01-01') or '1900-01-01', reverse=True)
                
        if not display_shows: st.info(f"Your {st.session_state.tv_tab.lower()} is currently empty.")
        else:
            for i in range(0, len(display_shows), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(display_shows):
                        show, t_eps, w_eps = display_shows[i + j]
                        with cols[j]:
                            with st.container(border=True):
                                if show.get("poster_path"): st.image(f"https://image.tmdb.org/t/p/w185{show['poster_path']}", use_container_width=True)
                                st.markdown(f'<div class="grid-title" title="{show["name"]}">{show["name"]}</div>', unsafe_allow_html=True)
                                st.progress(min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0)
                                if st.button("DETAILS", key=f"s_mgr_{show['id']}", use_container_width=True):
                                    details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
                                    manage_show_dialog(show['id'], show['name'], details)

# ==========================================
# TAB 5: MOVIE LIBRARY (CACHED FROM DB)
# ==========================================
with t_movies:
    st.markdown("""
        <style>
            .movie-wall-btn div.stButton > button {
                border: none !important; background-color: transparent !important; color: #aaa !important;
                font-size: 0.7rem !important; padding: 0 !important; margin-top: 2px !important; margin-bottom: 5px !important; text-transform: uppercase; letter-spacing: 1px;
            }
            .movie-wall-btn div.stButton > button:active { color: white !important; }
            .movie-poster-sharp img { border-radius: 0px !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### My Movies")
    if "mov_tab" not in st.session_state: st.session_state.mov_tab = "WATCHLIST"
        
    c1, c2, c3 = st.columns(3)
    if c1.button("Watchlist", type="primary" if st.session_state.mov_tab == "WATCHLIST" else "secondary", use_container_width=True, key="m_wl"):
        st.session_state.mov_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.mov_tab == "UPCOMING" else "secondary", use_container_width=True, key="m_up"):
        st.session_state.mov_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.mov_tab == "WATCHED" else "secondary", use_container_width=True, key="m_wd"):
        st.session_state.mov_tab = "WATCHED"; st.rerun()
        
    mov_sort = st.selectbox("Sort Library by:", ["Recently Added", "Alphabetical", "Release Date"], key="sort_mov")
    st.divider()
    
    movies = st.session_state.db.get("movies", [])
    if not movies: st.info("Your Movie library is empty.")
    else:
        display_movies = []
        for m in movies:
            r_date = m.get("release_date", "")
            is_watched = m.get("watched", False)
            is_upcoming = bool(r_date and r_date > TODAY)
            
            if st.session_state.mov_tab == "WATCHED" and is_watched: display_movies.append((m, is_watched))
            elif st.session_state.mov_tab == "UPCOMING" and is_upcoming and not is_watched: display_movies.append((m, is_watched))
            elif st.session_state.mov_tab == "WATCHLIST" and not is_upcoming and not is_watched: display_movies.append((m, is_watched))
                
        if mov_sort == "Alphabetical": display_movies.sort(key=lambda x: x[0]['name'].lower())
        elif mov_sort == "Release Date": display_movies.sort(key=lambda x: x[0].get('release_date', '1900-01-01') or '1900-01-01', reverse=True)
                
        if not display_movies: st.info(f"Your {st.session_state.mov_tab.lower()} is currently empty.")
        else:
            for i in range(0, len(display_movies), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(display_movies):
                        m, is_watched = display_movies[i + j]
                        st.markdown('<div class="movie-poster-sharp">', unsafe_allow_html=True)
                        if m.get("poster_path"): st.image(f"https://image.tmdb.org/t/p/w185{m['poster_path']}", use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                        if st.button("DETAILS", key=f"m_mgr_{m['id']}", use_container_width=True):
                            details = fetch_api(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}")
                            show_movie_details(m['id'], m['name'], details, is_watched)
                        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 6: PROFILE STATS, GRAPHS & IMPORT
# ==========================================
with t_profile:
    st.markdown("### Lifetime Stats")
    
    total_tv_mins = 0; total_episodes_watched = 0
    total_mov_mins = 0; total_movies_watched = 0
    
    for show in st.session_state.db["shows"]:
        w_eps = len(show.get("watched_episodes", []))
        total_episodes_watched += w_eps
        total_tv_mins += (w_eps * 45) 
        
    for m in st.session_state.db["movies"]:
        if m.get("watched", False):
            total_mov_mins += m.get("runtime", 120) 
            total_movies_watched += 1
            
    total_mins = total_tv_mins + total_mov_mins
    months = total_mins // 43800; days = (total_mins % 43800) // 1440; hours = (total_mins % 1440) // 60
    
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Months", f"{months}")
        c2.metric("Days", f"{days}")
        c3.metric("Hours", f"{hours}")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.metric("Episodes", total_episodes_watched)
        c2.metric("Movies", total_movies_watched)
        
    st.divider()
    
    # --- PANDAS GRAPHS: MONTHLY WATCH ACTIVITY ---
    st.markdown("### 📊 Watch Activity")
    history = st.session_state.db.get("history", [])
    
    if history:
        monthly_tv = {}; monthly_mov = {}
        for h in history:
            try:
                dt = datetime.strptime(h["watched_at"], '%Y-%m-%d %H:%M:%S')
                m_key = dt.strftime('%Y-%m')
                if h["type"] == "tv": monthly_tv[m_key] = monthly_tv.get(m_key, 0) + 1
                else: monthly_mov[m_key] = monthly_mov.get(m_key, 0) + 1
            except: pass
        
        if monthly_tv:
            df_tv = pd.DataFrame(list(monthly_tv.items()), columns=['Month', 'Episodes Watched']).set_index('Month').sort_index()
            df_tv.index = pd.to_datetime(df_tv.index).strftime('%b %Y')
            st.markdown("#### Series Watched per Month")
            st.bar_chart(df_tv, color="#FFC107")
        
        if monthly_mov:
            df_mov = pd.DataFrame(list(monthly_mov.items()), columns=['Month', 'Movies Watched']).set_index('Month').sort_index()
            df_mov.index = pd.to_datetime(df_mov.index).strftime('%b %Y')
            st.markdown("#### Movies Watched per Month")
            st.bar_chart(df_mov, color="#555555")
    else: st.info("Start watching to see your activity graph!")

    st.divider()
    
    # --- MONTHLY WATCH HISTORY JOURNAL ---
    st.markdown("### 📜 Watch History Journal")
    h_tv, h_mov = st.tabs(["📺 Series", "🎬 Movies"])
    history_sorted = sorted(history, key=lambda x: x["watched_at"], reverse=True)
    
    with h_tv:
        tv_hist = [h for h in history_sorted if h["type"] == "tv"]
        if not tv_hist: st.info("No series history recorded yet.")
        else:
            grouped_tv = {}
            for item in tv_hist:
                try:
                    dt = datetime.strptime(item["watched_at"], '%Y-%m-%d %H:%M:%S')
                    grouped_tv.setdefault(dt.strftime('%B %Y'), []).append((item, dt))
                except: pass
            
            for month_str, items in grouped_tv.items():
                st.markdown(f"#### {month_str}")
                for item, dt in items:
                    info_key = f"h_tv_{item['id']}_{item['detail']}_{item['watched_at']}"
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([5, 4, 1])
                        c1.markdown(f"**{item['title']}** \n\n*{item['detail']}*")
                        c2.caption(dt.strftime('%b %d • %I:%M %p'))
                        with c3:
                            st.markdown('<div class="hist-toggle-btn">', unsafe_allow_html=True)
                            def t_info(k=info_key): st.session_state[k] = not st.session_state.get(k, False)
                            is_open = st.session_state.get(info_key, False)
                            st.button("▲" if is_open else "▼", key=f"btn_{info_key}", on_click=t_info)
                            st.markdown('</div>', unsafe_allow_html=True)
                    if is_open:
                        try:
                            s_num, e_num = item["detail"].split("E")
                            ep_data = fetch_api(f"https://api.themoviedb.org/3/tv/{item['id']}/season/{s_num.replace('S', '')}/episode/{e_num}?api_key={TMDB_KEY}")
                        except: ep_data = {}
                        with st.container(border=True):
                            if ep_data.get("still_path"): st.image(f"https://image.tmdb.org/t/p/w500{ep_data['still_path']}", use_container_width=True)
                            st.write(ep_data.get("overview", "No synopsis available."))
                    
    with h_mov:
        mov_hist = [h for h in history_sorted if h["type"] == "movie"]
        if not mov_hist: st.info("No movie history recorded yet.")
        else:
            grouped_mov = {}
            for item in mov_hist:
                try:
                    dt = datetime.strptime(item["watched_at"], '%Y-%m-%d %H:%M:%S')
                    grouped_mov.setdefault(dt.strftime('%B %Y'), []).append((item, dt))
                except: pass
                
            for month_str, items in grouped_mov.items():
                st.markdown(f"#### {month_str}")
                for item, dt in items:
                    info_key = f"h_mov_{item['id']}_{item['watched_at']}"
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([5, 4, 1])
                        c1.markdown(f"**{item['title']}**")
                        c2.caption(dt.strftime('%b %d • %I:%M %p'))
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
                            st.write(details.get("overview", "No synopsis available."))

    st.divider()
    
    # --- TV TIME DATA IMPORTER (Smart Merging) ---
    with st.expander("⚙️ Import TV Time Data"):
        st.warning("Ensure you keep the app open until the progress bar reaches 100%. TMDB limits requests so this will process carefully.")
        wipe_db = st.checkbox("Wipe current test library before importing", value=True)
        m_file = st.file_uploader("Upload Movies JSON", type="json")
        t_file = st.file_uploader("Upload Series JSON", type="json")
        
        if st.button("Start Safe Import"):
            if m_file or t_file:
                prog = st.progress(0)
                stat_txt = st.empty()
                
                new_db = {
                    "movies": [] if wipe_db else st.session_state.db.get("movies", []),
                    "shows": [] if wipe_db else st.session_state.db.get("shows", []),
                    "history": [] if wipe_db else st.session_state.db.get("history", [])
                }
                
                # Process Movies
                if m_file:
                    stat_txt.text("Processing Movies... fetching data.")
                    try:
                        m_data = json.load(m_file)
                        for idx, m in enumerate(m_data):
                            prog.progress((idx + 1) / len(m_data))
                            time.sleep(0.05)
                            
                            imdb_id = m.get("id", {}).get("imdb")
                            raw_title = m.get("title") or ""
                            res = {}
                            
                            if not imdb_id and not raw_title:
                                continue # Safe guard against blank data
                                
                            if imdb_id:
                                res = fetch_robust(f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_KEY}&external_source=imdb_id")
                                
                            if not res.get("movie_results") and raw_title:
                                title_query = raw_title.replace(" ", "+")
                                res = fetch_robust(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={title_query}&year={m.get('year', '')}")
                                if res.get("results"): res["movie_results"] = [res["results"][0]]
                                
                            if res.get("movie_results"):
                                tmdb_id = res["movie_results"][0]["id"]
                                title = res["movie_results"][0]["title"]
                                is_watched = m.get("is_watched", False)
                                
                                if not any(movie["id"] == tmdb_id for movie in new_db["movies"]):
                                    full_m = fetch_robust(f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_KEY}")
                                    new_db["movies"].append({
                                        "id": tmdb_id, "name": title, "watched": is_watched,
                                        "poster_path": full_m.get("poster_path", ""), "release_date": full_m.get("release_date", ""),
                                        "runtime": full_m.get("runtime", 0)
                                    })
                                    if is_watched:
                                        w_dt = parse_tvtime_date(m.get("watched_at"))
                                        new_db["history"].append({"type": "movie", "id": tmdb_id, "title": title, "detail": "", "watched_at": w_dt})
                    except Exception as e: st.error(f"Error processing movies: {e}")
                
                prog.progress(0)
                
                # Process Shows
                if t_file:
                    stat_txt.text("Processing Series... fetching data.")
                    try:
                        t_data = json.load(t_file)
                        for idx, s in enumerate(t_data):
                            prog.progress((idx + 1) / len(t_data))
                            time.sleep(0.05)
                            
                            tvdb_id = s.get("id", {}).get("tvdb")
                            raw_title = s.get("title") or ""
                            res = {}
                            
                            if not tvdb_id and not raw_title:
                                continue # Safe guard against blank data
                                
                            if tvdb_id:
                                res = fetch_robust(f"https://api.themoviedb.org/3/find/{tvdb_id}?api_key={TMDB_KEY}&external_source=tvdb_id")
                            
                            if not res.get("tv_results") and raw_title:
                                title_query = re.sub(r'\(\d{4}\)', '', raw_title).strip().replace(" ", "+")
                                res = fetch_robust(f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_KEY}&query={title_query}")
                                if res.get("results"): res["tv_results"] = [res["results"][0]]
                                
                            if res.get("tv_results"):
                                tmdb_id = res["tv_results"][0]["id"]
                                title = res["tv_results"][0]["name"]
                                watched_eps = []
                                
                                for season in s.get("seasons", []):
                                    s_num = season.get("number")
                                    for ep in season.get("episodes", []):
                                        if ep.get("is_watched"):
                                            e_num = ep.get("number")
                                            e_code = f"S{s_num}E{e_num}"
                                            watched_eps.append(e_code)
                                            w_dt = parse_tvtime_date(ep.get("watched_at"))
                                            new_db["history"].append({"type": "tv", "id": tmdb_id, "title": title, "detail": e_code, "watched_at": w_dt})
                                            
                                if not any(show["id"] == tmdb_id for show in new_db["shows"]):
                                    full_s = fetch_robust(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={TMDB_KEY}")
                                    new_db["shows"].append({
                                        "id": tmdb_id, "name": title, "watched_episodes": watched_eps,
                                        "poster_path": full_s.get("poster_path", ""), "first_air_date": full_s.get("first_air_date", ""),
                                        "total_episodes": full_s.get("number_of_episodes", 1)
                                    })
                    except Exception as e: st.error(f"Error processing series: {e}")
                
                st.session_state.db = new_db
                save_db()
                stat_txt.text("✅ Safe Import Complete!")
                st.toast("Library successfully imported.")
                st.rerun()
            else:
                st.error("Please upload at least one JSON file first.")
