import streamlit as st
import requests
import pandas as pd
import json
import time
import re
import calendar
import random
from datetime import datetime, timedelta
from st_keyup import st_keyup
import altair as alt

# Mobile-friendly layout configuration
st.set_page_config(page_title="My TV Time", layout="centered", initial_sidebar_state="collapsed")

# --- MOBILE-FIRST TARGETED CSS OVERHAUL (AGGRESSIVE PREMIUM OVERRIDE) ---
st.markdown("""
<style>
    /* --- STREAMLIT UI ANNIHILATION --- */
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important; background: transparent !important;}
    footer {visibility: hidden !important; display: none !important;}
    
    /* THE BOTTOM-RIGHT POPUP KILLER */
    [data-testid="stAppViewContainer"] ~ div { display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important; }
    .viewerBadge_container, .viewerBadge_link, div[class^="viewerBadge"] {display: none !important; visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    
    /* --- PREMIUM OLED BACKGROUND (FORCED) --- */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #050505 !important;
        background-image: radial-gradient(circle at 50% 0%, #1A1D24 0%, #050505 80%) !important;
        background-attachment: fixed !important;
        color: #EDEDED !important;
    }
    
    /* True Mobile Edge-to-Edge Layout */
    .block-container { 
        padding: 1rem 0.5rem 5rem 0.5rem !important; 
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }
    
    img { border-radius: 8px !important; }
    [data-testid="stProgressBar"] > div > div { background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%) !important; }
    
    /* --- MODERATE "HALF-SQUEEZE" SPACING --- */
    [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
    hr { margin: 0.8rem 0 !important; border-color: rgba(255, 255, 255, 0.1) !important; }
    h1, h2, h3 { padding-top: 0.6rem !important; padding-bottom: 0.3rem !important; margin-bottom: 0 !important; }
    .stMarkdown p { margin-bottom: 0.5rem !important; }
    
    /* --- SLEEK TYPOGRAPHY & COLORS FOR HEADERS --- */
    h3 { 
        color: #FFD54F !important; 
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Pull the specific tab headers up into the empty space */
    h3.tab-title {
        margin-top: -0.8rem !important;
        padding-top: 0 !important;
    }
    
    /* --- SQUEEZE EMPTY SPACE OUT OF POSTER GRIDS ONLY --- */
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        gap: 0.25rem !important; 
    }
    
    /* --- SLICK NATIVE iOS-STYLE FULL WIDTH CONTROLS --- */
    div[data-testid="stRadio"] { width: 100% !important; }
    div[data-testid="stRadio"] > div { width: 100% !important; }
    
    /* Deep Recessed Navigation Container */
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        background-color: rgba(0, 0, 0, 0.7) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: inset 0px 4px 10px rgba(0,0,0,0.8) !important;
        padding: 4px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    div[role="radiogroup"] > label {
        flex: 1 1 0px !important;
        display: flex !important;
        justify-content: center !important;
        padding: 8px 0px !important;
        border-radius: 12px !important;
        margin: 0 !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        min-width: 0 !important;
    }
    div[role="radiogroup"] > label > div:first-child { display: none !important; }
    
    /* Premium Gold Glowing Active State (Using :has to force Streamlit override) */
    div[role="radiogroup"] > label:has(input:checked) { 
        background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%) !important; 
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4) !important;
        border: none !important;
    }
    div[role="radiogroup"] > label:has(input:checked) p { 
        color: #000 !important; 
        font-weight: 800 !important; 
        text-shadow: none !important;
    }
    div[role="radiogroup"] > label p { 
        font-size: 0.8rem !important; 
        font-weight: 600 !important; 
        margin: 0 !important; 
        color: #888 !important; 
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: clip !important;
    }
    
    /* Deep Recessed Selectboxes */
    div[data-baseweb="select"] > div:first-child {
        background-color: rgba(0, 0, 0, 0.7) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: inset 0px 4px 10px rgba(0,0,0,0.8) !important;
        padding: 4px !important;
    }
    
    /* --- PREMIUM GLASSMORPHISM CARDS (FORCED) --- */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, rgba(30, 32, 40, 0.6) 0%, rgba(15, 17, 22, 0.8) 100%) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 12px !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.6) !important; 
        padding: 0.3rem !important;
    }
    
    /* --- PRIMARY ACTION OVERRIDE (Tabs & Standard Buttons) --- */
    button[kind="primary"] { 
        background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%) !important; 
        color: #000 !important; 
        border: none !important; 
        border-radius: 20px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4) !important;
        letter-spacing: 0.5px !important;
    }
    button[kind="secondary"] { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        color: #F8F9FA !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 20px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover {
        border-color: rgba(255, 193, 7, 0.5) !important;
        color: #FFD54F !important; 
    }
    
    /* --- SLEEK FROSTED BLOCK BUTTONS (SCOPED TO POSTERS ONLY) --- */
    .movie-wall-btn div.stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 6px !important; 
        color: #E0E0E0 !important;
        font-size: 0.50rem !important; 
        font-weight: 700 !important;
        padding: 4px 1px !important; 
        margin: 0 !important;
        text-transform: uppercase;
        letter-spacing: -0.2px !important; 
        min-height: 1.8rem !important; 
        line-height: 1;
        width: 100% !important;
        white-space: nowrap !important; 
        overflow: hidden !important;
        text-overflow: clip !important;
        transition: all 0.2s !important;
    }
    .movie-wall-btn div.stButton > button:hover, 
    .movie-wall-btn div.stButton > button:active { 
        transform: scale(0.95); 
        background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%) !important; 
        color: #000 !important;
        border-color: #FFC107 !important;
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.5) !important;
    }
    
    /* --- SYMMETRICAL TOP NAVIGATION TABS (PREMIUM HEADER) --- */
    div[data-testid="stTabs"] > div[data-baseweb="tab-list"],
    div[data-testid="stTabs"] > div[role="tablist"] {
        display: flex !important; 
        width: 100vw !important;
        max-width: 100% !important;
        margin-left: -0.5rem !important; 
        padding: 0 0 5px 0 !important;
        gap: 0 !important; 
        overflow-x: hidden !important; 
        background-color: rgba(8, 9, 12, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    div[data-testid="stTabs"] button[role="tab"] {
        flex: 1 1 0px !important; 
        min-width: 0 !important; 
        padding: 10px 0px !important;
        margin: 0 !important;
        border-radius: 0 !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="stTabs"] button[role="tab"] p {
        font-size: 0.55rem !important; 
        font-weight: 700 !important;
        text-align: center !important;
        margin: 0 auto !important;
        white-space: nowrap !important;
        letter-spacing: -0.4px !important; 
        overflow: hidden !important;
        text-overflow: clip !important;
        color: #888 !important;
        transition: all 0.3s ease !important;
    }

    /* Active Gold Tab Glow (Using true aria-selected state) */
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        border-bottom: 3px solid #FFC107 !important;
        background: linear-gradient(to top, rgba(255, 193, 7, 0.15) 0%, transparent 100%) !important;
        box-shadow: inset 0px -10px 15px -10px rgba(255, 193, 7, 0.5) !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {
        color: #FFD54F !important;
        text-shadow: 0px 0px 10px rgba(255, 193, 7, 0.6) !important;
    }
    
    /* --- DISCOVER FEED: HORIZONTAL CAROUSEL HACK --- */
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker),
    div[data-testid="stColumns"]:has(.carousel-marker) {
        display: flex !important;
        flex-direction: row !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        scrollbar-width: none;
        -ms-overflow-style: none;
        padding-bottom: 15px !important;
        gap: 12px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker)::-webkit-scrollbar,
    div[data-testid="stColumns"]:has(.carousel-marker)::-webkit-scrollbar { 
        display: none; 
    }
    div[data-testid="column"]:has(.carousel-marker),
    div[data-testid="stColumn"]:has(.carousel-marker) {
        flex: 0 0 110px !important; 
        width: 110px !important;
        min-width: 110px !important;
        padding: 0 !important;
        display: block !important;
    }
    
    /* --- GRID LOCK FOR HIGH-DPI SCREENS --- */
    @media (max-width: 992px) {
        /* STRICT 3-COLUMN LOCK (Libraries) */
        div[data-testid="stHorizontalBlock"]:has(.grid-3-col),
        div[data-testid="stColumns"]:has(.grid-3-col) {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2% !important; 
        }
        div[data-testid="column"]:has(.grid-3-col),
        div[data-testid="stColumn"]:has(.grid-3-col) {
            width: 32% !important; flex: 1 1 32% !important; min-width: 0 !important; padding: 0 !important; display: block !important;
        }
        
        /* STRICT 2-COLUMN LOCK (For Button Row Splits inside Cards) */
        div[data-testid="stHorizontalBlock"]:has(.grid-2-col),
        div[data-testid="stColumns"]:has(.grid-2-col) {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 4% !important; 
        }
        div[data-testid="column"]:has(.grid-2-col),
        div[data-testid="stColumn"]:has(.grid-2-col) {
            width: 48% !important; flex: 1 1 48% !important; min-width: 0 !important; padding: 0 !important; display: block !important;
        }
        
        /* Widescreen Pop-up Dialogs */
        div[role="dialog"] {
            width: 95vw !important; max-width: 95vw !important; margin: 0 auto !important; padding: 1rem !important;
            background: rgba(15, 17, 22, 0.95) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    }
    
    /* Text formatting for tight mobile grids */
    .grid-title {
        font-size: 0.65rem !important; font-weight: 700; white-space: nowrap; overflow: hidden;
        text-overflow: ellipsis; text-align: center; margin-top: 2px; margin-bottom: 2px; line-height: 1.2; color: #ddd;
    }
    
    .badge {
        display: inline-block; background-color: rgba(255,255,255,0.1); color: #FFFFFF; padding: 3px 8px;
        border-radius: 12px; font-size: 0.7rem; font-weight: 600; margin-right: 4px; margin-bottom: 6px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .badge-gold { 
        background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%); 
        color: #000000; 
        border: none;
        box-shadow: 0 2px 6px rgba(255, 193, 7, 0.3);
    }
    
    /* Edge-to-Edge Poster Magic */
    .movie-poster-sharp img { border-radius: 6px !important; aspect-ratio: 2/3; object-fit: cover; }
</style>
""", unsafe_allow_html=True)

