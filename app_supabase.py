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

# --- PREMIUM MOBILE-FIRST CSS OVERHAUL ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important; background: transparent !important;}
    footer {visibility: hidden !important; display: none !important;}
    /* Targeted badge hiding.
       This used to be `[data-testid="stAppViewContainer"] ~ div {display:none}`,
       which hid EVERY sibling of the app container. Streamlit mounts dialogs
       and toasts into a portal that sits exactly there, so that rule silently
       swallowed every modal — rendered in the DOM, invisible on screen. */
    [data-testid="stAppViewContainer"] ~ div:has(> .viewerBadge_container),
    [data-testid="stAppViewContainer"] ~ div:has(> a[href*="streamlit.io"]) {
        display: none !important;
    }
    /* Allow-list: overlays must never be hidden, whatever else is going on. */
    div[role="dialog"],
    div[data-baseweb="modal"],
    div[data-baseweb="layer"],
    div[data-testid="stDialog"],
    div[data-testid="stToastContainer"],
    div[data-baseweb="toast"],
    div[data-testid="stToast"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
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

    [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
    hr { margin: 0.8rem 0 !important; border-color: rgba(255, 255, 255, 0.1) !important; }
    h1, h2, h3 { padding-top: 0.6rem !important; padding-bottom: 0.3rem !important; margin-bottom: 0 !important; }
    .stMarkdown p { margin-bottom: 0.5rem !important; }

    h3 { color: #FFD54F !important; font-weight: 800 !important; letter-spacing: -0.5px !important; }
    h3.tab-title { margin-top: -0.8rem !important; padding-top: 0 !important; }

    /* =========================================================
       CLICKABLE POSTER SYSTEM
       The invisible button is sized to the POSTER ONLY
       (width:100% + aspect-ratio 2/3) instead of stretching
       across the whole column. This means it can never swallow
       clicks belonging to any other widget that shares the
       column, which is what used to break other features.
       ========================================================= */
    div[data-testid="column"]:has(.poster-wrapper),
    div[data-testid="stColumn"]:has(.poster-wrapper) {
        position: relative !important;
        overflow: hidden !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
        background: #111 !important;
        transition: transform 0.25s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.25s ease !important;
        cursor: pointer !important;
    }
    div[data-testid="column"]:has(.poster-wrapper):hover,
    div[data-testid="stColumn"]:has(.poster-wrapper):hover {
        transform: scale(1.03) !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.8) !important;
    }
    div[data-testid="column"]:has(.poster-wrapper) > div,
    div[data-testid="stColumn"]:has(.poster-wrapper) > div {
        gap: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="column"]:has(.poster-wrapper) img,
    div[data-testid="stColumn"]:has(.poster-wrapper) img {
        transition: transform 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div[data-testid="column"]:has(.poster-wrapper):hover img,
    div[data-testid="stColumn"]:has(.poster-wrapper):hover img {
        transform: scale(1.06) !important;
    }
    /* the hit area itself.
       Every layer is stretched with inset:0 (top/right/bottom/left all zero)
       rather than a percentage height. A percentage height only resolves when
       the parent has a DEFINITE height, so `height:100%` inside an
       `aspect-ratio` box collapses the button to zero and the poster looks
       clickable (the hover lives on the column) while eating no clicks. */
    div[data-testid="column"]:has(.poster-wrapper) [data-testid="stElementContainer"]:has(div[data-testid="stButton"]),
    div[data-testid="stColumn"]:has(.poster-wrapper) [data-testid="stElementContainer"]:has(div[data-testid="stButton"]),
    div[data-testid="column"]:has(.poster-wrapper) div[data-testid="stButton"],
    div[data-testid="stColumn"]:has(.poster-wrapper) div[data-testid="stButton"] {
        position: absolute !important;
        top: 0 !important; right: 0 !important; bottom: 0 !important; left: 0 !important;
        width: 100% !important; height: 100% !important;
        min-height: 0 !important;
        z-index: 20 !important;
        opacity: 0 !important;
        margin: 0 !important; padding: 0 !important;
        pointer-events: auto !important;
    }
    div[data-testid="column"]:has(.poster-wrapper) div[data-testid="stButton"] button,
    div[data-testid="stColumn"]:has(.poster-wrapper) div[data-testid="stButton"] button {
        position: absolute !important;
        top: 0 !important; right: 0 !important; bottom: 0 !important; left: 0 !important;
        width: 100% !important; height: 100% !important;
        min-height: 0 !important;
        padding: 0 !important; margin: 0 !important;
        background: transparent !important; color: transparent !important; border: none !important;
        box-shadow: none !important;
        display: block !important;
        cursor: pointer !important;
    }
    div[data-testid="column"]:has(.poster-wrapper) div[data-testid="stButton"] button p,
    div[data-testid="stColumn"]:has(.poster-wrapper) div[data-testid="stButton"] button p {
        display: none !important;
    }

    /* --- INVISIBLE HISTORY CLICK SYSTEM --- */
    div[data-testid="column"]:has(.history-wrapper),
    div[data-testid="stColumn"]:has(.history-wrapper) {
        position: relative !important;
        transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        cursor: pointer !important;
    }
    div[data-testid="column"]:has(.history-wrapper):hover,
    div[data-testid="stColumn"]:has(.history-wrapper):hover {
        transform: translateX(5px) !important;
    }
    div[data-testid="column"]:has(.history-wrapper) > div,
    div[data-testid="stColumn"]:has(.history-wrapper) > div {
        gap: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="column"]:has(.history-wrapper) div[data-testid="stButton"],
    div[data-testid="stColumn"]:has(.history-wrapper) div[data-testid="stButton"] {
        position: absolute !important;
        top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
        z-index: 20 !important;
        opacity: 0 !important;
        height: 100% !important;
        width: 100% !important;
    }
    div[data-testid="column"]:has(.history-wrapper) div[data-testid="stButton"] button,
    div[data-testid="stColumn"]:has(.history-wrapper) div[data-testid="stButton"] button {
        width: 100% !important; height: 100% !important;
        display: block !important;
    }

    /* --- PILL NAVIGATION (DISCOVER) --- */
    div[role="radiogroup"] {
        display: flex !important; flex-direction: row !important; background-color: transparent !important;
        border: none !important; box-shadow: none !important; padding: 0 !important;
        width: 100% !important; overflow-x: auto !important; scrollbar-width: none; gap: 8px !important;
    }
    div[role="radiogroup"]::-webkit-scrollbar { display: none; }
    div[role="radiogroup"] > label {
        flex: 0 0 auto !important; background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 20px !important; padding: 6px 16px !important; margin: 0 !important; transition: all 0.2s !important;
    }
    div[role="radiogroup"] > label > div:first-child { display: none !important; }
    div[role="radiogroup"] > label:has(input:checked) { background: #FFC107 !important; border-color: #FFC107 !important; box-shadow: 0 4px 10px rgba(255, 193, 7, 0.3) !important; }
    div[role="radiogroup"] > label:has(input:checked) p { color: #000 !important; font-weight: 800 !important; }
    div[role="radiogroup"] > label p { font-size: 0.75rem !important; font-weight: 600 !important; margin: 0 !important; color: #EDEDED !important; white-space: nowrap !important; }

    /* --- TABS OVERHAUL --- */
    div[data-testid="stTabs"] > div[data-baseweb="tab-list"], div[data-testid="stTabs"] > div[role="tablist"] { display: flex !important; width: 100vw !important; max-width: 100% !important; margin-left: -0.5rem !important; padding: 0 0 5px 0 !important; gap: 0 !important; overflow-x: hidden !important; background-color: rgba(8, 9, 12, 0.85) !important; backdrop-filter: blur(12px) !important; -webkit-backdrop-filter: blur(12px) !important; border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important; }
    div[data-testid="stTabs"] button[role="tab"] { flex: 1 1 0px !important; min-width: 0 !important; padding: 10px 0px !important; margin: 0 !important; border-radius: 0 !important; transition: all 0.3s ease !important; }
    div[data-testid="stTabs"] button[role="tab"] p { font-size: 0.55rem !important; font-weight: 700 !important; text-align: center !important; margin: 0 auto !important; white-space: nowrap !important; letter-spacing: -0.4px !important; overflow: hidden !important; text-overflow: clip !important; color: #888 !important; transition: all 0.3s ease !important; }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { border-bottom: 3px solid #FFC107 !important; background: linear-gradient(to top, rgba(255, 193, 7, 0.15) 0%, transparent 100%) !important; box-shadow: inset 0px -10px 15px -10px rgba(255, 193, 7, 0.5) !important; }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p { color: #FFD54F !important; text-shadow: 0px 0px 10px rgba(255, 193, 7, 0.6) !important; }

    /* --- CAROUSEL HACKS --- */
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker), div[data-testid="stColumns"]:has(.carousel-marker) { display: flex !important; flex-direction: row !important; overflow-x: auto !important; flex-wrap: nowrap !important; scrollbar-width: none; padding-bottom: 15px !important; gap: 10px !important; }
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker)::-webkit-scrollbar, div[data-testid="stColumns"]:has(.carousel-marker)::-webkit-scrollbar { display: none; }
    div[data-testid="column"]:has(.carousel-marker), div[data-testid="stColumn"]:has(.carousel-marker) { flex: 0 0 115px !important; width: 115px !important; min-width: 115px !important; padding: 0 !important; display: block !important; }

    /* --- HORIZONTAL CAST HACKS & BUTTON TEXT FIX --- */
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker-cast), div[data-testid="stColumns"]:has(.carousel-marker-cast) { display: flex !important; flex-direction: row !important; overflow-x: auto !important; flex-wrap: nowrap !important; scrollbar-width: none; padding-bottom: 10px !important; gap: 10px !important; }
    div[data-testid="stHorizontalBlock"]:has(.carousel-marker-cast)::-webkit-scrollbar, div[data-testid="stColumns"]:has(.carousel-marker-cast)::-webkit-scrollbar { display: none; }
    div[data-testid="column"]:has(.carousel-marker-cast), div[data-testid="stColumn"]:has(.carousel-marker-cast) { flex: 0 0 85px !important; width: 85px !important; min-width: 85px !important; padding: 0 !important; display: block !important; text-align: center !important; }

    div[data-testid="column"]:has(.carousel-marker-cast) div[data-testid="stButton"] button[kind="tertiary"],
    div[data-testid="stColumn"]:has(.carousel-marker-cast) div[data-testid="stButton"] button[kind="tertiary"] {
        background: transparent !important; border: none !important; box-shadow: none !important; padding: 0 !important; margin: 0 !important;
        height: auto !important; min-height: 0 !important; width: 100% !important; display: block !important; transform: none !important;
    }
    div[data-testid="column"]:has(.carousel-marker-cast) div[data-testid="stButton"] button[kind="tertiary"] p,
    div[data-testid="stColumn"]:has(.carousel-marker-cast) div[data-testid="stButton"] button[kind="tertiary"] p {
        font-size: 0.55rem !important; font-weight: 500 !important; text-transform: none !important; letter-spacing: normal !important;
        white-space: pre-wrap !important; line-height: 1.1 !important; color: #aaa !important; margin: 0 !important;
    }
    div[data-testid="column"]:has(.carousel-marker-cast) div[data-testid="stButton"] button[kind="tertiary"]:hover p,
    div[data-testid="stColumn"]:has(.carousel-marker-cast) div[data-testid="stButton"] button[kind="tertiary"]:hover p { color: #FFC107 !important; text-decoration: underline !important;}

    /* --- INLINE SEARCH CLEAR BUTTON OVERRIDE --- */
    div[data-testid="stVerticalBlock"]:has(> div > div > .search-container-hook) { position: relative !important; }
    div:has(> .clear-btn-hook) + div { position: absolute !important; right: 8px !important; top: 7px !important; width: 26px !important; z-index: 100 !important; }
    div:has(> .clear-btn-hook) + div button { background: rgba(255,255,255,0.08) !important; border: none !important; box-shadow: none !important; color: #aaa !important; padding: 0 !important; min-height: 26px !important; height: 26px !important; width: 26px !important; border-radius: 50% !important; font-size: 0.7rem !important; display: flex !important; align-items: center !important; justify-content: center !important; margin: 0 !important; line-height: 1 !important; }
    div:has(> .clear-btn-hook) + div button:hover { background: rgba(255, 193, 7, 0.3) !important; color: #FFD54F !important; }

    .grid-title { font-size: 0.65rem; color: #ccc; text-align: center; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 600; }

    @media (max-width: 992px) {
        div[data-testid="stHorizontalBlock"]:has(.grid-3-col), div[data-testid="stColumns"]:has(.grid-3-col) { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 3% !important; }
        div[data-testid="column"]:has(.grid-3-col), div[data-testid="stColumn"]:has(.grid-3-col) { width: 31% !important; flex: 1 1 31% !important; min-width: 0 !important; padding: 0 !important; display: block !important; }
        div[data-testid="stHorizontalBlock"]:has(.grid-2-col), div[data-testid="stColumns"]:has(.grid-2-col) { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 4% !important; }
        div[data-testid="column"]:has(.grid-2-col), div[data-testid="stColumn"]:has(.grid-2-col) { width: 48% !important; flex: 1 1 48% !important; min-width: 0 !important; padding: 0 !important; display: block !important; }
        div[role="dialog"] { width: 95vw !important; max-width: 95vw !important; margin: 0 auto !important; padding: 0 !important; background: rgba(15, 17, 22, 0.95) !important; backdrop-filter: blur(20px) !important; -webkit-backdrop-filter: blur(20px) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; overflow: hidden !important;}
        div[role="dialog"] > div:first-child { padding: 0 15px 20px 15px !important; }
    }
    .badge { display: inline-block; background-color: rgba(255,255,255,0.1); color: #FFFFFF; padding: 3px 8px; border-radius: 12px; font-size: 0.65rem; font-weight: 600; margin-right: 4px; margin-bottom: 6px; border: 1px solid rgba(255,255,255,0.05); }
    .badge-gold { background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%); color: #000000; border: none; box-shadow: 0 2px 6px rgba(255, 193, 7, 0.3); }
</style>
""", unsafe_allow_html=True)


# --- DUBAI TIMEZONE OVERRIDE ---
def get_dubai_time():
    return datetime.utcnow() + timedelta(hours=4)


def parse_tvtime_date(date_str):
    """TV Time exports use a few different shapes; normalise them all."""
    if not date_str:
        return get_dubai_time().strftime("%Y-%m-%d %H:%M:%S")
    raw = str(date_str).strip().replace("Z", "")
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
    return get_dubai_time().strftime("%Y-%m-%d %H:%M:%S")


# --- STATES ---
for k in ["next_tv_limit", "next_mov_limit", "soon_tv_limit", "soon_mov_limit"]:
    if k not in st.session_state:
        st.session_state[k] = 30
for k in ["hist_tv_limit", "hist_mov_limit"]:
    if k not in st.session_state:
        st.session_state[k] = 20
for k in ["tv_lib_limit", "mov_lib_limit"]:
    if k not in st.session_state:
        st.session_state[k] = 50
if "c_limits" not in st.session_state:
    st.session_state.c_limits = {}
if "rec_show" not in st.session_state:
    st.session_state.rec_show = None
if "active_actor" not in st.session_state:
    st.session_state.active_actor = None
if "search_reset_ctr" not in st.session_state:
    st.session_state.search_reset_ctr = 0
if "lib_tv_reset_ctr" not in st.session_state:
    st.session_state.lib_tv_reset_ctr = 0
if "lib_mov_reset_ctr" not in st.session_state:
    st.session_state.lib_mov_reset_ctr = 0
# THE single source of truth for "which dialog should be open right now"
if "dialog" not in st.session_state:
    st.session_state.dialog = None

# --- DB PIPELINE ---
TMDB_KEY = st.secrets["TMDB_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
DB_ENDPOINT = f"{SUPABASE_URL}/rest/v1/tv_time_data?id=eq.1"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
# Flip to False to fall back to the old one-request-per-season path.
# Useful as a quick A/B if you ever suspect the bundling of a problem.
USE_BUNDLED_FETCH = True

TODAY = get_dubai_time().strftime('%Y-%m-%d')
PLATFORMS = ["None", "Stremio", "Netflix", "OSN+", "Amazon Prime", "Apple TV+", "Disney+", "Starzplay", "Cinema", "Downloaded", "Other"]
PREMIUM_EMOTIONS = ["None", "🤯 Mind Blown", "😂 Hilarious", "😭 Emotional", "😍 Loved it", "😡 Frustrated", "😴 Bored", "🍿 Pure Hype", "🧠 Genius Plot", "💔 Heartbroken", "🤬 Trash", "🫣 Edge of Seat", "📈 Peak Cinema"]


@st.cache_data(ttl=43200, max_entries=800, show_spinner=False)
def fetch_api(url):
    try:
        safe_url = requests.utils.requote_uri(url)
        r = requests.get(safe_url, timeout=5)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


def fetch_robust(url):
    safe_url = requests.utils.requote_uri(url)
    for _ in range(3):
        try:
            r = requests.get(safe_url, timeout=5)
            if r.status_code == 429:
                time.sleep(1.5)
                continue
            if r.status_code == 200:
                return r.json()
            return {}
        except Exception:
            time.sleep(1)
    return {}


def _fetch_uncached(url):
    """
    Plain fetch with NO st.cache_data wrapper.

    Used for the append_to_response calls inside fetch_show_bundle. Routing
    those through fetch_api would cache the raw mega-response AND the bundle
    built from it, holding every show's season data in memory twice — which
    is enough to OOM the container on a library of any size.
    """
    try:
        r = requests.get(requests.utils.requote_uri(url), timeout=8)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}


# Only the episode fields this app actually reads. Full TMDB season payloads
# carry crew, guest_stars and long overviews for every episode; keeping them
# is what makes the cache balloon.
_EP_KEYS = ("episode_number", "season_number", "air_date", "name", "still_path", "vote_average", "overview")
# Known-heavy keys on the show object that nothing here renders.
_SHOW_DROP = ("production_companies", "production_countries", "spoken_languages", "networks",
              "created_by", "languages", "last_episode_to_air", "next_episode_to_air", "images")


def _trim_episode(ep):
    return {k: ep.get(k) for k in _EP_KEYS if k in ep}


def _trim_show(base):
    out = {k: v for k, v in base.items() if k not in _SHOW_DROP}
    out["seasons"] = [{"season_number": s.get("season_number"), "name": s.get("name"), "episode_count": s.get("episode_count")}
                      for s in base.get("seasons", [])]
    return out


@st.cache_data(ttl=43200, max_entries=400, show_spinner=False)
def fetch_show_bundle(show_id):
    """
    One show + all of its seasons in as few HTTP calls as possible.

    TMDB's append_to_response folds sub-resources into the parent response,
    so a 6-season show costs 2 requests instead of 7. It caps at 20 appended
    items, so longer shows are fetched in chunks of 20. The result is shaped
    like the plain /tv/{id} response with extra "season/N" keys, so existing
    details.get(...) calls keep working — but trimmed to the fields this app
    renders, so the cache stays small enough to live in a 1GB container.
    """
    if not USE_BUNDLED_FETCH:
        return fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}?api_key={TMDB_KEY}")

    base = _fetch_uncached(f"https://api.themoviedb.org/3/tv/{show_id}?api_key={TMDB_KEY}")
    if not base:
        return {}

    nums = [s["season_number"] for s in base.get("seasons", []) if s.get("season_number", 0) > 0]
    bundle = _trim_show(base)
    if not nums:
        return bundle

    for start in range(0, len(nums), 20):
        chunk = nums[start:start + 20]
        appended = ",".join(f"season/{n}" for n in chunk)
        data = _fetch_uncached(f"https://api.themoviedb.org/3/tv/{show_id}?api_key={TMDB_KEY}&append_to_response={appended}")
        if not data:
            continue
        for n in chunk:
            key = f"season/{n}"
            if key in data:
                bundle[key] = {"episodes": [_trim_episode(e) for e in (data[key].get("episodes") or [])]}
        del data
    return bundle


def season_episodes(bundle, show_id, season_number):
    """Read a season out of a bundle, falling back to a direct call if absent."""
    key = f"season/{season_number}"
    if isinstance(bundle, dict) and key in bundle:
        return bundle[key].get("episodes") or []
    return fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/season/{season_number}?api_key={TMDB_KEY}").get("episodes") or []


def encode_eps(eps):
    seasons = {}
    for ep in eps:
        try:
            s, e = ep.split('E')
            seasons.setdefault(int(s.replace('S', '')), []).append(int(e))
        except Exception:
            pass
    res = []
    for s, e_list in seasons.items():
        if not e_list:
            continue
        e_list = sorted(list(set(e_list)))
        ranges, start, prev = [], e_list[0], e_list[0]
        for e in e_list[1:]:
            if e == prev + 1:
                prev = e
            else:
                ranges.append(str(start) if start == prev else f"{start}-{prev}")
                start = prev = e
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        res.append(f"{s}:{'.'.join(ranges)}")
    return "|".join(res)


def decode_eps(ep_str):
    if not ep_str:
        return []
    eps = []
    for s_part in str(ep_str).split('|'):
        if ':' not in s_part:
            continue
        s, e_part = s_part.split(':')
        for r in e_part.split('.'):
            if '-' in r:
                start, end = r.split('-')
                eps.extend([f"S{s}E{e}" for e in range(int(start), int(end) + 1)])
            else:
                if r:
                    eps.append(f"S{s}E{r}")
    return eps


def pack_db(db):
    packed = {"m": [], "s": [], "h": [], "a": {}}
    for m in db.get("movies", []):
        packed["m"].append([m["id"], m["name"], 1 if m["watched"] else 0, m.get("poster_path", ""), m.get("release_date", ""), m.get("runtime", 0), 1 if m.get("dropped") else 0])
    for s in db.get("shows", []):
        packed["s"].append([s["id"], s["name"], encode_eps(s.get("watched_episodes", [])), s.get("poster_path", ""), s.get("first_air_date", ""), s.get("total_episodes", 1), 1 if s.get("dropped") else 0])
    for h in db.get("history", []):
        packed["h"].append([1 if h.get("t") == "s" else 0, h.get("i"), h.get("e", ""), h.get("d"), h.get("r", 0), h.get("f", ""), h.get("p", "")])
    for k, v in db.get("analytics", {}).items():
        packed["a"][k] = [v.get("tv", 0), v.get("movie", 0)]
    packed["r"] = db.get("seen_recaps", [])
    return packed


def unpack_db(packed):
    db = {"movies": [], "shows": [], "history": [], "analytics": {}, "seen_recaps": []}
    for m in packed.get("m", []):
        db["movies"].append({"id": m[0], "name": m[1], "watched": bool(m[2]), "poster_path": m[3], "release_date": m[4], "runtime": m[5], "dropped": bool(m[6]) if len(m) > 6 else False})
    for s in packed.get("s", []):
        db["shows"].append({"id": s[0], "name": s[1], "watched_episodes": decode_eps(s[2]), "poster_path": s[3], "first_air_date": s[4], "total_episodes": s[5], "dropped": bool(s[6]) if len(s) > 6 else False})
    for h in packed.get("h", []):
        entry = {"t": "s" if h[0] == 1 else "m", "i": h[1], "e": h[2], "d": h[3]}
        if len(h) > 4:
            entry["r"] = h[4]
        if len(h) > 5:
            entry["f"] = h[5]
        if len(h) > 6:
            entry["p"] = h[6]
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
        return None
    except Exception:
        return None


def save_db():
    try:
        res = requests.patch(DB_ENDPOINT, json={"payload": pack_db(st.session_state.db)}, headers=HEADERS, timeout=5)
        return res.status_code in [200, 204]
    except Exception:
        return False


if "db" not in st.session_state:
    db_data = load_db()
    if db_data is None:
        st.stop()
    st.session_state.db = db_data


# =====================================================================
# WATCHED-STATE: ONE SOURCE OF TRUTH
# Every screen asks these helpers instead of passing an `is_watched`
# flag around. That is why an already-watched movie opened from Search,
# Discover, the Actor panel or Upcoming used to offer "Mark as Watched".
# =====================================================================
def get_show(show_id):
    return next((s for s in st.session_state.db.get("shows", []) if str(s["id"]) == str(show_id)), None)


def get_movie(movie_id):
    return next((m for m in st.session_state.db.get("movies", []) if str(m["id"]) == str(movie_id)), None)


def find_history(item_type, item_id, detail=""):
    """item_type is 'tv' or 'movie'. Returns the history log dict or None."""
    t_flag = "s" if item_type == "tv" else "m"
    for h in st.session_state.db.get("history", []):
        if h.get("t") != t_flag or str(h.get("i")) != str(item_id):
            continue
        if t_flag == "s" and str(h.get("e", "")) != str(detail):
            continue
        return h
    return None


def is_episode_watched(show_id, ep_code):
    show = get_show(show_id)
    if show and ep_code in show.get("watched_episodes", []):
        return True
    return find_history("tv", show_id, ep_code) is not None


def is_movie_watched(movie_id):
    movie = get_movie(movie_id)
    if movie and movie.get("watched"):
        return True
    return find_history("movie", movie_id) is not None


def reconcile_watch_state():
    """
    Additive one-way repair: anything present in history is marked watched
    on the library object too. Never removes, so un-marking still works.
    Runs once per session.
    """
    if st.session_state.get("_reconciled"):
        return
    st.session_state["_reconciled"] = True
    db = st.session_state.db
    dirty = False
    show_map = {str(s["id"]): s for s in db.get("shows", [])}
    movie_map = {str(m["id"]): m for m in db.get("movies", [])}
    for h in db.get("history", []):
        key = str(h.get("i"))
        if h.get("t") == "s":
            show = show_map.get(key)
            code = h.get("e", "")
            if show and code and code not in show.get("watched_episodes", []):
                show.setdefault("watched_episodes", []).append(code)
                dirty = True
        else:
            movie = movie_map.get(key)
            if movie and not movie.get("watched"):
                movie["watched"] = True
                dirty = True
    if dirty:
        save_db()


reconcile_watch_state()


def log_watch(item_type, item_id, detail=""):
    now_str = get_dubai_time().strftime('%Y-%m-%d %H:%M:%S')
    m_key = get_dubai_time().strftime('%Y-%m')
    db = st.session_state.db
    db.setdefault("analytics", {}).setdefault(m_key, {"tv": 0, "movie": 0})
    if item_type == "tv":
        db["analytics"][m_key]["tv"] += 1
    else:
        db["analytics"][m_key]["movie"] += 1
    db.setdefault("history", []).insert(0, {"t": "s" if item_type == "tv" else "m", "i": item_id, "e": detail, "d": now_str, "r": 0, "f": "", "p": ""})
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
            except Exception:
                pass
            break
    if item_type == "tv":
        show = get_show(item_id)
        if show and detail in show.get("watched_episodes", []):
            show["watched_episodes"].remove(detail)
    else:
        movie = get_movie(item_id)
        if movie:
            movie["watched"] = False
    save_db()


def mark_episode(show_id, ep_code, watched):
    """Idempotent setter used by every screen."""
    show = get_show(show_id)
    if not show:
        return
    currently = is_episode_watched(show_id, ep_code)
    if watched and not currently:
        if ep_code not in show["watched_episodes"]:
            show["watched_episodes"].append(ep_code)
        log_watch("tv", show_id, ep_code)
    elif not watched and currently:
        remove_watch("tv", show_id, ep_code)


def mark_movie(movie_id, watched):
    movie = get_movie(movie_id)
    if not movie:
        return
    currently = is_movie_watched(movie_id)
    if watched and not currently:
        movie["watched"] = True
        log_watch("movie", movie_id)
    elif not watched and currently:
        remove_watch("movie", movie_id)


def calc_time_remaining(date_str):
    if not date_str:
        return "Soon"
    try:
        target = datetime.strptime(date_str, '%Y-%m-%d')
        diff = target - get_dubai_time()
        days, hours = diff.days, diff.seconds // 3600
        if days > 0:
            return f"In {days}d {hours}h"
        elif days == 0 and hours > 0:
            return f"In {hours}h"
        elif diff.total_seconds() > 0:
            return "In <1h"
        else:
            return "Out Now"
    except Exception:
        return "Soon"


# =====================================================================
# DIALOG QUEUE
# Streamlit permits exactly ONE st.dialog per script run, and every tab
# body runs on every rerun. Opening dialogs directly from inside a tab
# therefore made tabs fight over the single slot. Now every click just
# records an intent and reruns; one router opens one dialog.
# =====================================================================
def open_dialog(kind, **payload):
    payload["kind"] = kind
    st.session_state.dialog = payload


def close_dialog():
    st.session_state.dialog = None


def cb_open_dialog(kind, **payload):
    open_dialog(kind, **payload)


# --- SMALL CALLBACKS ---
def cb_drop_tv(sid):
    show = get_show(sid)
    if show:
        show["dropped"] = True
    save_db()


def cb_restore_tv(sid):
    show = get_show(sid)
    if show:
        show["dropped"] = False
    save_db()


def cb_perm_delete_tv(sid):
    st.session_state.db["shows"] = [s for s in st.session_state.db["shows"] if str(s["id"]) != str(sid)]
    save_db()


def cb_drop_mov(mid):
    movie = get_movie(mid)
    if movie:
        movie["dropped"] = True
    save_db()


def cb_restore_mov(mid):
    movie = get_movie(mid)
    if movie:
        movie["dropped"] = False
    save_db()


def cb_perm_delete_mov(mid):
    st.session_state.db["movies"] = [mv for mv in st.session_state.db["movies"] if str(mv["id"]) != str(mid)]
    save_db()


def cb_toggle_episode(sid, ecode):
    mark_episode(sid, ecode, st.session_state.get(f"chk_dlg_{sid}_{ecode}", False))


def cb_watch_tv_feed(sid, sname, ecode):
    mark_episode(sid, ecode, True)
    open_dialog("episode", id=sid, name=sname, code=ecode)


def cb_set_active_actor(aid):
    st.session_state.active_actor = aid


def cb_close_active_actor():
    st.session_state.active_actor = None


def cb_clear_search():
    st.session_state.search_reset_ctr += 1


def cb_clear_lib_tv():
    st.session_state.lib_tv_reset_ctr += 1


def cb_clear_lib_mov():
    st.session_state.lib_mov_reset_ctr += 1


def cb_toggle_ep_info(sid, ecode):
    st.session_state[f"view_info_{sid}_{ecode}"] = not st.session_state.get(f"view_info_{sid}_{ecode}", False)


# --- VISUAL HELPERS ---
def render_poster_card(title, poster_path, subtitle="", progress_pct=-1.0):
    img_url = f"https://image.tmdb.org/t/p/w342{poster_path}" if poster_path else "https://via.placeholder.com/342x513/222222/555555?text=No+Poster"
    prog_width = min(progress_pct, 1.0) * 100
    prog_html = f'<div style="position: absolute; bottom: 0; left: 0; height: 4px; width: {prog_width}%; background: #FFC107; box-shadow: 0 0 8px #FFC107; z-index: 3;"></div>' if progress_pct >= 0 else ''
    sub_html = f'<div style="color: #FFC107; font-weight: 700; font-size: 0.6rem; margin-top: 2px;">{subtitle}</div>' if subtitle else ''

    html = (
        f'<div style="position: relative; aspect-ratio: 2/3; background-color: #111; border-radius: 8px; overflow: hidden;">'
        f'<img src="{img_url}" style="width: 100%; height: 100%; object-fit: cover; display: block;">'
        f'<div style="position: absolute; bottom: 0; left: 0; right: 0; height: 60%; background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0) 100%); z-index: 1;"></div>'
        f'<div class="poster-text" style="position: absolute; bottom: 10px; left: 10px; right: 10px; z-index: 2;">'
        f'<div style="color: white; font-weight: 800; font-size: 0.75rem; line-height: 1.2; text-shadow: 0 2px 4px rgba(0,0,0,0.8); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{title}</div>'
        f'{sub_html}'
        f'</div>'
        f'{prog_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def poster_button(title, poster_path, key, subtitle="", progress_pct=-1.0, marker="grid-3-col"):
    """
    Renders a poster whose entire artwork is one clickable hit area.
    The poster markdown and the button are the ONLY things placed in the
    column, so the invisible overlay can never intercept another widget.
    Returns True on click.
    """
    if marker:
        st.markdown(f'<span class="{marker}"></span>', unsafe_allow_html=True)
    render_poster_card(title, poster_path, subtitle=subtitle, progress_pct=progress_pct)
    st.markdown('<span class="poster-wrapper"></span>', unsafe_allow_html=True)
    return st.button("OPEN", key=key, use_container_width=True)


def show_cast_horizontal(cast_list, key_prefix, limit=15):
    if not cast_list:
        return
    cols = st.columns(len(cast_list[:limit]))
    for idx, actor in enumerate(cast_list[:limit]):
        with cols[idx]:
            st.markdown('<span class="carousel-marker-cast"></span>', unsafe_allow_html=True)
            img_url = f"https://image.tmdb.org/t/p/w185{actor['profile_path']}" if actor.get("profile_path") else "https://via.placeholder.com/185x278/222222/888888?text=No+Photo"
            encoded_name = requests.utils.quote(str(actor.get('name', '')))
            imdb_url = f"https://www.imdb.com/find/?q={encoded_name}"
            char_name = str(actor.get('character', '')).strip()

            html_img = (
                f'<a href="{imdb_url}" target="_blank">'
                f'<img src="{img_url}" style="width: 85px; height: 127px; border-radius: 8px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 6px; transition: transform 0.2s;">'
                f'</a>'
            )
            st.markdown(html_img, unsafe_allow_html=True)

            if char_name:
                html_char = f'<div style="font-size: 0.55rem; color: #FFC107; font-weight: 700; line-height: 1.1; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{char_name}</div>'
                st.markdown(html_char, unsafe_allow_html=True)

            st.button(actor.get('name', 'Unknown'), key=f"cast_{key_prefix}_{actor['id']}_{idx}", on_click=cb_set_active_actor, args=(actor['id'],), use_container_width=True, type="tertiary")


def render_apple_tv_header(backdrop_path, poster_path, title, badges_html):
    bg = f"https://image.tmdb.org/t/p/w780{backdrop_path}" if backdrop_path else f"https://image.tmdb.org/t/p/w342{poster_path}"
    post = f"https://image.tmdb.org/t/p/w185{poster_path}" if poster_path else "https://via.placeholder.com/185x278/222222/555555?text=No+Poster"
    blur = 0 if backdrop_path else 15

    html = (
        f'<div style="margin: -24px -24px 0 -24px; position: relative; overflow: hidden;">'
        f'<div style="width: 100%; height: 220px; background-image: url(\'{bg}\'); background-size: cover; background-position: center; filter: brightness(0.6) blur({blur}px);"></div>'
        f'<div style="position: absolute; bottom: 0; left: 0; right: 0; height: 120px; background: linear-gradient(to top, rgba(15,17,22,1) 0%, rgba(15,17,22,0) 100%);"></div>'
        f'<div style="position: absolute; bottom: -20px; left: 20px; right: 20px; display: flex; align-items: flex-end; gap: 15px; z-index: 10;">'
        f'<img src="{post}" style="width: 105px; height: 157px; border-radius: 8px; box-shadow: 0 8px 20px rgba(0,0,0,0.8); border: 1px solid rgba(255,255,255,0.1); object-fit: cover;">'
        f'<div style="padding-bottom: 25px; flex: 1; min-width: 0;">'
        f'<div style="margin: 0; padding: 0; font-size: 1.4rem; font-weight: 800; line-height: 1.1; text-shadow: 0 2px 4px rgba(0,0,0,0.8); color: white; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{title}</div>'
        f'<div style="margin-top: 6px;">{badges_html}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'<div style="height: 35px;"></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_journal_editor(h_log, key_suffix):
    """Shared platform / rating / feeling editor for both movies and episodes."""
    st.markdown("#### Journal & Review")
    curr_p = h_log.get("p", "")
    new_p = st.selectbox("Watched On:", PLATFORMS, index=PLATFORMS.index(curr_p) if curr_p in PLATFORMS else 0, key=f"p_{key_suffix}")

    c1, c2 = st.columns(2)
    with c1:
        ratings = [0, 1, 2, 3, 4, 5]
        curr_r = h_log.get("r", 0)
        new_r = st.selectbox("Rating (1-5):", ratings, index=curr_r if curr_r in ratings else 0, format_func=lambda x: f"{x} ⭐" if x > 0 else "Unrated", key=f"r_{key_suffix}")
    with c2:
        curr_f = h_log.get("f", "")
        new_f = st.selectbox("Feeling:", PREMIUM_EMOTIONS, index=PREMIUM_EMOTIONS.index(curr_f) if curr_f in PREMIUM_EMOTIONS else 0, key=f"f_{key_suffix}")

    if new_p != curr_p or new_r != curr_r or new_f != curr_f:
        h_log["p"] = new_p if new_p != "None" else ""
        h_log["r"] = new_r
        h_log["f"] = new_f if new_f != "None" else ""
        save_db()


def render_inline_actor_pokedex(actor_id):
    details = fetch_api(f"https://api.themoviedb.org/3/person/{actor_id}?api_key={TMDB_KEY}")
    credits = fetch_api(f"https://api.themoviedb.org/3/person/{actor_id}/combined_credits?api_key={TMDB_KEY}")

    db_shows = {str(s["id"]): s for s in st.session_state.db["shows"]}
    db_movies = {str(m["id"]): m for m in st.session_state.db["movies"]}

    owned_items = []
    seen_ids = set()
    for c in credits.get("cast", []):
        cid = str(c["id"])
        if c.get("media_type") == "tv" and cid in db_shows and cid not in seen_ids:
            owned_items.append({"id": cid, "title": db_shows[cid]["name"], "type": "tv", "poster": db_shows[cid].get("poster_path")})
            seen_ids.add(cid)
        elif c.get("media_type") == "movie" and cid in db_movies and cid not in seen_ids:
            owned_items.append({"id": cid, "title": db_movies[cid]["name"], "type": "movie", "poster": db_movies[cid].get("poster_path")})
            seen_ids.add(cid)

    st.markdown("<hr style='margin: 0.5rem 0; border-color: #FFC107;'>", unsafe_allow_html=True)
    with st.container(border=True):
        col_title, col_btn = st.columns([8, 2])
        with col_title:
            st.markdown(f"<h4 style='color: #FFD54F;'>{details.get('name', 'Actor Profile')}</h4>", unsafe_allow_html=True)
        with col_btn:
            st.button("✖ Close", key=f"close_act_{actor_id}", on_click=cb_close_active_actor, use_container_width=True)

        c1, c2 = st.columns([1, 2])
        with c1:
            img_url = f"https://image.tmdb.org/t/p/w185{details.get('profile_path')}" if details.get("profile_path") else "https://via.placeholder.com/185x278/222222/555555?text=No+Image"
            st.markdown(f'<img src="{img_url}" style="width: 100%; border-radius: 8px;">', unsafe_allow_html=True)
        with c2:
            st.caption(f"**Born:** {details.get('birthday', 'Unknown')}")
            bio = details.get("biography", "")
            if len(bio) > 150:
                bio = bio[:150] + "..."
            st.write(bio if bio else "No biography available.")

        if owned_items:
            st.markdown(f"**📚 In Your Library ({len(owned_items)})**")
            cols = st.columns(len(owned_items))
            for idx, item in enumerate(owned_items):
                with cols[idx]:
                    if poster_button(item["title"], item.get("poster"), key=f"act_own_{actor_id}_{item['id']}_{idx}", marker="carousel-marker"):
                        st.session_state.active_actor = None
                        open_dialog("show" if item["type"] == "tv" else "movie", id=item['id'], name=item['title'])
                        st.rerun()

        st.markdown("**🌟 Famous Roles**")
        top_credits = sorted(credits.get("cast", []), key=lambda x: x.get("popularity", 0), reverse=True)[:10]
        if top_credits:
            cols = st.columns(len(top_credits))
            for idx, item in enumerate(top_credits):
                with cols[idx]:
                    i_title = item.get("name") if item.get("media_type") == "tv" else item.get("title")
                    if poster_button(i_title, item.get("poster_path"), key=f"act_role_{actor_id}_{item['id']}_{idx}", marker="carousel-marker"):
                        st.session_state.active_actor = None
                        open_dialog("show" if item.get("media_type") == "tv" else "movie", id=item['id'], name=i_title)
                        st.rerun()


# --- RECAP ENGINE ---
@st.dialog("🌙 Monthly Wrap-Up")
def show_monthly_recap_dialog(month_key, month_title, stats, recap_id):
    st.markdown(f"## {month_title} Recap")
    st.write("Here is a quick look at your screening inventory from last month:")
    tv_count, mov_count = stats.get("tv", 0), stats.get("movie", 0)
    total_mins = (tv_count * 45) + (mov_count * 120)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("📺 Episodes Logged", f"{tv_count} eps")
    with c2:
        st.metric("🎬 Movies Watched", f"{mov_count} titles")
    st.markdown(f"⏳ **Screen Time Investment:** ~`{total_mins // 60}` hours spent streaming.")

    show_counts, plat_counts, feel_counts = {}, {}, {}
    for h in st.session_state.db.get("history", []):
        if str(h.get("d", "")).startswith(month_key):
            if h.get("t") == "s":
                show_counts[h["i"]] = show_counts.get(h["i"], 0) + 1
            if h.get("p") and h.get("p") != "None":
                plat_counts[h["p"]] = plat_counts.get(h["p"], 0) + 1
            if h.get("f") and h.get("f") != "None":
                feel_counts[h["f"]] = feel_counts.get(h["f"], 0) + 1

    if show_counts:
        top_show_id = max(show_counts, key=show_counts.get)
        show = get_show(top_show_id)
        if show:
            st.markdown(f"🔥 **Top Binge Focus:** *{show['name']}* ({show_counts[top_show_id]} episodes)")
    if plat_counts:
        st.markdown(f"📡 **Platform Loyalty:** Most watched on **{max(plat_counts, key=plat_counts.get)}**")
    if feel_counts:
        st.markdown(f"🎭 **Monthly Vibe:** **{max(feel_counts, key=feel_counts.get)}**")

    st.divider()
    is_seen = recap_id in st.session_state.db.get("seen_recaps", [])
    if st.button("✖ Close Recap" if is_seen else "Sweet!", use_container_width=True, key=f"close_month_recap_{recap_id}"):
        if not is_seen:
            st.session_state.db.setdefault("seen_recaps", []).append(recap_id)
            save_db()
        close_dialog()
        st.rerun()


@st.dialog("🏆 Your Cinematic Wrapped")
def show_yearly_recap_dialog(year, y_tv, y_mov, recap_id):
    st.markdown(f"# 🍿 {year} YEAR IN REVIEW")
    st.write("You smashed your theater goals last year! Check out your custom achievements:")
    total_time = (y_tv * 45) + (y_mov * 120)
    days = total_time // 1440

    html_hero = (
        f'<div style="background: linear-gradient(135deg, #FFD54F 0%, #FFC107 100%); border-radius: 14px; padding: 22px; color: black; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(255,193,7,0.3);">'
        f'<div style="font-size: 2.6rem; font-weight: 900; line-height:1;">{y_tv + y_mov:,}</div>'
        f'<div style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-top:4px;">Total Titles Inventoried</div>'
        f'</div>'
    )
    st.markdown(html_hero, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px; text-align: center;">'
            f'<div style="font-size: 1.4rem; font-weight: 800; color: #FFC107;">{y_tv}</div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight:700;">Episodes Logged</div>'
            f'</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px; text-align: center;">'
            f'<div style="font-size: 1.4rem; font-weight: 800; color: #FFC107;">{y_mov}</div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight:700;">Movies Checked</div>'
            f'</div>', unsafe_allow_html=True)

    st.markdown(f"⏳ **Time Commitment:** You dedicated a total of **{days} days** and **{(total_time % 1440) // 60} hours** to premium story arcs.")

    y_hist = [h for h in st.session_state.db.get("history", []) if str(h.get("d", "")).startswith(str(year))]
    date_counts, plat_counts, feel_counts, show_counts, ratings = {}, {}, {}, {}, []

    for h in y_hist:
        d_only = h["d"][:10]
        date_counts[d_only] = date_counts.get(d_only, 0) + 1
        if h.get("p") and h.get("p") != "None":
            plat_counts[h["p"]] = plat_counts.get(h["p"], 0) + 1
        if h.get("f") and h.get("f") != "None":
            feel_counts[h["f"]] = feel_counts.get(h["f"], 0) + 1
        if h["t"] == "s":
            show_counts[h["i"]] = show_counts.get(h["i"], 0) + 1
        if h.get("r", 0) > 0:
            ratings.append(h["r"])

    st.divider()
    st.markdown("### The Deep Dive")
    if ratings:
        st.markdown(f"⭐ **Average Rating:** {round(sum(ratings)/len(ratings), 1)} / 5.0")
    if plat_counts:
        st.markdown(f"📡 **Top Platform:** {max(plat_counts, key=plat_counts.get)}")
    if feel_counts:
        st.markdown(f"🎭 **Top Vibe:** {max(feel_counts, key=feel_counts.get)}")
    if date_counts:
        max_d, max_c = max(date_counts.items(), key=lambda x: x[1])
        st.markdown(f"🔥 **Ultimate Binge Day:** {max_c} items on {max_d}")

    if show_counts:
        st.markdown("**🏆 Top 3 Shows:**")
        for sid, sc in sorted(show_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            s_obj = get_show(sid)
            if s_obj:
                st.markdown(f"- {s_obj['name']} ({sc} eps)")

    if days > 12:
        tier_title, tier_desc = "👑 Emperor of the Couch", "Absolute legend. Hollywood production lines should put you on their payroll."
    elif days > 5:
        tier_title, tier_desc = "🍿 Marathon Veteran", "You know exactly how to lock down a weekend block and demolish complex plotlines."
    else:
        tier_title, tier_desc = "🎬 Curation Connoisseur", "High-taste selection habits. You filter for absolute choice cinema narrative styles."

    st.markdown(
        f'<div style="background: rgba(255, 193, 7, 0.08); border: 1px dashed #FFC107; border-radius: 12px; padding: 15px; margin-top: 15px; text-align: center;">'
        f'<div style="font-size: 1.15rem; font-weight: 800; color: #FFD54F;">{tier_title}</div>'
        f'<div style="font-size: 0.75rem; color: #eee; margin-top: 5px; line-height:1.3;">{tier_desc}</div>'
        f'</div>', unsafe_allow_html=True)
    st.divider()
    is_seen = recap_id in st.session_state.db.get("seen_recaps", [])
    if st.button("✖ Close Recap" if is_seen else "Claim Achievement Status", use_container_width=True, key=f"close_year_recap_{recap_id}"):
        if not is_seen:
            st.session_state.db.setdefault("seen_recaps", []).append(recap_id)
            save_db()
        close_dialog()
        st.rerun()


def queue_pending_recaps():
    """Queues a recap only if nothing else already owns the dialog slot."""
    if st.session_state.get("recaps_checked"):
        return
    st.session_state.recaps_checked = True
    if st.session_state.dialog:
        return
    db = st.session_state.db
    seen = db.setdefault("seen_recaps", [])
    now = get_dubai_time()

    last_day_of_prev_month = now.replace(day=1) - timedelta(days=1)
    prev_month_key = last_day_of_prev_month.strftime("%Y-%m")

    if f"monthly-{prev_month_key}" not in seen:
        stats = db.get("analytics", {}).get(prev_month_key, {"tv": 0, "movie": 0})
        if stats["tv"] > 0 or stats["movie"] > 0:
            open_dialog("recap_month", month_key=prev_month_key, title=last_day_of_prev_month.strftime("%B %Y"), stats=stats, recap_id=f"monthly-{prev_month_key}")
            return

    if f"yearly-{now.year - 1}" not in seen:
        y_tv, y_mov = 0, 0
        for k, v in db.get("analytics", {}).items():
            if k.startswith(str(now.year - 1)):
                y_tv += v.get("tv", 0)
                y_mov += v.get("movie", 0)
        if y_tv > 0 or y_mov > 0:
            open_dialog("recap_year", year=now.year - 1, y_tv=y_tv, y_mov=y_mov, recap_id=f"yearly-{now.year - 1}")


# --- CENTRALIZED MANAGEMENT DIALOGS ---
@st.dialog("Episode Details")
def show_episode_details(show_id, show_name, ep_code):
    ep_data = {}
    try:
        s_num, e_num = ep_code.split('E')[0].replace('S', ''), ep_code.split('E')[1]
        ep_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/season/{s_num}/episode/{e_num}?api_key={TMDB_KEY}") or {}
    except Exception:
        ep_data = {}

    s_details = fetch_show_bundle(show_id)
    is_watched = is_episode_watched(show_id, ep_code)

    badges = f'<span class="badge badge-gold">{ep_code}</span><span class="badge">⭐ {ep_data.get("vote_average", 0.0)}</span>'
    if is_watched:
        badges += '<span class="badge">✅ Watched</span>'
    render_apple_tv_header(ep_data.get("still_path") or s_details.get("backdrop_path"), s_details.get("poster_path"), ep_data.get('name', 'Untitled Episode'), badges)

    st.caption(f"**Aired:** {ep_data.get('air_date', 'N/A')}")
    st.write(ep_data.get("overview", "No synopsis available for this episode yet."))

    current_show = get_show(show_id)

    if is_watched:
        h_log = find_history("tv", show_id, ep_code)
        if h_log:
            try:
                st.success(f"✅ **Watched on:** {datetime.strptime(h_log['d'], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y at %I:%M %p')}")
            except Exception:
                pass
            render_journal_editor(h_log, f"s_{show_id}_{ep_code}")

    st.divider()
    st.markdown("#### Cast & Guest Stars")
    cast_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}").get("cast") or []
    guest_data = ep_data.get("guest_stars") or []
    show_cast_horizontal(cast_data + guest_data, key_prefix=f"ep_{show_id}_{ep_code}", limit=15)

    if st.session_state.get("active_actor"):
        render_inline_actor_pokedex(st.session_state["active_actor"])

    st.divider()
    if not current_show:
        st.warning("➕ Add this show to your library to track episodes!")
        if st.button("➕ Add to Library", use_container_width=True, type="primary"):
            st.session_state.db["shows"].append({"id": show_id, "name": show_name, "watched_episodes": [], "poster_path": s_details.get("poster_path", ""), "first_air_date": s_details.get("first_air_date", ""), "total_episodes": s_details.get("number_of_episodes", 1), "dropped": False})
            save_db()
            st.rerun()
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("❌ Unmark as Watched" if is_watched else "▶ Mark as Watched", use_container_width=True, type="secondary" if is_watched else "primary", key=f"ep_toggle_{show_id}_{ep_code}"):
                mark_episode(show_id, ep_code, not is_watched)
                st.rerun()
        with col_b:
            if st.button("📺 Open Series", use_container_width=True, key=f"ep_open_show_{show_id}"):
                open_dialog("show", id=show_id, name=show_name)
                st.rerun()


@st.dialog("Manage Show")
def manage_show_dialog(show_id, show_name):
    details = fetch_show_bundle(show_id)
    current_show = get_show(show_id)

    watched_list = current_show.get("watched_episodes", []) if current_show else []
    total_eps = (current_show.get("total_episodes") if current_show else None) or details.get("number_of_episodes", 0) or 0

    badges = f'<span class="badge badge-gold">{details.get("status")}</span>'
    if current_show:
        badges += f'<span class="badge">✅ {len(watched_list)}/{total_eps} watched</span>'
    badges += "".join([f'<span class="badge">{g["name"]}</span>' for g in details.get("genres", [])])
    render_apple_tv_header(details.get("backdrop_path"), details.get("poster_path"), show_name, badges)

    if not current_show:
        if st.button("➕ Add to Library", use_container_width=True, type="primary", key=f"add_show_{show_id}"):
            st.session_state.db["shows"].append({"id": show_id, "name": show_name, "watched_episodes": [], "poster_path": details.get("poster_path", ""), "first_air_date": details.get("first_air_date", ""), "total_episodes": details.get("number_of_episodes", 1), "dropped": False})
            save_db()
            st.rerun()
    else:
        is_dropped = current_show.get("dropped", False)
        c1, c2 = st.columns(2)
        with c1:
            if is_dropped:
                if st.button("↺ Restore Show", use_container_width=True, type="primary", key=f"restore_show_{show_id}"):
                    cb_restore_tv(show_id)
                    st.rerun()
            else:
                if st.button("⚰️ Drop Show", use_container_width=True, key=f"drop_show_{show_id}"):
                    cb_drop_tv(show_id)
                    st.rerun()
        with c2:
            if is_dropped:
                if st.button("🗑️ Delete Permanently", use_container_width=True, key=f"del_show_{show_id}"):
                    cb_perm_delete_tv(show_id)
                    close_dialog()
                    st.rerun()

    st.write(details.get("overview", "No overview available."))

    providers = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/watch/providers?api_key={TMDB_KEY}")
    if "AE" in providers.get("results", {}):
        streams = providers["results"]["AE"].get("flatrate", [])
        if streams:
            st.info(f"📱 **Streaming locally:** {', '.join([p['provider_name'] for p in streams])}")

    st.divider()
    st.markdown("#### Episodes")

    if not current_show:
        st.warning("➕ Add this show to your library to track episodes!")

    s_nums = [s["season_number"] for s in details.get("seasons", []) if s["season_number"] > 0]
    if s_nums:
        sel_s = st.selectbox("Select Season", s_nums, key=f"dlg_s_{show_id}")
        for ep in season_episodes(details, show_id, sel_s):
            e_code = f"S{sel_s}E{ep['episode_number']}"
            ep_watched = is_episode_watched(show_id, e_code)
            ep_col1, ep_col2 = st.columns([6, 1])
            with ep_col1:
                st.checkbox(f"**E{ep['episode_number']}.** {ep.get('name', 'Episode')}", value=ep_watched, key=f"chk_dlg_{show_id}_{e_code}", on_change=cb_toggle_episode, args=(show_id, e_code), disabled=(current_show is None))
                if ep_watched:
                    h_log = find_history("tv", show_id, e_code)
                    if h_log:
                        try:
                            st.markdown(
                                f"<div style='font-size: 0.65rem; color: #FFC107; margin-top:-10px; margin-left: 28px; margin-bottom: 8px;'>✅ Watched on {datetime.strptime(h_log['d'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')}</div>",
                                unsafe_allow_html=True)
                        except Exception:
                            pass
            with ep_col2:
                if st.button("ℹ INFO", key=f"inf_btn_ep_{show_id}_{e_code}"):
                    cb_toggle_ep_info(show_id, e_code)

            if st.session_state.get(f"view_info_{show_id}_{e_code}", False):
                with st.container(border=True):
                    if ep.get("still_path"):
                        st.image(f"https://image.tmdb.org/t/p/w500{ep['still_path']}", use_container_width=True)
                    st.caption(f"⭐ {ep.get('vote_average', 0.0)} | **Aired:** {ep.get('air_date', 'N/A')}")
                    st.write(ep.get("overview", "No synopsis available."))

    st.divider()
    st.markdown("#### Top Cast")
    cast_data = fetch_api(f"https://api.themoviedb.org/3/tv/{show_id}/credits?api_key={TMDB_KEY}").get("cast") or []
    show_cast_horizontal(cast_data, key_prefix=f"show_{show_id}", limit=15)
    if st.session_state.get("active_actor"):
        render_inline_actor_pokedex(st.session_state["active_actor"])


@st.dialog("Movie Details")
def show_movie_details(m_id, m_name):
    details = fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}?api_key={TMDB_KEY}")
    current_movie = get_movie(m_id)
    is_watched = is_movie_watched(m_id)
    is_dropped = bool(current_movie.get("dropped", False)) if current_movie else False

    badges = f'<span class="badge badge-gold">{details.get("runtime", 0)} mins</span>'
    if is_watched:
        badges += '<span class="badge">✅ Watched</span>'
    if is_dropped:
        badges += '<span class="badge">⚰️ Dropped</span>'
    badges += "".join([f'<span class="badge">{g["name"]}</span>' for g in details.get("genres", [])])
    render_apple_tv_header(details.get("backdrop_path"), details.get("poster_path"), m_name, badges)

    if not current_movie:
        if st.button("➕ Add to Library", use_container_width=True, type="primary", key=f"add_mov_{m_id}"):
            st.session_state.db["movies"].append({"id": m_id, "name": m_name, "watched": False, "poster_path": details.get("poster_path", ""), "release_date": details.get("release_date", ""), "runtime": details.get("runtime", 0) or 120, "dropped": False})
            save_db()
            st.rerun()
    else:
        c1, c2 = st.columns(2)
        with c1:
            if is_dropped:
                if st.button("↺ Restore Movie", use_container_width=True, type="primary", key=f"restore_mov_{m_id}"):
                    cb_restore_mov(m_id)
                    st.rerun()
            else:
                if st.button("⚰️ Drop Movie", use_container_width=True, key=f"drop_mov_{m_id}"):
                    cb_drop_mov(m_id)
                    st.rerun()
        with c2:
            if is_dropped:
                if st.button("🗑️ Delete Permanently", use_container_width=True, key=f"del_mov_{m_id}"):
                    cb_perm_delete_mov(m_id)
                    close_dialog()
                    st.rerun()

    st.write(details.get("overview", "No synopsis available."))

    if is_watched:
        h_log = find_history("movie", m_id)
        if h_log:
            try:
                st.success(f"✅ **Watched on:** {datetime.strptime(h_log['d'], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y at %I:%M %p')}")
            except Exception:
                pass
            render_journal_editor(h_log, f"m_{m_id}")

    st.divider()
    st.markdown("#### Top Cast")
    cast_data = fetch_api(f"https://api.themoviedb.org/3/movie/{m_id}/credits?api_key={TMDB_KEY}").get("cast") or []
    show_cast_horizontal(cast_data, key_prefix=f"mov_{m_id}", limit=15)
    if st.session_state.get("active_actor"):
        render_inline_actor_pokedex(st.session_state["active_actor"])

    st.divider()
    if current_movie and not is_dropped:
        if st.button("❌ Unmark as Watched" if is_watched else "▶ Mark as Watched", use_container_width=True, type="secondary" if is_watched else "primary", key=f"mov_toggle_{m_id}"):
            mark_movie(m_id, not is_watched)
            st.rerun()


# =====================================================================
# SINGLE GLOBAL DIALOG ROUTER
# Runs before the tabs so there is exactly one dialog per script run,
# no matter which tab (or which poster) requested it.
# =====================================================================
# Set to True to trace dialog opens with a toast. If you click a poster and
# see NO toast, the click never reached Python. If you see the toast but no
# modal, Python fired and the modal is being lost on the frontend.
DEBUG_DIALOG = True

# Streamlit renders at most one dialog per script run. Everything now goes
# through this guard, so a second attempt in the same run is dropped rather
# than silently clobbering the first.
DIALOG_GUARD = {"used": False, "last": None}


def show_dialog_once(fn, *args, **kwargs):
    """Open a dialog immediately, unless one already opened this run."""
    if DIALOG_GUARD["used"]:
        return False
    DIALOG_GUARD["used"] = True
    DIALOG_GUARD["last"] = f"{fn.__name__}{args}"
    fn(*args, **kwargs)
    return True


queue_pending_recaps()

_d = st.session_state.dialog
if _d:
    kind = _d.get("kind")
    if kind == "episode":
        show_dialog_once(show_episode_details, _d["id"], _d["name"], _d["code"])
    elif kind == "show":
        show_dialog_once(manage_show_dialog, _d["id"], _d["name"])
    elif kind == "movie":
        show_dialog_once(show_movie_details, _d["id"], _d["name"])
    elif kind == "recap_month":
        show_dialog_once(show_monthly_recap_dialog, _d["month_key"], _d["title"], _d["stats"], _d["recap_id"])
    elif kind == "recap_year":
        show_dialog_once(show_yearly_recap_dialog, _d["year"], _d["y_tv"], _d["y_mov"], _d["recap_id"])
    # cleared here so dismissing via the X does not re-open it next run
    st.session_state.dialog = None


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

    fifteen_days_ago = get_dubai_time() - timedelta(days=15)

    recent_active_ids = set()
    for h in st.session_state.db.get("history", []):
        try:
            if datetime.strptime(h.get("d", "2000-01-01 12:00:00"), '%Y-%m-%d %H:%M:%S') >= fifteen_days_ago:
                recent_active_ids.add((h.get("t"), str(h.get("i"))))
        except Exception:
            pass

    if next_filter == "📺 Series":
        needs_heal_next = False
        up_next_tv = []
        for show in st.session_state.db["shows"]:
            if show.get("dropped", False):
                continue
            w_eps = len(show.get("watched_episodes", []))
            t_eps = show.get("total_episodes", 1)

            details = fetch_show_bundle(show['id'])
            tmdb_total = details.get("number_of_episodes", t_eps)

            if tmdb_total != t_eps and tmdb_total > 0:
                show["total_episodes"] = tmdb_total
                needs_heal_next = True

            if w_eps >= tmdb_total and tmdb_total > 0:
                continue

            watched_set = set(show.get("watched_episodes", []))
            highest_s, highest_e = -1, -1
            for code in watched_set:
                try:
                    s_num, e_num = int(code.split('E')[0].replace('S', '')), int(code.split('E')[1])
                    if s_num > highest_s or (s_num == highest_s and e_num > highest_e):
                        highest_s, highest_e = s_num, e_num
                except Exception:
                    pass

            seasons = [s for s in details.get("seasons", []) if s["season_number"] > 0]
            start_s = max(1, highest_s)

            candidate_after_max = None
            for s_info in [s for s in seasons if s["season_number"] >= start_s]:
                for ep in season_episodes(details, show['id'], s_info['season_number']):
                    ep_code = f"S{s_info['season_number']}E{ep['episode_number']}"
                    air_date = str(ep.get("air_date") or "").strip()
                    if ep_code not in watched_set and air_date and air_date <= TODAY:
                        s_n, e_n = s_info['season_number'], ep['episode_number']
                        if s_n > highest_s or (s_n == highest_s and e_n > highest_e):
                            candidate_after_max = {"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date, "is_rec": ("s", str(show["id"])) in recent_active_ids, "is_skipped": False}
                            break
                if candidate_after_max:
                    break

            if candidate_after_max:
                up_next_tv.append(candidate_after_max)
            else:
                candidate_skipped = None
                for s_info in [s for s in seasons if s["season_number"] < start_s]:
                    for ep in season_episodes(details, show['id'], s_info['season_number']):
                        ep_code = f"S{s_info['season_number']}E{ep['episode_number']}"
                        air_date = str(ep.get("air_date") or "").strip()
                        if ep_code not in watched_set and air_date and air_date <= TODAY:
                            candidate_skipped = {"item": show, "details": details, "ep": ep, "code": ep_code, "date": air_date, "is_rec": False, "is_skipped": True}
                            break
                    if candidate_skipped:
                        break
                if candidate_skipped:
                    up_next_tv.append(candidate_skipped)

        if needs_heal_next:
            save_db()

        if next_sort == "Alphabetical":
            up_next_tv.sort(key=lambda x: x["item"]["name"].lower())
        elif next_sort == "Release Date":
            up_next_tv.sort(key=lambda x: x["date"] or "1900-01-01", reverse=True)
        elif next_sort == "Smart Priority":
            up_next_tv.sort(key=lambda x: (not x.get("is_skipped", False), x["is_rec"], x["date"] or "1900-01-01"), reverse=True)

        if not up_next_tv:
            st.info("You are completely caught up on series! 🎉")
        else:
            hero = up_next_tv[0]
            h_show, h_details, h_ep, h_code = hero["item"], hero["details"], hero["ep"], hero["code"]
            h_bg = f"https://image.tmdb.org/t/p/w780{h_details.get('backdrop_path')}" if h_details.get('backdrop_path') else f"https://image.tmdb.org/t/p/w342{h_show.get('poster_path')}"

            st.markdown(
                f'<div style="position: relative; border-radius: 12px; overflow: hidden; margin-bottom: 5px; box-shadow: 0 8px 24px rgba(0,0,0,0.6); height: 220px; margin-top: 10px;">'
                f'<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: url(\'{h_bg}\'); background-size: cover; background-position: center; filter: brightness(0.6);"></div>'
                f'<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(to top, rgba(15,17,22,1) 0%, rgba(15,17,22,0.2) 60%, rgba(15,17,22,0) 100%);"></div>'
                f'<div style="position: absolute; bottom: 20px; left: 20px; right: 20px;">'
                f'<div style="color: #FFC107; font-weight: 800; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Up Next</div>'
                f'<div style="color: white; font-weight: 900; font-size: 1.8rem; line-height: 1.1; text-shadow: 0 2px 8px rgba(0,0,0,0.8); margin-bottom: 5px;">{h_show["name"]}</div>'
                f'<div style="color: #ccc; font-weight: 600; font-size: 0.85rem;">{h_code} • {h_ep.get("name", "Episode")}</div>'
                f'</div>'
                f'</div>', unsafe_allow_html=True)

            c_h1, c_h2 = st.columns([7, 3])
            with c_h1:
                st.button("▶ Resume Watching", key=f"hero_w_tv_{h_show['id']}", on_click=cb_watch_tv_feed, args=(h_show['id'], h_show['name'], h_code), use_container_width=True, type="primary")
            with c_h2:
                if st.button("ℹ INFO", key=f"hero_i_tv_{h_show['id']}", use_container_width=True):
                    show_dialog_once(show_episode_details, h_show['id'], h_show['name'], h_code)

            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

            limit = st.session_state.next_tv_limit
            visible = up_next_tv[:limit]
            for i in range(1, len(visible), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        if idx < len(visible):
                            item = visible[idx]
                            show, details, ep_code = item["item"], item["details"], item["code"]
                            if poster_button(show["name"], show.get("poster_path") or details.get('poster_path'),
                                             key=f"n_i_tv_{show['id']}_{ep_code}_{idx}", subtitle=ep_code):
                                show_dialog_once(show_episode_details, show['id'], show['name'], ep_code)
                        else:
                            st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)

            if len(up_next_tv) > st.session_state.next_tv_limit:
                if st.button("Load More Series", use_container_width=True, key="load_more_next_tv"):
                    st.session_state.next_tv_limit += 30
                    st.rerun()

    else:
        up_next_mov = []
        for m in st.session_state.db["movies"]:
            if m.get("dropped", False):
                continue
            if not is_movie_watched(m["id"]):
                r_date = str(m.get("release_date") or "").strip()
                if r_date and r_date <= TODAY:
                    up_next_mov.append({"item": m, "date": r_date, "is_rec": ("m", str(m["id"])) in recent_active_ids})

        if next_sort == "Alphabetical":
            up_next_mov.sort(key=lambda x: x["item"]["name"].lower())
        elif next_sort == "Release Date":
            up_next_mov.sort(key=lambda x: x["date"] or "1900-01-01", reverse=True)
        elif next_sort == "Smart Priority":
            up_next_mov.sort(key=lambda x: (x["is_rec"], x["date"] or "1900-01-01"), reverse=True)

        if not up_next_mov:
            st.info("You have no unwatched movies left! 🎉")
        else:
            limit = st.session_state.next_mov_limit
            visible = up_next_mov[:limit]
            for i in range(0, len(visible), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        if idx < len(visible):
                            m = visible[idx]["item"]
                            if poster_button(m["name"], m.get('poster_path'), key=f"n_i_mov_{m['id']}_{idx}"):
                                show_dialog_once(show_movie_details, m['id'], m['name'])
                        else:
                            st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)

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
        needs_heal_soon = False
        soon_tv = []
        for show in st.session_state.db["shows"]:
            if show.get("dropped", False):
                continue
            w_eps = len(show.get("watched_episodes", []))
            t_eps = show.get("total_episodes", 1)

            details = fetch_show_bundle(show['id'])
            tmdb_total = details.get("number_of_episodes", t_eps)

            if tmdb_total != t_eps and tmdb_total > 0:
                show["total_episodes"] = tmdb_total
                needs_heal_soon = True

            found_next = False
            watched_set = set(show.get("watched_episodes", []))
            for s_info in [s for s in details.get("seasons", []) if s["season_number"] > 0]:
                if found_next:
                    break
                for ep in season_episodes(details, show['id'], s_info['season_number']):
                    ep_code = f"S{s_info['season_number']}E{ep['episode_number']}"
                    e_air_date = str(ep.get("air_date") or "").strip()
                    if ep_code not in watched_set and e_air_date and e_air_date > TODAY:
                        soon_tv.append({"item": show, "details": details, "ep": ep, "code": ep_code, "date": e_air_date})
                        found_next = True
                        break

        if needs_heal_soon:
            save_db()

        if soon_sort == "Alphabetical":
            soon_tv.sort(key=lambda x: x["item"]["name"].lower())
        else:
            soon_tv.sort(key=lambda x: x["date"] or "2099-01-01")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if not soon_tv:
            st.info("No upcoming episodes scheduled yet.")
        else:
            limit = st.session_state.soon_tv_limit
            visible = soon_tv[:limit]
            for i in range(0, len(visible), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        if idx < len(visible):
                            item = visible[idx]
                            show, details, ep_code = item["item"], item["details"], item["code"]
                            if poster_button(show["name"], show.get("poster_path") or details.get('poster_path'),
                                             key=f"s_i_tv_{show['id']}_{ep_code}_{idx}",
                                             subtitle=f"{ep_code} • {calc_time_remaining(item['date'])}"):
                                show_dialog_once(show_episode_details, show['id'], show['name'], ep_code)
                        else:
                            st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)

            if len(soon_tv) > st.session_state.soon_tv_limit:
                if st.button("Load More Upcoming Series", use_container_width=True, key="load_more_soon_tv"):
                    st.session_state.soon_tv_limit += 30
                    st.rerun()

    else:
        soon_mov = []
        for m in st.session_state.db["movies"]:
            if m.get("dropped", False) or is_movie_watched(m["id"]):
                continue
            r_date = str(m.get("release_date") or "").strip()
            if r_date and r_date > TODAY:
                soon_mov.append({"item": m, "date": r_date})

        if soon_sort == "Alphabetical":
            soon_mov.sort(key=lambda x: x["item"]["name"].lower())
        else:
            soon_mov.sort(key=lambda x: x["date"] or "2099-01-01")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if not soon_mov:
            st.info("No upcoming movies scheduled yet.")
        else:
            limit = st.session_state.soon_mov_limit
            visible = soon_mov[:limit]
            for i in range(0, len(visible), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        if idx < len(visible):
                            item = visible[idx]
                            m = item["item"]
                            if poster_button(m["name"], m.get('poster_path'), key=f"s_i_mov_{m['id']}_{idx}",
                                             subtitle=calc_time_remaining(item["date"])):
                                show_dialog_once(show_movie_details, m['id'], m['name'])
                        else:
                            st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)

            if len(soon_mov) > st.session_state.soon_mov_limit:
                if st.button("Load More Upcoming Movies", use_container_width=True, key="load_more_soon_mov"):
                    st.session_state.soon_mov_limit += 30
                    st.rerun()

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

        safe_query = requests.utils.quote(str(search_query))
        results = fetch_api(f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_KEY}&query={safe_query}").get("results", [])

        if results:
            search_results = results[:30]
            for i in range(0, len(search_results), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        if idx < len(search_results):
                            item = search_results[idx]
                            item_id = item["id"]
                            title = item.get("name") if search_type == "TV Shows" else item.get("title")
                            if poster_button(title, item.get("poster_path"), key=f"inf_{item_id}_{idx}"):
                                show_dialog_once(manage_show_dialog if search_type == "TV Shows" else show_movie_details, item_id, title)
                        else:
                            st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)
    else:
        genre_options = ["🔥 Trending", "🤣 Comedy", "💥 Action", "🐉 Sci-Fi", "🔪 Thriller", "👻 Horror"]
        selected_genre = st.radio("Filters", genre_options, label_visibility="collapsed", horizontal=True)
        st.divider()

        def render_carousel(title, items, c_type):
            if not items:
                return
            st.markdown(f"<h5 style='margin-bottom:5px;'>{title}</h5>", unsafe_allow_html=True)
            limit = st.session_state.c_limits.get(title, 10)
            render_items, show_load_more = items[:limit], limit < len(items)
            cols = st.columns(len(render_items) + (1 if show_load_more else 0))

            safe_title = "".join(e for e in title if e.isalnum())

            for idx, item in enumerate(render_items):
                with cols[idx]:
                    i_title = item.get("name") if c_type == "tv" else item.get("title")
                    item_id = item["id"]
                    if poster_button(i_title, item.get("poster_path"), key=f"c_inf_{safe_title}_{item_id}_{idx}", marker="carousel-marker"):
                        show_dialog_once(manage_show_dialog if c_type == "tv" else show_movie_details, item_id, i_title)

            if show_load_more:
                with cols[-1]:
                    st.markdown('<span class="carousel-marker"></span><div style="height: 60px;"></div>', unsafe_allow_html=True)
                    if st.button("＋ More", key=f"c_more_{safe_title}", use_container_width=True):
                        st.session_state.c_limits[title] = limit + 10
                        st.rerun()

        if selected_genre == "🔥 Trending":
            if not st.session_state.rec_show:
                watched_tv = [s for s in st.session_state.db.get("shows", []) if s.get("watched_episodes")]
                if watched_tv:
                    st.session_state.rec_show = random.choice(watched_tv)
            if st.session_state.rec_show:
                recs = fetch_api(f"https://api.themoviedb.org/3/tv/{st.session_state.rec_show['id']}/recommendations?api_key={TMDB_KEY}")
                if recs.get("results"):
                    render_carousel(f"Because you watched {st.session_state.rec_show['name']}", recs["results"], "tv")
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
            genre_map_tv = {"🤣 Comedy": 35, "💥 Action": 10759, "🐉 Sci-Fi": 10765, "🔪 Thriller": 9648, "👻 Horror": 9648}
            genre_map_mov = {"🤣 Comedy": 35, "💥 Action": 28, "🐉 Sci-Fi": 878, "🔪 Thriller": 53, "👻 Horror": 27}
            tv_g = fetch_api(f"https://api.themoviedb.org/3/discover/tv?api_key={TMDB_KEY}&with_genres={genre_map_tv[selected_genre]}&sort_by=popularity.desc")
            mov_g = fetch_api(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_KEY}&with_genres={genre_map_mov[selected_genre]}&sort_by=popularity.desc")
            render_carousel(f"Top {selected_genre} Series", tv_g.get("results", []), "tv")
            render_carousel(f"Top {selected_genre} Movies", mov_g.get("results", []), "movie")

# ==========================================
# TAB 4: TV LIBRARY
# ==========================================
with t_tv:
    st.markdown("<h3 class='tab-title'>My TV Collection</h3>", unsafe_allow_html=True)
    if "tv_tab" not in st.session_state:
        st.session_state.tv_tab = "WATCHLIST"

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Watchlist", type="primary" if st.session_state.tv_tab == "WATCHLIST" else "secondary", use_container_width=True, key="tv_wl"):
        st.session_state.tv_tab = "WATCHLIST"
        st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.tv_tab == "UPCOMING" else "secondary", use_container_width=True, key="tv_up"):
        st.session_state.tv_tab = "UPCOMING"
        st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.tv_tab == "WATCHED" else "secondary", use_container_width=True, key="tv_wd"):
        st.session_state.tv_tab = "WATCHED"
        st.rerun()
    if c4.button("Dropped", type="primary" if st.session_state.tv_tab == "DROPPED" else "secondary", use_container_width=True, key="tv_dr"):
        st.session_state.tv_tab = "DROPPED"
        st.rerun()

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<span class="search-container-hook"></span>', unsafe_allow_html=True)
        lib_search_tv = st_keyup("Search Library", debounce=500, key=f"lib_sq_tv_{st.session_state.lib_tv_reset_ctr}", placeholder="Filter shows...", label_visibility="collapsed")
        if lib_search_tv:
            st.markdown('<span class="clear-btn-hook"></span>', unsafe_allow_html=True)
            st.button("✖", key=f"clr_lib_tv_{st.session_state.lib_tv_reset_ctr}", on_click=cb_clear_lib_tv)

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    tv_sort = st.selectbox("Sort Library by:", ["Release Date", "Alphabetical", "Recently Added"], label_visibility="collapsed", key="sort_tv_lib")
    st.divider()

    shows = st.session_state.db.get("shows", [])
    if not shows:
        st.info("Your TV library is empty.")
    else:
        display_shows = []
        for show in shows:
            if lib_search_tv and lib_search_tv.lower() not in show["name"].lower():
                continue

            air_date = str(show.get("first_air_date") or "").strip()
            t_eps = show.get("total_episodes", 1)
            w_eps = len(show.get("watched_episodes", []))

            is_upcoming = bool(air_date and air_date > TODAY)
            is_completed = (w_eps >= t_eps and t_eps > 0)
            is_dropped = show.get("dropped", False)

            if st.session_state.tv_tab == "DROPPED" and is_dropped:
                display_shows.append((show, t_eps, w_eps))
            elif not is_dropped:
                if st.session_state.tv_tab == "WATCHED" and is_completed:
                    display_shows.append((show, t_eps, w_eps))
                elif st.session_state.tv_tab == "UPCOMING" and is_upcoming and not is_completed:
                    display_shows.append((show, t_eps, w_eps))
                elif st.session_state.tv_tab == "WATCHLIST" and not is_upcoming and not is_completed:
                    display_shows.append((show, t_eps, w_eps))

        if tv_sort == "Alphabetical":
            display_shows.sort(key=lambda x: x[0]['name'].lower())
        elif tv_sort == "Release Date":
            is_upc = (st.session_state.tv_tab == "UPCOMING")
            fallback = '2099-01-01' if is_upc else '1900-01-01'
            display_shows.sort(key=lambda x: x[0].get('first_air_date') or fallback, reverse=not is_upc)
        elif tv_sort == "Recently Added":
            display_shows.reverse()

        if not display_shows:
            if lib_search_tv:
                st.info(f"No shows match '{lib_search_tv}' in this tab.")
            else:
                st.info(f"Your {st.session_state.tv_tab.lower()} is currently empty.")
        else:
            total_tv_display = len(display_shows)
            paginated_shows = display_shows[:st.session_state.tv_lib_limit]

            for i in range(0, len(paginated_shows), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        if idx < len(paginated_shows):
                            show, t_eps, w_eps = paginated_shows[idx]
                            prog_val = min(w_eps / t_eps, 1.0) if t_eps > 0 else 0.0
                            if poster_button(show["name"], show.get("poster_path"), key=f"s_mgr_{show['id']}_{idx}", progress_pct=prog_val):
                                show_dialog_once(manage_show_dialog, show['id'], show['name'])
                        else:
                            st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)

            if total_tv_display > st.session_state.tv_lib_limit:
                if st.button("Load 50 More", use_container_width=True, key="load_more_tv_lib"):
                    st.session_state.tv_lib_limit += 50
                    st.rerun()

# ==========================================
# TAB 5: MOVIE LIBRARY
# ==========================================
with t_movies:
    st.markdown("<h3 class='tab-title'>My Movies</h3>", unsafe_allow_html=True)
    if "mov_tab" not in st.session_state:
        st.session_state.mov_tab = "WATCHLIST"

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Watchlist", type="primary" if st.session_state.mov_tab == "WATCHLIST" else "secondary", use_container_width=True, key="m_wl"):
        st.session_state.mov_tab = "WATCHLIST"
        st.rerun()
    if c2.button("Upcoming", type="primary" if st.session_state.mov_tab == "UPCOMING" else "secondary", use_container_width=True, key="m_up"):
        st.session_state.mov_tab = "UPCOMING"
        st.rerun()
    if c3.button("Watched", type="primary" if st.session_state.mov_tab == "WATCHED" else "secondary", use_container_width=True, key="m_wd"):
        st.session_state.mov_tab = "WATCHED"
        st.rerun()
    if c4.button("Dropped", type="primary" if st.session_state.mov_tab == "DROPPED" else "secondary", use_container_width=True, key="m_dr"):
        st.session_state.mov_tab = "DROPPED"
        st.rerun()

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<span class="search-container-hook"></span>', unsafe_allow_html=True)
        lib_search_mov = st_keyup("Search Library", debounce=500, key=f"lib_sq_mov_{st.session_state.lib_mov_reset_ctr}", placeholder="Filter movies...", label_visibility="collapsed")
        if lib_search_mov:
            st.markdown('<span class="clear-btn-hook"></span>', unsafe_allow_html=True)
            st.button("✖", key=f"clr_lib_mov_{st.session_state.lib_mov_reset_ctr}", on_click=cb_clear_lib_mov)

    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    mov_sort = st.selectbox("Sort Library by:", ["Release Date", "Alphabetical", "Recently Added"], label_visibility="collapsed", key="sort_mov_lib")
    st.divider()

    movies = st.session_state.db.get("movies", [])
    if not movies:
        st.info("Your Movie library is empty.")
    else:
        display_movies = []
        for m in movies:
            if lib_search_mov and lib_search_mov.lower() not in m["name"].lower():
                continue

            r_date = str(m.get("release_date") or "").strip()
            m_watched = is_movie_watched(m["id"])
            is_dropped = bool(m.get("dropped", False))
            is_upcoming = bool(r_date and r_date > TODAY)

            if st.session_state.mov_tab == "DROPPED" and is_dropped:
                display_movies.append((m, m_watched))
            elif not is_dropped:
                if st.session_state.mov_tab == "WATCHED" and m_watched:
                    display_movies.append((m, m_watched))
                elif st.session_state.mov_tab == "UPCOMING" and is_upcoming and not m_watched:
                    display_movies.append((m, m_watched))
                elif st.session_state.mov_tab == "WATCHLIST" and not is_upcoming and not m_watched:
                    display_movies.append((m, m_watched))

        if mov_sort == "Alphabetical":
            display_movies.sort(key=lambda x: x[0]['name'].lower())
        elif mov_sort == "Release Date":
            is_upc = (st.session_state.mov_tab == "UPCOMING")
            fallback = '2099-01-01' if is_upc else '1900-01-01'
            display_movies.sort(key=lambda x: x[0].get('release_date') or fallback, reverse=not is_upc)
        elif mov_sort == "Recently Added":
            display_movies.reverse()

        if not display_movies:
            if lib_search_mov:
                st.info(f"No movies match '{lib_search_mov}' in this tab.")
            else:
                st.info(f"Your {st.session_state.mov_tab.lower()} is currently empty.")
        else:
            total_mov_display = len(display_movies)
            paginated_movies = display_movies[:st.session_state.mov_lib_limit]

            for i in range(0, len(paginated_movies), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    with cols[j]:
                        if idx < len(paginated_movies):
                            m, m_watched = paginated_movies[idx]
                            if poster_button(m["name"], m.get("poster_path"), key=f"m_mgr_{m['id']}_{idx}",
                                             progress_pct=1.0 if m_watched else -1.0):
                                show_dialog_once(show_movie_details, m['id'], m['name'])
                        else:
                            st.markdown('<span class="grid-3-col"></span>', unsafe_allow_html=True)

            if total_mov_display > st.session_state.mov_lib_limit:
                if st.button("Load 50 More", use_container_width=True, key="load_more_mov_lib"):
                    st.session_state.mov_lib_limit += 50
                    st.rerun()

# ==========================================
# TAB 6: PROFILE STATS, GRAPHS & IMPORT
# ==========================================
with t_profile:
    st.markdown("<h3 class='tab-title'>Control Center</h3>", unsafe_allow_html=True)
    t_prof_stats, t_prof_health, t_prof_graphs, t_prof_hist, t_prof_recaps, t_prof_set = st.tabs(["Stats", "Health", "Graphs", "Journal", "Recaps", "Import"])

    history_sorted = sorted(st.session_state.db.get("history", []), key=lambda x: x.get("d", "2000-01-01 12:00:00"), reverse=True)

    with t_prof_stats:
        total_tv_mins = 0
        total_episodes_watched = 0
        total_mov_mins = 0
        total_movies_watched = 0
        shows = st.session_state.db.get("shows", [])

        dropped_shows = sum(1 for s in shows if s.get("dropped", False))

        for show in shows:
            w_eps = len(show.get("watched_episodes", []))
            total_episodes_watched += w_eps
            total_tv_mins += (w_eps * 45)

        for m in st.session_state.db["movies"]:
            if m.get("watched", False):
                total_mov_mins += m.get("runtime", 120) or 120
                total_movies_watched += 1

        total_mins = total_tv_mins + total_mov_mins
        months = total_mins // 43800
        days = (total_mins % 43800) // 1440
        hours = (total_mins % 1440) // 60

        completed_shows = sum(1 for s in shows if not s.get("dropped") and len(s.get("watched_episodes", [])) >= s.get("total_episodes", 1) and s.get("total_episodes", 1) > 0)
        started_shows = sum(1 for s in shows if not s.get("dropped") and 0 < len(s.get("watched_episodes", [])) < s.get("total_episodes", 1))

        tv_ratings = [h["r"] for h in history_sorted if h["t"] == "s" and h.get("r", 0) > 0]
        mov_ratings = [h["r"] for h in history_sorted if h["t"] == "m" and h.get("r", 0) > 0]
        avg_tv_r = round(sum(tv_ratings) / len(tv_ratings), 1) if tv_ratings else 0.0
        avg_mov_r = round(sum(mov_ratings) / len(mov_ratings), 1) if mov_ratings else 0.0

        plat_counts, feel_counts, date_counts = {}, {}, {}
        night_owl_count = 0
        for h in history_sorted:
            if h.get("p") and h.get("p") != "None":
                plat_counts[h["p"]] = plat_counts.get(h["p"], 0) + 1
            if h.get("f") and h.get("f") != "None":
                feel_counts[h["f"]] = feel_counts.get(h["f"], 0) + 1
            try:
                dt = datetime.strptime(h["d"], "%Y-%m-%d %H:%M:%S")
                if 1 <= dt.hour <= 5:
                    night_owl_count += 1
                date_counts[dt.date()] = date_counts.get(dt.date(), 0) + 1
            except Exception:
                pass

        top_plat_global = max(plat_counts, key=plat_counts.get) if plat_counts else "N/A"
        top_feel_global = max(feel_counts, key=feel_counts.get) if feel_counts else "N/A"
        max_binge_day = max(date_counts.values()) if date_counts else 0

        flairs = []
        if night_owl_count >= 10:
            flairs.append("🦉 Night Owl")
        if max_binge_day >= 6:
            flairs.append("🍿 Marathoner")
        if completed_shows >= 10:
            flairs.append("👑 Completionist")
        if not flairs:
            flairs.append("🌱 Newcomer")

        st.markdown("#### User Flair")
        st.markdown("".join([f'<span style="background: rgba(255,255,255,0.1); color: #fff; padding: 4px 12px; border-radius: 16px; font-size: 0.75rem; font-weight: 700; margin-right: 8px; border: 1px solid rgba(255,255,255,0.1);">{f}</span>' for f in flairs]), unsafe_allow_html=True)
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        st.markdown(
            f'<div style="display: flex; gap: 10px; margin-bottom: 10px; margin-top: 10px;">'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 1.8rem; font-weight: 800; color: #FFC107; line-height: 1;">{months}</div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Months</div></div>'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 1.8rem; font-weight: 800; color: #FFC107; line-height: 1;">{days}</div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Days</div></div>'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 1.8rem; font-weight: 800; color: #FFC107; line-height: 1;">{hours}</div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Hours</div></div>'
            f'</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="display: flex; gap: 10px; margin-bottom: 10px;">'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1;">{total_episodes_watched:,}</div>'
            f'<div style="font-size: 0.75rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Episodes</div></div>'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1;">{total_movies_watched:,}</div>'
            f'<div style="font-size: 0.75rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Movies</div></div>'
            f'</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="display: flex; gap: 10px; margin-bottom: 10px;">'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 1.4rem; font-weight: 800; color: #FFC107; line-height: 1;">{completed_shows} <span style="font-size:0.8rem; color:#aaa;">/ {started_shows}</span></div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Shows Finished / Active</div></div>'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 1.4rem; font-weight: 800; color: #FFC107; line-height: 1;">{avg_tv_r} <span style="font-size:0.8rem; color:#aaa;">/ {avg_mov_r}</span></div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Avg TV / Movie ⭐</div></div>'
            f'</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="display: flex; gap: 10px; margin-bottom: 10px;">'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 1.1rem; font-weight: 800; color: #FFC107; line-height: 1.2;">{top_plat_global}</div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Top Platform</div></div>'
            f'<div style="flex: 1; background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">'
            f'<div style="font-size: 1.1rem; font-weight: 800; color: #FFC107; line-height: 1.2;">{top_feel_global}</div>'
            f'<div style="font-size: 0.65rem; color: #aaa; text-transform: uppercase; font-weight: 600; margin-top: 4px;">Signature Vibe</div></div>'
            f'</div>', unsafe_allow_html=True)

    with t_prof_health:
        total_ep_db = 0
        watched_ep_db = 0
        eps_last_7 = 0
        mins_last_30 = 0
        thirty_days_ago = get_dubai_time() - timedelta(days=30)
        seven_days_ago = get_dubai_time() - timedelta(days=7)

        watched_dates = set()
        for h in history_sorted:
            try:
                h_dt = datetime.strptime(h["d"], "%Y-%m-%d %H:%M:%S")
                watched_dates.add(h_dt.date())
                if h_dt >= thirty_days_ago:
                    mins_last_30 += 45 if h["t"] == "s" else 120
                if h_dt >= seven_days_ago and h["t"] == "s":
                    eps_last_7 += 1
            except Exception:
                pass

        daily_avg_mins = mins_last_30 / 30.0 if mins_last_30 > 0 else 1.0

        streak = 0
        curr_d = get_dubai_time().date()
        if curr_d not in watched_dates:
            curr_d -= timedelta(days=1)
        while curr_d in watched_dates:
            streak += 1
            curr_d -= timedelta(days=1)

        stagnant_shows, almost_finished = [], []
        for s in st.session_state.db["shows"]:
            if s.get("dropped", False):
                continue
            t_eps = s.get("total_episodes", 1)
            w_eps = len(s.get("watched_episodes", []))
            total_ep_db += t_eps
            watched_ep_db += w_eps
            rem = t_eps - w_eps

            if 0 < rem <= 3:
                almost_finished.append({"name": s["name"], "rem": rem})

            if 0 < w_eps < t_eps:
                s_hist = [h for h in history_sorted if h["t"] == "s" and str(h["i"]) == str(s["id"])]
                if s_hist:
                    try:
                        if (get_dubai_time() - datetime.strptime(s_hist[0]["d"], "%Y-%m-%d %H:%M:%S")).days > 90:
                            stagnant_shows.append({"name": s["name"], "id": s["id"]})
                    except Exception:
                        pass

        total_mov_db = len(st.session_state.db["movies"])
        watched_mov_db = sum(1 for m in st.session_state.db["movies"] if m.get("watched") and not m.get("dropped"))
        backlog_mins = ((total_ep_db - watched_ep_db) * 45) + ((total_mov_db - watched_mov_db) * 120)
        days_to_clear = int(backlog_mins / daily_avg_mins) if daily_avg_mins > 0 else 999
        total_items = total_ep_db + total_mov_db
        completion_pct = int(((watched_ep_db + watched_mov_db) / total_items) * 100) if total_items > 0 else 0

        st.markdown("#### Clearance Dashboard")
        st.progress(min(completion_pct, 100) / 100.0)
        st.caption(f"**Total Active Library Completion:** {completion_pct}%")

        c1, c2, c3 = st.columns(3)
        for col, val, unit, label in [
            (c1, days_to_clear, "Days", "To Clear Backlog"),
            (c2, eps_last_7, "Eps", "Binge Velocity"),
            (c3, streak, "Days", "Current Streak"),
        ]:
            with col:
                st.markdown(
                    f'<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 5px; text-align: center; margin-top: 15px;">'
                    f'<div style="font-size: 1.5rem; font-weight: 800; color: #FFC107;">{val} <span style="font-size:0.7rem; color:#aaa;">{unit}</span></div>'
                    f'<div style="font-size: 0.60rem; color: #aaa; text-transform: uppercase; font-weight:700;">{label}</div>'
                    f'</div>', unsafe_allow_html=True)

        if almost_finished:
            st.markdown("#### 🏁 Almost Finished")
            for s in almost_finished[:5]:
                st.markdown(f"• **{s['name']}** *(Only {s['rem']} eps left!)*")

        if stagnant_shows:
            st.markdown("#### ⚠️ Stagnant Stock Warning")
            st.info(f"You have {len(stagnant_shows)} abandoned shows in your inventory. Consider dropping them to clean your backlog.")
            for s in stagnant_shows[:5]:
                st.markdown(f"• **{s['name']}**")

    with t_prof_graphs:
        c_tab1, c_tab2, c_tab3, c_tab4, c_tab5, c_tab6 = st.tabs(["Activity", "DNA", "Heatmap", "Platforms", "Vibe", "Ratings"])

        with c_tab1:
            st.markdown("**📺 TV Series Activity**")
            analytics = st.session_state.db.get("analytics", {})
            last_12_months = []
            try:
                for i in range(11, -1, -1):
                    last_12_months.append(get_dubai_time() - pd.DateOffset(months=i))
            except Exception:
                for i in range(11, -1, -1):
                    last_12_months.append(get_dubai_time() - timedelta(days=30 * i))
            data_tv, data_mov = [], []
            for dt in last_12_months:
                m_key, label = dt.strftime('%Y-%m'), dt.strftime('%b \'%y')
                stats = analytics.get(m_key, {"tv": 0, "movie": 0})
                data_tv.append({"Month": label, "Episodes": stats["tv"]})
                data_mov.append({"Month": label, "Movies": stats["movie"]})
            df_tv, df_mov = pd.DataFrame(data_tv), pd.DataFrame(data_mov)

            if not df_tv.empty and df_tv["Episodes"].sum() > 0:
                chart_tv = alt.Chart(df_tv).mark_bar(color="#FFC107", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x=alt.X("Month:N", title=None, axis=alt.Axis(labelAngle=-90, labelColor="#aaa", labelFontSize=9), sort=None), y=alt.Y("Episodes:Q", title=None, axis=alt.Axis(labelColor="#aaa")))
                text_tv = chart_tv.mark_text(align='center', baseline='bottom', dy=-5, color='#EDEDED', fontSize=10, fontWeight='bold').encode(text='Episodes:Q')
                st.altair_chart((chart_tv + text_tv).properties(height=200), use_container_width=True)
            else:
                st.info("No series history available.")

            st.markdown("**🎬 Movies Activity**")
            if not df_mov.empty and df_mov["Movies"].sum() > 0:
                chart_mov = alt.Chart(df_mov).mark_bar(color="#555555", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x=alt.X("Month:N", title=None, axis=alt.Axis(labelAngle=-90, labelColor="#aaa", labelFontSize=9), sort=None), y=alt.Y("Movies:Q", title=None, axis=alt.Axis(labelColor="#aaa")))
                text_mov = chart_mov.mark_text(align='center', baseline='bottom', dy=-5, color='#EDEDED', fontSize=10, fontWeight='bold').encode(text='Movies:Q')
                st.altair_chart((chart_mov + text_mov).properties(height=200), use_container_width=True)
            else:
                st.info("No movie history available.")

        with c_tab2:
            st.markdown("**🧬 Cinematic Taste Profile**")
            top_interactions = {}
            for h in history_sorted:
                top_interactions[(h["t"], h["i"])] = top_interactions.get((h["t"], h["i"]), 0) + 1
            top_10 = sorted(top_interactions.keys(), key=lambda k: top_interactions[k], reverse=True)[:15]

            genre_counts = {}
            for t, i in top_10:
                details = fetch_api(f"https://api.themoviedb.org/3/{'tv' if t == 's' else 'movie'}/{i}?api_key={TMDB_KEY}")
                for g in details.get("genres", []):
                    genre_counts[g["name"]] = genre_counts.get(g["name"], 0) + 1

            if genre_counts:
                df_g = pd.DataFrame(list(genre_counts.items()), columns=["Genre", "Count"])
                chart_dna = alt.Chart(df_g).mark_arc(innerRadius=20, stroke="#050505", strokeWidth=2).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Genre", type="nominal", scale=alt.Scale(scheme='dark2'), legend=alt.Legend(title=None, labelColor="#EDEDED")),
                    radius=alt.Radius(field="Count", scale=alt.Scale(type="sqrt", zero=True, rangeMin=20)),
                    tooltip=["Genre", "Count"]
                )
                st.altair_chart(chart_dna.properties(height=350), use_container_width=True)
            else:
                st.info("Keep watching to unlock your Taste Profile DNA.")

        with c_tab3:
            st.markdown("**🔥 The Binge Matrix**")
            heatmap_data = []
            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for h in history_sorted:
                try:
                    dt = datetime.strptime(h["d"], "%Y-%m-%d %H:%M:%S")
                    heatmap_data.append({"Day": dt.strftime("%A"), "Hour": dt.hour, "Count": 1})
                except Exception:
                    pass
            if heatmap_data:
                df_heat = pd.DataFrame(heatmap_data).groupby(["Day", "Hour"]).count().reset_index()
                chart_heat = alt.Chart(df_heat).mark_rect(cornerRadius=4).encode(
                    x=alt.X('Hour:O', title='Hour of Day', axis=alt.Axis(labelAngle=0, labelColor="#aaa")),
                    y=alt.Y('Day:O', sort=days_order, title=None, axis=alt.Axis(labelColor="#aaa")),
                    color=alt.Color('Count:Q', scale=alt.Scale(scheme='yellowgreen'), legend=None),
                    tooltip=['Day', 'Hour', 'Count']
                )
                st.altair_chart(chart_heat.properties(height=300), use_container_width=True)
            else:
                st.info("Not enough history to generate a binge heatmap.")

        with c_tab4:
            st.markdown("**📡 Platform Usage**")
            plat_data = [h["p"] for h in history_sorted if h.get("p") and h["p"] != "None"]
            if plat_data:
                df_plat = pd.Series(plat_data).value_counts().reset_index()
                df_plat.columns = ['Platform', 'Count']
                chart_p = alt.Chart(df_plat).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Platform", type="nominal", scale=alt.Scale(scheme='category20'), legend=alt.Legend(title=None, labelColor="#EDEDED")),
                    tooltip=["Platform", "Count"]
                )
                st.altair_chart(chart_p.properties(height=300), use_container_width=True)
            else:
                st.info("You haven't logged any viewing platforms in your journal yet.")

        with c_tab5:
            st.markdown("**🎭 The Mood Ring**")
            feel_data = [h["f"] for h in history_sorted if h.get("f") and h["f"] != "None"]
            if feel_data:
                df_feel = pd.Series(feel_data).value_counts().reset_index()
                df_feel.columns = ['Vibe', 'Count']
                chart_feel = alt.Chart(df_feel).mark_arc(innerRadius=60).encode(
                    theta=alt.Theta(field="Count", type="quantitative"),
                    color=alt.Color(field="Vibe", type="nominal", legend=alt.Legend(title=None, labelColor="#EDEDED")),
                    tooltip=["Vibe", "Count"]
                )
                st.altair_chart(chart_feel.properties(height=350), use_container_width=True)
            else:
                st.info("You haven't logged any emotional vibes in your journal yet.")

        with c_tab6:
            st.markdown("**⭐ Rating Distribution**")
            rat_data = [h["r"] for h in history_sorted if h.get("r", 0) > 0]
            if rat_data:
                df_r = pd.Series(rat_data).value_counts().reset_index()
                df_r.columns = ['Stars', 'Count']
                chart_r = alt.Chart(df_r).mark_bar(color="#FFC107", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                    x=alt.X("Stars:N", title="Star Rating", axis=alt.Axis(labelAngle=0, labelColor="#aaa", titleColor="#aaa"), sort=[1, 2, 3, 4, 5]),
                    y=alt.Y("Count:Q", title="Total Given", axis=alt.Axis(labelColor="#aaa", titleColor="#aaa"))
                )
                text_r = chart_r.mark_text(align='center', baseline='bottom', dy=-5, color='#EDEDED', fontSize=12, fontWeight='bold').encode(text='Count:Q')
                st.altair_chart((chart_r + text_r).properties(height=300), use_container_width=True)
            else:
                st.info("You haven't left any star ratings in your journal yet.")

    with t_prof_hist:
        h_tv, h_mov = st.tabs(["📺 Series", "🎬 Movies"])

        def history_card_html(title, poster_url, dt, badges_html):
            return (
                f'<div style="border-left: 2px solid rgba(255, 193, 7, 0.3); padding-left: 15px; margin-bottom: 5px; position: relative; padding-bottom: 5px;">'
                f'<div style="position: absolute; left: -5px; top: 40px; width: 8px; height: 8px; border-radius: 50%; background: #FFC107; box-shadow: 0 0 8px #FFC107;"></div>'
                f'<div style="position: relative; border-radius: 12px; overflow: hidden; padding: 12px; border: 1px solid rgba(255,255,255,0.05); background-color: rgba(15, 17, 22, 0.6);">'
                f'<div style="position: absolute; top: -20px; left: -20px; right: -20px; bottom: -20px; background-image: url(\'{poster_url}\'); background-size: cover; background-position: center; filter: blur(12px) brightness(0.5); z-index: 0;"></div>'
                f'<div style="position: relative; z-index: 1; display: flex; align-items: center;">'
                f'<img src="{poster_url}" style="width: 55px; height: 82px; border-radius: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.6); margin-right: 15px; border: 1px solid rgba(255,255,255,0.1);">'
                f'<div style="flex: 1; min-width: 0;">'
                f'<div style="font-size: 1rem; font-weight: 800; color: #fff; line-height: 1.2; text-shadow: 0 2px 4px rgba(0,0,0,0.8); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{title}</div>'
                f'<div style="font-size: 0.65rem; color: #ccc; margin-bottom: 6px; margin-top: 2px;">{dt.strftime("%b %d, %Y • %I:%M %p")}</div>'
                f'<div style="display: flex; gap: 5px; flex-wrap: wrap;">{badges_html}</div>'
                f'</div></div></div></div>'
            )

        def pill(text, gold=False):
            if not text:
                return ''
            if gold:
                return f'<span style="background: rgba(255,193,7,0.2); color: #FFD54F; padding: 2px 6px; border-radius: 8px; font-size: 0.6rem; font-weight: 700; border: 1px solid rgba(255,193,7,0.3);">{text}</span>'
            return f'<span style="background: rgba(255,255,255,0.1); color: #eee; padding: 2px 6px; border-radius: 8px; font-size: 0.6rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.05);">{text}</span>'

        with h_tv:
            tv_hist = [h for h in history_sorted if h.get("t") == "s"]
            if not tv_hist:
                st.info("No series history recorded yet.")
            else:
                grouped_tv = {}
                for h_idx, h in enumerate(tv_hist[:st.session_state.hist_tv_limit]):
                    try:
                        dt = datetime.strptime(h["d"], '%Y-%m-%d %H:%M:%S')
                        grouped_tv.setdefault(dt.strftime('%B %Y'), []).append((h, dt, h_idx))
                    except Exception:
                        pass
                for month_str, items in grouped_tv.items():
                    st.markdown(f"<h4 style='color: #FFC107; margin-top: 1.5rem; margin-bottom: 0.8rem; font-weight: 800;'>{month_str}</h4>", unsafe_allow_html=True)
                    for h, dt, h_idx in items:
                        show = get_show(h.get("i"))
                        if show:
                            s_name, poster = show["name"], show.get("poster_path", "")
                        else:
                            s_data = fetch_api(f"https://api.themoviedb.org/3/tv/{h.get('i')}?api_key={TMDB_KEY}")
                            s_name, poster = s_data.get("name", "Unknown Series"), s_data.get("poster_path", "")

                        ep_code = h.get('e', '')
                        r_stars = ("⭐" * h.get('r', 0)) if h.get('r', 0) > 0 else ""
                        f_moji = h.get('f', '')
                        poster_url = f"https://image.tmdb.org/t/p/w185{poster}" if poster else "https://via.placeholder.com/185x278/222222/555555?text=No+Img"

                        badges = pill(ep_code, gold=True) + pill(r_stars) + pill(f_moji if f_moji and f_moji != "None" else "") + pill(f"📡 {h.get('p')}" if h.get("p") and h.get("p") != "None" else "")

                        c_col, = st.columns(1)
                        with c_col:
                            st.markdown(history_card_html(s_name, poster_url, dt, badges), unsafe_allow_html=True)
                            st.markdown('<span class="history-wrapper"></span>', unsafe_allow_html=True)
                            if st.button("INFO", key=f"h_r_tv_{h['i']}_{ep_code}_{h_idx}", use_container_width=True):
                                show_dialog_once(show_episode_details, h['i'], s_name, ep_code)
                if len(tv_hist) > st.session_state.hist_tv_limit:
                    if st.button("Load More Series", use_container_width=True, key="load_more_tv_hist"):
                        st.session_state.hist_tv_limit += 20
                        st.rerun()

        with h_mov:
            mov_hist = [h for h in history_sorted if h.get("t") == "m"]
            if not mov_hist:
                st.info("No movie history recorded yet.")
            else:
                grouped_mov = {}
                for h_idx, h in enumerate(mov_hist[:st.session_state.hist_mov_limit]):
                    try:
                        dt = datetime.strptime(h["d"], '%Y-%m-%d %H:%M:%S')
                        grouped_mov.setdefault(dt.strftime('%B %Y'), []).append((h, dt, h_idx))
                    except Exception:
                        pass
                for month_str, items in grouped_mov.items():
                    st.markdown(f"<h4 style='color: #FFC107; margin-top: 1.5rem; margin-bottom: 0.8rem; font-weight: 800;'>{month_str}</h4>", unsafe_allow_html=True)
                    for h, dt, h_idx in items:
                        mov = get_movie(h.get("i"))
                        if mov:
                            m_name, poster = mov["name"], mov.get("poster_path", "")
                        else:
                            m_data = fetch_api(f"https://api.themoviedb.org/3/movie/{h.get('i')}?api_key={TMDB_KEY}")
                            m_name, poster = m_data.get("title", "Unknown Movie"), m_data.get("poster_path", "")

                        r_stars = ("⭐" * h.get('r', 0)) if h.get('r', 0) > 0 else ""
                        f_moji = h.get('f', '')
                        poster_url = f"https://image.tmdb.org/t/p/w185{poster}" if poster else "https://via.placeholder.com/185x278/222222/555555?text=No+Img"

                        badges = pill("🎬 Movie", gold=True) + pill(r_stars) + pill(f_moji if f_moji and f_moji != "None" else "") + pill(f"📡 {h.get('p')}" if h.get("p") and h.get("p") != "None" else "")

                        c_col, = st.columns(1)
                        with c_col:
                            st.markdown(history_card_html(m_name, poster_url, dt, badges), unsafe_allow_html=True)
                            st.markdown('<span class="history-wrapper"></span>', unsafe_allow_html=True)
                            if st.button("OPEN", key=f"h_r_mov_{h['i']}_{h_idx}", use_container_width=True):
                                show_dialog_once(show_movie_details, h['i'], m_name)
                if len(mov_hist) > st.session_state.hist_mov_limit:
                    if st.button("Load More Movies", use_container_width=True, key="load_more_mov_hist"):
                        st.session_state.hist_mov_limit += 20
                        st.rerun()

    with t_prof_recaps:
        seen_recaps = sorted(list(set(st.session_state.db.get("seen_recaps", []))), reverse=True)
        if not seen_recaps:
            st.info("No recaps available yet. Keep watching to unlock your monthly and yearly wraps!")
        else:
            st.markdown("#### 🎞️ Your Cinematic Archive")
            for r_id in seen_recaps:
                if r_id.startswith("monthly-"):
                    m_key = r_id.replace("monthly-", "")
                    try:
                        m_title = datetime.strptime(m_key, "%Y-%m").strftime("%B %Y")
                    except Exception:
                        m_title = m_key
                    stats = st.session_state.db.get("analytics", {}).get(m_key, {"tv": 0, "movie": 0})
                    if st.button(f"📅 {m_title} Wrap-Up", key=f"btn_recap_{r_id}", use_container_width=True):
                        show_dialog_once(show_monthly_recap_dialog, m_key, m_title, stats, r_id)

                elif r_id.startswith("yearly-"):
                    year_str = r_id.replace("yearly-", "")
                    y_tv, y_mov = 0, 0
                    for k, v in st.session_state.db.get("analytics", {}).items():
                        if k.startswith(year_str):
                            y_tv += v.get("tv", 0)
                            y_mov += v.get("movie", 0)
                    if st.button(f"🏆 {year_str} YEAR IN REVIEW", key=f"btn_recap_{r_id}", use_container_width=True):
                        show_dialog_once(show_yearly_recap_dialog, int(year_str), y_tv, y_mov, r_id)

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
                                    if not imdb_id and not raw_title:
                                        continue

                                    res = fetch_robust(f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_KEY}&external_source=imdb_id") if imdb_id else {}

                                    if not res.get("movie_results") and raw_title:
                                        title_query = requests.utils.quote(str(raw_title))
                                        res = fetch_robust(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={title_query}&year={m.get('year', '')}")
                                        if res.get("results"):
                                            res["movie_results"] = [res["results"][0]]

                                    if res.get("movie_results"):
                                        match = res["movie_results"][0]
                                        tmdb_id, title = match["id"], match.get("title", raw_title)
                                        poster, release_date = match.get("poster_path", ""), match.get("release_date", "")
                                        was_watched = m.get("is_watched", False)

                                        if not any(str(movie["id"]) == str(tmdb_id) for movie in new_db["movies"]):
                                            new_db["movies"].append({"id": tmdb_id, "name": title, "watched": was_watched, "poster_path": poster or "", "release_date": release_date or "", "runtime": 120, "dropped": False})
                                            if was_watched:
                                                w_dt = parse_tvtime_date(m.get("watched_at"))
                                                m_key = datetime.strptime(w_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                                                new_db["analytics"].setdefault(m_key, {"tv": 0, "movie": 0})
                                                new_db["analytics"][m_key]["movie"] += 1
                                                new_db["history"].append({"t": "m", "i": tmdb_id, "e": "", "d": w_dt, "r": 0, "f": "", "p": ""})
                                except Exception:
                                    continue
                        except Exception as e:
                            st.error(f"Error processing movies: {e}")

                    if m_file and t_file:
                        prog.progress(0)

                    if t_file:
                        stat_txt.text("Processing Series... fetching data safely.")
                        try:
                            t_data = json.load(t_file)
                            for idx, s in enumerate(t_data):
                                prog.progress((idx + 1) / len(t_data))
                                try:
                                    raw_title = s.get("title") or ""
                                    tvdb_id = s.get("id", {}).get("tvdb") if s.get("id") else None
                                    if not tvdb_id and not raw_title:
                                        continue

                                    res = fetch_robust(f"https://api.themoviedb.org/3/find/{tvdb_id}?api_key={TMDB_KEY}&external_source=tvdb_id") if tvdb_id else {}

                                    if not res.get("tv_results") and raw_title:
                                        title_query = re.sub(r'\(\d{4}\)', '', raw_title).strip().replace(" ", "+")
                                        res = fetch_robust(f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_KEY}&query={title_query}")
                                        if res.get("results"):
                                            res["tv_results"] = [res["results"][0]]

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
                                                    w_dt = parse_tvtime_date(ep.get("watched_at"))
                                                    m_key = datetime.strptime(w_dt, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                                                    new_db["analytics"].setdefault(m_key, {"tv": 0, "movie": 0})
                                                    new_db["analytics"][m_key]["tv"] += 1
                                                    new_db["history"].append({"t": "s", "i": tmdb_id, "e": e_code, "d": w_dt, "r": 0, "f": "", "p": ""})

                                        if is_new_show:
                                            new_db["shows"].append({"id": tmdb_id, "name": title, "watched_episodes": watched_eps, "poster_path": poster or "", "first_air_date": first_air_date or "", "total_episodes": t_eps, "dropped": False})
                                        else:
                                            for show in new_db["shows"]:
                                                if str(show["id"]) == str(tmdb_id):
                                                    show["watched_episodes"] = list(set(show["watched_episodes"] + watched_eps))
                                                    break
                                except Exception:
                                    continue
                        except Exception as e:
                            st.error(f"Error processing series: {e}")

                    new_db["history"].sort(key=lambda x: x.get("d", "2000-01-01 12:00:00"), reverse=True)
                    tv_h = [h for h in new_db["history"] if h.get("t") == "s"][:100]
                    mov_h = [h for h in new_db["history"] if h.get("t") == "m"][:100]
                    new_db["history"] = tv_h + mov_h
                    st.session_state.db = new_db
                    st.session_state["_reconciled"] = False

                    if save_db():
                        stat_txt.text("✅ Mass Import & Supabase Sync Complete!")
                        st.toast("Library successfully imported.")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        stat_txt.text("🛑 Import finished, but the cloud save failed. See error above.")
                else:
                    st.error("Please upload at least one JSON file first.")


# ---------------------------------------------------------------------
# DEBUG READOUT — rendered in the page body (NOT a toast), because toasts
# share the same portal as dialogs. If a dialog is being hidden by CSS,
# a toast would be hidden too and tell you nothing.
# ---------------------------------------------------------------------
if DEBUG_DIALOG:
    st.divider()
    if DIALOG_GUARD["used"]:
        st.success(f"Python fired a dialog this run: {DIALOG_GUARD['last']}")
        st.caption("If you see this line but no modal appeared, the dialog is rendering and being hidden by CSS.")
    else:
        st.info("No dialog was opened this run.")
        st.caption("If you just clicked a poster and see this, the click did not reach Python.")
