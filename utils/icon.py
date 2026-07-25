from pathlib import Path
import streamlit as st

ICON_DIR = Path("assets/icons")

def icon(name, width=28):
    st.image(str(ICON_DIR / f"{name}.svg"), width=width)