# --- DUBAI TIMEZONE OVERRIDE ---
def get_dubai_time():
    return datetime.utcnow() + timedelta(hours=4)

# --- PAGINATION STATES ---
if "next_tv_limit" not in st.session_state: st.session_state.next_tv_limit = 30
if "next_mov_limit" not in st.session_state: st.session_state.next_mov_limit = 30
if "soon_tv_limit" not in st.session_state: st.session_state.soon_tv_limit = 30
if "soon_mov_limit" not in st.session_state: st.session_state.soon_mov_limit = 30
if "hist_tv_limit" not in st.session_state: st.session_state.hist_tv_limit = 20
if "hist_mov_limit" not in st.session_state: st.session_state.hist_mov_limit = 20
if "tv_lib_limit" not in st.session_state: st.session_state.tv_lib_limit = 50
if "mov_lib_limit" not in st.session_state: st.session_state.mov_lib_limit = 50
if "c_limits" not in st.session_state: st.session_state.c_limits = {}
if "rec_show" not in st.session_state: st.session_state.rec_show = None 
if "last_action" not in st.session_state: st.session_state.last_action = None
if "rate_item" not in st.session_state: st.session_state.rate_item = None

# --- SUPABASE DATABASE PIPELINE ---
TMDB_KEY = st.secrets["TMDB_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"].rstrip("/") 
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
DB_ENDPOINT = f"{SUPABASE_URL}/rest/v1/tv_time_data?id=eq.1"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
TODAY = get_dubai_time().strftime('%Y-%m-%d')

# --- PERSISTENT DISK CACHING (12 HOURS) ---
@st.cache_data(ttl=43200, persist="disk")
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

def pack_db(db):
    packed = {"m": [], "s": [], "h": [], "a": {}}
    for m in db.get("movies", []):
        packed["m"].append([m["id"], m["name"], 1 if m["watched"] else 0, m.get("poster_path", ""), m.get("release_date", ""), m.get("runtime", 0)])
    for s in db.get("shows", []):
        packed["s"].append([s["id"], s["name"], encode_eps(s.get("watched_episodes", [])), s.get("poster_path", ""), s.get("first_air_date", ""), s.get("total_episodes", 1)])
    for h in db.get("history", []):
        packed["h"].append([1 if h.get("t") == "s" else 0, h.get("i"), h.get("e", ""), h.get("d"), h.get("r", 0), h.get("f", ""), h.get("p", "")])
    for k, v in db.get("analytics", {}).items():
        packed["a"][k] = [v.get("tv", 0), v.get("movie", 0)]
    packed["r"] = db.get("seen_recaps", [])
    return packed

def unpack_db(packed):
    db = {"movies": [], "shows": [], "history": [], "analytics": {}, "seen_recaps": []}
    for m in packed.get("m", []):
        db["movies"].append({"id": m[0], "name": m[1], "watched": bool(m[2]), "poster_path": m[3], "release_date": m[4], "runtime": m[5]})
    for s in packed.get("s", []):
        db["shows"].append({"id": s[0], "name": s[1], "watched_episodes": decode_eps(s[2]), "poster_path": s[3], "first_air_date": s[4], "total_episodes": s[5]})
    for h in packed.get("h", []):
        entry = {"t": "s" if h[0]==1 else "m", "i": h[1], "e": h[2], "d": h[3]}
        if len(h) > 4: entry["r"] = h[4]
        if len(h) > 5: entry["f"] = h[5]
        if len(h) > 6: entry["p"] = h[6]
        db["history"].append(entry)
    for k, v in packed.get("a", {}).items():
        db["analytics"][k] = {"tv": v[0], "movie": v[1]}
    db["seen_recaps"] = packed.get("r", [])
    return db

