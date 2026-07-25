import streamlit as st

from config import APP_NAME
from components.home import show_home
from components.dashboard import show_dashboard
from components.compare_cities import show_compare_cities
from components.about import show_about
from components.help import show_help

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Session State
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "Home"

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.title("🌍 UrbanHeat AI")

    st.caption("Smarter Decisions for Cooler Cities")

    st.divider()

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"

    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"

    if st.button("🏙️ Compare Cities", use_container_width=True):
        st.session_state.page = "Compare Cities"

    st.divider()

    if st.button("ℹ About", use_container_width=True):
        st.session_state.page = "About"

    if st.button("❓ Help", use_container_width=True):
        st.session_state.page = "Help"

    st.divider()

    st.toggle("🌙 Dark Mode", value=True)

# --------------------------------------------------
# Main Area
# --------------------------------------------------

page = st.session_state.page

if page == "Home":

    show_home()

elif page == "Dashboard":

    show_dashboard()

elif page == "Compare Cities":
    show_compare_cities()

elif page == "About":
    show_about()

elif page == "Help":
    show_help()



elif page == "Cause":

    st.title("Cause Analysis")

    st.info("Cause Analysis page coming next.")

elif page == "Priority":

    st.title("Priority Ranking")

    st.info("Priority Ranking page coming next.")

elif page == "Recommendations":

    st.title("Recommendations")

    st.info("Recommendations page coming next.")

elif page == "Assistant":

    st.title("AI Planning Assistant")

    st.info("AI Assistant page coming next.")