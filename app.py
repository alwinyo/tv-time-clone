import streamlit as st
import requests
from datetime import datetime

# Mobile-friendly layout configuration
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS: NATIVE APP AESTHETIC ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    
    img {
        border-radius: 12px;
    }
    
    div.stButton > button {
        border-radius: 20px;
        font-weight: 600;
        border: 1px solid #4a4a4a;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:active {
        transform: scale(0.95);
    }
    
    button[data-baseweb="tab"] {
        font-size: 14px;
        padding-left: 10px;
        padding-right: 10px;
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
        return data
    return {"shows": [], "movies": []}

def save_db():
    requests.put(BIN_URL, json=st.session_state.db, headers=headers)

if "db" not in st.session_state:
    st.session_state.db = load_db()

def quick_watch_episode(show_id, ep_code):
    for s in st.session_state.db["shows"]:
        if s["id"] == show_id:
            if ep_code not in s["watched_episodes"]:
                s["watched_episodes"].append(ep_code)
                save_db()
                st.toast(f"Marked {ep_code} as watched! ✅")
                st.rerun()

# --- VISUAL CAST GRID HELPER ---
def show_cast_grid(cast_list, limit=6):
    cast_list = cast_list[:limit]
    if not cast_list:
        return
    
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
                    st.caption(f"**{actor['name']}** \n*{actor.get('character', '')}*")

# --- DIALOG / POPUP FUNCTIONS ---
@st.dialog("Episode Details")
def show_episode_details(show_id, show_name, ep_code, ep_data, is_watched):
    if ep_data.get("still_path"):
        st.image(f"https://image.tmdb.org/t/p/w500{ep_data['still_path']}", use_container_width=True)
    
    st.markdown(f"### {ep_data.get('name', 'Untitled Episode')}")
    st.caption(f"**{show_name}** • {ep_code} • Aired: {ep_data.get('air_date', 'N/A')} • ⭐ {ep_data.get('vote_average', 0.0)}/10")
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
                elif not is_watched and ep_code not in s["watched_episodes"]:
                    s["watched_episodes"].append(ep_code)
                save_db()
                break
        st.rerun()

@st.dialog("Manage Show")
def manage_show_dialog(show_id, show_name, details):
    if details.get("backdrop_path"):
        st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
    
    st.markdown(f"### {show_name}")
    genres = ", ".join([g["name"] for g in details.get("genres", [])])
    st.caption(f"**Status:** {details.get('status')} • **Genres:** {genres} • ⭐ {details.get('vote_average', 0.0)}/10")
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
        sel_s = st.selectbox("Season", s_nums, key=f"dlg_s_{show_id}")
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
            
            st.checkbox(
                f"E{ep['episode_number']}. {ep.get('name', 'Episode')}",
                value=is_watched,
                key=f"chk_dlg_{show_id}_{e_code}",
                on_change=on_check
            )

    st.divider()
    st.markdown("#### Top Cast")
    credits = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}")
    show_cast_grid(credits.get("cast", []), limit=6)

@st.dialog("Movie Details")
def show_movie_details(m_id, m_name, details, is_watched):
    if details.get("backdrop_path"):
        st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
    
    st.markdown(f"### {m_name}")
    genres = ", ".join([g["name"] for g in details.get("genres", [])])
    st.caption(f"**Released:** {details.get('release_date', 'N/A')} • **Runtime:** {details.get('runtime', 0)} mins • {genres}")
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
                save_db()
                break
        st.rerun()

# --- APP NAVIGATION BAR ---
t_next, t_soon, t_search, t_tv, t_movies, t_profile = st.tabs(["🔥 Next", "📅 Soon", "🔍 Search", "📺 TV", "🎬 Movies", "👤 Stats"])

# ==========================================
# TAB 1: UP NEXT DASHBOARD
# ==========================================
with t_next:
    st.markdown("## Up Next to Watch")
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
                        if ep.get("still_path"):
                            st.image(f"https://image.tmdb.org/t/p/w500{ep['still_path']}", use_container_width=True)
                        elif details.get("backdrop_path"):
                            st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_container_width=True)
                        
                        st.markdown(f"### {show['name']} — {ep_code}")
                        st.caption(f"*{ep.get('name', 'Episode')}*")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("ℹ️ Info", key=f"info_next_{show['id']}_{ep_code}", use_container_width=True):
                                show_episode_details(show['id'], show['name'], ep_code, ep, is_watched=False)
                        with c2:
                            def fast_watch(sid=show['id'], ecode=ep_code):
                                for s in st.session_state.db["shows"]:
                                    if s["id"] == sid:
                                        s["watched_episodes"].append(ecode)
                                        save_db(); st.toast("Watched! ✅"); break
                            st.button("✔️ Watched", key=f"btn_next_{show['id']}_{ep_code}", on_click=fast_watch, use_container_width=True)
                    break

    if up_next_count == 0:
        st.info("You are completely caught up! 🎉")