def load_db():
    try:
        res = requests.get(DB_ENDPOINT, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 0:
                payload = data[0].get("payload", {})
                if "m" in payload and "s" in payload:
                    return unpack_db(payload)
            return {"shows": [], "movies": [], "history": [], "analytics": {}, "seen_recaps": []}
        else:
            st.error(f"⚠️ Supabase Connection Failed: {res.status_code}")
            return None
    except Exception as e:
        st.error(f"⚠️ Database Error: {e}")
        return None

def save_db():
    try:
        packed = pack_db(st.session_state.db)
        res = requests.patch(DB_ENDPOINT, json={"payload": packed}, headers=HEADERS, timeout=5)
        if res.status_code not in [200, 204]:
            st.error(f"⚠️ Supabase Save Blocked! Code: {res.status_code} | Reason: {res.text}")
            return False
        return True
    except Exception as e:
        st.error(f"Database Engine Error: {e}")
        return False

if "db" not in st.session_state:
    db_data = load_db()
    if db_data is None: st.stop()
    st.session_state.db = db_data

# --- HISTORY RECOVERY SYSTEM (PREVENTS DUPLICATE OR ORPHAN DATA) ---
def get_watched_from_history(item_type, item_id):
    t_flag = "s" if item_type == "tv" else "m"
    watched = []
    for h in st.session_state.db.get("history", []):
        if h.get("t") == t_flag and str(h.get("i")) == str(item_id):
            if item_type == "tv" and h.get("e"): 
                watched.append(h.get("e"))
            elif item_type == "movie": 
                return True
    return list(set(watched)) if item_type == "tv" else False

# --- CENTRALIZED HISTORY LOGGER ---
def log_watch(item_type, item_id, detail=""):
    now_str = get_dubai_time().strftime('%Y-%m-%d %H:%M:%S')
    m_key = get_dubai_time().strftime('%Y-%m')
    db = st.session_state.db
    
    db.setdefault("analytics", {}).setdefault(m_key, {"tv": 0, "movie": 0})
    if item_type == "tv": db["analytics"][m_key]["tv"] += 1
    else: db["analytics"][m_key]["movie"] += 1
    
    t_flag = "s" if item_type == "tv" else "m"
    db.setdefault("history", []).insert(0, {"t": t_flag, "i": item_id, "e": detail, "d": now_str, "r": 0, "f": "", "p": ""})
    
    st.session_state.last_action = {"t": item_type, "i": item_id, "e": detail}
    
    tv_h = [h for h in db["history"] if h.get("t") == "s"][:100]
    mov_h = [h for h in db["history"] if h.get("t") == "m"][:100]
    db["history"] = tv_h + mov_h
    save_db()

def remove_watch(item_type, item_id, detail=""):
    db = st.session_state.db
    t_flag = "s" if item_type == "tv" else "m"
    
    # Unmark from History
    for idx, h in enumerate(db.get("history", [])):
        if h.get("t") == t_flag and str(h.get("i")) == str(item_id) and str(h.get("e", "")) == str(detail):
            removed = db["history"].pop(idx)
            try:
                m_key = datetime.strptime(removed["d"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                if m_key in db.get("analytics", {}) and db["analytics"][m_key].get(item_type, 0) > 0:
                    db["analytics"][m_key][item_type] -= 1
            except: pass
            break
            
    # Unmark from Library State
    if item_type == "tv":
        for show in db.get("shows", []):
            if str(show.get("id")) == str(item_id):
                if detail in show.get("watched_episodes", []):
                    show["watched_episodes"].remove(detail)
                break
    else:
        for m in db.get("movies", []):
            if str(m.get("id")) == str(item_id):
                m["watched"] = False
                break
    save_db()

def calc_time_remaining(date_str):
    if not date_str: return "Soon"
    try:
        target = datetime.strptime(date_str, '%Y-%m-%d')
        now = get_dubai_time()
        diff = target - now
        days = diff.days
        hours = diff.seconds // 3600
        if days > 0: return f"In {days}d {hours}h"
        elif days == 0 and hours > 0: return f"In {hours}h"
        else: return "Today"
    except: return "Soon"

# --- TOP-LEVEL GLOBAL CALLBACKS (CRASH PREVENTION & AUTO-POP) ---
def cb_watch_tv(sid, ecode):
    for s in st.session_state.db["shows"]:
        if str(s["id"]) == str(sid):
            if ecode not in s["watched_episodes"]:
                s["watched_episodes"].append(ecode)
                log_watch("tv", sid, ecode)
                st.session_state.rate_item = {"t": "tv", "id": sid, "e": ecode}
            break

def cb_watch_mov(mid):
    for mv in st.session_state.db["movies"]:
        if str(mv["id"]) == str(mid):
            if not mv.get("watched"):
                mv["watched"] = True
                log_watch("movie", mid)
                st.session_state.rate_item = {"t": "movie", "id": mid}
            break
            
def cb_delete_tv(sid):
    st.session_state.db["shows"] = [s for s in st.session_state.db["shows"] if str(s["id"]) != str(sid)]
    save_db()
    
def cb_delete_mov(mid):
    st.session_state.db["movies"] = [mv for mv in st.session_state.db["movies"] if str(mv["id"]) != str(mid)]
    save_db()
    
def cb_toggle_episode(sid, ecode):
    chkd = st.session_state.get(f"chk_dlg_{sid}_{ecode}", False)
    for s in st.session_state.db["shows"]:
        if str(s["id"]) == str(sid):
            if chkd and ecode not in s["watched_episodes"]: 
                s["watched_episodes"].append(ecode)
                log_watch("tv", sid, ecode)
            elif not chkd and ecode in s["watched_episodes"]: 
                s["watched_episodes"].remove(ecode)
                remove_watch("tv", sid, ecode)
            break


# --- AUTOMATED POP-UP RECAP ENGINE (MONTHLY & YEARLY AUTOMATION) ---
@st.dialog("🌙 Monthly Wrap-Up")
def show_monthly_recap_dialog(month_key, month_title, stats, recap_id):
    st.markdown(f"## {month_title} Recap")
    st.write("Here is a quick look at your screening inventory from last month:")
    
    tv_count = stats.get("tv", 0)
    mov_count = stats.get("movie", 0)
    total_mins = (tv_count * 45) + (mov_count * 120)
    hours = total_mins // 60
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("📺 Episodes Logged", f"{tv_count} eps")
    with c2:
        st.metric("🎬 Movies Watched", f"{mov_count} titles")
        
    st.markdown(f"⏳ **Screen Time Investment:** ~`{hours}` hours spent streaming.")
    
    show_counts = {}
    plat_counts = {}
    for h in st.session_state.db.get("history", []):
        if str(h.get("d", "")).startswith(month_key):
            if h.get("t") == "s":
                show_counts[h["i"]] = show_counts.get(h["i"], 0) + 1
            if h.get("p") and h.get("p") != "None":
                plat_counts[h["p"]] = plat_counts.get(h["p"], 0) + 1
            
    if show_counts:
        top_show_id = max(show_counts, key=show_counts.get)
        show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(top_show_id)), None)
        if show: st.markdown(f"🔥 **Top Binge Focus:** *{show['name']}* ({show_counts[top_show_id]} episodes)")
            
    if plat_counts:
        top_p = max(plat_counts, key=plat_counts.get)
        st.markdown(f"📡 **Platform Loyalty:** Most watched on **{top_p}**")
            
    st.divider()
    if st.button("Sweet!", use_container_width=True, key="close_month_recap_btn"):
        st.session_state.db.setdefault("seen_recaps", []).append(recap_id)
        save_db()
        st.rerun()

@st.dialog("🏆 Your Cinematic Wrapped")
def show_yearly_recap_dialog(year, y_tv, y_mov, recap_id):
    st.markdown(f"# 🍿 {year} YEAR IN REVIEW")
    st.write("You smashed your theater goals last year! Check out your custom achievements:")
    
    total_time = (y_tv * 45) + (y_mov * 120)
    days = total_time // 1440
    rem_hours = (total_time % 1440) // 60
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%); border-radius: 14px; padding: 22px; color: black; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(255,193,7,0.3);">
        <div style="font-size: 2.6rem; font-weight: 900; line-height:1;">{y_tv + y_mov:,}</div>
        <div style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-top:4px;">Total Titles Inventoried</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px; text-align: center;">
            <div style="font-size: 1.4rem; font-weight: 800; color: #FFC107;">{y_tv}</div>
            <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight:700;">Episodes Logged</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px; text-align: center;">
            <div style="font-size: 1.4rem; font-weight: 800; color: #FFC107;">{y_mov}</div>
            <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight:700;">Movies Checked</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"⏳ **Time Commitment:** You dedicated total of **{days} days** and **{rem_hours} hours** to premium story arcs.")
    
    if days > 12: tier_title, tier_desc = "👑 Emperor of the Couch", "Absolute legend. Hollywood production lines should put you on their payroll."
    elif days > 5: tier_title, tier_desc = "🍿 Marathon Veteran", "You know exactly how to lock down a weekend block and demolish complex plotlines."
    else: tier_title, tier_desc = "🎬 Curation Connoisseur", "High-taste selection habits. You filter for absolute choice cinema narrative styles."
        
    st.markdown(f"""
    <div style="background: rgba(255, 193, 7, 0.08); border: 1px dashed #FFC107; border-radius: 12px; padding: 15px; margin-top: 15px; text-align: center;">
        <div style="font-size: 1.15rem; font-weight: 800; color: #FFD54F;">{tier_title}</div>
        <div style="font-size: 0.75rem; color: #eee; margin-top: 5px; line-height:1.3;">{tier_desc}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    if st.button("Claim Achievement Status", use_container_width=True, key="close_year_recap_btn"):
        st.session_state.db.setdefault("seen_recaps", []).append(recap_id)
        save_db()
        st.rerun()

def evaluate_and_trigger_recaps():
    if "recaps_checked" in st.session_state: return
    st.session_state.recaps_checked = True
    
    db = st.session_state.db
    seen = db.setdefault("seen_recaps", [])
    now = get_dubai_time()
    
    first_of_this_month = now.replace(day=1)
    last_day_of_prev_month = first_of_this_month - timedelta(days=1)
    prev_month_key = last_day_of_prev_month.strftime("%Y-%m")
    prev_month_name = last_day_of_prev_month.strftime("%B %Y")
    
    month_recap_id = f"monthly-{prev_month_key}"
    if month_recap_id not in seen:
        stats = db.get("analytics", {}).get(prev_month_key, {"tv": 0, "movie": 0})
        if stats["tv"] > 0 or stats["movie"] > 0:
            show_monthly_recap_dialog(prev_month_key, prev_month_name, stats, month_recap_id)
            
    prev_year_num = now.year - 1
    year_recap_id = f"yearly-{prev_year_num}"
    if year_recap_id not in seen:
        y_tv, y_mov = 0, 0
        for k, v in db.get("analytics", {}).items():
            if k.startswith(str(prev_year_num)):
                y_tv += v.get("tv", 0)
                y_mov += v.get("movie", 0)
        if y_tv > 0 or y_mov > 0:
            show_yearly_recap_dialog(prev_year_num, y_tv, y_mov, year_recap_id)

evaluate_and_trigger_recaps()

# --- HELPERS ---
def render_badges(items, is_gold=False):
    css_class = "badge badge-gold" if is_gold else "badge"
    html = "".join([f'<span class="{css_class}">{item}</span>' for item in items])
    st.markdown(html, unsafe_allow_html=True)

def display_poster(path, width=185):
    if path and str(path).lower() not in ["none", "null", ""]:
        st.image(f"https://image.tmdb.org/t/p/w{width}{path}", use_container_width=True)
    else:
        st.markdown(f'<div style="background-color: rgba(255,255,255,0.05); border-radius:8px; width:100%; aspect-ratio: 2/3; display:flex; align-items:center; justify-content:center; color:#555; font-size:0.8rem; text-align:center; margin-bottom:5px;">No Image</div>', unsafe_allow_html=True)

def show_cast_horizontal(cast_list, limit=12):
    if not cast_list: return
    html = '<div style="display: flex; overflow-x: auto; gap: 14px; padding-bottom: 10px; scrollbar-width: none; -ms-overflow-style: none;">'
    for actor in cast_list[:limit]:
        img_url = f"https://image.tmdb.org/t/p/w185{actor['profile_path']}" if actor.get("profile_path") else "https://via.placeholder.com/185x278/222222/888888?text=No+Photo"
        char_name = str(actor.get('character', '')).replace('"', '&quot;').replace("'", "&#39;")
        safe_name = str(actor.get('name', '')).replace('"', '&quot;').replace("'", "&#39;")
        encoded_name = str(actor.get('name', '')).replace(" ", "+")
        imdb_url = f"https://www.imdb.com/find/?q={encoded_name}"
        html += f'<div style="flex: 0 0 85px; width: 85px; text-align: center;"><a href="{imdb_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="{img_url}" style="width: 85px; height: 127px; border-radius: 8px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 6px;"><div style="font-size: 0.55rem; color: #FFC107; font-weight: 700; line-height: 1.1; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{char_name}</div><div style="font-size: 0.6rem; font-weight: 600; color: #E0E0E0; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{safe_name}</div></a></div>'
    html += '</div>'
    html = html.replace('\n', '')
    st.markdown(html, unsafe_allow_html=True)

# --- DIALOGS ---
@st.dialog("Episode Details")
def show_episode_details(show_id, show_name, ep_code, ep_data=None):
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
    
    current_show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(show_id)), None)
    btn_disabled = (current_show is None)
    
    is_watched = current_show and ep_code in current_show.get("watched_episodes", [])
    
    if is_watched:
        h_log = next((h for h in st.session_state.db.get("history", []) if h.get("t")=="s" and str(h.get("i"))==str(show_id) and h.get("e")==ep_code), None)
        if h_log:
            try:
                dt_obj = datetime.strptime(h_log["d"], "%Y-%m-%d %H:%M:%S")
                st.success(f"✅ **Watched on:** {dt_obj.strftime('%B %d, %Y at %I:%M %p')}")
            except: pass
            
            st.markdown("#### Journal & Review")
            platforms = ["None", "Stremio", "Netflix", "OSN+", "Amazon Prime", "Apple TV+", "Disney+", "Starzplay", "Cinema", "Downloaded", "Other"]
            curr_p = h_log.get("p", "")
            p_idx = platforms.index(curr_p) if curr_p in platforms else 0
            new_p = st.selectbox("Watched On:", platforms, index=p_idx, key=f"p_s_{show_id}_{ep_code}")
            
            c1, c2 = st.columns(2)
            with c1:
                ratings = [0, 1, 2, 3, 4, 5]
                curr_r = h_log.get("r", 0)
                r_idx = curr_r if curr_r in ratings else 0
                new_r = st.selectbox("Rating (1-5):", ratings, index=r_idx, format_func=lambda x: f"{x} ⭐" if x>0 else "Unrated", key=f"r_s_{show_id}_{ep_code}")
            with c2:
                feelings = ["None", "🤯 Mind Blown", "😂 Hilarious", "😭 Emotional", "😍 Loved it", "😡 Frustrated", "😴 Bored"]
                curr_f = h_log.get("f", "")
                f_idx = feelings.index(curr_f) if curr_f in feelings else 0
                new_f = st.selectbox("Feeling:", feelings, index=f_idx, key=f"f_s_{show_id}_{ep_code}")
                
            if new_p != curr_p or new_r != curr_r or new_f != curr_f:
                h_log["p"] = new_p if new_p != "None" else ""
                h_log["r"] = new_r
                h_log["f"] = new_f if new_f != "None" else ""
                save_db()
                
    st.divider()
    st.markdown("#### Cast & Guest Stars")
    credits = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}")
    combined_cast = credits.get("cast", []) + ep_data.get("guest_stars", [])
    show_cast_horizontal(combined_cast, limit=15)
    st.divider()
    
    if btn_disabled: st.warning("➕ Add this show to your library to track episodes!")
        
    btn_label = "❌ Unmark as Watched" if is_watched else "✅ Mark as Watched"
    def toggle_watch():
        if is_watched:
            current_show["watched_episodes"].remove(ep_code)
            remove_watch("tv", show_id, ep_code)
        else:
            current_show["watched_episodes"].append(ep_code)
            log_watch("tv", show_id, ep_code)
            st.session_state.rate_item = {"t": "tv", "id": show_id, "e": ep_code}
    st.button(btn_label, use_container_width=True, key=f"dlg_btn_tv_{show_id}_{ep_code}", disabled=btn_disabled, on_click=toggle_watch)

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
    
    current_show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(show_id)), None)
    if not current_show:
        st.warning("➕ Add this show to your library to track episodes!")
        
    s_nums = [s["season_number"] for s in details.get("seasons", []) if s["season_number"] > 0]
    if s_nums:
        sel_s = st.selectbox("Select Season", s_nums, key=f"dlg_s_{show_id}")
        s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/season/{sel_s}?api_key={TMDB_KEY}")
        watched_list = current_show.get("watched_episodes", []) if current_show else []
        for ep in s_data.get("episodes", []):
            e_code = f"S{sel_s}E{ep['episode_number']}"
            is_watched = e_code in watched_list
            info_key = f"view_info_{show_id}_{e_code}"
            
            ep_col1, ep_col2 = st.columns([6, 1])
            with ep_col1:
                st.checkbox(f"**E{ep['episode_number']}.** {ep.get('name', 'Episode')}", value=is_watched, key=f"chk_dlg_{show_id}_{e_code}", on_change=cb_toggle_episode, args=(show_id, e_code), disabled=(current_show is None))
            if st.session_state.get(info_key, False):
                with st.container(border=True):
                    display_poster(ep.get("still_path"), width=500)
                    st.caption(f"⭐ {ep.get('vote_average', 0.0)} | **Aired:** {ep.get('air_date', 'N/A')}")
                    st.write(ep.get("overview", "No synopsis available."))
    st.divider()
    st.markdown("#### Top Cast")
    credits = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}")
    show_cast_horizontal(credits.get("cast", []), limit=15)

@st.dialog("Movie Details")
def show_movie_details(m_id, m_name, details=None):
    if not details:
        details = fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={TMDB_KEY}")
        
    display_poster(details.get("backdrop_path"), width=500)
    st.markdown(f"### {m_name}")
    genres = [g["name"] for g in details.get("genres", [])]
    render_badges([f"{details.get('runtime', 0)} mins"] + genres)
    st.write(details.get("overview", "No synopsis available."))
    
    current_movie = next((m for m in st.session_state.db["movies"] if str(m["id"]) == str(m_id)), None)
    btn_disabled = (current_movie is None)
    
    is_watched = current_movie and current_movie.get("watched", False)
    
    if is_watched:
        h_log = next((h for h in st.session_state.db.get("history", []) if h.get("t")=="m" and str(h.get("i"))==str(m_id)), None)
        if h_log:
            try:
                dt_obj = datetime.strptime(h_log["d"], "%Y-%m-%d %H:%M:%S")
                st.success(f"✅ **Watched on:** {dt_obj.strftime('%B %d, %Y at %I:%M %p')}")
            except: pass
            
            st.markdown("#### Journal & Review")
            platforms = ["None", "Stremio", "Netflix", "OSN+", "Amazon Prime", "Apple TV+", "Disney+", "Starzplay", "Cinema", "Downloaded", "Other"]
            curr_p = h_log.get("p", "")
            p_idx = platforms.index(curr_p) if curr_p in platforms else 0
            new_p = st.selectbox("Watched On:", platforms, index=p_idx, key=f"p_m_{m_id}")
            
            c1, c2 = st.columns(2)
            with c1:
                ratings = [0, 1, 2, 3, 4, 5]
                curr_r = h_log.get("r", 0)
                r_idx = curr_r if curr_r in ratings else 0
                new_r = st.selectbox("Rating (1-5):", ratings, index=r_idx, format_func=lambda x: f"{x} ⭐" if x>0 else "Unrated", key=f"r_m_{m_id}")
            with c2:
                feelings = ["None", "🤯 Mind Blown", "😂 Hilarious", "😭 Emotional", "😍 Loved it", "😡 Frustrated", "😴 Bored"]
                curr_f = h_log.get("f", "")
                f_idx = feelings.index(curr_f) if curr_f in feelings else 0
                new_f = st.selectbox("Feeling:", feelings, index=f_idx, key=f"f_m_{m_id}")
                
            if new_p != curr_p or new_r != curr_r or new_f != curr_f:
                h_log["p"] = new_p if new_p != "None" else ""
                h_log["r"] = new_r
                h_log["f"] = new_f if new_f != "None" else ""
                save_db()
                
    st.divider()
    st.markdown("#### Top Cast")
    credits = fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}/credits?api_key={TMDB_KEY}")
    show_cast_horizontal(credits.get("cast", []), limit=15)
    st.divider()
    
    if btn_disabled: st.warning("➕ Add this movie to your library to mark it as watched!")
        
    btn_label = "❌ Unmark as Watched" if is_watched else "✅ Mark as Watched"
    def toggle_watch():
        if is_watched:
            current_movie["watched"] = False
            remove_watch("movie", m_id)
        else:
            current_movie["watched"] = True
            log_watch("movie", m_id)
            st.session_state.rate_item = {"t": "movie", "id": m_id}
    st.button(btn_label, use_container_width=True, key=f"dlg_btn_mov_{m_id}", disabled=btn_disabled, on_click=toggle_watch)

# --- AUTO-POP INTERCEPTOR ---
if st.session_state.get("rate_item"):
    ri = st.session_state.rate_item
    st.session_state.rate_item = None
    if ri["t"] == "tv":
        show_episode_details(ri["id"], "Episode", ri["e"])
    else:
        show_movie_details(ri["id"], "Movie")

# ==========================================
# GLOBAL UNDO TOAST CONTROLLER (AUTO-FADING)
# ==========================================
if st.session_state.last_action:
    la = st.session_state.last_action
    
    st.markdown("""
    <style>
        @keyframes fadeOutUndo {
            0% { opacity: 1; max-height: 200px; transform: scaleY(1); }
            80% { opacity: 1; max-height: 200px; transform: scaleY(1); }
            100% { opacity: 0; max-height: 0px; margin: 0; padding: 0; overflow: hidden; pointer-events: none; transform: scaleY(0); border: none; }
        }
        div[data-testid="stVerticalBlock"]:has(#undo-wrapper):not(:has(div[data-testid="stVerticalBlock"]:has(#undo-wrapper))) {
            animation: fadeOutUndo 5s forwards !important;
            transform-origin: top;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<span id="undo-wrapper"></span>', unsafe_allow_html=True)
        st.success(f"Watched! ✅")
        if st.button(f"↩️ Undo Last Action", use_container_width=True):
            remove_watch(la["t"], la["i"], la["e"])
            st.session_state.last_action = None
            st.rerun()

# --- APP NAVIGATION BAR ---
t_next, t_soon, t_search, t_tv, t_movies, t_profile = st.tabs(["🔥 Next", "📅 Soon", "🔍 Search", "📺 TV", "🎬 Movies", "👤 Profile"])

# ==========================================
# TAB 1: UP NEXT DASHBOARD
# ==========================================
with t_next:
    st.markdown("<h3 class='tab-title'>Up Next</h3>", unsafe_allow_html=True)
    next_filter = st.selectbox("Category:", ["📺 Series", "🎬 Movies"], label_visibility="collapsed", key="next_filter_box")
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    next_sort = st.selectbox("Sort by:", ["Smart Priority", "Release Date", "Alphabetical"], label_visibility="collapsed", key="next_sort_box")
    st.divider()
    
    try: fifteen_days_ago = get_dubai_time() - pd.DateOffset(days=15)
    except: fifteen_days_ago = get_dubai_time() - timedelta(days=15)
    
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
            watched_set = set(show.get("watched_episodes", []))
            
            highest_s, highest_e = -1, -1
            for code in watched_set:
                try:
                    s_num, e_num = int(code.split('E')[0].replace('S','')), int(code.split('E')[1])
                    if s_num > highest_s or (s_num == highest_s and e_num > highest_e):
                        highest_s, highest_e = s_num, e_num
                except: pass

            seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
            start_s = max(1, highest_s)
            
            candidate_after_max = None
            for s_info in [s for s in seasons if s["season_number"] >= start_s]:
                s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/season/{s_info['season_number']}?api_key={TMDB_KEY}")
                for ep in s_data.get("episodes", []):
                    ep_code = f"S{s_info['season_number']}E{ep['episode_number']}"
                    air_date = ep.get("air_date", "")
                    if ep_code not in watched_set and air_date and air_date <= TODAY:
                        s_n, e_n = s_info['season_number'], ep['episode_number']
                        if s_n > highest_s or (s_n == highest_s and e_n > highest_e):
                            is_rec = ("s", str(show["id"])) in recent_active_ids
                            candidate_after_max = {"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date, "is_rec": is_rec, "is_skipped": False}
                            break
                if candidate_after_max: break
                
            if candidate_after_max:
                up_next_tv.append(candidate_after_max)
            else:
                candidate_skipped = None
                for s_info in [s for s in seasons if s["season_number"] < start_s]:
                    s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/season/{s_info['season_number']}?api_key={TMDB_KEY}")
                    for ep in s_data.get("episodes", []):
                        ep_code = f"S{s_info['season_number']}E{ep['episode_number']}"
                        air_date = ep.get("air_date", "")
                        if ep_code not in watched_set and air_date and air_date <= TODAY:
                            candidate_skipped = {"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date, "is_rec": False, "is_skipped": True}
                            break
                    if candidate_skipped: break
                if candidate_skipped:
                    up_next_tv.append(candidate_skipped)

        if next_sort == "Alphabetical": up_next_tv.sort(key=lambda x: x["item"]["name"].lower())
        elif next_sort == "Release Date": up_next_tv.sort(key=lambda x: x["date"] or "1900-01-01", reverse=True)
        elif next_sort == "Smart Priority": up_next_tv.sort(key=lambda x: (not x.get("is_skipped", False), x["is_rec"], x["date"] or "1900-01-01"), reverse=True)

        if not up_next_tv: 
            st.info("You are completely caught up on series! 🎉")
        else:
            limit = st.session_state.next_tv_limit
            for i in range(0, len(up_next_tv[:limit]), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)
                        if idx < len(up_next_tv[:limit]):
                            item = up_next_tv[idx]
                            show, details, ep, ep_code = item["item"], item["details"], item["ep"], item["code"]
                            with st.container(border=True):
                                display_poster(show.get("poster_path") or details.get('poster_path'), width=185)
                                st.markdown(f'<div class="grid-title" title="{show["name"]}">{show["name"]}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div style="text-align:center; font-size:0.7rem; color:#aaa; margin-bottom:5px; font-weight:600;">{ep_code}</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                st.button("✔️ Watch", key=f"n_w_tv_{show['id']}_{ep_code}_{idx}", on_click=cb_watch_tv, args=(show['id'], ep_code), use_container_width=True)
                                if st.button("ℹ️ Info", key=f"n_i_tv_{show['id']}_{ep_code}_{idx}", use_container_width=True):
                                    show_episode_details(show['id'], show['name'], ep_code, ep)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
            if len(up_next_tv) > st.session_state.next_tv_limit:
                if st.button("Load More Series", use_container_width=True, key="load_more_next_tv"):
                    st.session_state.next_tv_limit += 30
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
            limit = st.session_state.next_mov_limit
            for i in range(0, len(up_next_mov[:limit]), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)
                        if idx < len(up_next_mov[:limit]):
                            m = up_next_mov[idx]["item"]
                            with st.container(border=True):
                                display_poster(m.get('poster_path'), width=185)
                                st.markdown(f'<div class="grid-title" title="{m["name"]}">{m["name"]}</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                st.button("✔️ Watch", key=f"n_w_mov_{m['id']}_{idx}", on_click=cb_watch_mov, args=(m['id'],), use_container_width=True)
                                if st.button("ℹ️ Info", key=f"n_i_mov_{m['id']}_{idx}", use_container_width=True):
                                    show_movie_details(m['id'], m['name'], details=None)
                                st.markdown('</div>', unsafe_allow_html=True)
                        
            if len(up_next_mov) > st.session_state.next_mov_limit:
                if st.button("Load More Movies", use_container_width=True, key="load_more_next_mov"):
                    st.session_state.next_mov_limit += 30
                    st.rerun()

# ==========================================
# TAB 2: UPCOMING CALENDAR
# ==========================================
with t_soon:
    st.markdown("<h3 class='tab-title'>Upcoming Releases</h3>", unsafe_allow_html=True)
    soon_filter = st.selectbox("Category:", ["📺 Series", "🎬 Movies"], label_visibility="collapsed", key="soon_filter_box")
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    soon_sort = st.selectbox("Sort by:", ["Release Date", "Alphabetical"], label_visibility="collapsed", key="soon_sort_box")
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
        else: soon_tv.sort(key=lambda x: x["date"] or "2099-01-01", reverse=False)

        if not soon_tv: 
            st.info("No upcoming episodes scheduled yet.")
        else:
            limit = st.session_state.soon_tv_limit
            for i in range(0, len(soon_tv[:limit]), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)
                        if idx < len(soon_tv[:limit]):
                            item = soon_tv[idx]
                            show, details, ep, ep_code = item["item"], item["details"], item["ep"], item["code"]
                            time_rem = calc_time_remaining(item["date"])
                            with st.container(border=True):
                                display_poster(show.get("poster_path") or details.get('poster_path'), width=185)
                                st.markdown(f'<div class="grid-title" title="{show["name"]}">{show["name"]}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div style="text-align:center; font-size:0.65rem; color:#FFC107; margin-bottom:5px; font-weight:600;">{ep_code} • {time_rem}</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                st.button("✔️ Watch", key=f"s_w_tv_{show['id']}_{ep_code}_{idx}", on_click=cb_watch_tv, args=(show['id'], ep_code), use_container_width=True)
                                if st.button("ℹ️ Info", key=f"s_i_tv_{show['id']}_{ep_code}_{idx}", use_container_width=True):
                                    show_episode_details(show['id'], show['name'], ep_code, ep)
                                st.markdown('</div>', unsafe_allow_html=True)

            if len(soon_tv) > st.session_state.soon_tv_limit:
                if st.button("Load More Upcoming Series", use_container_width=True, key="load_more_soon_tv"):
                    st.session_state.soon_tv_limit += 30
                    st.rerun()

    else:
        soon_mov = []
        for m in st.session_state.db["movies"]:
            if not m.get("watched"):
                r_date = m.get("release_date", "")
                if r_date and r_date > TODAY:
                    soon_mov.append({"item": m, "date": r_date})

        if soon_sort == "Alphabetical": soon_mov.sort(key=lambda x: x["item"]["name"].lower())
        else: soon_mov.sort(key=lambda x: x["date"] or "2099-01-01", reverse=False)

        if not soon_mov: 
            st.info("No upcoming movies scheduled yet.")
        else:
            limit = st.session_state.soon_mov_limit
            for i in range(0, len(soon_mov[:limit]), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)
                        if idx < len(soon_mov[:limit]):
                            item = soon_mov[idx]
                            m = item["item"]
                            time_rem = calc_time_remaining(item["date"])
                            with st.container(border=True):
                                display_poster(m.get('poster_path'), width=185)
                                st.markdown(f'<div class="grid-title" title="{m["name"]}">{m["name"]}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div style="text-align:center; font-size:0.65rem; color:#FFC107; margin-bottom:5px; font-weight:600;">{time_rem}</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                st.button("✔️ Watch", key=f"s_w_mov_{m['id']}_{idx}", on_click=cb_watch_mov, args=(m['id'],), use_container_width=True)
                                if st.button("ℹ️ Info", key=f"s_i_mov_{m['id']}_{idx}", use_container_width=True):
                                    show_movie_details(m['id'], m['name'], details=None)
                                st.markdown('</div>', unsafe_allow_html=True)

            if len(soon_mov) > st.session_state.soon_mov_limit:
                if st.button("Load More Upcoming Movies", use_container_width=True, key="load_more_soon_mov"):
                    st.session_state.soon_mov_limit += 30
                    st.rerun()

# ==========================================
# TAB 3: GLOBAL SEARCH / DISCOVER FEED
# ==========================================
with t_search:
    st.markdown("<h3 class='tab-title'>Discover</h3>", unsafe_allow_html=True)
    
    # --- DYNAMIC SEARCH-AS-YOU-TYPE ENGINE ---
    search_query = st_keyup("Search", debounce=2000, key="search_query_input", placeholder="Search TV shows, movies, actors...", label_visibility="collapsed")

    if search_query:
        # --- SEARCH MODE (3x3 GRID) ---
        search_type = st.selectbox("Search in:", ["TV Shows", "Movies"], label_visibility="collapsed", key="search_filter_box")
        endpoint = "tv" if search_type == "TV Shows" else "movie"
        res = fetch_api(f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_KEY}&query={search_query}")
        results = res.get("results", [])
        if results:
            limit = 30
            search_results = results[:limit]
            for i in range(0, len(search_results), 3):
                cols = st.columns(3)
                for j in range(3):
                    with cols[j]:
                        st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)
                        if i + j < len(search_results):
                            item = search_results[i + j]
                            item_id = item["id"]
                            title = item.get("name") if search_type == "TV Shows" else item.get("title")
                            
                            with st.container(border=True):
                                display_poster(item.get("poster_path"), width=185)
                                st.markdown(f'<div class="grid-title" title="{title}">{title}</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                
                                is_tv = (search_type == "TV Shows")
                                added = any(str(x["id"]) == str(item_id) for x in st.session_state.db["shows" if is_tv else "movies"])
                                
                                if not added:
                                    if st.button("➕ ADD", key=f"add_{item_id}_{i+j}", use_container_width=True):
                                        details = fetch_api(f"https://api.themoviedb.org/3/{'tv' if is_tv else 'movie'}/{item_id}?api_key={TMDB_KEY}")
                                        if is_tv:
                                            st.session_state.db["shows"].append({
                                                "id": item_id, "name": title, "watched_episodes": get_watched_from_history("tv", item_id),
                                                "poster_path": details.get("poster_path", ""), "first_air_date": details.get("first_air_date", ""),
                                                "total_episodes": details.get("number_of_episodes", 1)
                                            })
                                        else:
                                            st.session_state.db["movies"].append({
                                                "id": item_id, "name": title, "watched": get_watched_from_history("movie", item_id),
                                                "poster_path": details.get("poster_path", ""), "release_date": details.get("release_date", ""),
                                                "runtime": details.get("runtime", 0)
                                            })
                                        if save_db(): st.rerun()
                                else:
                                    st.button("✔️ ADDED", key=f"dsb_{item_id}_{i+j}", disabled=True, use_container_width=True)
                                
                                if st.button("ℹ️ INFO", key=f"inf_{item_id}_{i+j}", use_container_width=True):
                                    details = fetch_api(f"https://api.themoviedb.org/3/{'tv' if is_tv else 'movie'}/{item_id}?api_key={TMDB_KEY}")
                                    if is_tv: manage_show_dialog(item_id, title, details)
                                    else: show_movie_details(item_id, title, details)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # --- DISCOVER MODE (NETFLIX-STYLE FEED) ---
        genre_options = ["🔥 Trending", "🤣 Comedy", "💥 Action", "🐉 Sci-Fi/Fantasy", "🔪 Thriller", "👻 Horror"]
        selected_genre = st.selectbox("Filters", genre_options, label_visibility="collapsed")
        st.divider()

        def render_carousel(title, items, c_type):
            if not items: return
            st.markdown(f"<h5 style='margin-bottom:0;'>{title}</h5>", unsafe_allow_html=True)
            
            limit = st.session_state.c_limits.get(title, 10)
            render_items = items[:limit]
            show_load_more = limit < len(items)
            
            num_cols = len(render_items) + (1 if show_load_more else 0)
            cols = st.columns(num_cols)
            
            for idx, item in enumerate(render_items):
                with cols[idx]:
                    st.markdown('<span class="carousel-marker"></span>', unsafe_allow_html=True)
                    display_poster(item.get("poster_path"), width=154)
                    i_title = item.get("name") if c_type == "tv" else item.get("title")
                    st.markdown(f'<div class="grid-title" title="{i_title}">{i_title}</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                    
                    item_id = item["id"]
                    added = False
                    if c_type == "tv": added = any(str(s["id"]) == str(item_id) for s in st.session_state.db["shows"])
                    else: added = any(str(m["id"]) == str(item_id) for m in st.session_state.db["movies"])
                        
                    if not added:
                        if st.button("➕ ADD", key=f"c_add_{c_type}_{item_id}_{idx}", use_container_width=True):
                            details = fetch_api(f"https://api.themoviedb.org/3/{c_type}/{item_id}?api_key={TMDB_KEY}")
                            if c_type == "tv":
                                st.session_state.db["shows"].append({
                                    "id": item_id, "name": i_title, "watched_episodes": get_watched_from_history("tv", item_id),
                                    "poster_path": details.get("poster_path", ""), "first_air_date": details.get("first_air_date", ""),
                                    "total_episodes": details.get("number_of_episodes", 1)
                                })
                            else:
                                st.session_state.db["movies"].append({
                                    "id": item_id, "name": i_title, "watched": get_watched_from_history("movie", item_id),
                                    "poster_path": details.get("poster_path", ""), "release_date": details.get("release_date", ""),
                                    "runtime": details.get("runtime", 0)
                                })
                            if save_db(): st.rerun()
                    else: 
                        st.button("✔️ ADDED", key=f"c_dsb_{c_type}_{item_id}_{idx}", disabled=True, use_container_width=True)
                    
                    if st.button("ℹ️ INFO", key=f"c_inf_{c_type}_{item_id}_{idx}", use_container_width=True):
                        details = fetch_api(f"https://api.themoviedb.org/3/{c_type}/{item_id}?api_key={TMDB_KEY}")
                        if c_type == "tv": manage_show_dialog(item_id, i_title, details)
                        else: show_movie_details(item_id, i_title, details)
                            
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if show_load_more:
                with cols[-1]:
                    st.markdown('<span class="carousel-marker"></span>', unsafe_allow_html=True)
                    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                    if st.button("➕ More", key=f"c_more_{title}", use_container_width=True):
                        st.session_state.c_limits[title] = limit + 10
                        st.rerun()

        if selected_genre == "🔥 Trending":
            if not st.session_state.rec_show:
                watched_tv = [s for s in st.session_state.db.get("shows", []) if s.get("watched_episodes")]
                if watched_tv:
                    st.session_state.rec_show = random.choice(watched_tv)
            
            if st.session_state.rec_show:
                random_show = st.session_state.rec_show
                recs = fetch_api(f"https://api.themoviedb.org/3/tv/{random_show['id']}/recommendations?api_key={TMDB_KEY}")
                if recs.get("results"):
                    render_carousel(f"Because you watched {random_show['name']}", recs["results"], "tv")

            trend_tv = fetch_api(f"https://api.themoviedb.org/3/trending/tv/day?api_key={TMDB_KEY}")
            trend_mov = fetch_api(f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_KEY}")
            
            if trend_tv.get("results"):
                render_carousel("🔥 Trending Series", trend_tv["results"], "tv")
            if trend_mov.get("results"):
                render_carousel("🎬 Trending Movies", trend_mov["results"], "movie")

            current_date = get_dubai_time()
            start_month = current_date.replace(day=1).strftime('%Y-%m-%d')
            last_day = calendar.monthrange(current_date.year, current_date.month)[1]
            end_month_str = current_date.replace(day=last_day).strftime('%Y-%m-%d')
            
            k_tv = fetch_api(f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_KEY}&with_original_language=ko&first_air_date.gte={start_month}&first_air_date.lte={end_month_str}&sort_by=popularity.desc")
            if k_tv.get("results"):
                render_carousel(f"🇰🇷 K-Dramas ({current_date.strftime('%B %Y')})", k_tv["results"], "tv")
                
            k_mov = fetch_api(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&with_original_language=ko&primary_release_date.gte={start_month}&primary_release_date.lte={end_month_str}&sort_by=popularity.desc")
            if k_mov.get("results"):
                render_carousel(f"🇰🇷 K-Movies ({current_date.strftime('%B %Y')})", k_mov["results"], "movie")

        else:
            genre_map_tv = {"🤣 Comedy": 35, "💥 Action": 10759, "🐉 Sci-Fi/Fantasy": 10765, "🔪 Thriller": 9648, "👻 Horror": 9648} 
            genre_map_mov = {"🤣 Comedy": 35, "💥 Action": 28, "🐉 Sci-Fi/Fantasy": 878, "🔪 Thriller": 53, "👻 Horror": 27}
            
            tv_g = fetch_api(f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_KEY}&with_genres={genre_map_tv[selected_genre]}&sort_by=popularity.desc")
            mov_g = fetch_api(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&with_genres={genre_map_mov[selected_genre]}&sort_by=popularity.desc")
            
            render_carousel(f"Top {selected_genre} Series", tv_g.get("results", []), "tv")
            render_carousel(f"Top {selected_genre} Movies", mov_g.get("results", []), "movie")

# ==========================================
# TAB 4: TV LIBRARY 
# ==========================================
with t_tv:
    st.markdown("<h3 class='tab-title'>My TV Collection</h3>", unsafe_allow_html=True)
    if "tv_tab" not in st.session_state: st.session_state.tv_tab = "WATCHLIST"
        
    c1, c2, c3 = st.columns(3)
    if c1.button("Watchlist", type="primary" if st.session_state.tv_tab == "WATCHLIST" else "secondary", use_container_width=True, key="tv_wl"):
        st.session_state.tv_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.tv_tab == "UPCOMING" else "secondary", use_container_width=True, key="tv_up"):
        st.session_state.tv_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.tv_tab == "WATCHED" else "secondary", use_container_width=True, key="tv_wd"):
        st.session_state.tv_tab = "WATCHED"; st.rerun()
        
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    tv_sort = st.selectbox("Sort Library by:", ["Release Date", "Alphabetical", "Recently Added"], label_visibility="collapsed", key="sort_tv_lib")
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
                
        if tv_sort == "Alphabetical": 
            display_shows.sort(key=lambda x: x[0]['name'].lower())
        elif tv_sort == "Release Date":
            is_upc = (st.session_state.tv_tab == "UPCOMING")
            def_date = '2099-01-01' if is_upc else '1900-01-01'
            display_shows.sort(key=lambda x: x[0].get('first_air_date', def_date) or def_date, reverse=not is_upc)
        elif tv_sort == "Recently Added":
            display_shows.reverse()
                
        if not display_shows: st.info(f"Your {st.session_state.tv_tab.lower()} is currently empty.")
        else:
            total_tv_display = len(display_shows)
            paginated_shows = display_shows[:st.session_state.tv_lib_limit]
            
            for i in range(0, len(paginated_shows), 3):
                cols = st.columns(3)
                for j in range(3):
                    with cols[j]:
                        st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)
                        if i + j < len(paginated_shows):
                            show, t_eps, w_eps = paginated_shows[i + j]
                            with st.container(border=True):
                                display_poster(show.get("poster_path"), width=185)
                                st.markdown(f'<div class="grid-title" title="{show["name"]}">{show["name"]}</div>', unsafe_allow_html=True)
                                st.progress(min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0)
                                
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                
                                if st.session_state.tv_tab == "WATCHLIST":
                                    st.markdown('<span class="grid-2-col"></span>', unsafe_allow_html=True)
                                    bc1, bc2 = st.columns(2)
                                    with bc1:
                                        if st.button("ℹ️ INFO", key=f"s_mgr_{show['id']}", use_container_width=True):
                                            details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
                                            manage_show_dialog(show['id'], show['name'], details)
                                    with bc2:
                                        st.button("🗑️ DEL", key=f"s_del_{show['id']}", on_click=cb_delete_tv, args=(show['id'],), use_container_width=True)
                                else:
                                    if st.button("ℹ️ INFO", key=f"s_mgr_{show['id']}", use_container_width=True):
                                        details = fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}")
                                        manage_show_dialog(show['id'], show['name'], details)
                                    
                                st.markdown('</div>', unsafe_allow_html=True)
                                
            if total_tv_display > st.session_state.tv_lib_limit:
                if st.button("Load 50 More", use_container_width=True, key="load_more_tv_lib"):
                    st.session_state.tv_lib_limit += 50
                    st.rerun()

# ==========================================
# TAB 5: MOVIE LIBRARY 
# ==========================================
with t_movies:
    st.markdown("<h3 class='tab-title'>My Movies</h3>", unsafe_allow_html=True)
    if "mov_tab" not in st.session_state: st.session_state.mov_tab = "WATCHLIST"
        
    c1, c2, c3 = st.columns(3)
    if c1.button("Watchlist", type="primary" if st.session_state.mov_tab == "WATCHLIST" else "secondary", use_container_width=True, key="m_wl"):
        st.session_state.mov_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.mov_tab == "UPCOMING" else "secondary", use_container_width=True, key="m_up"):
        st.session_state.mov_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.mov_tab == "WATCHED" else "secondary", use_container_width=True, key="m_wd"):
        st.session_state.mov_tab = "WATCHED"; st.rerun()
        
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    mov_sort = st.selectbox("Sort Library by:", ["Release Date", "Alphabetical", "Recently Added"], label_visibility="collapsed", key="sort_mov_lib")
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
                
        if mov_sort == "Alphabetical": 
            display_movies.sort(key=lambda x: x[0]['name'].lower())
        elif mov_sort == "Release Date":
            is_upc = (st.session_state.mov_tab == "UPCOMING")
            def_date = '2099-01-01' if is_upc else '1900-01-01'
            display_movies.sort(key=lambda x: x[0].get('release_date', def_date) or def_date, reverse=not is_upc)
        elif mov_sort == "Recently Added":
            display_movies.reverse()
                
        if not display_movies: st.info(f"Your {st.session_state.mov_tab.lower()} is currently empty.")
        else:
            total_mov_display = len(display_movies)
            paginated_movies = display_movies[:st.session_state.mov_lib_limit]
            
            for i in range(0, len(paginated_movies), 3):
                cols = st.columns(3)
                for j in range(3):
                    with cols[j]:
                        st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)
                        if i + j < len(paginated_movies):
                            m, is_watched = paginated_movies[i + j]
                            with st.container(border=True):
                                display_poster(m.get("poster_path"), width=185)
                                st.markdown(f'<div class="grid-title" title="{m["name"]}">{m["name"]}</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                
                                if st.session_state.mov_tab == "WATCHLIST":
                                    st.markdown('<span class="grid-2-col"></span>', unsafe_allow_html=True)
                                    bc1, bc2 = st.columns(2)
                                    with bc1:
                                        if st.button("ℹ️ INFO", key=f"m_mgr_{m['id']}", use_container_width=True):
                                            show_movie_details(m['id'], m['name'], details=None)
                                    with bc2:
                                        st.button("🗑️ DEL", key=f"m_del_{m['id']}", on_click=cb_delete_mov, args=(m['id'],), use_container_width=True)
                                else:
                                    if st.button("ℹ️ INFO", key=f"m_mgr_{m['id']}", use_container_width=True):
                                        show_movie_details(m['id'], m['name'], details=None)
                                    
                                st.markdown('</div>', unsafe_allow_html=True)
                                
            if total_mov_display > st.session_state.mov_lib_limit:
                if st.button("Load 50 More", use_container_width=True, key="load_more_mov_lib"):
                    st.session_state.mov_lib_limit += 50
                    st.rerun()

# ==========================================
# TAB 6: PROFILE STATS, GRAPHS & IMPORT
# ==========================================
with t_profile:
    st.markdown("<h3 class='tab-title'>Lifetime Stats</h3>", unsafe_allow_html=True)
    
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
    
    # --- REDESIGNED SLEEK PROFILE METRICS ---
    html_stats = f"""
    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
        <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 1.8rem; font-weight: 800; color: #FFC107; line-height: 1;">{months}</div>
            <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Months</div>
        </div>
        <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 1.8rem; font-weight: 800; color: #FFC107; line-height: 1;">{days}</div>
            <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Days</div>
        </div>
        <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 1.8rem; font-weight: 800; color: #FFC107; line-height: 1;">{hours}</div>
            <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Hours</div>
        </div>
    </div>
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1;">{total_episodes_watched:,}</div>
            <div style="font-size: 0.75rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Episodes</div>
        </div>
        <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1;">{total_movies_watched:,}</div>
            <div style="font-size: 0.75rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Movies</div>
        </div>
    </div>
    """
    st.markdown(html_stats, unsafe_allow_html=True)
    st.divider()
    
    # --- CHRONOLOGICAL TIMELINE SLER DATA MAP ---
    st.markdown("<h3 class='tab-title'>📊 Watch Activity</h3>", unsafe_allow_html=True)
    chart_tab1, chart_tab2 = st.tabs(["📺 Series Activity", "🎬 Movie Activity"])
    analytics = st.session_state.db.get("analytics", {})
    
    last_12_months = []
    try:
        for i in range(11, -1, -1):
            last_12_months.append(get_dubai_time() - pd.DateOffset(months=i))
    except:
        for i in range(11, -1, -1):
            last_12_months.append(get_dubai_time() - timedelta(days=30*i))
            
    data_tv = []
    data_mov = []
    for dt in last_12_months:
        m_key = dt.strftime('%Y-%m') 
        label = dt.strftime('%Y-%m')
        stats = analytics.get(m_key, {"tv": 0, "movie": 0})
        data_tv.append({"Month": label, "Episodes": stats["tv"]})
        data_mov.append({"Month": label, "Movies": stats["movie"]})
        
    df_tv = pd.DataFrame(data_tv).sort_values("Month")
    df_mov = pd.DataFrame(data_mov).sort_values("Month")
    
    # --- UPGRADED ALTAIR GRAPH MARK OVERLAYS (VERTICAL LABELS) ---
    with chart_tab1:
        if not df_tv.empty and df_tv["Episodes"].sum() > 0:
            chart_tv = alt.Chart(df_tv).mark_bar(color="#FFC107", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("Month:N", title=None, axis=alt.Axis(labelAngle=-90, labelColor="#aaa", labelFontSize=9)),
                y=alt.Y("Episodes:Q", title="Episodes Watched", axis=alt.Axis(labelColor="#aaa", titleColor="#aaa"))
            )
            text_tv = chart_tv.mark_text(
                align='center', baseline='bottom', dy=-5, color='#EDEDED', fontSize=10, fontWeight='bold'
            ).encode(text='Episodes:Q')
            st.altair_chart((chart_tv + text_tv).properties(height=260), use_container_width=True)
        else:
            st.info("No series log history available for the last 12 months.")
        
    with chart_tab2:
        if not df_mov.empty and df_mov["Movies"].sum() > 0:
            chart_mov = alt.Chart(df_mov).mark_bar(color="#555555", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("Month:N", title=None, axis=alt.Axis(labelAngle=-90, labelColor="#aaa", labelFontSize=9)),
                y=alt.Y("Movies:Q", title="Movies Watched", axis=alt.Axis(labelColor="#aaa", titleColor="#aaa"))
            )
            text_mov = chart_mov.mark_text(
                align='center', baseline='bottom', dy=-5, color='#EDEDED', fontSize=10, fontWeight='bold'
            ).encode(text='Movies:Q')
            st.altair_chart((chart_mov + text_mov).properties(height=260), use_container_width=True)
        else:
            st.info("No movie log history available for the last 12 months.")

    st.divider()
    
    # --- PURE NATIVE TV TIME WATCH HISTORY FEED ---
    st.markdown("<h3 class='tab-title'>📜 Watch History Journal</h3>", unsafe_allow_html=True)
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
                st.markdown(f"<h4 style='color: #FFC107; margin-top: 1rem; margin-bottom: 0.5rem;'>{month_str}</h4>", unsafe_allow_html=True)
                for h, dt, h_idx in items:
                    show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(h.get("i"))), None)
                    if show:
                        s_name = show["name"]
                        poster = show.get("poster_path", "")
                    else:
                        s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{h.get('i')}?api_key={TMDB_KEY}")
                        s_name = s_data.get("name", "Unknown Series")
                        poster = s_data.get("poster_path", "")
                        
                    ep_code = h.get('e', '')
                    r_stars = ("⭐" * h.get('r')) if h.get('r', 0) > 0 else ""
                    f_moji = h.get('f', '')
                    tag_line = f"{r_stars} {f_moji}".strip()
                    
                    poster_url = f"https://image.tmdb.org/t/p/w92{poster}" if poster else "https://via.placeholder.com/92x138/222222/555555?text=No+Img"
                    
                    html = f"""
                    <div style="display: flex; align-items: center; margin-bottom: 12px; background-color: transparent; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                        <img src="{poster_url}" style="width: 45px; height: 68px; border-radius: 4px; object-fit: cover; margin-right: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                        <div style="display: flex; flex-direction: column; justify-content: center;">
                            <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; line-height: 1.2;">{s_name}</div>
                            <div style="font-size: 0.75rem; font-weight: 600; color: #FFC107; margin-bottom: 2px;">{ep_code} <span style="color:#EDEDED; margin-left:4px;">{tag_line}</span></div>
                            <div style="font-size: 0.7rem; color: #888888;">{dt.strftime('%b %d, %Y • %I:%M %p')}</div>
                        </div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
                                
            if len(tv_hist) > st.session_state.hist_tv_limit:
                if st.button("Load More Series", use_container_width=True, key="load_more_tv_hist"):
                    st.session_state.hist_tv_limit += 20
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
                st.markdown(f"<h4 style='color: #FFC107; margin-top: 1rem; margin-bottom: 0.5rem;'>{month_str}</h4>", unsafe_allow_html=True)
                for h, dt, h_idx in items:
                    mov = next((m for m in st.session_state.db["movies"] if str(m["id"]) == str(h.get("i"))), None)
                    if mov:
                        m_name = mov["name"]
                        poster = mov.get("poster_path", "")
                    else:
                        m_data = fetch_api(f"https://api.themoviedb.org/3/movie/{h.get('i')}?api_key={TMDB_KEY}")
                        m_name = m_data.get("title", "Unknown Movie")
                        poster = m_data.get("poster_path", "")
                        
                    r_stars = ("⭐" * h.get('r')) if h.get('r', 0) > 0 else ""
                    f_moji = h.get('f', '')
                    tag_line = f"{r_stars} {f_moji}".strip()
                        
                    poster_url = f"https://image.tmdb.org/t/p/w92{poster}" if poster else "https://via.placeholder.com/92x138/222222/555555?text=No+Img"
                    
                    html = f"""
                    <div style="display: flex; align-items: center; margin-bottom: 12px; background-color: transparent; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                        <img src="{poster_url}" style="width: 45px; height: 68px; border-radius: 4px; object-fit: cover; margin-right: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                        <div style="display: flex; flex-direction: column; justify-content: center;">
                            <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; line-height: 1.2;">{m_name}</div>
                            <div style="font-size: 0.75rem; font-weight: 600; color: #FFC107; margin-bottom: 2px;">Movie <span style="color:#EDEDED; margin-left:4px;">{tag_line}</span></div>
                            <div style="font-size: 0.7rem; color: #888888;">{dt.strftime('%b %d, %Y • %I:%M %p')}</div>
                        </div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)

            if len(mov_hist) > st.session_state.hist_mov_limit:
                if st.button("Load More Movies", use_container_width=True, key="load_more_mov_hist"):
                    st.session_state.hist_mov_limit += 20
                    st.rerun()

    st.divider()
    
    # --- TV TIME DATA IMPORTER (SUPABASE EDITION) ---
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
                    "history": [] if wipe_db else st.session_state.db.get("history", []),
                    "seen_recaps": [] if wipe_db else st.session_state.db.get("seen_recaps", [])
                }
                
                # Process Movies
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
                                            w_dt = parse_tvtime_date(w_dt_raw) if w_dt_raw else get_dubai_time().strftime("%Y-%m-%d %H:%M:%S")
                                            m_key = datetime.strptime(w_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                                            
                                            new_db["analytics"].setdefault(m_key, {"tv": 0, "movie": 0})
                                            new_db["analytics"][m_key]["movie"] += 1
                                            new_db["history"].append({"t": "m", "i": tmdb_id, "e": "", "d": w_dt, "r": 0, "f": "", "p": ""})
                            except Exception as item_error: continue 
                    except Exception as e: st.error(f"Error processing movies: {e}")
                
                if m_file and t_file: prog.progress(0)
                
                # Process Shows
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
                                                w_dt = parse_tvtime_date(w_dt_raw) if w_dt_raw else get_dubai_time().strftime("%Y-%m-%d %H:%M:%S")
                                                m_key = datetime.strptime(w_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                                                
                                                new_db["analytics"].setdefault(m_key, {"tv": 0, "movie": 0})
                                                new_db["analytics"][m_key]["tv"] += 1
                                                new_db["history"].append({"t": "s", "i": tmdb_id, "e": e_code, "d": w_dt, "r": 0, "f": "", "p": ""})
                                                
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
                    stat_txt.text("✅ Mass Import & Supabase Sync Complete!")
                    st.toast("Library successfully imported.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    stat_txt.text("🛑 Import finished, but the cloud save failed. See error above.")
            else:
                st.error("Please upload at least one JSON file first.")
