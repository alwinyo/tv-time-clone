import streamlit as st
import requests
from datetime import datetime

# Mobile-friendly layout configuration
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")
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

# --- DIALOG / POPUP FUNCTIONS ---
@st.dialog("Episode Details")
def show_episode_details(show_id, show_name, ep_code, ep_data, is_watched):
    if ep_data.get("still_path"):
        st.image(f"https://image.tmdb.org/t/p/w500{ep_data['still_path']}", use_column_width=True)
    
    st.markdown(f"### {ep_data.get('name', 'Untitled Episode')}")
    st.caption(f"**{show_name}** • {ep_code} • Aired: {ep_data.get('air_date', 'N/A')} • ⭐ {ep_data.get('vote_average', 0.0)}/10")
    st.write(ep_data.get("overview", "No synopsis available for this episode yet."))
    
    # NEW: Pull Guest Stars specific to this episode
    guest_stars = ep_data.get("guest_stars", [])[:5]
    if guest_stars:
        st.markdown("**Guest Stars:**")
        st.caption(" • ".join([f"{g['name']} ({g.get('character', '')})" for g in guest_stars]))
    
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

@st.dialog("Show Info")
def show_series_details(show_id, show_name, details):
    if details.get("poster_path"):
        st.image(f"https://image.tmdb.org/t/p/w342{details['poster_path']}", use_column_width=True)
    st.markdown(f"### {show_name}")
    genres = ", ".join([g["name"] for g in details.get("genres", [])])
    st.caption(f"**Status:** {details.get('status')} • **Genres:** {genres} • ⭐ {details.get('vote_average', 0.0)}/10")
    st.write(details.get("overview", "No overview available."))
    
    # NEW: Pull Top Cast for the Show
    credits = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}")
    cast = credits.get("cast", [])[:6]
    if cast:
        st.markdown("**Top Cast:**")
        st.caption(" • ".join([f"{c['name']} ({c.get('character', '')})" for c in cast]))

@st.dialog("Movie Details")
def show_movie_details(m_id, m_name, details, is_watched):
    if details.get("backdrop_path"):
        st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_column_width=True)
    st.markdown(f"### {m_name}")
    genres = ", ".join([g["name"] for g in details.get("genres", [])])
    st.caption(f"**Released:** {details.get('release_date', 'N/A')} • **Runtime:** {details.get('runtime', 0)} mins • {genres}")
    st.write(details.get("overview", "No synopsis available."))
    
    # NEW: Pull Top Cast for the Movie
    credits = fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}/credits?api_key={TMDB_KEY}")
    cast = credits.get("cast", [])[:6]
    if cast:
        st.markdown("**Top Cast:**")
        st.caption(" • ".join([f"{c['name']} ({c.get('character', '')})" for c in cast]))
    
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
t_next, t_soon, t_search, t_tv, t_movies, t_profile = st.tabs(["🔥 Next", "📅 Soon", "🔍", "📺", "🎬", "👤"])

# ==========================================
# TAB 1: UP NEXT DASHBOARD
# ==========================================
with t_next:
    st.subheader("Up Next to Watch")
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
                            st.image(f"https://image.tmdb.org/t/p/w500{ep['still_path']}", use_column_width=True)
                        elif details.get("backdrop_path"):
                            st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_column_width=True)
                        
                        st.markdown(f"**{show['name']}** — {ep_code}")
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
    st.subheader("Upcoming Episodes")
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
    st.subheader("Discover")
    search_type = st.radio("Looking for:", ["TV Shows", "Movies"], horizontal=True)
    search_query = st.text_input("Enter title:")

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
                            st.image(f"https://image.tmdb.org/t/p/w342{item['poster_path']}", use_column_width=True)
                        
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
# TABS 4 & 5: TV & MOVIE LIBRARY
# ==========================================
with t_tv:
    st.subheader("My TV Collection")
    for show in st.session_state.db["shows"]:
        details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
        t_eps = details.get("number_of_episodes", 0)
        w_eps = len(show.get("watched_episodes", []))
        
        with st.expander(f"📺 {show['name']} ({w_eps}/{t_eps})"):
            if details.get("backdrop_path"):
                st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_column_width=True)
            
            st.progress(min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0)
            
            if st.button("ℹ️ About this Show", key=f"s_info_{show['id']}", use_container_width=True):
                show_series_details(show['id'], show['name'], details)
            
            providers = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/watch/providers?api_key={TMDB_KEY}")
            if "AE" in providers.get("results", {}):
                streams = providers["results"]["AE"].get("flatrate", [])
                if streams:
                    p_names = ", ".join([p["provider_name"] for p in streams])
                    st.caption(f"📱 **Streaming on:** {p_names}")
            
            s_nums = [s["season_number"] for s in details.get("seasons", []) if s["season_number"] > 0]
            if s_nums:
                sel_s = st.selectbox("Season", s_nums, key=f"lib_s_{show['id']}")
                s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/season/{sel_s}?api_key={TMDB_KEY}")
                
                for ep in s_data.get("episodes", []):
                    e_code = f"S{sel_s}E{ep['episode_number']}"
                    is_watched = e_code in show.get("watched_episodes", [])
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        def on_check(sid=show['id'], ecode=e_code):
                            chkd = st.session_state[f"chk_{sid}_{ecode}"]
                            for s in st.session_state.db["shows"]:
                                if s["id"] == sid:
                                    if chkd and ecode not in s["watched_episodes"]: s["watched_episodes"].append(ecode)
                                    elif not chkd and ecode in s["watched_episodes"]: s["watched_episodes"].remove(ecode)
                                    save_db(); break
                        
                        st.checkbox(
                            f"E{ep['episode_number']}. {ep.get('name', 'Episode')}",
                            value=is_watched,
                            key=f"chk_{show['id']}_{e_code}",
                            on_change=on_check
                        )
                    with col2:
                        if st.button("ℹ️", key=f"info_{show['id']}_{e_code}"):
                            show_episode_details(show['id'], show['name'], e_code, ep, is_watched)

with t_movies:
    st.subheader("My Movies")
    for m in st.session_state.db["movies"]:
        details = fetch_api(f"https://api.themoviedb.org/3/movie/{m['id']}?api_key={TMDB_KEY}")
        is_watched = m.get("watched", False)
        
        with st.expander(f"🎬 {m['name']}"):
            if details.get("backdrop_path"):
                st.image(f"https://image.tmdb.org/t/p/w500{details['backdrop_path']}", use_column_width=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("ℹ️ Movie Info", key=f"m_info_{m['id']}", use_container_width=True):
                    show_movie_details(m['id'], m['name'], details, is_watched)
            with c2:
                def on_mov_check(mid=m['id']):
                    st.session_state.db["movies"] = [mov | {"watched": st.session_state[f"mov_{mid}"]} if mov["id"] == mid else mov for mov in st.session_state.db["movies"]]
                    save_db()
                
                st.checkbox("✅ Watched", value=is_watched, key=f"mov_{m['id']}", on_change=on_mov_check)

# ==========================================
# TAB 6: PROFILE STATS
# ==========================================
with t_profile:
    st.subheader("Profile Stats")
    
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
    
    st.markdown("### Time Spent Watching")
    col1, col2, col3 = st.columns(3)
    col1.metric("Months", f"{months}")
    col2.metric("Days", f"{days}")
    col3.metric("Hours", f"{hours}")
    
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Episodes Watched", total_episodes_watched)
    c2.metric("Movies Watched", total_movies_watched)
