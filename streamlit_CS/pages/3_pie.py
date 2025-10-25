import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------- Settings you can edit ----------
PIE_TITLE = "Favorite Fruits — Pie Demo"   # change this, save, and watch the page update
# Resolve CSV path relative to this file so the page finds the data
# regardless of the working directory used to start Streamlit.
CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "pie_demo.csv"
LABEL_COL = "label"
VALUE_COL = "value"
# ------------------------------------------

st.set_page_config(page_title="3_Pie", page_icon="🥧", layout="centered")
st.title("🥧 3_Pie")

# Debug info: show the absolute path we're attempting to read (helps when
# Streamlit is started from a different working directory).
st.caption(f"Looking for CSV at: {CSV_PATH} (exists={CSV_PATH.exists()})")

# Safety checks
if not CSV_PATH.exists():
    st.error(f"CSV not found at `{CSV_PATH}`. Create the file and refresh.")
    st.stop()

df = pd.read_csv(CSV_PATH)

# Minimal validation
missing_cols = [c for c in (LABEL_COL, VALUE_COL) if c not in df.columns]
if missing_cols:
    st.error(f"CSV must include columns: {LABEL_COL!r} and {VALUE_COL!r}. Missing: {missing_cols}")
    st.stop()

# Clean data
work = df[[LABEL_COL, VALUE_COL]].dropna()
# Coerce values to numeric (non-numeric -> NaN -> drop)
work[VALUE_COL] = pd.to_numeric(work[VALUE_COL], errors="coerce")
work = work.dropna(subset=[VALUE_COL])
work = work.groupby(LABEL_COL, as_index=False)[VALUE_COL].sum()

if work.empty:
    st.warning("No valid rows to display after cleaning.")
else:
    fig = px.pie(
        work,
        names=LABEL_COL,
        values=VALUE_COL,
        title=PIE_TITLE,
        hole=0  # set to 0.4 for a donut
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("CSV preview"):
    st.dataframe(df)
st.caption("Tip: Edit the CSV or the PIE_TITLE above, save the file(s), then refresh the page (or rely on Streamlit’s auto-rerun).")