# ==========================================
# TAB 2: UPCOMING CALENDAR
# ==========================================
with t_soon:
    st.markdown("## Upcoming Episodes")
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
                    air_date_obj = datetime.strptime(air_date, '%Y-%m-%d')
                    days_left = (air_date_obj - datetime.today()).days
                    
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 3])
                        if details.get("poster_path"):
                            c1.image(f"https://image.tmdb.org/t/p/w92{details['poster_path']}")
                        with c2:
                            st.markdown(f"**{show['name']}**")
                            st.markdown(f"*{ep_code} airs in **{days_left} days***")
                            st.caption(f"Date: {air_date}")
                    break

    if upcoming_count == 0:
        st.info("No upcoming episodes scheduled yet.")

# ==========================================
# TAB 3: GLOBAL SEARCH (GRID LAYOUT)
# ==========================================
with t_search:
    st.markdown("## Discover")
    search_type = st.radio("Looking for:", ["TV Shows", "Movies"], horizontal=True)
    search_query = st.text_input("Enter title to search:")

    if search_query:
        endpoint = "tv" if search_type == "TV Shows" else "movie"
        res = fetch_api(f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_KEY}&query={search_query}")
        results = res.get("results", [])
        
        if results:
            cols = st.columns(2)
            for idx, item in enumerate(results):
                with cols[idx % 2]:
                    with st.container(border=True):
                        item_id = item["id"]
                        title = item["name"] if search_type == "TV Shows" else item["title"]
                        
                        if item.get("poster_path"): 
                            st.image(f"https://image.tmdb.org/t/p/w342{item['poster_path']}", use_container_width=True)
                        
                        st.markdown(f"**{title}**")
                        st.caption(f"⭐ {item.get('vote_average', 0.0)}/10")
                        
                        if search_type == "TV Shows":
                            if not any(s["id"] == item_id for s in st.session_state.db["shows"]):
                                if st.button("➕ Add", key=f"add_tv_{item_id}", use_container_width=True):
                                    st.session_state.db["shows"].append({"id": item_id, "name": title, "watched_episodes": []})
                                    save_db(); st.success("Added!"); st.rerun()
                            else:
                                st.button("✔️ Added", key=f"dsbl_tv_{item_id}", disabled=True, use_container_width=True)
                        else:
                            if not any(m["id"] == item_id for m in st.session_state.db["movies"]):
                                if st.button("➕ Add", key=f"add_mov_{item_id}", use_container_width=True):
                                    st.session_state.db["movies"].append({"id": item_id, "name": title, "watched": False})
                                    save_db(); st.success("Added!"); st.rerun()
                            else:
                                st.button("✔️ Added", key=f"dsbl_mov_{item_id}", disabled=True, use_container_width=True)

# ==========================================
# TAB 4: TV LIBRARY (CARD LAYOUT)
# ==========================================
with t_tv:
    st.markdown("## My TV Collection")
    
    if not st.session_state.db["shows"]:
        st.info("Your TV library is empty.")
    
    for show in st.session_state.db["shows"]:
        details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
        t_eps = details.get("number_of_episodes", 1) 
        w_eps = len(show.get("watched_episodes", []))
        
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                if details.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w342{details['poster_path']}", use_container_width=True)
            with c2:
                st.markdown(f"### {show['name']}")
                st.caption(details.get("overview", "")[:90] + "...")
                
                st.progress(min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0)
                st.caption(f"{w_eps} of {t_eps} episodes watched")
                
                if st.button("Manage Show", key=f"s_mgr_{show['id']}", use_container_width=True):
                    manage_show_dialog(show['id'], show['name'], details)

# ==========================================
# TAB 5: MOVIE LIBRARY (CARD LAYOUT)
# ==========================================
with t_movies:
    st.markdown("## My Movies")
    
    if not st.session_state.db["movies"]:
        st.info("Your Movie library is empty.")
        
    for m in st.session_state.db["movies"]:
        details = fetch_api(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}")
        is_watched = m.get("watched", False)
        
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                if details.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w342{details['poster_path']}", use_container_width=True)
            with c2:
                st.markdown(f"### {m['name']}")
                st.caption(details.get("overview", "")[:90] + "...")
                
                def on_mov_check(mid=m['id']):
                    st.session_state.db["movies"] = [mov | {"watched": st.session_state[f"mov_{mid}"]} if mov["id"] == mid else mov for mov in st.session_state.db["movies"]]
                    save_db()
                
                st.checkbox("✅ Watched", value=is_watched, key=f"mov_{m['id']}", on_change=on_mov_check)
                
                if st.button("Movie Info", key=f"m_mgr_{m['id']}", use_container_width=True):
                    show_movie_details(m['id'], m['name'], details, is_watched)

# ==========================================
# TAB 6: PROFILE STATS
# ==========================================
with t_profile:
    st.markdown("## Lifetime Stats")
    
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
    
    st.markdown("### Total Time Spent Watching")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Months", f"{months}")
        col2.metric("Days", f"{days}")
        col3.metric("Hours", f"{hours}")
    
    st.markdown("### Content Breakdown")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.metric("Episodes", total_episodes_watched)
        c2.metric("Movies", total_movies_watched)
