import streamlit as st
import requests
import pandas as pd
import json
import time
import re
import zlib
import base64
from datetime import datetime, timedelta

# Mobile-friendly layout configuration
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")

# --- MOBILE-FIRST NATIVE APP CSS ---
st.markdown("""
<style>
    /* Hide Default Streamlit Clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* True Mobile Edge-to-Edge Layout */
    .block-container { 
        padding: 1rem 0.5rem 5rem 0.5rem !important; 
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }
    
    img { border-radius: 8px !important; }
    [data-testid="stProgressBar"] > div > div { background-color: #FFC107 !important; }
    
    /* Sleek Native-App Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important; 
        border: 1px solid rgba(200, 200, 200, 0.2) !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05) !important; 
        padding: 0.5rem !important;
    }
    
    /* Touch-Friendly Button Targets */
    div.stButton > button {
        border-radius: 20px; font-weight: 600; transition: all 0.2s;
        padding: 4px 8px !important; font-size: 0.75rem !important;
        min-height: 2.2rem;
    }
    div.stButton > button:active { transform: scale(0.95); }
    
    button[kind="primary"] { background-color: #FFC107 !important; color: #000 !important; border: none !important; }
    button[kind="secondary"] { background-color: #222 !important; color: #ccc !important; border: 1px solid #444 !important; }
    
    /* --- RESPONSIVE MOBILE MAGIC --- */
    @media (max-width: 768px) {
        /* 1. Swipeable Top Navigation Tabs */
        div[data-testid="stTabs"] > div[role="tablist"] {
            display: flex !important; overflow-x: auto !important;
            scrollbar-width: none; -ms-overflow-style: none;
        }
        div[data-testid="stTabs"] > div[role="tablist"]::-webkit-scrollbar { display: none; }
        
        /* 2. Override Streamlit's Auto-Stacking */
        div[data-testid="stHorizontalBlock"], div[data-testid="stColumns"] {
            flex-direction: row !important;
            flex-wrap: wrap !important;
        }
        
        /* 3. Mathematical 3x3 Grid Lock for Posters */
        div[data-testid="column"]:nth-child(1):nth-last-child(3),
        div[data-testid="column"]:nth-child(2):nth-last-child(2),
        div[data-testid="column"]:nth-child(3):nth-last-child(1),
        div[data-testid="stColumn"]:nth-child(1):nth-last-child(3),
        div[data-testid="stColumn"]:nth-child(2):nth-last-child(2),
        div[data-testid="stColumn"]:nth-child(3):nth-last-child(1) {
            flex: 0 0 calc(33.333% - 0.5rem) !important;
            max-width: calc(33.333% - 0.5rem) !important;
            min-width: calc(33.333% - 0.5rem) !important;
            padding: 0 !important;
        }
        
        /* 4. Fluid Width for 2-Column Elements (like Feed & Toggles) */
        div[data-testid="column"]:nth-child(1):nth-last-child(2),
        div[data-testid="column"]:nth-child(2):nth-last-child(1),
        div[data-testid="stColumn"]:nth-child(1):nth-last-child(2),
        div[data-testid="stColumn"]:nth-child(2):nth-last-child(1) {
            min-width: 0 !important; 
            padding: 0 0.2rem !important;
        }
        
        /* 5. Widescreen Pop-up Dialogs */
        div[role="dialog"] {
            width: 95vw !important; max-width: 95vw !important;
            margin: 0 auto !important; padding: 1rem !important;
        }
    }
    
    /* Text formatting for tight mobile grids */
    .grid-title {
        font-size: 0.65rem !important; font-weight: 700; white-space: nowrap; overflow: hidden;
        text-overflow: ellipsis; text-align: center; margin-top: 6px; line-height: 1.2;
    }
    
    .badge {
        display: inline-block; background-color: #333333; color: #FFFFFF; padding: 3px 8px;
        border-radius: 12px; font-size: 0.7rem; font-weight: 600; margin-right: 4px; margin-bottom: 6px;
    }
    .badge-gold { background-color: #FFC107; color: #000000; }
    
    /* Edge-to-Edge Poster Magic */
    .movie-poster-sharp img { border-radius: 6px !important; aspect-ratio: 2/3; object-fit: cover; }
    .movie-wall-btn div.stButton > button {
        border: none !important; background-color: transparent !important; color: #aaa !important;
        font-size: 0.7rem !important; padding: 0 !important; margin-top: 2px !important; margin-bottom: 5px !important; 
        text-transform: uppercase; letter-spacing: 1px; min-height: 1.5rem !important;
    }
    .movie-wall-btn div.stButton > button:active { color: white !important; }
    
    /* Feed Stylings for Watch Journal */
    .feed-title { font-size: 0.95rem !important; font-weight: 700; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .feed-date { font-size: 0.75rem !important; color: #aaa; margin-top: 4px; margin-bottom: 6px;}
</style>
""", unsafe_allow_html=True)

# --- PAGINATION STATES ---
if "next_tv_limit" not in st.session_state: st.session_state.next_tv_limit = 50
if "next_mov_limit" not in st.session_state: st.session_state.next_mov_limit = 50
if "soon_tv_limit" not in st.session_state: st.session_state.soon_tv_limit = 50
if "soon_mov_limit" not in st.session_state: st.session_state.soon_mov_limit = 50
if "hist_tv_limit" not in st.session_state: st.session_state.hist_tv_limit = 10
if "hist_mov_limit" not in st.session_state: st.session_state.hist_mov_limit = 10

