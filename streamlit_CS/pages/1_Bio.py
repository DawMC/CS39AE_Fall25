import streamlit as st

st.title("👋 My Bio")

# ---------- TODO: Replace with your own info ----------
NAME = "Dawson Cummings"
PROGRAM = "Computer Science"
INTRO = (
    "I am in my final semester of college in my computer science program. During this time I am also a bartender at an Italian Restaruant in Englewood. "

)
FUN_FACTS = [
    "I love being outside and exploring new places.",
    "I’m learning how to make more classic cocktails and then make my own spin on them.",
    "I want to build something original that I can be proud to call mine",
]
PHOTO_PATH = "your_photo.jpeg"  # Put a file in repo root or set a URL

# ---------- Layout ----------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    try:
        st.image(PHOTO_PATH, caption=NAME, use_container_width=True)
    except Exception:
        st.info("Add a photo named `your_photo.jpg` to the repo root, or change PHOTO_PATH.")
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")
