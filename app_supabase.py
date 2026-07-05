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

# --- MOBILE-FIRST TARGETED CSS OVERHAUL ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important; background: transparent !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stAppViewContainer"] ~ div { display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important; }
    .viewerBadge_container, .viewerBadge_link, div[class^="viewerBadge"] {display: none !important; visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #050505 !important;
        background-image: radial-gradient(circle at 50% 0%, #1A1D24 0%, #050505 80%) !important;
        background-attachment: fixed !important;
        color: #EDEDED !important;
    }
    
    .block-container { padding: 1rem 0.5rem 5rem 0.5rem !important; max-width: 100vw !important; overflow-x: hidden !important; }
    img { border-radius: 8px !important; }
    [data-testid="stProgressBar"] > div > div { background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%) !important; }
    
    [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
    hr { margin: 0.8rem 0 !important; border-color: rgba(255, 255, 255, 0.1) !important; }
    h1, h2, h3 { padding-top: 0.6rem !important; padding-bottom: 0.3rem !important; margin-bottom: 0 !important; }
    .stMarkdown p { margin-bottom: 0.5rem !important; }
    
    h3 { color: #FFD54F !important; font-weight: 800 !important; letter-spacing: -0.5px !important; }
    h3.tab-title { margin-top: -0.8rem !important; padding-top: 0 !important; }
    
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] { gap: 0.25rem !important; }
    div[data-testid="stRadio"] { width: 100% !important; }
    div[data-testid="stRadio"] > div { width: 100% !important; }
    
    div[role="radiogroup"] {
        display: flex !important; flex-direction: row !important; background-color: rgba(0, 0, 0, 0.7) !important; border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important; box-shadow: inset 0px 4px 10px rgba(0,0,0,0.8) !important;
        padding: 4px !important; width: 100% !important; box-sizing: border-box !important;
    }
    div[role="radiogroup"] > label {
        flex: 1 1 0px !important; display: flex !important; justify-content: center !important; padding: 8px 0px !important; border-radius: 12px !important; margin: 0 !important; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; min-width: 0 !important;
    }
    div[role="radiogroup"] > label > div:first-child { display: none !important; }
    div[role="radiogroup"] > label:has(input:checked) { background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%) !important; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4) !important; border: none !important; }
    div[role="radiogroup"] > label:has(input:checked) p { color: #000 !important; font-weight: 800 !important; text-shadow: none !important; }
    div[role="radiogroup"] > label p { font-size: 0.8rem !important; font-weight: 600 !important; margin: 0 !important; color: #888 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: clip !important; }
    
    div[data-baseweb="select"] > div:first-child {
        background-color: rgba(0, 0, 0, 0.7) !important; border-radius: 14px !important; border: 1px solid rgba(255, 255, 255, 0.05) !important; box-shadow: inset 0px 4px 10px rgba(0,0,0,0.8) !important; padding: 4px !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, rgba(30, 32, 40, 0.6) 0%, rgba(15, 17, 22, 0.8) 100%) !important; backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important; border-radius: 12px !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.6) !important; padding: 0.3rem !important;
    }
    
    button[kind="primary"] { background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%) !important; color: #000 !important; border: none !important; border-radius: 20px !important; font-weight: 800 !important; box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4) !important; letter-spacing: 0.5px !important; }
    button[kind="secondary"] { background-color: rgba(255, 255, 255, 0.05) !important; color: #F8F9FA !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 20px !important; font-weight: 700 !important; letter-spacing: 0.5px !important; transition: all 0.2s ease !important; }
    button[kind="secondary"]:hover { border-color: rgba(255, 193, 7, 0.5) !important; color: #FFD54F !important; }
    
    .movie-wall-btn div.stButton > button { background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(5px) !important; -webkit-backdrop-filter: blur(5px) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 6px !important; color: #E0E0E0 !important; font-size: 0.50rem !important; font-weight: 700 !important; padding: 4px 1px !important; margin: 0 !important; text-transform: uppercase; letter-spacing: -0.2px !important; min-height: 1.8rem !important; line-height: 1; width: 100% !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: clip !important; transition: all 0.2s !important; }
    .movie-wall-btn div.stButton > button:hover, .movie-wall-btn div.stButton > button:active { transform: scale(0.95); background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%) !important; color: #000 !important; border-color: #FFC107 !important; box-shadow: 0 0 10px rgba(255, 193, 7, 0.5) !important; }
    
    div[data-testid="stTabs"] > div[data-baseweb="tab-list"], div[data-testid="stTabs"] > div[role="tablist"] { display: flex !important; width: 100vw !important; max-width: 100% !important; margin-left: -0.5rem !important; padding: 0 0 5px 0 !important; gap: 0 !important; overflow-x: hidden !important; background-color: rgba(8, 9, 12, 0.85) !important; backdrop-filter: blur(12px) !important; -webkit-backdrop-filter: blur(12px) !important; border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important; }
    div[data-testid="stTabs"] button[role="tab"] { flex: 1 1 0px !important; min-width: 0 !important; padding: 10px 0px !important; margin: 0 !important; border-radius: 0 !important; transition: all 0.3s ease !important; }
    div[data-testid="stTabs"] button[role="tab"] p { font-size: 0.55rem !important; font-weight: 700 !important; text-align: center !important; margin: 0 auto !important; white-space: nowrap !important; letter-spacing: -0.4px !important; overflow: hidden !important; text-overflow: clip !important; color: #888 !important; transition: all 0.3s ease !important; }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { border-bottom: 3px solid #FFC107 !important; background: linear-gradient(to top, rgba(255, 193, 7, 0.15) 0%, transparent 100%) !important; box-shadow: inset 0px -10px 15px -10px rgba(255, 193, 7, 0.5) !important; }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p { color: #FFD54F !important; text-shadow: 0px 0px 10px rgba(255, 193, 7, 0.6) !important; }
    
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker), div[data-testid="stColumns"]:has(.carousel-marker) { display: flex !important; flex-direction: row !important; overflow-x: auto !important; flex-wrap: nowrap !important; scrollbar-width: none; padding-bottom: 15px !important; gap: 12px !important; }
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker)::-webkit-scrollbar, div[data-testid="stColumns"]:has(.carousel-marker)::-webkit-scrollbar { display: none; }
    div[data-testid="column"]:has(.carousel-marker), div[data-testid="stColumn"]:has(.carousel-marker) { flex: 0 0 110px !important; width: 110px !important; min-width: 110px !important; padding: 0 !important; display: block !important; }

    div[data-testid="stHorizontalBlock"]:has(.carousel-marker-cast), div[data-testid="stColumns"]:has(.carousel-marker-cast) { display: flex !important; flex-direction: row !important; overflow-x: auto !important; flex-wrap: nowrap !important; scrollbar-width: none; padding-bottom: 10px !important; gap: 10px !important; }
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker-cast)::-webkit-scrollbar, div[data-testid="stColumns"]:has(.carousel-marker-cast)::-webkit-scrollbar { display: none; }
    div[data-testid="column"]:has(.carousel-marker-cast), div[data-testid="stColumn"]:has(.carousel-marker-cast) { flex: 0 0 85px !important; width: 85px !important; min-width: 85px !important; padding: 0 !important; display: block !important; text-align: center !important; }
    div[data-testid="column"]:has(.carousel-marker-cast) div[data-testid="stButton"] button { background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; margin: 0 !important; color: #E0E0E0 !important; font-size: 0.6rem !important; font-weight: 600 !important; line-height: 1.2 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; height: auto !important; min-height: 0 !important; width: 100% !important; display: block !important; }
    div[data-testid="column"]:has(.carousel-marker-cast) div[data-testid="stButton"] button:hover { color: #FFC107 !important; transform: none !important; text-decoration: underline !important;}
    
    /* --- INLINE SEARCH CLEAR BUTTON OVERRIDE --- */
    div[data-testid="stVerticalBlock"]:has(> div > div > .search-container-hook) { position: relative !important; }
    div:has(> .clear-btn-hook) + div { position: absolute !important; right: 8px !important; top: 7px !important; width: 26px !important; z-index: 100 !important; }
    div:has(> .clear-btn-hook) + div button { background: rgba(255,255,255,0.08) !important; border: none !important; box-shadow: none !important; color: #aaa !important; padding: 0 !important; min-height: 26px !important; height: 26px !important; width: 26px !important; border-radius: 50% !important; font-size: 0.7rem !important; display: flex !important; align-items: center !important; justify-content: center !important; margin: 0 !important; line-height: 1 !important; }
    div:has(> .clear-btn-hook) + div button:hover { background: rgba(255, 193, 7, 0.3) !important; color: #FFD54F !important; }

    @media (max-width: 992px) {
        div[data-testid="stHorizontalBlock"]:has(.grid-3-col), div[data-testid="stColumns"]:has(.grid-3-col) { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 2% !important; }
        div[data-testid="column"]:has(.grid-3-col), div[data-testid="stColumn"]:has(.grid-3-col) { width: 32% !important; flex: 1 1 32% !important; min-width: 0 !important; padding: 0 !important; display: block !important; }
        div[data-testid="stHorizontalBlock"]:has(.grid-2-col), div[data-testid="stColumns"]:has(.grid-2-col) { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 4% !important; }
        div[data-testid="column"]:has(.grid-2-col), div[data-testid="stColumn"]:has(.grid-2-col) { width: 48% !important; flex: 1 1 48% !important; min-width: 0 !important; padding: 0 !important; display: block !important; }
        div[role="dialog"] { width: 95vw !important; max-width: 95vw !important; margin: 0 auto !important; padding: 1rem !important; background: rgba(15, 17, 22, 0.95) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; }
    }
    .grid-title { font-size: 0.65rem !important; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; margin-top: 2px; margin-bottom: 2px; line-height: 1.2; color: #ddd; }
    .badge { display: inline-block; background-color: rgba(255,255,255,0.1); color: #FFFFFF; padding: 3px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; margin-right: 4px; margin-bottom: 6px; border: 1px solid rgba(255,255,255,0.05); }
    .badge-gold { background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%); color: #000000; border: none; box-shadow: 0 2px 6px rgba(255, 193, 7, 0.3); }
</style>
""", unsafe_allow_html=True)

# --- DUBAI TIMEZONE OVERRIDE ---
def get_dubai_time(): return datetime.utcnow() + timedelta(hours=4)

# --- STATES ---
for k in ["next_tv_limit", "next_mov_limit", "soon_tv_limit", "soon_mov_limit"]:
    if k not in st.session_state: st.session_state[k] = 30
for k in ["hist_tv_limit", "hist_mov_limit"]:
    if k not in st.session_state: st.session_state[k] = 20
for k in ["tv_lib_limit", "mov_lib_limit"]:
    if k not in st.session_state: st.session_state[k] = 50
if "c_limits" not in st.session_state: st.session_state.c_limits = {}
if "rec_show" not in st.session_state: st.session_state.rec_show = None 
if "last_action" not in st.session_state: st.session_state.last_action = None
if "active_actor" not in st.session_state: st.session_state.active_actor = None
if "prompt_review" not in st.session_state: st.session_state.prompt_review = None
if "search_reset_ctr" not in st.session_state: st.session_state.search_reset_ctr = 0

# --- DB PIPELINE ---
TMDB_KEY = st.secrets["TMDB_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"].rstrip("/") 
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
DB_ENDPOINT = f"{SUPABASE_URL}/rest/v1/tv_time_data?id=eq.1"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
TODAY = get_dubai_time().strftime('%Y-%m-%d')

# NOTE: Removed persist="disk" to force TTL expiration every 12 hours.
@st.cache_data(ttl=43200)
def fetch_api(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def fetch_robust(url):
    for _ in range(3):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 429: time.sleep(1.5); continue
            if r.status_code == 200: return r.json()
            return {}
        except: time.sleep(1)
    return {}

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
    for m in db.get("movies", []): packed["m"].append([m["id"], m["name"], 1 if m["watched"] else 0, m.get("poster_path", ""), m.get("release_date", ""), m.get("runtime", 0)])
    for s in db.get("shows", []): packed["s"].append([s["id"], s["name"], encode_eps(s.get("watched_episodes", [])), s.get("poster_path", ""), s.get("first_air_date", ""), s.get("total_episodes", 1)])
    for h in db.get("history", []): packed["h"].append([1 if h.get("t") == "s" else 0, h.get("i"), h.get("e", ""), h.get("d"), h.get("r", 0), h.get("f", ""), h.get("p", "")])
    for k, v in db.get("analytics", {}).items(): packed["a"][k] = [v.get("tv", 0), v.get("movie", 0)]
    packed["r"] = db.get("seen_recaps", [])
    return packed

def unpack_db(packed):
    db = {"movies": [], "shows": [], "history": [], "analytics": {}, "seen_recaps": []}
    for m in packed.get("m", []): db["movies"].append({"id": m[0], "name": m[1], "watched": bool(m[2]), "poster_path": m[3], "release_date": m[4], "runtime": m[5]})
    for s in packed.get("s", []): db["shows"].append({"id": s[0], "name": s[1], "watched_episodes": decode_eps(s[2]), "poster_path": s[3], "first_air_date": s[4], "total_episodes": s[5]})
    for h in packed.get("h", []):
        entry = {"t": "s" if h[0]==1 else "m", "i": h[1], "e": h[2], "d": h[3]}
        if len(h) > 4: entry["r"] = h[4]
        if len(h) > 5: entry["f"] = h[5]
        if len(h) > 6: entry["p"] = h[6]
        db["history"].append(entry)
    for k, v in packed.get("a", {}).items(): db["analytics"][k] = {"tv": v[0], "movie": v[1]}
    db["seen_recaps"] = packed.get("r", [])
    return db

def load_db():
    try:
        res = requests.get(DB_ENDPOINT, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 0:
                payload = data[0].get("payload", {})
                if "m" in payload and "s" in payload: return unpack_db(payload)
            return {"shows": [], "movies": [], "history": [], "analytics": {}, "seen_recaps": []}
        return None
    except: return None

def save_db():
    try:
        res = requests.patch(DB_ENDPOINT, json={"payload": pack_db(st.session_state.db)}, headers=HEADERS, timeout=5)
        return res.status_code in [200, 204]
    except: return False

if "db" not in st.session_state:
    db_data = load_db()
    if db_data is None: st.stop()
    st.session_state.db = db_data

def get_watched_from_history(item_type, item_id):
    t_flag = "s" if item_type == "tv" else "m"
    watched = []
    for h in st.session_state.db.get("history", []):
        if h.get("t") == t_flag and str(h.get("i")) == str(item_id):
            if item_type == "tv" and h.get("e"): watched.append(h.get("e"))
            elif item_type == "movie": return True
    return list(set(watched)) if item_type == "tv" else False

def log_watch(item_type, item_id, detail=""):
    now_str = get_dubai_time().strftime('%Y-%m-%d %H:%M:%S')
    m_key = get_dubai_time().strftime('%Y-%m')
    db = st.session_state.db
    db.setdefault("analytics", {}).setdefault(m_key, {"tv": 0, "movie": 0})
    if item_type == "tv": db["analytics"][m_key]["tv"] += 1
    else: db["analytics"][m_key]["movie"] += 1
    db.setdefault("history", []).insert(0, {"t": "s" if item_type == "tv" else "m", "i": item_id, "e": detail, "d": now_str, "r": 0, "f": "", "p": ""})
    st.session_state.last_action = {"t": item_type, "i": item_id, "e": detail}
    db["history"] = [h for h in db["history"] if h.get("t") == "s"][:100] + [h for h in db["history"] if h.get("t") == "m"][:100]
    save_db()

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
    if item_type == "tv":
        for show in db.get("shows", []):
            if str(show.get("id")) == str(item_id):
                if detail in show.get("watched_episodes", []): show["watched_episodes"].remove(detail)
                break
    else:
        for m in db.get("movies", []):
            if str(m.get("id")) == str(item_id):
                m["watched"] = False
                break
    save_db()

# --- SMART NETWORK OFFSET ENGINE ---
def calc_time_remaining(date_str, media_type="movie", details=None):
    if not date_str: return "Soon"
    try:
        base_target = datetime.strptime(date_str, '%Y-%m-%d')
        offset_hours = 28 # Default US Broadcast (4 AM Next Day Dubai)
        
        if media_type == "tv" and details:
            networks = [n.get("name", "").lower() for n in details.get("networks", [])]
            origin = details.get("origin_country", [])
            streaming = ["netflix", "amazon", "apple", "disney", "hulu", "paramount"]
            
            if any(any(sp in n for sp in streaming) for n in networks):
                offset_hours = 12 # Noon Dubai (Midnight PT)
            elif "KR" in origin or "JP" in origin:
                offset_hours = 17 # 5 PM Dubai
        elif media_type == "movie":
            offset_hours = 12 # Movies usually Midnight PT / Noon Dubai
            
        target = base_target + timedelta(hours=offset_hours)
        diff = target - get_dubai_time()
        
        if diff.days > 0: return f"In {diff.days}d {diff.seconds // 3600}h"
        elif diff.days == 0 and (diff.seconds // 3600) > 0: return f"In {diff.seconds // 3600}h"
        elif diff.total_seconds() > 0: return "In <1h"
        else: return "Out Now"
    except: return "Soon"

# --- TOP-LEVEL GLOBAL CALLBACKS ---
def cb_watch_tv_feed(sid, sname, ecode):
    for s in st.session_state.db["shows"]:
        if str(s["id"]) == str(sid):
            if ecode not in s["watched_episodes"]:
                s["watched_episodes"].append(ecode)
                log_watch("tv", sid, ecode)
            break
    st.session_state.prompt_review = {"t": "s", "id": sid, "name": sname, "code": ecode}

def cb_watch_mov_feed(mid, mname):
    for mv in st.session_state.db["movies"]:
        if str(mv["id"]) == str(mid):
            if not mv.get("watched"):
                mv["watched"] = True
                log_watch("movie", mid)
            break
    st.session_state.prompt_review = {"t": "m", "id": mid, "name": mname}

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
            
def cb_set_active_actor(aid):
    st.session_state.active_actor = aid

def cb_close_active_actor():
    st.session_state.active_actor = None

def cb_clear_action():
    st.session_state.last_action = None
    st.session_state.prompt_review = None

def cb_undo_action(t, i, e):
    remove_watch(t, i, e)
    st.session_state.last_action = None
    st.session_state.prompt_review = None

def cb_clear_search():
    st.session_state.search_reset_ctr += 1

# --- GLOBAL SAFE UNDO BANNER ---
if st.session_state.last_action and not st.session_state.prompt_review:
    la = st.session_state.last_action
    with st.container(border=True):
        c1, c2, c3 = st.columns([6, 2, 2])
        with c1: st.success("✅ Logged successfully!")
        with c2: st.button("↩️ Undo", key="undo_btn", on_click=cb_undo_action, args=(la["t"], la["i"], la["e"]), use_container_width=True)
        with c3: st.button("✖", key="dismiss_undo", on_click=cb_clear_action, use_container_width=True)

# --- HELPERS ---
def render_badges(items, is_gold=False):
    css_class = "badge badge-gold" if is_gold else "badge"
    st.markdown("".join([f'<span class="{css_class}">{item}</span>' for item in items]), unsafe_allow_html=True)

def display_poster(path, width=185):
    if path and str(path).lower() not in ["none", "null", ""]: st.image(f"https://image.tmdb.org/t/p/w{width}{path}", use_container_width=True)
    else: st.markdown(f'<div style="background-color: rgba(255,255,255,0.05); border-radius:8px; width:100%; aspect-ratio: 2/3; display:flex; align-items:center; justify-content:center; color:#555; font-size:0.8rem; text-align:center; margin-bottom:5px;">No Image</div>', unsafe_allow_html=True)

def show_cast_horizontal(cast_list, key_prefix, limit=15):
    if not cast_list: return
    cols = st.columns(len(cast_list[:limit]))
    for idx, actor in enumerate(cast_list[:limit]):
        with cols[idx]:
            st.markdown('<span class="carousel-marker-cast"></span>', unsafe_allow_html=True)
            img_url = f"https://image.tmdb.org/t/p/w185{actor['profile_path']}" if actor.get("profile_path") else "https://via.placeholder.com/185x278/222222/888888?text=No+Photo"
            
            encoded_name = str(actor.get('name', '')).replace(" ", "+")
            imdb_url = f"https://www.imdb.com/find/?q={encoded_name}"
            st.markdown(f'<a href="{imdb_url}" target="_blank"><img src="{img_url}" style="width: 85px; height: 127px; border-radius: 8px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 6px; transition: transform 0.2s;"></a>', unsafe_allow_html=True)
            
            char_name = str(actor.get('character', '')).strip()
            if char_name: st.markdown(f'<div style="font-size: 0.55rem; color: #FFC107; font-weight: 700; line-height: 1.1; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{char_name}</div>', unsafe_allow_html=True)
            st.button(actor.get('name', 'Unknown'), key=f"cast_{key_prefix}_{actor['id']}_{idx}", on_click=cb_set_active_actor, args=(actor['id'],), use_container_width=True)

def render_inline_actor_pokedex(actor_id):
    details = fetch_api(f"https://api.themoviedb.org/3/person/{actor_id}?api_key={TMDB_KEY}")
    credits = fetch_api(f"https://api.themoviedb.org/3/person/{actor_id}/combined_credits?api_key={TMDB_KEY}")
    
    db_shows = {str(s["id"]): s for s in st.session_state.db["shows"]}
    db_movies = {str(m["id"]): m for m in st.session_state.db["movies"]}
    
    owned_items = []
    seen_ids = set()
    for c in credits.get("cast", []):
        cid = str(c["id"])
        if c["media_type"] == "tv" and cid in db_shows and cid not in seen_ids:
            owned_items.append({"id": cid, "title": db_shows[cid]["name"], "type": "tv", "poster": db_shows[cid].get("poster_path")})
            seen_ids.add(cid)
        elif c["media_type"] == "movie" and cid in db_movies and cid not in seen_ids:
            owned_items.append({"id": cid, "title": db_movies[cid]["name"], "type": "movie", "poster": db_movies[cid].get("poster_path")})
            seen_ids.add(cid)
            
    st.markdown("<hr style='margin: 0.5rem 0; border-color: #FFC107;'>", unsafe_allow_html=True)
    with st.container(border=True):
        col_title, col_btn = st.columns([8, 2])
        with col_title: st.markdown(f"<h4 style='color: #FFD54F;'>{details.get('name', 'Actor Profile')}</h4>", unsafe_allow_html=True)
        with col_btn: st.button("✖ Close", key=f"close_act_{actor_id}", on_click=cb_close_active_actor, use_container_width=True)
        
        c1, c2 = st.columns([1, 2])
        with c1: display_poster(details.get("profile_path"), width=185)
        with c2:
            st.caption(f"**Born:** {details.get('birthday', 'Unknown')}")
            bio = details.get("biography", "")
            if len(bio) > 150: bio = bio[:150] + "..."
            st.write(bio if bio else "No biography available.")
            
        if owned_items:
            st.markdown(f"**📚 In Your Library ({len(owned_items)})**")
            cols = st.columns(len(owned_items))
            for idx, item in enumerate(owned_items):
                with cols[idx]:
                    st.markdown('<span class="carousel-marker"></span>', unsafe_allow_html=True)
                    display_poster(item.get("poster"), width=154)
                    st.markdown(f'<div class="grid-title" title="{item["title"]}">{item["title"]}</div>', unsafe_allow_html=True)
        
        st.markdown("**🌟 Famous Roles**")
        top_credits = sorted(credits.get("cast", []), key=lambda x: x.get("popularity", 0), reverse=True)[:10]
        if top_credits:
            cols = st.columns(len(top_credits))
            for idx, item in enumerate(top_credits):
                with cols[idx]:
                    st.markdown('<span class="carousel-marker"></span>', unsafe_allow_html=True)
                    display_poster(item.get("poster_path"), width=154)
                    i_title = item.get("name") if item.get("media_type") == "tv" else item.get("title")
                    st.markdown(f'<div class="grid-title" title="{i_title}">{i_title}</div>', unsafe_allow_html=True)

# --- RECAP ENGINE ---
@st.dialog("🌙 Monthly Wrap-Up")
def show_monthly_recap_dialog(month_key, month_title, stats, recap_id):
    st.markdown(f"## {month_title} Recap")
    st.write("Here is a quick look at your screening inventory from last month:")
    tv_count, mov_count = stats.get("tv", 0), stats.get("movie", 0)
    total_mins = (tv_count * 45) + (mov_count * 120)
    
    c1, c2 = st.columns(2)
    with c1: st.metric("📺 Episodes Logged", f"{tv_count} eps")
    with c2: st.metric("🎬 Movies Watched", f"{mov_count} titles")
    st.markdown(f"⏳ **Screen Time Investment:** ~`{total_mins // 60}` hours spent streaming.")
    
    show_counts, plat_counts, feel_counts = {}, {}, {}
    for h in st.session_state.db.get("history", []):
        if str(h.get("d", "")).startswith(month_key):
            if h.get("t") == "s": show_counts[h["i"]] = show_counts.get(h["i"], 0) + 1
            if h.get("p") and h.get("p") != "None": plat_counts[h["p"]] = plat_counts.get(h["p"], 0) + 1
            if h.get("f") and h.get("f") != "None": feel_counts[h["f"]] = feel_counts.get(h["f"], 0) + 1
            
    if show_counts:
        top_show_id = max(show_counts, key=show_counts.get)
        show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(top_show_id)), None)
        if show: st.markdown(f"🔥 **Top Binge Focus:** *{show['name']}* ({show_counts[top_show_id]} episodes)")
    if plat_counts: st.markdown(f"📡 **Platform Loyalty:** Most watched on **{max(plat_counts, key=plat_counts.get)}**")
    if feel_counts: st.markdown(f"🎭 **Monthly Vibe:** **{max(feel_counts, key=feel_counts.get)}**")
            
    st.divider()
    if st.button("Sweet!", use_container_width=True, key="close_month_recap_btn"):
        st.session_state.db.setdefault("seen_recaps", []).append(recap_id); save_db(); st.rerun()

@st.dialog("🏆 Your Cinematic Wrapped")
def show_yearly_recap_dialog(year, y_tv, y_mov, recap_id):
    st.markdown(f"# 🍿 {year} YEAR IN REVIEW")
    st.write("You smashed your theater goals last year! Check out your custom achievements:")
    total_time = (y_tv * 45) + (y_mov * 120)
    days = total_time // 1440
    
    st.markdown(f"""<div style="background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%); border-radius: 14px; padding: 22px; color: black; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(255,193,7,0.3);"><div style="font-size: 2.6rem; font-weight: 900; line-height:1;">{y_tv + y_mov:,}</div><div style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-top:4px;">Total Titles Inventoried</div></div>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"""<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px; text-align: center;"><div style="font-size: 1.4rem; font-weight: 800; color: #FFC107;">{y_tv}</div><div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight:700;">Episodes Logged</div></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px; text-align: center;"><div style="font-size: 1.4rem; font-weight: 800; color: #FFC107;">{y_mov}</div><div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight:700;">Movies Checked</div></div>""", unsafe_allow_html=True)
        
    st.markdown(f"⏳ **Time Commitment:** You dedicated total of **{days} days** and **{(total_time % 1440) // 60} hours** to premium story arcs.")
    
    y_hist = [h for h in st.session_state.db.get("history", []) if str(h.get("d", "")).startswith(str(year))]
    date_counts, plat_counts, feel_counts, show_counts, ratings = {}, {}, {}, {}, []
    
    for h in y_hist:
        d_only = h["d"][:10]
        date_counts[d_only] = date_counts.get(d_only, 0) + 1
        if h.get("p") and h.get("p") != "None": plat_counts[h["p"]] = plat_counts.get(h["p"], 0) + 1
        if h.get("f") and h.get("f") != "None": feel_counts[h["f"]] = feel_counts.get(h["f"], 0) + 1
        if h["t"] == "s": show_counts[h["i"]] = show_counts.get(h["i"], 0) + 1
        if h.get("r", 0) > 0: ratings.append(h["r"])
        
    st.divider()
    st.markdown("### The Deep Dive")
    if ratings: st.markdown(f"⭐ **Average Rating:** {round(sum(ratings)/len(ratings), 1)} / 5.0")
    if plat_counts: st.markdown(f"📡 **Top Platform:** {max(plat_counts, key=plat_counts.get)}")
    if feel_counts: st.markdown(f"🎭 **Top Vibe:** {max(feel_counts, key=feel_counts.get)}")
    if date_counts: 
        max_d, max_c = max(date_counts.items(), key=lambda x: x[1])
        st.markdown(f"🔥 **Ultimate Binge Day:** {max_c} items on {max_d}")
        
    if show_counts:
        st.markdown("**🏆 Top 3 Shows:**")
        top_shows = sorted(show_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for sid, sc in top_shows:
            s_obj = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(sid)), None)
            if s_obj: st.markdown(f"- {s_obj['name']} ({sc} eps)")

    if days > 12: tier_title, tier_desc = "👑 Emperor of the Couch", "Absolute legend. Hollywood production lines should put you on their payroll."
    elif days > 5: tier_title, tier_desc = "🍿 Marathon Veteran", "You know exactly how to lock down a weekend block and demolish complex plotlines."
    else: tier_title, tier_desc = "🎬 Curation Connoisseur", "High-taste selection habits. You filter for absolute choice cinema narrative styles."
        
    st.markdown(f"""<div style="background: rgba(255, 193, 7, 0.08); border: 1px dashed #FFC107; border-radius: 12px; padding: 15px; margin-top: 15px; text-align: center;"><div style="font-size: 1.15rem; font-weight: 800; color: #FFD54F;">{tier_title}</div><div style="font-size: 0.75rem; color: #eee; margin-top: 5px; line-height:1.3;">{tier_desc}</div></div>""", unsafe_allow_html=True)
    st.divider()
    if st.button("Claim Achievement Status", use_container_width=True, key="close_year_recap_btn"):
        st.session_state.db.setdefault("seen_recaps", []).append(recap_id); save_db(); st.rerun()

def evaluate_and_trigger_recaps():
    if "recaps_checked" in st.session_state: return
    st.session_state.recaps_checked = True
    db = st.session_state.db
    seen = db.setdefault("seen_recaps", [])
    now = get_dubai_time()
    
    first_of_this_month = now.replace(day=1)
    last_day_of_prev_month = first_of_this_month - timedelta(days=1)
    prev_month_key = last_day_of_prev_month.strftime("%Y-%m")
    
    if f"monthly-{prev_month_key}" not in seen:
        stats = db.get("analytics", {}).get(prev_month_key, {"tv": 0, "movie": 0})
        if stats["tv"] > 0 or stats["movie"] > 0: show_monthly_recap_dialog(prev_month_key, last_day_of_prev_month.strftime("%B %Y"), stats, f"monthly-{prev_month_key}")
            
    if f"yearly-{now.year - 1}" not in seen:
        y_tv, y_mov = 0, 0
        for k, v in db.get("analytics", {}).items():
            if k.startswith(str(now.year - 1)): y_tv += v.get("tv", 0); y_mov += v.get("movie", 0)
        if y_tv > 0 or y_mov > 0: show_yearly_recap_dialog(now.year - 1, y_tv, y_mov, f"yearly-{now.year - 1}")

evaluate_and_trigger_recaps()

# --- DIALOGS ---
@st.dialog("Episode Details")
def show_episode_details(show_id, show_name, ep_code, ep_data=None, is_watched=False):
    if not ep_data:
        try:
            s_num, e_num = ep_code.split('E')[0].replace('S', ''), ep_code.split('E')[1]
            ep_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/season/{s_num}/episode/{e_num}?api_key={TMDB_KEY}")
        except: ep_data = {}
        
    display_poster(ep_data.get("still_path"), width=500)
    st.markdown(f"### {ep_data.get('name', 'Untitled Episode')}")
    render_badges([ep_code, f"⭐ {ep_data.get('vote_average', 0.0)}"], is_gold=True)
    st.caption(f"**Aired:** {ep_data.get('air_date', 'N/A')}")
    st.write(ep_data.get("overview", "No synopsis available for this episode yet."))
    
    current_show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(show_id)), None)
    btn_disabled = (current_show is None)
    
    if is_watched:
        h_log = next((h for h in st.session_state.db.get("history", []) if h.get("t")=="s" and str(h.get("i"))==str(show_id) and h.get("e")==ep_code), None)
        if h_log:
            try:
                st.success(f"✅ **Watched on:** {datetime.strptime(h_log['d'], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y at %I:%M %p')}")
            except: pass
            
            st.markdown("#### Journal & Review")
            platforms = ["None", "Stremio", "Netflix", "OSN+", "Amazon Prime", "Apple TV+", "Disney+", "Starzplay", "Cinema", "Downloaded", "Other"]
            curr_p = h_log.get("p", "")
            new_p = st.selectbox("Watched On:", platforms, index=platforms.index(curr_p) if curr_p in platforms else 0, key=f"p_s_{show_id}_{ep_code}")
            
            c1, c2 = st.columns(2)
            with c1:
                ratings = [0, 1, 2, 3, 4, 5]
                curr_r = h_log.get("r", 0)
                new_r = st.selectbox("Rating (1-5):", ratings, index=curr_r if curr_r in ratings else 0, format_func=lambda x: f"{x} ⭐" if x>0 else "Unrated", key=f"r_s_{show_id}_{ep_code}")
            with c2:
                feelings = ["None", "🤯 Mind Blown", "😂 Hilarious", "😭 Emotional", "😍 Loved it", "😡 Frustrated", "😴 Bored"]
                curr_f = h_log.get("f", "")
                new_f = st.selectbox("Feeling:", feelings, index=feelings.index(curr_f) if curr_f in feelings else 0, key=f"f_s_{show_id}_{ep_code}")
                
            if new_p != curr_p or new_r != curr_r or new_f != curr_f:
                h_log["p"] = new_p if new_p != "None" else ""
                h_log["r"] = new_r
                h_log["f"] = new_f if new_f != "None" else ""
                save_db()
                
    st.divider()
    st.markdown("#### Cast & Guest Stars")
    show_cast_horizontal(fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}").get("cast", []) + ep_data.get("guest_stars", []), key_prefix=f"ep_{show_id}_{ep_code}", limit=15)
    
    if st.session_state.get("active_actor"): render_inline_actor_pokedex(st.session_state["active_actor"])
        
    st.divider()
    if btn_disabled: st.warning("➕ Add this show to your library to track episodes!")
    if st.button("❌ Unmark as Watched" if is_watched else "✅ Mark as Watched", use_container_width=True, disabled=btn_disabled):
        for s in st.session_state.db["shows"]:
            if str(s["id"]) == str(show_id):
                if is_watched and ep_code in s["watched_episodes"]: s["watched_episodes"].remove(ep_code); remove_watch("tv", show_id, ep_code)
                elif not is_watched and ep_code not in s["watched_episodes"]: s["watched_episodes"].append(ep_code); log_watch("tv", show_id, ep_code)
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
        if streams: st.info(f"📱 **Streaming locally:** {', '.join([p['provider_name'] for p in streams])}")
            
    st.divider()
    st.markdown("#### Episodes")
    
    current_show = next((s for s in st.session_state.db["shows"] if str(s["id"]) == str(show_id)), None)
    if not current_show: st.warning("➕ Add this show to your library to track episodes!")
        
    s_nums = [s["season_number"] for s in details.get("seasons", []) if s["season_number"] > 0]
    if s_nums:
        sel_s = st.selectbox("Select Season", s_nums, key=f"dlg_s_{show_id}")
        watched_list = current_show.get("watched_episodes", []) if current_show else []
        for ep in fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/season/{sel_s}?api_key={TMDB_KEY}").get("episodes", []):
            e_code = f"S{sel_s}E{ep['episode_number']}"
            ep_col1, ep_col2 = st.columns([6, 1])
            with ep_col1: st.checkbox(f"**E{ep['episode_number']}.** {ep.get('name', 'Episode')}", value=(e_code in watched_list), key=f"chk_dlg_{show_id}_{e_code}", on_change=cb_toggle_episode, args=(show_id, e_code), disabled=(current_show is None))
    st.divider()
    st.markdown("#### Top Cast")
    show_cast_horizontal(fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}").get("cast", []), key_prefix=f"show_{show_id}", limit=15)
    if st.session_state.get("active_actor"): render_inline_actor_pokedex(st.session_state["active_actor"])

@st.dialog("Movie Details")
def show_movie_details(m_id, m_name, details=None, is_watched=False):
    if not details: details = fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={TMDB_KEY}")
    display_poster(details.get("backdrop_path"), width=500)
    st.markdown(f"### {m_name}")
    render_badges([f"{details.get('runtime', 0)} mins"] + [g["name"] for g in details.get("genres", [])])
    st.write(details.get("overview", "No synopsis available."))
    
    current_movie = next((m for m in st.session_state.db["movies"] if str(m["id"]) == str(m_id)), None)
    btn_disabled = (current_movie is None)
    
    if is_watched:
        h_log = next((h for h in st.session_state.db.get("history", []) if h.get("t")=="m" and str(h.get("i"))==str(m_id)), None)
        if h_log:
            try:
                st.success(f"✅ **Watched on:** {datetime.strptime(h_log['d'], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y at %I:%M %p')}")
            except: pass
            
            st.markdown("#### Journal & Review")
            platforms = ["None", "Stremio", "Netflix", "OSN+", "Amazon Prime", "Apple TV+", "Disney+", "Starzplay", "Cinema", "Downloaded", "Other"]
            curr_p = h_log.get("p", "")
            new_p = st.selectbox("Watched On:", platforms, index=platforms.index(curr_p) if curr_p in platforms else 0, key=f"p_m_{m_id}")
            
            c1, c2 = st.columns(2)
            with c1:
                ratings = [0, 1, 2, 3, 4, 5]
                curr_r = h_log.get("r", 0)
                new_r = st.selectbox("Rating (1-5):", ratings, index=curr_r if curr_r in ratings else 0, format_func=lambda x: f"{x} ⭐" if x>0 else "Unrated", key=f"r_m_{m_id}")
            with c2:
                feelings = ["None", "🤯 Mind Blown", "😂 Hilarious", "😭 Emotional", "😍 Loved it", "😡 Frustrated", "😴 Bored"]
                curr_f = h_log.get("f", "")
                new_f = st.selectbox("Feeling:", feelings, index=feelings.index(curr_f) if curr_f in feelings else 0, key=f"f_m_{m_id}")
                
            if new_p != curr_p or new_r != curr_r or new_f != curr_f:
                h_log["p"] = new_p if new_p != "None" else ""
                h_log["r"] = new_r
                h_log["f"] = new_f if new_f != "None" else ""
                save_db()
                
    st.divider()
    st.markdown("#### Top Cast")
    show_cast_horizontal(fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}/credits?api_key={TMDB_KEY}").get("cast", []), key_prefix=f"mov_{m_id}", limit=15)
    if st.session_state.get("active_actor"): render_inline_actor_pokedex(st.session_state["active_actor"])
        
    st.divider()
    if btn_disabled: st.warning("➕ Add this movie to your library to mark it as watched!")
    if st.button("❌ Unmark as Watched" if is_watched else "✅ Mark as Watched", use_container_width=True, disabled=btn_disabled):
        for m in st.session_state.db["movies"]:
            if str(m["id"]) == str(m_id):
                m["watched"] = not is_watched
                if m["watched"]: log_watch("movie", m_id)
                else: remove_watch("movie", m_id)
                break
        st.rerun()

# --- IMMEDIATE REVIEW EVALUATOR ---
if st.session_state.get("prompt_review"):
    pr = st.session_state.prompt_review
    st.session_state.prompt_review = None
    if pr["t"] == "s": show_episode_details(pr["id"], pr["name"], pr["code"], ep_data=None, is_watched=True)
    else: show_movie_details(pr["id"], pr["name"], details=None, is_watched=True)

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
            if datetime.strptime(h.get("d", "2000-01-01 12:00:00"), '%Y-%m-%d %H:%M:%S') >= fifteen_days_ago: recent_active_ids.add((h.get("t"), str(h.get("i"))))
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
                    if s_num > highest_s or (s_num == highest_s and e_num > highest_e): highest_s, highest_e = s_num, e_num
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
                            candidate_after_max = {"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date, "is_rec": ("s", str(show["id"])) in recent_active_ids, "is_skipped": False}
                            break
                if candidate_after_max: break
                
            if candidate_after_max: up_next_tv.append(candidate_after_max)
            else:
                candidate_skipped = None
                for s_info in [s for s in seasons if s["season_number"] < start_s]:
                    for ep in fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/season/{s_info['season_number']}?api_key={TMDB_KEY}").get("episodes", []):
                        ep_code = f"S{s_info['season_number']}E{ep['episode_number']}"
                        air_date = ep.get("air_date", "")
                        if ep_code not in watched_set and air_date and air_date <= TODAY:
                            candidate_skipped = {"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date, "is_rec": False, "is_skipped": True}
                            break
                    if candidate_skipped: break
                if candidate_skipped: up_next_tv.append(candidate_skipped)

        if next_sort == "Alphabetical": up_next_tv.sort(key=lambda x: x["item"]["name"].lower())
        elif next_sort == "Release Date": up_next_tv.sort(key=lambda x: x["date"] or "1900-01-01", reverse=True)
        elif next_sort == "Smart Priority": up_next_tv.sort(key=lambda x: (not x.get("is_skipped", False), x["is_rec"], x["date"] or "1900-01-01"), reverse=True)

        if not up_next_tv: st.info("You are completely caught up on series! 🎉")
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
                                st.button("✔️ Watch", key=f"n_w_tv_{show['id']}_{ep_code}_{idx}", on_click=cb_watch_tv_feed, args=(show['id'], show['name'], ep_code), use_container_width=True)
                                if st.button("ℹ️ Info", key=f"n_i_tv_{show['id']}_{ep_code}_{idx}", use_container_width=True):
                                    st.session_state.active_actor = None; show_episode_details(show['id'], show['name'], ep_code, ep, is_watched=False)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
            if len(up_next_tv) > st.session_state.next_tv_limit:
                if st.button("Load More Series", use_container_width=True, key="load_more_next_tv"):
                    st.session_state.next_tv_limit += 30; st.rerun()

    else:
        up_next_mov = []
        for m in st.session_state.db["movies"]:
            if not m.get("watched"):
                r_date = m.get("release_date", "")
                if r_date and r_date <= TODAY:
                    up_next_mov.append({"item": m, "date": r_date, "is_rec": ("m", str(m["id"])) in recent_active_ids})

        if next_sort == "Alphabetical": up_next_mov.sort(key=lambda x: x["item"]["name"].lower())
        elif next_sort == "Release Date": up_next_mov.sort(key=lambda x: x["date"] or "1900-01-01", reverse=True)
        elif next_sort == "Smart Priority": up_next_mov.sort(key=lambda x: (x["is_rec"], x["date"] or "1900-01-01"), reverse=True)

        if not up_next_mov: st.info("You have no unwatched movies left! 🎉")
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
                                st.button("✔️ Watch", key=f"n_w_mov_{m['id']}_{idx}", on_click=cb_watch_mov_feed, args=(m['id'], m['name']), use_container_width=True)
                                if st.button("ℹ️ Info", key=f"n_i_mov_{m['id']}_{idx}", use_container_width=True):
                                    st.session_state.active_actor = None; show_movie_details(m['id'], m['name'], details=None, is_watched=False)
                                st.markdown('</div>', unsafe_allow_html=True)
                        
            if len(up_next_mov) > st.session_state.next_mov_limit:
                if st.button("Load More Movies", use_container_width=True, key="load_more_next_mov"):
                    st.session_state.next_mov_limit += 30; st.rerun()

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
            for s_info in [s for s in details.get("seasons", []) if s["season_number"] > 0]:
                if found_next: break
                for ep in fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}/season/{s_info['season_number']}?api_key={TMDB_KEY}").get("episodes", []):
                    ep_code = f"S{s_info['season_number']}E{ep['episode_number']}"
                    air_date = ep.get("air_date", "")
                    if ep_code not in watched_set and air_date and air_date > TODAY:
                        soon_tv.append({"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date})
                        found_next = True; break

        if soon_sort == "Alphabetical": soon_tv.sort(key=lambda x: x["item"]["name"].lower())
        else: soon_tv.sort(key=lambda x: x["date"] or "2099-01-01", reverse=False)

        if not soon_tv: st.info("No upcoming episodes scheduled yet.")
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
                            with st.container(border=True):
                                display_poster(show.get("poster_path") or details.get('poster_path'), width=185)
                                st.markdown(f'<div class="grid-title" title="{show["name"]}">{show["name"]}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div style="text-align:center; font-size:0.65rem; color:#FFC107; margin-bottom:5px; font-weight:600;">{ep_code} • {calc_time_remaining(item["date"], "tv", details)}</div>', unsafe_allow_html=True)
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                st.button("✔️ Watch", key=f"s_w_tv_{show['id']}_{ep_code}_{idx}", on_click=cb_watch_tv_feed, args=(show['id'], show['name'], ep_code), use_container_width=True)
                                if st.button("ℹ️ Info", key=f"s_i_tv_{show['id']}_{ep_code}_{idx}", use_container_width=True):
                                    st.session_state.active_actor = None; show_episode_details(show['id'], show['name'], ep_code, ep, is_watched=False)
                                st.markdown('</div>', unsafe_allow_html=True)

            if len(soon_tv) > st.session_state.soon_tv_limit:
                if st.button("Load More Upcoming Series", use_container_width=True, key="load_more_soon_tv"):
                    st.session_state.soon_tv_limit += 30; st.rerun()

    else:
        soon_mov = []
        for m in st.session_state.db["movies"]:
            r_date = m.get("release_date", "")
            if not m.get("watched") and r_date and r_date > TODAY: soon_mov.append({"item": m, "date": r_date})

        if soon_sort == "Alphabetical": soon_mov.sort(key=lambda x: x["item"]["name"].lower())
        else: soon_mov.sort(key=lambda x: x["date"] or "2099-01-01", reverse=False)

        if not soon_mov: st.info("No upcoming movies scheduled yet.")
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
                            with st.container(border=True):
                                display_poster(m.get('poster_path'), width=185)
                                st.markdown(f'<div class="grid-title" title="{m["name"]}">{m["name"]}</div>', unsafe_allow_html=True)
                                st.markdown(f'<div style="text-align:center; font-size:0.65rem; color:#FFC107; margin-bottom:5px; font-weight:600;">{calc_time_remaining(item["date"], "movie")}</div>', unsafe_allow_html=True)
                                st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                                st.button("✔️ Watch", key=f"s_w_mov_{m['id']}_{idx}", on_click=cb_watch_mov_feed, args=(m['id'], m['name']), use_container_width=True)
                                if st.button("ℹ️ Info", key=f"s_i_mov_{m['id']}_{idx}", use_container_width=True):
                                    st.session_state.active_actor = None; show_movie_details(m['id'], m['name'], details=None, is_watched=False)
                                st.markdown('</div>', unsafe_allow_html=True)

            if len(soon_mov) > st.session_state.soon_mov_limit:
                if st.button("Load More Upcoming Movies", use_container_width=True, key="load_more_soon_mov"):
                    st.session_state.soon_mov_limit += 30; st.rerun()

# ==========================================
# TAB 3: GLOBAL SEARCH / DISCOVER FEED
# ==========================================
with t_search:
    st.markdown("<h3 class='tab-title'>Discover</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<span class="search-container-hook"></span>', unsafe_allow_html=True)
        search_query = st_keyup("Search", debounce=1500, key=f"sq_{st.session_state.search_reset_ctr}", placeholder="Search TV shows, movies...", label_visibility="collapsed")
        if search_query:
            st.markdown('<span class="clear-btn-hook"></span>', unsafe_allow_html=True)
            st.button("✖", key=f"clr_btn_{st.session_state.search_reset_ctr}", on_click=cb_clear_search)

    if search_query:
        search_type = st.selectbox("Search in:", ["TV Shows", "Movies"], label_visibility="collapsed", key="search_filter_box")
        endpoint = "tv" if search_type == "TV Shows" else "movie"
        results = fetch_api(f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_KEY}&query={search_query}").get("results", [])
        if results:
            search_results = results[:30]
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
                                        if is_tv: st.session_state.db["shows"].append({"id": item_id, "name": title, "watched_episodes": get_watched_from_history("tv", item_id), "poster_path": details.get("poster_path", ""), "first_air_date": details.get("first_air_date", ""), "total_episodes": details.get("number_of_episodes", 1)})
                                        else: st.session_state.db["movies"].append({"id": item_id, "name": title, "watched": get_watched_from_history("movie", item_id), "poster_path": details.get("poster_path", ""), "release_date": details.get("release_date", ""), "runtime": details.get("runtime", 0)})
                                        if save_db(): st.rerun()
                                else: st.button("✔️ ADDED", key=f"dsb_{item_id}_{i+j}", disabled=True, use_container_width=True)
                                
                                if st.button("ℹ️ INFO", key=f"inf_{item_id}_{i+j}", use_container_width=True):
                                    st.session_state.active_actor = None
                                    details = fetch_api(f"https://api.themoviedb.org/3/{'tv' if is_tv else 'movie'}/{item_id}?api_key={TMDB_KEY}")
                                    if is_tv: manage_show_dialog(item_id, title, details)
                                    else: show_movie_details(item_id, title, details, is_watched=False)
                                st.markdown('</div>', unsafe_allow_html=True)
    else:
        genre_options = ["🔥 Trending", "🤣 Comedy", "💥 Action", "🐉 Sci-Fi/Fantasy", "🔪 Thriller", "👻 Horror"]
        selected_genre = st.selectbox("Filters", genre_options, label_visibility="collapsed")
        st.divider()

        def render_carousel(title, items, c_type):
            if not items: return
            st.markdown(f"<h5 style='margin-bottom:0;'>{title}</h5>", unsafe_allow_html=True)
            limit = st.session_state.c_limits.get(title, 10)
            render_items, show_load_more = items[:limit], limit < len(items)
            cols = st.columns(len(render_items) + (1 if show_load_more else 0))
            for idx, item in enumerate(render_items):
                with cols[idx]:
                    st.markdown('<span class="carousel-marker"></span>', unsafe_allow_html=True)
                    display_poster(item.get("poster_path"), width=154)
                    i_title = item.get("name") if c_type == "tv" else item.get("title")
                    st.markdown(f'<div class="grid-title" title="{i_title}">{i_title}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="movie-wall-btn">', unsafe_allow_html=True)
                    
                    item_id = item["id"]
                    added = any(str(x["id"]) == str(item_id) for x in st.session_state.db["shows" if c_type == "tv" else "movies"])
                        
                    if not added:
                        if st.button("➕ ADD", key=f"c_add_{c_type}_{item_id}_{idx}", use_container_width=True):
                            details = fetch_api(f"https://api.themoviedb.org/3/{c_type}/{item_id}?api_key={TMDB_KEY}")
                            if c_type == "tv": st.session_state.db["shows"].append({"id": item_id, "name": i_title, "watched_episodes": get_watched_from_history("tv", item_id), "poster_path": details.get("poster_path", ""), "first_air_date": details.get("first_air_date", ""), "total_episodes": details.get("number_of_episodes", 1)})
                            else: st.session_state.db["movies"].append({"id": item_id, "name": i_title, "watched": get_watched_from_history("movie", item_id), "poster_path": details.get("poster_path", ""), "release_date": details.get("release_date", ""), "runtime": details.get("runtime", 0)})
                            if save_db(): st.rerun()
                    else: st.button("✔️ ADDED", key=f"c_dsb_{c_type}_{item_id}_{idx}", disabled=True, use_container_width=True)
                    
                    if st.button("ℹ️ INFO", key=f"c_inf_{c_type}_{item_id}_{idx}", use_container_width=True):
                        st.session_state.active_actor = None
                        details = fetch_api(f"https://api.themoviedb.org/3/{c_type}/{item_id}?api_key={TMDB_KEY}")
                        if c_type == "tv": manage_show_dialog(item_id, i_title, details)
                        else: show_movie_details(item_id, i_title, details, is_watched=False)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if show_load_more:
                with cols[-1]:
                    st.markdown('<span class="carousel-marker"></span><div style="height: 60px;"></div>', unsafe_allow_html=True)
                    if st.button("➕ More", key=f"c_more_{title}", use_container_width=True):
                        st.session_state.c_limits[title] = limit + 10; st.rerun()

        if selected_genre == "🔥 Trending":
            if not st.session_state.rec_show:
                watched_tv = [s for s in st.session_state.db.get("shows", []) if s.get("watched_episodes")]
                if watched_tv: st.session_state.rec_show = random.choice(watched_tv)
            if st.session_state.rec_show:
                recs = fetch_api(f"https://api.themoviedb.org/3/tv/{st.session_state.rec_show['id']}/recommendations?api_key={TMDB_KEY}")
                if recs.get("results"): render_carousel(f"Because you watched {st.session_state.rec_show['name']}", recs["results"], "tv")
            trend_tv = fetch_api(f"https://api.themoviedb.org/3/trending/tv/day?api_key={TMDB_KEY}")
            trend_mov = fetch_api(f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_KEY}")
            if trend_tv.get("results"): render_carousel("🔥 Trending Series", trend_tv["results"], "tv")
            if trend_mov.get("results"): render_carousel("🎬 Trending Movies", trend_mov["results"], "movie")
            
            current_date = get_dubai_time()
            start_month = current_date.replace(day=1).strftime('%Y-%m-%d')
            last_day = calendar.monthrange(current_date.year, current_date.month)[1]
            end_month_str = current_date.replace(day=last_day).strftime('%Y-%m-%d')
            
            k_tv = fetch_api(f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_KEY}&with_original_language=ko&first_air_date.gte={start_month}&first_air_date.lte={end_month_str}&sort_by=popularity.desc")
            if k_tv.get("results"): render_carousel(f"🇰🇷 K-Dramas ({current_date.strftime('%B %Y')})", k_tv["results"], "tv")
            k_mov = fetch_api(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&with_original_language=ko&primary_release_date.gte={start_month}&primary_release_date.lte={end_month_str}&sort_by=popularity.desc")
            if k_mov.get("results"): render_carousel(f"🇰🇷 K-Movies ({current_date.strftime('%B %Y')})", k_mov["results"], "movie")
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
    if c1.button("Watchlist", type="primary" if st.session_state.tv_tab == "WATCHLIST" else "secondary", use_container_width=True, key="tv_wl"): st.session_state.tv_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.tv_tab == "UPCOMING" else "secondary", use_container_width=True, key="tv_up"): st.session_state.tv_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.tv_tab == "WATCHED" else "secondary", use_container_width=True, key="tv_wd"): st.session_state.tv_tab = "WATCHED"; st.rerun()
        
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
                
        if tv_sort == "Alphabetical": display_shows.sort(key=lambda x: x[0]['name'].lower())
        elif tv_sort == "Release Date":
            is_upc = (st.session_state.tv_tab == "UPCOMING")
            display_shows.sort(key=lambda x: x[0].get('first_air_date', '2099-01-01' if is_upc else '1900-01-01') or ('2099-01-01' if is_upc else '1900-01-01'), reverse=not is_upc)
        elif tv_sort == "Recently Added": display_shows.reverse()
                
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
                                            st.session_state.active_actor = None; manage_show_dialog(show['id'], show['name'], fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}"))
                                    with bc2:
                                        st.button("🗑️ DEL", key=f"s_del_{show['id']}", on_click=cb_delete_tv, args=(show['id'],), use_container_width=True)
                                else:
                                    if st.button("ℹ️ INFO", key=f"s_mgr_{show['id']}", use_container_width=True):
                                        st.session_state.active_actor = None; manage_show_dialog(show['id'], show['name'], fetch_api(f"https://api.themoviedb.org/3/tv/{show['id']}?api_key={TMDB_KEY}"))
                                st.markdown('</div>', unsafe_allow_html=True)
                                
            if total_tv_display > st.session_state.tv_lib_limit:
                if st.button("Load 50 More", use_container_width=True, key="load_more_tv_lib"):
                    st.session_state.tv_lib_limit += 50; st.rerun()

# ==========================================
# TAB 5: MOVIE LIBRARY 
# ==========================================
with t_movies:
    st.markdown("<h3 class='tab-title'>My Movies</h3>", unsafe_allow_html=True)
    if "mov_tab" not in st.session_state: st.session_state.mov_tab = "WATCHLIST"
        
    c1, c2, c3 = st.columns(3)
    if c1.button("Watchlist", type="primary" if st.session_state.mov_tab == "WATCHLIST" else "secondary", use_container_width=True, key="m_wl"): st.session_state.mov_tab = "WATCHLIST"; st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.mov_tab == "UPCOMING" else "secondary", use_container_width=True, key="m_up"): st.session_state.mov_tab = "UPCOMING"; st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.mov_tab == "WATCHED" else "secondary", use_container_width=True, key="m_wd"): st.session_state.mov_tab = "WATCHED"; st.rerun()
        
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
                
        if mov_sort == "Alphabetical": display_movies.sort(key=lambda x: x[0]['name'].lower())
        elif mov_sort == "Release Date":
            is_upc = (st.session_state.mov_tab == "UPCOMING")
            display_movies.sort(key=lambda x: x[0].get('release_date', '2099-01-01' if is_upc else '1900-01-01') or ('2099-01-01' if is_upc else '1900-01-01'), reverse=not is_upc)
        elif mov_sort == "Recently Added": display_movies.reverse()
                
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
                                            st.session_state.active_actor = None; show_movie_details(m['id'], m['name'], details=None, is_watched=is_watched)
                                    with bc2:
                                        st.button("🗑️ DEL", key=f"m_del_{m['id']}", on_click=cb_delete_mov, args=(m['id'],), use_container_width=True)
                                else:
                                    if st.button("ℹ️ INFO", key=f"m_mgr_{m['id']}", use_container_width=True):
                                        st.session_state.active_actor = None; show_movie_details(m['id'], m['name'], details=None, is_watched=is_watched)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
            if total_mov_display > st.session_state.mov_lib_limit:
                if st.button("Load 50 More", use_container_width=True, key="load_more_mov_lib"):
                    st.session_state.mov_lib_limit += 50; st.rerun()

# ==========================================
# TAB 6: PROFILE STATS, GRAPHS & IMPORT
# ==========================================
with t_profile:
    st.markdown("<h3 class='tab-title'>Control Center</h3>", unsafe_allow_html=True)
    t_prof_stats, t_prof_health, t_prof_graphs, t_prof_hist, t_prof_set = st.tabs(["Stats", "Health", "Graphs", "Journal", "Import"])

    history_sorted = sorted(st.session_state.db.get("history", []), key=lambda x: x.get("d", "2000-01-01 12:00:00"), reverse=True)

    with t_prof_stats:
        total_tv_mins = 0; total_episodes_watched = 0
        total_mov_mins = 0; total_movies_watched = 0
        shows = st.session_state.db.get("shows", [])
        
        for show in shows:
            w_eps = len(show.get("watched_episodes", []))
            total_episodes_watched += w_eps; total_tv_mins += (w_eps * 45) 
            
        for m in st.session_state.db["movies"]:
            if m.get("watched", False):
                total_mov_mins += m.get("runtime", 120); total_movies_watched += 1
                
        total_mins = total_tv_mins + total_mov_mins
        months = total_mins // 43800; days = (total_mins % 43800) // 1440; hours = (total_mins % 1440) // 60
        
        completed_shows = sum(1 for s in shows if len(s.get("watched_episodes",[])) >= s.get("total_episodes",1) and s.get("total_episodes",1) > 0)
        started_shows = sum(1 for s in shows if 0 < len(s.get("watched_episodes",[])) < s.get("total_episodes",1))
        
        tv_ratings = [h["r"] for h in history_sorted if h["t"]=="s" and h.get("r",0) > 0]
        mov_ratings = [h["r"] for h in history_sorted if h["t"]=="m" and h.get("r",0) > 0]
        avg_tv_r = round(sum(tv_ratings)/len(tv_ratings), 1) if tv_ratings else 0.0
        avg_mov_r = round(sum(mov_ratings)/len(mov_ratings), 1) if mov_ratings else 0.0
        
        plat_counts, feel_counts = {}, {}
        for h in history_sorted:
            if h.get("p") and h.get("p") != "None": plat_counts[h["p"]] = plat_counts.get(h["p"], 0) + 1
            if h.get("f") and h.get("f") != "None": feel_counts[h["f"]] = feel_counts.get(h["f"], 0) + 1
            
        top_plat_global = max(plat_counts, key=plat_counts.get) if plat_counts else "N/A"
        top_feel_global = max(feel_counts, key=feel_counts.get) if feel_counts else "N/A"
        
        st.markdown(f"""
        <div style="display: flex; gap: 10px; margin-bottom: 10px; margin-top: 10px;">
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
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1;">{total_episodes_watched:,}</div>
                <div style="font-size: 0.75rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Episodes</div>
            </div>
            <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1;">{total_movies_watched:,}</div>
                <div style="font-size: 0.75rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Movies</div>
            </div>
        </div>
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 1.4rem; font-weight: 800; color: #FFC107; line-height: 1;">{completed_shows} <span style="font-size:0.8rem; color:#aaa;">/ {started_shows}</span></div>
                <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Shows Finished / Active</div>
            </div>
            <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 1.4rem; font-weight: 800; color: #FFC107; line-height: 1;">{avg_tv_r} <span style="font-size:0.8rem; color:#aaa;">/ {avg_mov_r}</span></div>
                <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Avg TV / Movie ⭐</div>
            </div>
        </div>
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 1.1rem; font-weight: 800; color: #FFC107; line-height: 1.2;">{top_plat_global}</div>
                <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Top Platform</div>
            </div>
            <div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 1.1rem; font-weight: 800; color: #FFC107; line-height: 1.2;">{top_feel_global}</div>
                <div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Signature Vibe</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t_prof_health:
        total_ep_db = 0; watched_ep_db = 0
        eps_last_7 = 0; mins_last_30 = 0
        thirty_days_ago = get_dubai_time() - timedelta(days=30)
        seven_days_ago = get_dubai_time() - timedelta(days=7)
        
        watched_dates = set()
        for h in history_sorted:
            try:
                h_dt = datetime.strptime(h["d"], "%Y-%m-%d %H:%M:%S")
                watched_dates.add(h_dt.date())
                if h_dt >= thirty_days_ago: mins_last_30 += 45 if h["t"] == "s" else 120
                if h_dt >= seven_days_ago and h["t"] == "s": eps_last_7 += 1
            except: pass
            
        daily_avg_mins = mins_last_30 / 30.0 if mins_last_30 > 0 else 1.0
        
        streak = 0
        curr_d = get_dubai_time().date()
        if curr_d not in watched_dates: curr_d -= timedelta(days=1)
        while curr_d in watched_dates:
            streak += 1
            curr_d -= timedelta(days=1)
        
        stagnant_shows, almost_finished = [], []
        for s in st.session_state.db["shows"]:
            t_eps = s.get("total_episodes", 1)
            w_list = s.get("watched_episodes", [])
            w_eps = len(w_list)
            total_ep_db += t_eps; watched_ep_db += w_eps
            rem = t_eps - w_eps
            
            if 0 < rem <= 3: almost_finished.append({"name": s["name"], "rem": rem})
            
            if 0 < w_eps < t_eps:
                s_hist = [h for h in history_sorted if h["t"] == "s" and str(h["i"]) == str(s["id"])]
                if s_hist:
                    try:
                        if (get_dubai_time() - datetime.strptime(s_hist[0]["d"], "%Y-%m-%d %H:%M:%S")).days > 90:
                            stagnant_shows.append({"name": s["name"], "id": s["id"]})
                    except: pass

        total_mov_db = len(st.session_state.db["movies"])
        watched_mov_db = sum(1 for m in st.session_state.db["movies"] if m.get("watched"))
        backlog_mins = ((total_ep_db - watched_ep_db) * 45) + ((total_mov_db - watched_mov_db) * 120)
        days_to_clear = int(backlog_mins / daily_avg_mins) if daily_avg_mins > 0 else 999
        total_items = total_ep_db + total_mov_db
        completion_pct = int(((watched_ep_db + watched_mov_db) / total_items) * 100) if total_items > 0 else 0
        
        st.markdown(f"#### Clearance Dashboard")
        st.progress(completion_pct / 100.0)
        st.caption(f"**Total Library Completion:** {completion_pct}%")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 5px; text-align: center; margin-top: 15px;"><div style="font-size: 1.5rem; font-weight: 800; color: #FFC107;">{days_to_clear} <span style="font-size:0.7rem; color:#aaa;">Days</span></div><div style="font-size: 0.60rem; color: #aaa; text-transform: uppercase; font-weight:700;">To Clear Backlog</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 5px; text-align: center; margin-top: 15px;"><div style="font-size: 1.5rem; font-weight: 800; color: #FFC107;">{eps_last_7} <span style="font-size:0.7rem; color:#aaa;">Eps</span></div><div style="font-size: 0.60rem; color: #aaa; text-transform: uppercase; font-weight:700;">Binge Velocity</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 5px; text-align: center; margin-top: 15px;"><div style="font-size: 1.5rem; font-weight: 800; color: #FFC107;">{streak} <span style="font-size:0.7rem; color:#aaa;">Days</span></div><div style="font-size: 0.60rem; color: #aaa; text-transform: uppercase; font-weight:700;">Current Streak</div></div>""", unsafe_allow_html=True)

        if almost_finished:
            st.markdown("#### 🏁 Almost Finished")
            for s in almost_finished[:5]: st.markdown(f"• **{s['name']}** *(Only {s['rem']} eps left!)*")

        if stagnant_shows:
            st.markdown("#### ⚠️ Stagnant Stock Warning")
            st.info(f"You have {len(stagnant_shows)} abandoned shows in your inventory. Consider dropping them to clean your backlog.")
            for s in stagnant_shows[:5]: st.markdown(f"• **{s['name']}**")

    with t_prof_graphs:
        c_tab1, c_tab2, c_tab3 = st.tabs(["Activity", "Platforms", "Ratings"])
        with c_tab1:
            analytics = st.session_state.db.get("analytics", {})
            last_12_months = []
            try:
                for i in range(11, -1, -1): last_12_months.append(get_dubai_time() - pd.DateOffset(months=i))
            except:
                for i in range(11, -1, -1): last_12_months.append(get_dubai_time() - timedelta(days=30*i))
            data_tv, data_mov = [], []
            for dt in last_12_months:
                m_key, label = dt.strftime('%Y-%m'), dt.strftime('%b \'%y')
                stats = analytics.get(m_key, {"tv": 0, "movie": 0})
                data_tv.append({"Month": label, "Episodes": stats["tv"]})
                data_mov.append({"Month": label, "Movies": stats["movie"]})
            df_tv, df_mov = pd.DataFrame(data_tv), pd.DataFrame(data_mov)
            
            st.markdown("**📺 TV Series**")
            if not df_tv.empty and df_tv["Episodes"].sum() > 0:
                chart_tv = alt.Chart(df_tv).mark_bar(color="#FFC107", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x=alt.X("Month:N", title=None, axis=alt.Axis(labelAngle=-90, labelColor="#aaa", labelFontSize=9), sort=None), y=alt.Y("Episodes:Q", title=None, axis=alt.Axis(labelColor="#aaa")))
                text_tv = chart_tv.mark_text(align='center', baseline='bottom', dy=-5, color='#EDEDED', fontSize=10, fontWeight='bold').encode(text='Episodes:Q')
                st.altair_chart((chart_tv + text_tv).properties(height=200), use_container_width=True)
            else: st.info("No series history available.")
            
            st.markdown("**🎬 Movies**")
            if not df_mov.empty and df_mov["Movies"].sum() > 0:
                chart_mov = alt.Chart(df_mov).mark_bar(color="#555555", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x=alt.X("Month:N", title=None, axis=alt.Axis(labelAngle=-90, labelColor="#aaa", labelFontSize=9), sort=None), y=alt.Y("Movies:Q", title=None, axis=alt.Axis(labelColor="#aaa")))
                text_mov = chart_mov.mark_text(align='center', baseline='bottom', dy=-5, color='#EDEDED', fontSize=10, fontWeight='bold').encode(text='Movies:Q')
                st.altair_chart((chart_mov + text_mov).properties(height=200), use_container_width=True)
            else: st.info("No movie history available.")

        with c_tab2:
            plat_data = [h["p"] for h in history_sorted if h.get("p") and h["p"]!="None"]
            if plat_data:
                df_plat = pd.Series(plat_data).value_counts().reset_index()
                df_plat.columns = ['Platform', 'Count']
                chart_p = alt.Chart(df_plat).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Platform", type="nominal", scale=alt.Scale(scheme='category20'), legend=alt.Legend(title=None, labelColor="#EDEDED")),
                    tooltip=["Platform", "Count"]
                )
                st.altair_chart(chart_p.properties(height=300), use_container_width=True)
            else: st.info("You haven't logged any viewing platforms in your journal yet.")
            
        with c_tab3:
            rat_data = [h["r"] for h in history_sorted if h.get("r", 0) > 0]
            if rat_data:
                df_r = pd.Series(rat_data).value_counts().reset_index()
                df_r.columns = ['Stars', 'Count']
                chart_r = alt.Chart(df_r).mark_bar(color="#FFC107", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                    x=alt.X("Stars:N", title="Star Rating", axis=alt.Axis(labelAngle=0, labelColor="#aaa", titleColor="#aaa"), sort=[1,2,3,4,5]),
                    y=alt.Y("Count:Q", title="Total Given", axis=alt.Axis(labelColor="#aaa", titleColor="#aaa"))
                )
                text_r = chart_r.mark_text(align='center', baseline='bottom', dy=-5, color='#EDEDED', fontSize=12, fontWeight='bold').encode(text='Count:Q')
                st.altair_chart((chart_r + text_r).properties(height=300), use_container_width=True)
            else: st.info("You haven't left any star ratings in your journal yet.")

    with t_prof_hist:
        h_tv, h_mov = st.tabs(["📺 Series", "🎬 Movies"])
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
                        if show: s_name, poster = show["name"], show.get("poster_path", "")
                        else:
                            s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{h.get('i')}?api_key={TMDB_KEY}")
                            s_name, poster = s_data.get("name", "Unknown Series"), s_data.get("poster_path", "")
                            
                        ep_code, r_stars, f_moji = h.get('e', ''), ("⭐" * h.get('r')) if h.get('r', 0) > 0 else "", h.get('f', '')
                        poster_url = f"https://image.tmdb.org/t/p/w92{poster}" if poster else "https://via.placeholder.com/92x138/222222/555555?text=No+Img"
                        
                        html = f"""
                        <div style="display: flex; align-items: center; margin-bottom: 6px; background-color: transparent; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px;">
                            <img src="{poster_url}" style="width: 45px; height: 68px; border-radius: 4px; object-fit: cover; margin-right: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                            <div style="display: flex; flex-direction: column; justify-content: center;">
                                <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; line-height: 1.2;">{s_name}</div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: #FFC107; margin-bottom: 2px;">{ep_code} <span style="color:#EDEDED; margin-left:4px;">{f"{r_stars} {f_moji}".strip()}</span></div>
                                <div style="font-size: 0.7rem; color: #888888;">{dt.strftime('%b %d, %Y • %I:%M %p')}</div>
                            </div>
                        </div>"""
                        c_left, c_right = st.columns([5, 1])
                        with c_left: st.markdown(html, unsafe_allow_html=True)
                        with c_right:
                            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                            if st.button("📝", key=f"h_r_tv_{h['i']}_{ep_code}_{h_idx}", help="Rate & Review"): 
                                st.session_state.active_actor = None
                                show_episode_details(h['i'], s_name, ep_code, ep_data=None, is_watched=True)
                if len(tv_hist) > st.session_state.hist_tv_limit:
                    if st.button("Load More Series", use_container_width=True, key="load_more_tv_hist"):
                        st.session_state.hist_tv_limit += 20; st.rerun()
                        
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
                        if mov: m_name, poster = mov["name"], mov.get("poster_path", "")
                        else:
                            m_data = fetch_api(f"https://api.themoviedb.org/3/movie/{h.get('i')}?api_key={TMDB_KEY}")
                            m_name, poster = m_data.get("title", "Unknown Movie"), m_data.get("poster_path", "")
                            
                        r_stars, f_moji = ("⭐" * h.get('r')) if h.get('r', 0) > 0 else "", h.get('f', '')
                        poster_url = f"https://image.tmdb.org/t/p/w92{poster}" if poster else "https://via.placeholder.com/92x138/222222/555555?text=No+Img"
                        
                        html = f"""
                        <div style="display: flex; align-items: center; margin-bottom: 6px; background-color: transparent; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px;">
                            <img src="{poster_url}" style="width: 45px; height: 68px; border-radius: 4px; object-fit: cover; margin-right: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                            <div style="display: flex; flex-direction: column; justify-content: center;">
                                <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; line-height: 1.2;">{m_name}</div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: #FFC107; margin-bottom: 2px;">Movie <span style="color:#EDEDED; margin-left:4px;">{f"{r_stars} {f_moji}".strip()}</span></div>
                                <div style="font-size: 0.7rem; color: #888888;">{dt.strftime('%b %d, %Y • %I:%M %p')}</div>
                            </div>
                        </div>"""
                        c_left, c_right = st.columns([5, 1])
                        with c_left: st.markdown(html, unsafe_allow_html=True)
                        with c_right:
                            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                            if st.button("📝", key=f"h_r_mov_{h['i']}_{h_idx}", help="Rate & Review"): 
                                st.session_state.active_actor = None
                                show_movie_details(h['i'], m_name, details=None, is_watched=True)
                if len(mov_hist) > st.session_state.hist_mov_limit:
                    if st.button("Load More Movies", use_container_width=True, key="load_more_mov_hist"):
                        st.session_state.hist_mov_limit += 20; st.rerun()

    with t_prof_set:
        with st.expander("⚙️ Import TV Time Data", expanded=True):
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
                                        tmdb_id, title = match["id"], match.get("title", raw_title)
                                        poster, release_date = match.get("poster_path", ""), match.get("release_date", "")
                                        is_watched = m.get("is_watched", False)
                                        
                                        if not any(str(movie["id"]) == str(tmdb_id) for movie in new_db["movies"]):
                                            new_db["movies"].append({"id": tmdb_id, "name": title, "watched": is_watched, "poster_path": poster if poster else "", "release_date": release_date if release_date else "", "runtime": 120})
                                            if is_watched:
                                                w_dt_raw = m.get("watched_at")
                                                w_dt = parse_tvtime_date(w_dt_raw) if w_dt_raw else get_dubai_time().strftime("%Y-%m-%d %H:%M:%S")
                                                m_key = datetime.strptime(w_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                                                new_db["analytics"].setdefault(m_key, {"tv": 0, "movie": 0})
                                                new_db["analytics"][m_key]["movie"] += 1
                                                new_db["history"].append({"t": "m", "i": tmdb_id, "e": "", "d": w_dt, "r": 0, "f": "", "p": ""})
                                except: continue 
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
                                        tmdb_id, title = match["id"], match.get("name", raw_title)
                                        poster, first_air_date = match.get("poster_path", ""), match.get("first_air_date", "")
                                        watched_eps = []
                                        
                                        is_new_show = not any(str(show["id"]) == str(tmdb_id) for show in new_db["shows"])
                                        t_eps = fetch_robust(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={TMDB_KEY}").get("number_of_episodes", 1) if is_new_show else 1
                                        
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
                                                    
                                        if is_new_show: new_db["shows"].append({"id": tmdb_id, "name": title, "watched_episodes": watched_eps, "poster_path": poster if poster else "", "first_air_date": first_air_date if first_air_date else "", "total_episodes": t_eps})
                                        else:
                                            for show in new_db["shows"]:
                                                if str(show["id"]) == str(tmdb_id):
                                                    show["watched_episodes"] = list(set(show["watched_episodes"] + watched_eps))
                                                    break
                                except: continue 
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
                    else: stat_txt.text("🛑 Import finished, but the cloud save failed. See error above.")
                else: st.error("Please upload at least one JSON file first.")