# --- CREDENTIALS & DB ---
TMDB_KEY = st.secrets["TMDB_KEY"]
BIN_KEY = st.secrets["JSONBIN_KEY"]
BIN_ID = st.secrets["JSONBIN_ID"]
BIN_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
headers = {
    "X-Master-Key": BIN_KEY, 
    "Content-Type": "application/json",
    "X-Bin-Versioning": "false" 
}
TODAY = datetime.today().strftime('%Y-%m-%d')

@st.cache_data(ttl=3600)
def fetch_api(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def fetch_robust(url):
    for _ in range(3):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 429:
                time.sleep(1.5)
                continue
            if r.status_code == 200:
                return r.json()
            return {}
        except: time.sleep(1)
    return {}

# --- MATHEMATICAL RANGE ENCODER ---
def encode_eps(eps):
    seasons = {}
    for ep in eps:
        try:
            s, e = ep.split('E')
            seasons.setdefault(int(s.replace('S', '')), []).append(int(e))
        except: pass
    res = []
    for s, e_list in seasons.items():
        if not e_list: continue
        e_list = sorted(list(set(e_list)))
        ranges, start, prev = [], e_list[0], e_list[0]
        for e in e_list[1:]:
            if e == prev + 1: prev = e
            else:
                ranges.append(str(start) if start == prev else f"{start}-{prev}")
                start = prev = e
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        res.append(f"{s}:{'.'.join(ranges)}")
    return "|".join(res)

def decode_eps(ep_str):
    if not ep_str: return []
    eps = []
    for s_part in str(ep_str).split('|'):
        if ':' not in s_part: continue
        s, e_part = s_part.split(':')
        for r in e_part.split('.'):
            if '-' in r:
                start, end = r.split('-')
                eps.extend([f"S{s}E{e}" for e in range(int(start), int(end)+1)])
            else:
                if r: eps.append(f"S{s}E{r}")
    return eps

# --- DEEP COMPRESSION ENGINE ---
def pack_db(db):
    packed = {"m": [], "s": [], "h": [], "a": {}}
    for m in db.get("movies", []):
        packed["m"].append([m["id"], m["name"], 1 if m["watched"] else 0, m.get("poster_path", ""), m.get("release_date", ""), m.get("runtime", 0)])
    for s in db.get("shows", []):
        packed["s"].append([s["id"], s["name"], encode_eps(s.get("watched_episodes", [])), s.get("poster_path", ""), s.get("first_air_date", ""), s.get("total_episodes", 1)])
    for h in db.get("history", []):
        packed["h"].append([1 if h.get("t") == "s" else 0, h.get("i"), h.get("e", ""), h.get("d")])
    for k, v in db.get("analytics", {}).items():
        packed["a"][k] = [v.get("tv", 0), v.get("movie", 0)]
    return packed

def unpack_db(packed):
    db = {"movies": [], "shows": [], "history": [], "analytics": {}}
    for m in packed.get("m", []):
        db["movies"].append({"id": m[0], "name": m[1], "watched": bool(m[2]), "poster_path": m[3], "release_date": m[4], "runtime": m[5]})
    for s in packed.get("s", []):
        db["shows"].append({"id": s[0], "name": s[1], "watched_episodes": decode_eps(s[2]), "poster_path": s[3], "first_air_date": s[4], "total_episodes": s[5]})
    for h in packed.get("h", []):
        db["history"].append({"t": "s" if h[0]==1 else "m", "i": h[1], "e": h[2], "d": h[3]})
    for k, v in packed.get("a", {}).items():
        db["analytics"][k] = {"tv": v[0], "movie": v[1]}
    return db

def load_db():
    url = f"{BIN_URL}?meta=false&t={int(time.time())}" 
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        if "record" in data: data = data["record"]
        if "payload" in data:
            try:
                dec = base64.b64decode(data["payload"])
                decomp = zlib.decompress(dec).decode('utf-8')
                packed_data = json.loads(decomp)
                return unpack_db(packed_data)
            except Exception as e:
                st.error(f"Error extracting compressed database: {e}")
                return None
        elif "m" in data and "s" in data:
            return unpack_db(data)
        
        if "shows" not in data: data["shows"] = []
        if "movies" not in data: data["movies"] = []
        if "history" not in data: data["history"] = []
        if "analytics" not in data: data["analytics"] = {}
        return data
    else:
        st.error(f"⚠️ Failed to connect to JSONBin. Code: {res.status_code} | Msg: {res.text}")
        return None

def save_db():
    try:
        packed = pack_db(st.session_state.db)
        raw_str = json.dumps(packed, separators=(',', ':'))
        comp = zlib.compress(raw_str.encode('utf-8'), level=9)
        b64 = base64.b64encode(comp).decode('utf-8')
        payload = {"payload": b64}
        
        res = requests.put(BIN_URL, json=payload, headers=headers)
        if res.status_code != 200:
            st.error(f"⚠️ Cloud Save Blocked! Code: {res.status_code} | Reason: {res.text}")
            return False
        return True
    except Exception as e:
        st.error(f"Compression Engine Error: {e}")
        return False

if "db" not in st.session_state:
    db_data = load_db()
    if db_data is None: st.stop()
    st.session_state.db = db_data

# --- CENTRALIZED HISTORY LOGGER ---
def log_watch(item_type, item_id, detail=""):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    m_key = datetime.now().strftime('%Y-%m')
    db = st.session_state.db
    
    db.setdefault("analytics", {}).setdefault(m_key, {"tv": 0, "movie": 0})
    if item_type == "tv": db["analytics"][m_key]["tv"] += 1
    else: db["analytics"][m_key]["movie"] += 1
    
    t_flag = "s" if item_type == "tv" else "m"
    db.setdefault("history", []).insert(0, {"t": t_flag, "i": item_id, "e": detail, "d": now_str})
    
    tv_h = [h for h in db["history"] if h.get("t") == "s"][:100]
    mov_h = [h for h in db["history"] if h.get("t") == "m"][:100]
    db["history"] = tv_h + mov_h
    if save_db(): st.toast("Watched! ✅")

def remove_watch(item_type, item_id, detail=""):
    db = st.session_state.db
    t_flag = "s" if item_type == "tv" else "m"
    
    for idx, h in enumerate(db.get("history", [])):
        if h.get("t") == t_flag and str(h.get("i")) == str(item_id) and str(h.get("e", "")) == str(detail):
            removed = db["history"].pop(idx)
            try:
                m_key = datetime.strptime(removed["d"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                if m_key in db.get("analytics", {}) and db["analytics"][m_key].get(item_type, 0) > 0:
                    db["analytics"][m_key][item_type] -= 1
            except: pass
            break
    save_db()

# --- HELPERS ---
def render_badges(items, is_gold=False):
    css_class = "badge badge-gold" if is_gold else "badge"
    html = "".join([f'<span class="{css_class}">{item}</span>' for item in items])
    st.markdown(html, unsafe_allow_html=True)

def display_poster(path, width=185):
    if path and str(path).lower() not in ["none", "null", ""]:
        st.image(f"https://image.tmdb.org/t/p/w{width}{path}", use_container_width=True)
    else:
        st.markdown(f'<div style="background-color:#222; border-radius:8px; width:100%; aspect-ratio: 2/3; display:flex; align-items:center; justify-content:center; color:#555; font-size:0.8rem; text-align:center; margin-bottom:5px;">No Image</div>', unsafe_allow_html=True)

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
        clean_str = str(d_str).replace("Z", "").replace("T", " ").split(".")[0]
        dt = datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except: return "2000-01-01 12:00:00"

# --- DIALOGS (Lazy Loaded for Speed) ---
@st.dialog("Episode Details")
def show_episode_details(show_id, show_name, ep_code, ep_data=None, is_watched=False):
    # Lazy fetch API data only when button is clicked!
    if not ep_data:
        try:
            s_num = ep_code.split('E')[0].replace('S', '')
            e_num = ep_code.split('E')[1]
            ep_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/season/{s_num}/episode/{e_num}?api_key={TMDB_KEY}")
        except: ep_data = {}
        
    display_poster(ep_data.get("still_path"), width=500)
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
    if st.button(btn_label, use_container_width=True, key=f"dlg_btn_tv_{show_id}_{ep_code}"):
        for s in st.session_state.db["shows"]:
            if str(s["id"]) == str(show_id):
                if is_watched and ep_code in s["watched_episodes"]: 
                    s["watched_episodes"].remove(ep_code)
                    remove_watch("tv", show_id, ep_code)
                elif not is_watched and ep_code not in s["watched_episodes"]: 
                    s["watched_episodes"].append(ep_code)
                    log_watch("tv", show_id, ep_code)
                break
        st.rerun()

@st.dialog("Manage Show")
def manage_show_dialog(show_id, show_name, details):
    display_poster(details.get("backdrop_path"), width=500)
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
        current_show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(show_id)), None)
        watched_list = current_show.get("watched_episodes", []) if current_show else []
        for ep in s_data.get("episodes", []):
            e_code = f"S{sel_s}E{ep['episode_number']}"
            is_watched = e_code in watched_list
            info_key = f"view_info_{show_id}_{e_code}"
            def on_check(sid=show_id, sname=show_name, ecode=e_code):
                chkd = st.session_state[f"chk_dlg_{sid}_{ecode}"]
                for s in st.session_state.db["shows"]:
                    if str(s["id"]) == str(sid):
                        if chkd and ecode not in s["watched_episodes"]: 
                            s["watched_episodes"].append(ecode)
                            log_watch("tv", sid, ecode)
                        elif not chkd and ecode in s["watched_episodes"]: 
                            s["watched_episodes"].remove(ecode)
                            remove_watch("tv", sid, ecode)
                        break
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
                    display_poster(ep.get("still_path"), width=500)
                    st.caption(f"⭐ {ep.get('vote_average', 0.0)} | **Aired:** {ep.get('air_date', 'N/A')}")
                    st.write(ep.get("overview", "No synopsis available."))
    st.divider()
    st.markdown("#### Top Cast")
    credits = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}")
    show_cast_grid(credits.get("cast", []), limit=6)

