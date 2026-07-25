import streamlit as st
from utils.uhi_utils import run_analysis

def show_home():

    st.container()

    col1, col2 = st.columns([2, 7.9], gap="small")

    with col1:
        st.title("UrbanHeat AI")

    with col2:
        st.write("")
        st.image("assets/icons/urbanheat.svg", width=50)

    st.markdown("#### Smarter Decisions for Cooler Cities")
    
    st.divider()

    st.header("Welcome to UrbanHeat AI")

    st.markdown("##### Our platform simplifies heat analysis. Easily finds hot areas (Urban Heat Islands), understand what causes them, and instantly see which high-risk areas need help first. Finally, get AI-powered infrastructure recommendations to design cooler, smarter cities.")   

    st.divider()

    st.markdown("## How It Works")

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    # ---------------- Step 1 ----------------

    with c1:
        with st.container(border=True):

            top_left, top_right = st.columns([4, 1])

            with top_left:
                st.caption("Step 1")

            with top_right:
                st.image("assets/icons/detect.svg", width=105)

            st.markdown("### Detect Hotspots")

            st.markdown(
                "Automatically identify areas having high temperature "
                "using the chosen analysis method and visualize them."
            )


    # ---------------- Step 2 ----------------

    with c2:
        with st.container(border=True):

            top_left, top_right = st.columns([4, 1])

            with top_left:
                st.caption("Step 2")

            with top_right:
                st.image("assets/icons/analyze.svg", width=105)

            st.markdown("### Analyze Causes")

            st.markdown(
                "Uncover the major factors responsible for "
                "heat buildup and temperature anomalies."
            )


    # ---------------- Step 3 ----------------

    with c3:
        with st.container(border=True):

            top_left, top_right = st.columns([4, 1])

            with top_left:
                st.caption("Step 3")

            with top_right:
                st.image("assets/icons/prioritize.svg", width=105)

            st.markdown("### Prioritize Zones")

            st.markdown(
                "Rank locations based on heat intensity, "
                "risk level, and expected impact."
            )


    # ---------------- Step 4 ----------------

    with c4:
        with st.container(border=True):

            top_left, top_right = st.columns([4, 1])

            with top_left:
                st.caption("Step 4")

            with top_right:
                st.image("assets/icons/recommends.svg", width=105)

            st.markdown("### Get AI Recommendations")

            st.markdown(
                "Receive AI-powered infrastructure suggestions "
                "to create cooler and smarter cities."
            )


    st.divider()

    left, right = st.columns([1, 1], gap="medium")

    # ===================== STEP 1 =====================

    with left:

        with st.container(border=True):

            st.markdown("## Step 1: Pick Your Dataset")
            st.markdown(
                "Choose a dataset to begin your Urban Heat Island analysis."
            )

            choice1, choice2 = st.columns(2, gap="medium")

            with choice1:

                with st.container(border=True):

                    c1, c2, c3 = st.columns([1, 1, 1])

                    with c2:
                        st.image("assets/icons/dataset.svg", width=60)

                    st.markdown("#### USE SAMPLE DATASET")

                    st.markdown(
                        "Start instantly using a built-in sample city for demonstration."
                    )

                    sample = st.button(
                        "Load Sample Dataset",
                        key="sample_btn",
                        use_container_width=True,
                    )

                    if sample:
                        st.session_state.show_city = True
                        st.rerun()

                    if st.session_state.get("show_city", False):

                        sample_city = st.selectbox(
                            "Choose City",
                            ["Lucknow", "Delhi", "Mumbai", "Bengaluru"],
                            key="sample_city",
                        )
                    else:
                        sample_city = "Lucknow"
                    
            with choice2:

                with st.container(border=True):

                    c1, c2, c3 = st.columns([1, 1, 1])

                    with c2:
                        st.image("assets/icons/upload.svg", width=60)

                    st.markdown("#### UPLOAD CUSTOM DATASET")

                    st.markdown(
                            "Upload Landsat GeoTIFF Bands (B3, B4, B5, B6 & B10)."
                    )

                    upload = st.button(
                        "Upload Dataset",
                        key="upload_btn",
                        use_container_width=True,
                    )

                    green_file = None
                    red_file = None
                    nir_file = None
                    swir1_file = None
                    thermal_file = None


                    if st.session_state.get("dataset") == "Custom Dataset":

                        green_file = st.file_uploader(
                            "Band 3 (Green)",
                            type=["tif", "TIF"],
                            key="green"
                        )

                        red_file = st.file_uploader(
                            "Band 4 (Red)",
                            type=["tif", "TIF"],
                            key="red"
                        )

                        nir_file = st.file_uploader(
                            "Band 5 (NIR)",
                            type=["tif", "TIF"],
                            key="nir"
                        )

                        swir1_file = st.file_uploader(
                            "Band 6 (SWIR1)",
                            type=["tif", "TIF"],
                            key="swir1"
                        )

                        thermal_file = st.file_uploader(
                            "Band 10 (Thermal)",
                            type=["tif", "TIF"],
                            key="thermal"
                        )

                    

            if "dataset" not in st.session_state:
                st.session_state.dataset = "Lucknow"


            if st.session_state.get("show_city", False) and "sample_city" in st.session_state:
                st.session_state.dataset = st.session_state.sample_city

            if upload:
                st.session_state.dataset = "Custom Dataset"

            dataset = st.session_state.dataset

            st.success(f"✅ Selected: {dataset}")

    # ===================== STEP 2 =====================

    with right:

        with st.container(border=True):

            st.markdown("## Step 2: Choose Analysis Method")

            st.markdown(
                "Select how UrbanHeat AI should detect Urban Heat Island hotspots."
            )

            choice1, choice2 = st.columns(2, gap="medium")

            with choice1:

                with st.container(border=True):

                    c1, c2, c3 = st.columns([1, 1, 1])

                    with c2:
                        st.image("assets/icons/ai.svg", width=60)

                    st.markdown("#### AI-BASED DETECTION")

                    st.markdown(
                        "Automatically identifies heat patterns using AI analysis."
                    )

                    ai = st.button(
                        "Use AI Detection",
                        key="ai_btn",
                        use_container_width=True,
                    )

            with choice2:

                with st.container(border=True):

                    c1, c2, c3 = st.columns([1, 1, 1])

                    with c2:
                        st.image("assets/icons/temperature.svg", width=60)

                    st.markdown("#### THRESHOLD-BASED DETECTION")

                    st.markdown(
                        "Detect hotspots using predefined temperature thresholds."
                    )

                    threshold = st.button(
                        "Use Threshold",
                        key="threshold_btn",
                        use_container_width=True,
                    )

            if "method" not in st.session_state:
                st.session_state.method = "AI-Based Detection"

            if ai:
                st.session_state.method = "AI-Based Detection"

            if threshold:
                st.session_state.method = "Threshold-Based Detection"

            method = st.session_state.method

            st.success(f"✅ Selected: {method}")

    st.divider()

    start = st.button(
        "🚀 Start Analysis",
        use_container_width=True,
        type="primary",
    )

    if start:

        with st.spinner("Please wait while we analyze the satellite data..."):

            if dataset != "Custom Dataset":

                results = run_analysis(
                    sample_city,
                    None,
                    None,
                    None,
                    None,
                    method="AI" if "AI" in method else "Threshold",
                )

            else:

                if None in (
                    green_file,
                    red_file,
                    nir_file,
                    swir1_file,
                    thermal_file,
                ):
                    st.error("Please upload all five Landsat bands.")
                    st.stop()

                results = run_analysis(
                    green_file,
                    red_file,
                    nir_file,
                    swir1_file,
                    thermal_file,
                    method="AI" if "AI" in method else "Threshold",
                )

            st.session_state.results = results

            st.session_state.page = "Dashboard"

            st.rerun()


    return dataset, method, start