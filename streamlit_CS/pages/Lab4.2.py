# pages/2_Weather_Live.py
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
from datetime import timedelta

st.set_page_config(page_title="Live Weather (Denver) — Open-Meteo", page_icon="🌡️", layout="wide")
st.markdown("""
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

st.title("🌡️ Live Weather — Denver (Open-Meteo)")
st.caption("Auto-refreshing line chart with cached API calls and a short rolling history stored in session state.")

LAT, LON = 39.7392, -104.9903  # Denver
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}
HISTORY_MINUTES_DEFAULT = 120  # keep last 2 hours by default

def build_url(lat: float, lon: float) -> str:
    # Current weather endpoint – includes ISO timestamp, temperature (°C), and wind (m/s)
    return (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,wind_speed_10m"
        "&timezone=auto"
    )

API_URL = build_url(LAT, LON)

# Fallback sample so the page never crashes if API is down/rate-limited
SAMPLE_DF = pd.DataFrame(
    [{
        "time": pd.Timestamp.utcnow(),
        "temperature": 22.0,  # °C
        "wind": 3.2          # m/s
    }]
)

# ──────────────────────────────────────────────────────────────────────────────
# Cached fetch (polite + fast)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)  # cache for 10 minutes
def get_weather(url: str):
    """Return (df, err). Never raise; safe for beginners."""
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "a bit")
            return None, f"429 Too Many Requests — try again after {retry_after}s"
        resp.raise_for_status()
        j = resp.json().get("current", {})
        df = pd.DataFrame([{
            "time": pd.to_datetime(j.get("time")),
            "temperature": j.get("temperature_2m"),
            "wind": j.get("wind_speed_10m"),
        }])
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"
    except (ValueError, KeyError) as e:
        return None, f"Parsing error: {e}"

# ──────────────────────────────────────────────────────────────────────────────
# Auto refresh controls
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("🔁 Auto Refresh")
cols = st.columns([1,1,2,2])
with cols[0]:
    refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)
with cols[1]:
    auto_refresh = st.toggle("Enable auto-refresh", value=False)
with cols[2]:
    window_min = st.slider("History window (minutes)", 10, 240, HISTORY_MINUTES_DEFAULT)
with cols[3]:
    st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# ──────────────────────────────────────────────────────────────────────────────
# Session-state rolling history
# ──────────────────────────────────────────────────────────────────────────────
if "weather_hist" not in st.session_state:
    st.session_state.weather_hist = pd.DataFrame(columns=["time", "temperature", "wind"])

df_now, err = get_weather(API_URL)
if err:
    st.warning(f"{err}\nShowing sample data so the demo continues.")
    df_now = SAMPLE_DF.copy()

# Append only if it's new or first sample
hist = st.session_state.weather_hist
if not df_now.empty:
    new_row = df_now.iloc[0]
    if hist.empty or pd.isna(new_row["time"]) or new_row["time"] != hist.iloc[-1]["time"]:
        st.session_state.weather_hist = pd.concat([hist, df_now], ignore_index=True)

# Enforce rolling time window
hist = st.session_state.weather_hist.copy()
if not hist.empty:
    hist = hist.sort_values("time")
    cutoff = (hist["time"].max() - timedelta(minutes=window_min))
    hist = hist[hist["time"] >= cutoff]
    # persist the trimmed history back
    st.session_state.weather_hist = hist.reset_index(drop=True)

# ──────────────────────────────────────────────────────────────────────────────
# Metrics row
# ──────────────────────────────────────────────────────────────────────────────
st.subheader("📈 Metrics")
m1, m2, m3, m4 = st.columns(4)
if hist.empty:
    m1.metric("Current Temp (°C)", "—")
    m2.metric("Wind (m/s)", "—")
    m3.metric("Window Min/Max (°C)", "—")
    m4.metric("Δ since last (°C)", "—")
else:
    curr = hist.iloc[-1]
    prev = hist.iloc[-2] if len(hist) > 1 else None
    delta = (curr["temperature"] - prev["temperature"]) if prev is not None else 0.0
    m1.metric("Current Temp (°C)", f"{curr['temperature']:.2f}")
    m2.metric("Wind (m/s)", f"{curr['wind']:.2f}")
    m3.metric(
        "Window Min/Max (°C)",
        f"{hist['temperature'].min():.2f} / {hist['temperature'].max():.2f}"
    )
    m4.metric("Δ since last (°C)", f"{delta:+.2f}")

st.subheader("Temperature over Time")
if hist.empty:
    st.info("No samples yet. Enable auto-refresh or click the Refresh button below.")
else:
    fig = px.line(
        hist,
        x="time",
        y="temperature",
        markers=True,
        title="Denver — Temperature (°C) vs Time"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), xaxis_title="Time", yaxis_title="°C")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(hist.sort_values("time", ascending=False), use_container_width=True, hide_index=True)

left, right = st.columns([1,3])
with left:
    if st.button("🔄 Refresh now"):
        get_weather.clear()   # invalidate cached function result
        st.rerun()

# If auto-refresh is ON, sleep, clear cache, and rerun
if auto_refresh:
    time.sleep(refresh_sec)
    get_weather.clear()
    st.rerun()
