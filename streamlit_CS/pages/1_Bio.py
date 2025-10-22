#Bio page code, make changes for you

import streamlit as st
from pathlib import Path

st.title("My Bio")

# ---------- TODO: Replace with your own info ----------
NAME = "Dawson Cummings"
PROGRAM = "Computer Science"
INTRO = (
    "I am in my final year of studying Computer Science and while I am doing that I am a bartender at a restaurant in Englewood."
FUN_FACTS = [
     "I love to go out and explore new places.",
     "I’m learning how to build a dataset that actively pulls from a seperate inventory system",
     "I want to build a server for my parents business so they can better track their sales and inventory.",
])

def find_photo(filename="your_photo.jpg"):
     # Photo was saved in assets folder
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        script_dir = Path.cwd()

    candidates = [
        script_dir / "assets" / filename,          # pages/assets/...
        script_dir.parent / "assets" / filename,   # root/assets/... (common)
        Path("assets") / filename,                  # cwd/assets/...
    ]
    for p in candidates:
        if p.exists():
            return str(p)
        return None

photo_src = find_photo("your_photo.jpg")

# -------------------- LAYOUT --------------------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    if photo_src:
        st.image(photo_src, caption=NAME, use_container_width=True)
    else:
         st.info(
             "📷 Place `your_photo.jpg` inside an `assets/` folder at the app root "
             "or update the path in `find_photo()`."
 )
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
     st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")