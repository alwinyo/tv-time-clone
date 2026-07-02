import streamlit as st
import requests
from datetime import datetime, timedelta

# Mobile-friendly layout configuration
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS: SMART MOBILE GRID & APP STYLING ---
st.markdown("""
<style>
    /* Hide Streamlit Header & Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove top padding for a flush, native feel */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* Round all images (overridden later for the movie wall) */
    img {
        border-radius: 8px !important;
    }
    
    /* TV Time Gold Theme for Progress Bars */
    [data-testid="stProgressBar"] > div > div {
        background-color: #FFC107 !important;
    }
    
    /* Floating App Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        border: 1px solid rgba(200, 200, 200, 0.2) !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1) !important;
        padding: 0.5rem !important;
    }
    
    /* Premium Pill Buttons */
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
    
    /* Gold Theme for Active (Primary) Tabs */
    button[kind="primary"] {
        background-color: #FFC107 !important;
        color: #000 !important;
        border: none !important;
    }
    /* Sleek Dark Theme for Inactive (Secondary) Tabs */
    button[kind="secondary"] {
        background-color: #222 !important;
        color: #ccc !important;
        border: 1px solid #444 !important;
    }
    
    /* CLEAN EPISODE ACCORDION TOGGLE */
    .ep-toggle-btn div.stButton > button {
        background: transparent !important;
        border: none !important;
        color: #888 !important;
        font-size: 0.9rem !important;
        padding: 0 !important;
        margin-top: 6px !important; /* Perfect vertical alignment with checkbox */
        box-shadow: none !important;
    }
    .ep-toggle-btn div.stButton > button:active {
        color: #FFC107 !important;
        transform: none !important;
    }
    
    /* ========================================================
       THE MAGIC FIX: ONLY FORCE 3-COLUMN GRIDS ON MOBILE 
       ======================================================== */
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
    
    /* Genre Badges */
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

# 3. Database Core Operations & Migration
def load_db():
    res = requests.get(BIN_URL, headers=headers)
    if res.status_code == 200:
        data = res.json().get("record", {})
        if "shows" not in data: data["shows"] = []
        if "movies" not in data: data["movies"] = []
        
        # --- DATABASE MIGRATION: ADD HISTORY LEDGER ---
        if "history" not in data:
            data["history"] = []
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d 12:00:00')
            
            for m in data["movies"]:
                if m.get("watched"):
                    data["history"].append({"type": "movie", "id": m["id"], "title": m["name"], "detail": "", "watched_at": yesterday})
            
            for s in data["shows"]:
                for ep in s.get("watched_episodes", []):
                    data["history"].append({"type": "tv", "id": s["id"], "title": s["name"], "detail": ep, "watched_at": yesterday})
            
            requests.put(BIN_URL, json=data, headers=headers)
            
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
                    if actor.get("profile_path"):
                        st.image(f"https://image.tmdb.org/t/p/w185{actor['profile_path']}", use_container_width=True)
                    else:
                        st.info("No Photo") 
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
            
            # --- CLEAN INLINE ACCORDION LOGIC ---
            ep_col1, ep_col2 = st.columns([6, 1])
            with ep_col1:
                st.checkbox(f"**E{ep['episode_number']}.** {ep.get('name', 'Episode')}", value=is_watched, key=f"chk_dlg_{show_id}_{e_code}", on_change=on_check)
            with ep_col2:
                # Apply custom CSS to make it a borderless chevron
                st.markdown('<div class="ep-toggle-btn">', unsafe_allow_html=True)
                def toggle_info(k=info_key):
                    st.session_state[k] = not st.session_state.get(k, False)
                is_open = st.session_state.get(info_key, False)
                st.button("▲" if is_open else "▼", key=f"btn_i_{show_id}_{e_code}", on_click=toggle_info)
                st.markdown('</div>', unsafe_allow_html=True)

            # Instantly opens a sleek inline card below the episode if the chevron is clicked
            if st.session_state.get(info_key, False):
                with st.container(border=True):
                    if ep.get("still_path"): 
                        st.image(f"https://image.tmdb.org/t/p/w500{ep['still_path']}", use_container_width=True)
                    st.caption(f"⭐ {ep.get('vote_average', 0.0)} | **Aired:** {ep.get('air_date', 'N/A')}")
                    st.write(ep.get("overview", "No synopsis available."))
                    guest_stars = ep.get("guest_stars", [])
                    if guest_stars:
                        st.markdown("**Guest Stars:**")
                        show_cast_grid(guest_stars, limit=3)

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
                    break

    if up_next_count == 0:
        st.info("You are completely caught up! 🎉")

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

    if upcoming_count == 0:
        st.info("No upcoming episodes scheduled yet.")

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
                            else:
                                st.button("✔️ Added", key=f"dsbl_tv_{item_id}", disabled=True, use_container_width=True)
                        else:
                            if not any(m["id"] == item_id for m in st.session_state.db["movies"]):
                                if st.button("➕ Add", key=f"add_mov_{item_id}", use_container_width=True):
                                    st.session_state.db["movies"].append({"id": item_id, "name": title, "watched": False})
                                    save_db(); st.toast("Added!"); st.rerun()
                            else:
                                st.button("✔️ Added", key=f"dsbl_mov_{item_id}", disabled=True, use_container_width=True)

# ==========================================
# TAB 4: TV LIBRARY 
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
        
    st.divider()
    
    shows = st.session_state.db.get("shows", [])
    if not shows:
        st.info("Your TV library is empty.")
    else:
        display_shows = []
        for show in shows:
            details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
            air_date = details.get("first_air_date", "")
            
            t_eps = details.get("number_of_episodes", 1) 
            w_eps = len(show.get("watched_episodes", []))
            
            is_upcoming = bool(air_date and air_date > TODAY)
            is_completed = (w_eps >= t_eps and t_eps > 0)
            
            if st.session_state.tv_tab == "WATCHED" and is_completed:
                display_shows.append((show, details, t_eps, w_eps))
            elif st.session_state.tv_tab == "UPCOMING" and is_upcoming and not is_completed:
                display_shows.append((show, details, t_eps, w_eps))
            elif st.session_state.tv_tab == "WATCHLIST" and not is_upcoming and not is_completed:
                display_shows.append((show, details, t_eps, w_eps))
                
        if not display_shows:
            st.info(f"Your {st.session_state.tv_tab.lower()} is currently empty.")
        else:
            for i in range(0, len(display_shows), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(display_shows):
                        show, details, t_eps, w_eps = display_shows[i + j]
                        
                        with cols[j]:
                            with st.container(border=True):
                                if details.get("poster_path"):
                                    st.image(f"https://image.tmdb.org/t/p/w185{details['poster_path']}", use_container_width=True)
                                
                                st.markdown(f'<div class="grid-title" title="{show["name"]}">{show["name"]}</div>', unsafe_allow_html=True)
                                st.progress(min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0)
                                
                                if st.button("DETAILS", key=f"s_mgr_{show['id']}", use_container_width=True):
                                    manage_show_dialog(show['id'], show['name'], details)

# ==========================================
# TAB 5: MOVIE LIBRARY 
# ==========================================
with t_movies:
    st.markdown("""
        <style>
            .movie-wall-btn div.stButton > button {
                border: none !important;
                background-color: transparent !important;
                color: #aaa !important;
                font-size: 0.7rem !important;
                padding: 0 !important;
                margin-top: 2px !important;
                margin-bottom: 5px !important;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .movie-wall-btn div.stButton > button:active {
                color: white !important;
            }
            .movie-poster-sharp img {
                border-radius: 0px !important;
            }
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
        
    st.divider()
    
    movies = st.session_state.db.get("movies", [])
    if not movies:
        st.info("Your Movie library is empty.")
    else:
        display_movies = []
        for m in movies:
            details = fetch_api(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}")
            r_date = details.get("release_date", "")
            is_watched = m.get("watched", False)
            
            is_upcoming = bool(r_date and r_date > TODAY)
            
            if st.session_state.mov_tab == "WATCHED" and is_watched:
                display_movies.append((m, details, is_watched))
            elif st.session_state.mov_tab == "UPCOMING" and is_upcoming and not is_watched:
                display_movies.append((m, details, is_watched))
            elif st.session_state.mov_tab == "WATCHLIST" and not is_upcoming and not is_watched:
                display_movies.append((m, details, is_watched))
                
        if not display_movies:
            st.info(f"Your {st.session_state.mov_tab.lower()} is currently empty.")
        else:
            for i in range(0, len(display_movies), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(display_movies):
                        m, details, is_watched = display_movies[i + j]
                        
                        st.markdown('<div class="movie-poster-sharp">', unsafe_allow_html=True)
                        if details.get("poster_path"):
                            st.image(f"https://image.tmdb.org/t/p/w185{details['poster_path']}", use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                        if st.button("DETAILS", key=f"m_mgr_{m['id']}", use_container_width=True):
                            show_movie_details(m['id'], m['name'], details, is_watched)
                        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 6: PROFILE STATS & HISTORY
# ==========================================
with t_profile:
    st.markdown("### Lifetime Stats")
    
    total_tv_mins = 0
    total_episodes_watched = 0
    total_mov_mins = 0
    total_movies_watched = 0
    
    for show in st.session_state.db["shows"]:
        details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
        w_eps = len(show.get("watched_episodes", []))
        total_episodes_watched += w_eps
        
        runtimes = details.get("episode_run_time", [])
        avg_runtime = runtimes[0] if runtimes else 45
        total_tv_mins += (w_eps * avg_runtime)
        
    for m in st.session_state.db["movies"]:
        if m.get("watched", False):
            details = fetch_api(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}")
            total_mov_mins += details.get("runtime", 0)
            total_movies_watched += 1
            
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
    
    # --- SEPARATED HISTORY VIEWS ---
    st.markdown("### 📜 Watch History")
    h_tv, h_mov = st.tabs(["📺 Series", "🎬 Movies"])
    
    history = sorted(st.session_state.db.get("history", []), key=lambda x: x["watched_at"], reverse=True)
    
    with h_tv:
        tv_hist = [h for h in history if h["type"] == "tv"]
        if not tv_hist:
            st.info("No series history recorded yet.")
        else:
            for item in tv_hist:
                dt = datetime.strptime(item["watched_at"], '%Y-%m-%d %H:%M:%S')
                date_str = dt.strftime('%b %d, %Y • %I:%M %p')
                with st.container(border=True):
                    st.markdown(f"**{item['title']}** — {item['detail']}")
                    st.caption(date_str)
                    
    with h_mov:
        mov_hist = [h for h in history if h["type"] == "movie"]
        if not mov_hist:
            st.info("No movie history recorded yet.")
        else:
            for item in mov_hist:
                dt = datetime.strptime(item["watched_at"], '%Y-%m-%d %H:%M:%S')
                date_str = dt.strftime('%b %d, %Y • %I:%M %p')
                with st.container(border=True):
                    st.markdown(f"**{item['title']}**")
                    st.caption(date_str)