@st.dialog("Movie Details")
def show_movie_details(m_id, m_name, details=None, is_watched=False):
    # Lazy fetch API data only when button is clicked!
    if not details:
        details = fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={TMDB_KEY}")
        
    display_poster(details.get("backdrop_path"), width=500)
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
    if st.button(btn_label, use_container_width=True, key=f"dlg_btn_mov_{m_id}"):
        for m in st.session_state.db["movies"]:
            if str(m["id"]) == str(m_id):
                m["watched"] = not is_watched
                if m["watched"]: log_watch("movie", m_id)
                else: remove_watch("movie", m_id)
                break
        st.rerun()

# --- APP NAVIGATION BAR ---
t_next, t_soon, t_search, t_tv, t_movies, t_profile = st.tabs(["🔥 Next", "📅 Soon", "🔍 Search", "📺 TV", "🎬 Movies", "👤 Profile"])

# ==========================================
# TAB 1: UP NEXT DASHBOARD
# ==========================================
with t_next:
    st.markdown("### Up Next")
    col1, col2 = st.columns([1, 1])
    with col1:
        next_filter = st.radio("Category", ["📺 Series", "🎬 Movies"], horizontal=True, label_visibility="collapsed", key="next_filter_radio")
    with col2:
        next_sort = st.selectbox("Sort", ["Smart Priority", "Release Date", "Alphabetical"], label_visibility="collapsed", key="next_sort_box")
    st.divider()
    
    try: fifteen_days_ago = datetime.now() - pd.DateOffset(days=15)
    except: fifteen_days_ago = datetime.today() - timedelta(days=15)
    
    recent_active_ids = set()
    for h in st.session_state.db.get("history", []):
        try:
            dt = datetime.strptime(h.get("d", "2000-01-01 12:00:00"), '%Y-%m-%d %H:%M:%S')
            if dt >= fifteen_days_ago: recent_active_ids.add((h.get("t"), str(h.get("i"))))
        except: pass
    
    if next_filter == "📺 Series":
        up_next_tv = []
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
                        is_rec = ("s", str(show["id"])) in recent_active_ids
                        up_next_tv.append({"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date, "is_rec": is_rec})
                        found_next = True; break

        if next_sort == "Alphabetical": up_next_tv.sort(key=lambda x: x["item"]["name"].lower())
        elif next_sort == "Release Date": up_next_tv.sort(key=lambda x: x["date"] or "1900-01-01", reverse=True)
        elif next_sort == "Smart Priority": up_next_tv.sort(key=lambda x: (x["is_rec"], x["date"] or "1900-01-01"), reverse=True)

        if not up_next_tv: 
            st.info("You are completely caught up on series! 🎉")
        else:
            for item in up_next_tv[:st.session_state.next_tv_limit]:
                show, details, ep, ep_code = item["item"], item["details"], item["ep"], item["code"]
                with st.container(border=True):
                    if ep.get("still_path"): display_poster(ep['still_path'], width=500)
                    else: display_poster(details.get('backdrop_path'), width=500)
                    st.markdown(f"#### {show['name']}")
                    render_badges([ep_code, "Up Next"], is_gold=True)
                    st.markdown(f"*{ep.get('name', 'Episode')}*")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("ℹ️ Info", key=f"next_i_tv_{show['id']}_{ep_code}", use_container_width=True):
                            show_episode_details(show['id'], show['name'], ep_code, ep, is_watched=False)
                    with c2:
                        def f_w_tv(sid=show['id'], sname=show['name'], ecode=ep_code):
                            for s in st.session_state.db["shows"]:
                                if str(s["id"]) == str(sid):
                                    s["watched_episodes"].append(ecode)
                                    log_watch("tv", sid, ecode)
                                    break
                        st.button("✔️ Watched", key=f"next_w_tv_{show['id']}_{ep_code}", on_click=f_w_tv, use_container_width=True)
                        
            if len(up_next_tv) > st.session_state.next_tv_limit:
                if st.button("Load More Series", use_container_width=True, key="load_more_next_tv"):
                    st.session_state.next_tv_limit += 50
                    st.rerun()

    else:
        up_next_mov = []
        for m in st.session_state.db["movies"]:
            if not m.get("watched"):
                r_date = m.get("release_date", "")
                if r_date and r_date <= TODAY:
                    is_rec = ("m", str(m["id"])) in recent_active_ids
                    up_next_mov.append({"item": m, "date": r_date, "is_rec": is_rec})

        if next_sort == "Alphabetical": up_next_mov.sort(key=lambda x: x["item"]["name"].lower())
        elif next_sort == "Release Date": up_next_mov.sort(key=lambda x: x["date"] or "1900-01-01", reverse=True)
        elif next_sort == "Smart Priority": up_next_mov.sort(key=lambda x: (x["is_rec"], x["date"] or "1900-01-01"), reverse=True)

        if not up_next_mov: 
            st.info("You have no unwatched movies left! 🎉")
        else:
            for item in up_next_mov[:st.session_state.next_mov_limit]:
                m = item["item"]
                with st.container(border=True):
                    display_poster(m.get('poster_path'), width=500)
                    st.markdown(f"#### {m['name']}")
                    render_badges(["Movie", "Up Next"], is_gold=True)
                    st.caption(f"Released: {item['date']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("ℹ️ Info", key=f"next_i_mov_{m['id']}", use_container_width=True):
                            show_movie_details(m['id'], m['name'], details=None, is_watched=False)
                    with c2:
                        def f_w_mov(mid=m['id']):
                            for mv in st.session_state.db["movies"]:
                                if str(mv["id"]) == str(mid):
                                    mv["watched"] = True
                                    log_watch("movie", mid)
                                    break
                        st.button("✔️ Watched", key=f"next_w_mov_{m['id']}", on_click=f_w_mov, use_container_width=True)
                        
            if len(up_next_mov) > st.session_state.next_mov_limit:
                if st.button("Load More Movies", use_container_width=True, key="load_more_next_mov"):
                    st.session_state.next_mov_limit += 50
                    st.rerun()

# ==========================================
# TAB 2: UPCOMING CALENDAR
# ==========================================
with t_soon:
    st.markdown("### Upcoming Releases")
    col1, col2 = st.columns([1, 1])
    with col1:
        soon_filter = st.radio("Category", ["📺 Series", "🎬 Movies"], horizontal=True, label_visibility="collapsed", key="soon_filter_radio")
    with col2:
        soon_sort = st.selectbox("Sort", ["Release Date", "Alphabetical"], label_visibility="collapsed", key="soon_sort_box")
    st.divider()
    
    if soon_filter == "📺 Series":
        soon_tv = []
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
                        soon_tv.append({"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date})
                        found_next = True; break

        if soon_sort == "Alphabetical": soon_tv.sort(key=lambda x: x["item"]["name"].lower())
        else: soon_tv.sort(key=lambda x: x["date"] or "2099-01-01")

        if not soon_tv: 
            st.info("No upcoming episodes scheduled yet.")
        else:
            for item in soon_tv[:st.session_state.soon_tv_limit]:
                days_left = (datetime.strptime(item["date"], '%Y-%m-%d') - datetime.today()).days
                show, details, ep, ep_code = item["item"], item["details"], item["ep"], item["code"]
                with st.container(border=True):
                    if ep.get("still_path"): display_poster(ep['still_path'], width=500)
                    else: display_poster(details.get('backdrop_path'), width=500)
                    st.markdown(f"#### {show['name']}")
                    render_badges([ep_code, f"In {days_left} days"], is_gold=False)
                    st.markdown(f"*{ep.get('name', 'Episode')}*")
                    st.caption(f"Air Date: {item['date']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("ℹ️ Info", key=f"soon_i_tv_{show['id']}_{ep_code}", use_container_width=True):
                            show_episode_details(show['id'], show['name'], ep_code, ep, is_watched=False)
                    with c2:
                        def f_w_s_tv(sid=show['id'], sname=show['name'], ecode=ep_code):
                            for s in st.session_state.db["shows"]:
                                if str(s["id"]) == str(sid):
                                    s["watched_episodes"].append(ecode)
                                    log_watch("tv", sid, ecode)
                                    break
                        st.button("✔️ Watched", key=f"soon_w_tv_{show['id']}_{ep_code}", on_click=f_w_s_tv, use_container_width=True)

            if len(soon_tv) > st.session_state.soon_tv_limit:
                if st.button("Load More Upcoming Series", use_container_width=True, key="load_more_soon_tv"):
                    st.session_state.soon_tv_limit += 50
                    st.rerun()

    else:
        soon_mov = []
        for m in st.session_state.db["movies"]:
            if not m.get("watched"):
                r_date = m.get("release_date", "")
                if r_date and r_date > TODAY:
                    soon_mov.append({"item": m, "date": r_date})

        if soon_sort == "Alphabetical": soon_mov.sort(key=lambda x: x["item"]["name"].lower())
        else: soon_mov.sort(key=lambda x: x["date"] or "2099-01-01")

        if not soon_mov: 
            st.info("No upcoming movies scheduled yet.")
        else:
            for item in soon_mov[:st.session_state.soon_mov_limit]:
                days_left = (datetime.strptime(item["date"], '%Y-%m-%d') - datetime.today()).days
                m = item["item"]
                with st.container(border=True):
                    display_poster(m.get('poster_path'), width=500)
                    st.markdown(f"#### {m['name']}")
                    render_badges(["Movie", f"In {days_left} days"], is_gold=False)
                    st.caption(f"Release Date: {item['date']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("ℹ️ Info", key=f"soon_i_mov_{m['id']}", use_container_width=True):
                            show_movie_details(m['id'], m['name'], details=None, is_watched=False)
                    with c2:
                        def f_w_s_mov(mid=m['id']):
                            for mv in st.session_state.db["movies"]:
                                if str(mv["id"]) == str(mid):
                                    mv["watched"] = True
                                    log_watch("movie", mid)
                                    break
                        st.button("✔️ Watched", key=f"soon_w_mov_{m['id']}", on_click=f_w_s_mov, use_container_width=True)

            if len(soon_mov) > st.session_state.soon_mov_limit:
                if st.button("Load More Upcoming Movies", use_container_width=True, key="load_more_soon_mov"):
                    st.session_state.soon_mov_limit += 50
                    st.rerun()

# ==========================================
# TAB 3: GLOBAL SEARCH 
# ==========================================
with t_search:
    st.markdown("### Discover")
    search_type = st.radio("Category:", ["TV Shows", "Movies"], horizontal=True, key="search_filter_radio")
    search_query = st.text_input("Enter title to search:", key="search_query_input")

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
                        display_poster(item.get("poster_path"), width=154)
                    with c2:
                        st.markdown(f"**{title}**")
                        render_badges([f"⭐ {item.get('vote_average', 0.0)}"])
                        if search_type == "TV Shows":
                            if not any(str(s["id"]) == str(item_id) for s in st.session_state.db["shows"]):
                                if st.button("➕ Add", key=f"add_tv_{item_id}", use_container_width=True):
                                    details = fetch_api(f"https://api.themoviedb.org/3/tv/{item_id}?api_key={TMDB_KEY}")
                                    st.session_state.db["shows"].append({
                                        "id": item_id, "name": title, "watched_episodes": [],
                                        "poster_path": details.get("poster_path", ""), "first_air_date": details.get("first_air_date", ""),
                                        "total_episodes": details.get("number_of_episodes", 1)
                                    })
                                    if save_db():
                                        st.toast("Added!")
                                        st.rerun()
                            else: st.button("✔️ Added", key=f"dsbl_tv_{item_id}", disabled=True, use_container_width=True)
                        else:
                            if not any(str(m["id"]) == str(item_id) for m in st.session_state.db["movies"]):
                                if st.button("➕ Add", key=f"add_mov_{item_id}", use_container_width=True):
                                    details = fetch_api(f"https://api.themoviedb.org/3/movie/{item_id}?api_key={TMDB_KEY}")
                                    st.session_state.db["movies"].append({
                                        "id": item_id, "name": title, "watched": False,
                                        "poster_path": details.get("poster_path", ""), "release_date": details.get("release_date", ""),
                                        "runtime": details.get("runtime", 0)
                                    })
                                    if save_db():
                                        st.toast("Added!")
                                        st.rerun()
                            else: st.button("✔️ Added", key=f"dsbl_mov_{item_id}", disabled=True, use_container_width=True)

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
        
    tv_sort = st.selectbox("Sort Library by:", ["Release Date", "Alphabetical", "Recently Added"], key="sort_tv_lib")
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
                                display_poster(show.get("poster_path"), width=185)
                                st.markdown(f'<div class="grid-title" title="{show["name"]}">{show["name"]}</div>', unsafe_allow_html=True)
                                st.progress(min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0)
                                if st.button("DETAILS", key=f"s_mgr_{show['id']}", use_container_width=True):
                                    details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
                                    manage_show_dialog(show['id'], show['name'], details)

# ==========================================
# TAB 5: MOVIE LIBRARY
# ==========================================
with t_movies:
    st.markdown("### My Movies")
    if "mov_tab" not in st.session_state: st.session_state.mov_tab = "WATCHLIST"
        
    c1, c2, c3 = st.columns(3)
    if c1.button("Watchlist", type="primary" if st.session_state.mov_tab == "WATCHLIST" else "secondary", use_container_width=True, key="m_wl"):
        st.session_state.mov_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.mov_tab == "UPCOMING" else "secondary", use_container_width=True, key="m_up"):
        st.session_state.mov_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.mov_tab == "WATCHED" else "secondary", use_container_width=True, key="m_wd"):
        st.session_state.mov_tab = "WATCHED"; st.rerun()
        
    mov_sort = st.selectbox("Sort Library by:", ["Release Date", "Alphabetical", "Recently Added"], key="sort_mov_lib")
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
                        with cols[j]:
                            with st.container(border=True):
                                display_poster(m.get("poster_path"), width=185)
                                st.markdown(f'<div class="grid-title" title="{m["name"]}">{m["name"]}</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                if st.button("DETAILS", key=f"m_mgr_{m['id']}", use_container_width=True):
                                    show_movie_details(m['id'], m['name'], details=None, is_watched=is_watched)
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
    
    # --- PANDAS GRAPHS: 12-MONTH ROLLING WATCH ACTIVITY ---
    st.markdown("### 📊 Watch Activity")
    chart_tab1, chart_tab2 = st.tabs(["📺 Series Activity", "🎬 Movie Activity"])
    analytics = st.session_state.db.get("analytics", {})
    
    last_12_months = []
    try:
        for i in range(11, -1, -1):
            last_12_months.append((datetime.today() - pd.DateOffset(months=i)).strftime('%Y-%m'))
    except:
        for i in range(11, -1, -1):
            last_12_months.append((datetime.today() - timedelta(days=30*i)).strftime('%Y-%m'))
            
    analytics_12m = {m_str: analytics.get(m_str, {"tv": 0, "movie": 0}) for m_str in last_12_months}
    df = pd.DataFrame.from_dict(analytics_12m, orient='index')
    df.index = pd.to_datetime(df.index, format='%Y-%m').strftime('%b %Y')
    
    with chart_tab1:
        st.bar_chart(df[["tv"]], color="#FFC107")
        
    with chart_tab2:
        st.bar_chart(df[["movie"]], color="#555555")

    st.divider()
    
    # --- NATIVE APP WATCH HISTORY FEED ---
    st.markdown("### 📜 Watch History Journal")
    h_tv, h_mov = st.tabs(["📺 Series", "🎬 Movies"])
    
    history_sorted = sorted(st.session_state.db.get("history", []), key=lambda x: x.get("d", "2000-01-01 12:00:00"), reverse=True)
    
    with h_tv:
        tv_hist = [h for h in history_sorted if h.get("t") == "s"]
        if not tv_hist: st.info("No series history recorded yet.")
        else:
            grouped_tv = {}
            for h_idx, h in enumerate(tv_hist[:st.session_state.hist_tv_limit]):
                try:
                    dt = datetime.strptime(h["d"], '%Y-%m-%d %H:%M:%S')
                    grouped_tv.setdefault(dt.strftime('%B %Y'), []).append((h, dt, h_idx))
                except: pass
            
            for month_str, items in grouped_tv.items():
                st.markdown(f"#### {month_str}")
                for h, dt, h_idx in items:
                    show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(h.get("i"))), None)
                    s_name = show["name"] if show else "Unknown Series"
                    ep_code = h.get('e', '')
                    poster = show.get("poster_path", "") if show else ""
                    
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 3])
                        with c1: display_poster(poster, width=92)
                        with c2:
                            st.markdown(f'<div class="feed-title">{s_name}</div>', unsafe_allow_html=True)
                            if ep_code: render_badges([ep_code], is_gold=False)
                            st.markdown(f'<div class="feed-date">{dt.strftime("%b %d • %I:%M %p")}</div>', unsafe_allow_html=True)
                            if st.button("Details", key=f"hist_tv_btn_{h.get('i')}_{ep_code}_{h_idx}"):
                                show_episode_details(h.get('i'), s_name, ep_code, ep_data=None, is_watched=True)
                                
            if len(tv_hist) > st.session_state.hist_tv_limit:
                if st.button("Load More Series", use_container_width=True, key="load_more_tv_hist"):
                    st.session_state.hist_tv_limit += 10
                    st.rerun()
                    
    with h_mov:
        mov_hist = [h for h in history_sorted if h.get("t") == "m"]
        if not mov_hist: st.info("No movie history recorded yet.")
        else:
            grouped_mov = {}
            for h_idx, h in enumerate(mov_hist[:st.session_state.hist_mov_limit]):
                try:
                    dt = datetime.strptime(h["d"], '%Y-%m-%d %H:%M:%S')
                    grouped_mov.setdefault(dt.strftime('%B %Y'), []).append((h, dt, h_idx))
                except: pass
                
            for month_str, items in grouped_mov.items():
                st.markdown(f"#### {month_str}")
                for h, dt, h_idx in items:
                    mov = next((m for m in st.session_state.db["movies"] if str(m["id"]) == str(h.get("i"))), None)
                    m_name = mov["name"] if mov else "Unknown Movie"
                    poster = mov.get("poster_path", "") if mov else ""
                    
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 3])
                        with c1: display_poster(poster, width=92)
                        with c2:
                            st.markdown(f'<div class="feed-title">{m_name}</div>', unsafe_allow_html=True)
                            render_badges(["Movie"], is_gold=False)
                            st.markdown(f'<div class="feed-date">{dt.strftime("%b %d • %I:%M %p")}</div>', unsafe_allow_html=True)
                            if st.button("Details", key=f"hist_mov_btn_{h.get('i')}_{h_idx}"):
                                show_movie_details(h.get('i'), m_name, details=None, is_watched=True)

            if len(mov_hist) > st.session_state.hist_mov_limit:
                if st.button("Load More Movies", use_container_width=True, key="load_more_mov_hist"):
                    st.session_state.hist_mov_limit += 10
                    st.rerun()

    st.divider()
    
    # --- TV TIME ZLIB COMPRESSED IMPORTER ---
    with st.expander("⚙️ Import TV Time Data"):
        st.warning("Ensure you keep the app open until the progress bar reaches 100%.")
        wipe_db = st.checkbox("Wipe current library before importing", value=True, key="wipe_chk")
        m_file = st.file_uploader("Upload Movies JSON", type="json", key="import_movies")
        t_file = st.file_uploader("Upload Series JSON", type="json", key="import_shows")
        
        if st.button("Start Safe Import", key="start_import_btn"):
            if m_file or t_file:
                prog = st.progress(0)
                stat_txt = st.empty()
                
                new_db = {
                    "movies": [] if wipe_db else st.session_state.db.get("movies", []),
                    "shows": [] if wipe_db else st.session_state.db.get("shows", []),
                    "analytics": {} if wipe_db else st.session_state.db.get("analytics", {}),
                    "history": [] if wipe_db else st.session_state.db.get("history", [])
                }
                
                if m_file:
                    stat_txt.text("Processing Movies... fetching data safely.")
                    try:
                        m_data = json.load(m_file)
                        for idx, m in enumerate(m_data):
                            prog.progress((idx + 1) / len(m_data))
                            try:
                                raw_title = m.get("title") or ""
                                imdb_id = m.get("id", {}).get("imdb") if m.get("id") else None
                                if not imdb_id and not raw_title: continue 
                                
                                res = fetch_robust(f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_KEY}&external_source=imdb_id") if imdb_id else {}
                                    
                                if not res.get("movie_results") and raw_title:
                                    title_query = raw_title.replace(" ", "+")
                                    res = fetch_robust(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={title_query}&year={m.get('year', '')}")
                                    if res.get("results"): res["movie_results"] = [res["results"][0]]
                                    
                                if res.get("movie_results"):
                                    match = res["movie_results"][0]
                                    tmdb_id = match["id"]
                                    title = match.get("title", raw_title)
                                    poster = match.get("poster_path", "")
                                    release_date = match.get("release_date", "")
                                    is_watched = m.get("is_watched", False)
                                    
                                    if not any(str(movie["id"]) == str(tmdb_id) for movie in new_db["movies"]):
                                        new_db["movies"].append({
                                            "id": tmdb_id, "name": title, "watched": is_watched,
                                            "poster_path": poster if poster else "",
                                            "release_date": release_date if release_date else "",
                                            "runtime": 120
                                        })
                                        if is_watched:
                                            w_dt_raw = m.get("watched_at")
                                            w_dt = parse_tvtime_date(w_dt_raw) if w_dt_raw else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            m_key = datetime.strptime(w_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                                            
                                            new_db["analytics"].setdefault(m_key, {"tv": 0, "movie": 0})
                                            new_db["analytics"][m_key]["movie"] += 1
                                            new_db["history"].append({"t": "m", "i": tmdb_id, "e": "", "d": w_dt})
                            except Exception as item_error: continue 
                    except Exception as e: st.error(f"Error processing movies: {e}")
                
                if m_file and t_file: prog.progress(0)
                
                if t_file:
                    stat_txt.text("Processing Series... fetching data safely.")
                    try:
                        t_data = json.load(t_file)
                        for idx, s in enumerate(t_data):
                            prog.progress((idx + 1) / len(t_data))
                            try:
                                raw_title = s.get("title") or ""
                                tvdb_id = s.get("id", {}).get("tvdb") if s.get("id") else None
                                if not tvdb_id and not raw_title: continue 
                                    
                                res = fetch_robust(f"https://api.themoviedb.org/3/find/{tvdb_id}?api_key={TMDB_KEY}&external_source=tvdb_id") if tvdb_id else {}
                                
                                if not res.get("tv_results") and raw_title:
                                    title_query = re.sub(r'\(\d{4}\)', '', raw_title).strip().replace(" ", "+")
                                    res = fetch_robust(f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_KEY}&query={title_query}")
                                    if res.get("results"): res["tv_results"] = [res["results"][0]]
                                    
                                if res.get("tv_results"):
                                    match = res["tv_results"][0]
                                    tmdb_id = match["id"]
                                    title = match.get("name", raw_title)
                                    poster = match.get("poster_path", "")
                                    first_air_date = match.get("first_air_date", "")
                                    watched_eps = []
                                    
                                    is_new_show = not any(str(show["id"]) == str(tmdb_id) for show in new_db["shows"])
                                    if is_new_show:
                                        full_s = fetch_robust(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={TMDB_KEY}")
                                        t_eps = full_s.get("number_of_episodes", 1) if full_s else 1
                                    else: t_eps = 1
                                    
                                    for season in s.get("seasons", []):
                                        s_num = season.get("number")
                                        for ep in season.get("episodes", []):
                                            if ep.get("is_watched"):
                                                e_code = f"S{s_num}E{ep.get('number')}"
                                                watched_eps.append(e_code)
                                                w_dt_raw = ep.get("watched_at")
                                                w_dt = parse_tvtime_date(w_dt_raw) if w_dt_raw else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                m_key = datetime.strptime(w_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                                                
                                                new_db["analytics"].setdefault(m_key, {"tv": 0, "movie": 0})
                                                new_db["analytics"][m_key]["tv"] += 1
                                                new_db["history"].append({"t": "s", "i": tmdb_id, "e": e_code, "d": w_dt})
                                                
                                    if is_new_show:
                                        new_db["shows"].append({
                                            "id": tmdb_id, "name": title, "watched_episodes": watched_eps,
                                            "poster_path": poster if poster else "",
                                            "first_air_date": first_air_date if first_air_date else "",
                                            "total_episodes": t_eps
                                        })
                                    else:
                                        for show in new_db["shows"]:
                                            if str(show["id"]) == str(tmdb_id):
                                                show["watched_episodes"] = list(set(show["watched_episodes"] + watched_eps))
                                                break
                            except Exception as item_error: continue 
                    except Exception as e: st.error(f"Error processing series: {e}")
                
                new_db["history"].sort(key=lambda x: x.get("d", "2000-01-01 12:00:00"), reverse=True)
                tv_h = [h for h in new_db["history"] if h.get("t") == "s"][:100]
                mov_h = [h for h in new_db["history"] if h.get("t") == "m"][:100]
                new_db["history"] = tv_h + mov_h
                
                st.session_state.db = new_db
                
                if save_db():
                    stat_txt.text("✅ Mass Import & Cloud Sync Complete!")
                    st.toast("Library successfully imported.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    stat_txt.text("🛑 Import finished, but the cloud save failed. See error above.")
            else:
                st.error("Please upload at least one JSON file first.")
