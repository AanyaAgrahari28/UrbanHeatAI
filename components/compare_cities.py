import streamlit as st
import plotly.graph_objects as go
from utils.uhi_utils import run_analysis
from utils.gemini_service import compare_cities_ai


def show_compare_cities():
    st.title("Compare Cities 🏙️")

    # ---------------------------------------
    # Session State Initialization
    # ---------------------------------------

    if "compare_city1_results" not in st.session_state:
        st.session_state.compare_city1_results = None

    if "compare_city2_results" not in st.session_state:
        st.session_state.compare_city2_results = None

    # ---------------------------------------
    # Top Controls
    # ---------------------------------------

    col1, col2, col3, col4 = st.columns([4, 0.7, 4, 2])

    with col1:

        city1 = st.selectbox(
            "City 1",
            [
                "Lucknow",
                "Delhi",
                "Mumbai",
                "Bengaluru",
            ],
            key="compare_city1",
        )

    with col2:
        pass

    with col3:

        city2 = st.selectbox(
            "City 2",
            [
                "Lucknow",
                "Delhi",
                "Mumbai",
                "Bengaluru",
            ],
            index=1,
            key="compare_city2",
        )

    with col4:

        st.markdown("<br>", unsafe_allow_html=True)

        compare = st.button(
            "📊 Compare",
            use_container_width=True,
        )

    # ---------------------------------------
    # Run Analysis
    # ---------------------------------------

    if compare:

        with st.spinner("Comparing cities..."):

            city1_results = run_analysis(
                city1,
                None,
                None,
                None,
                None,
                method="AI",
            )

            city2_results = run_analysis(
                city2,
                None,
                None,
                None,
                None,
                method="AI",
            )

            st.session_state.compare_city1_results = city1_results
            st.session_state.compare_city2_results = city2_results

    # ---------------------------------------
    # Stop if comparison not yet run
    # ---------------------------------------

    if (
        st.session_state.compare_city1_results is None
        or
        st.session_state.compare_city2_results is None
    ):
        return

    city1_results = st.session_state.compare_city1_results
    city2_results = st.session_state.compare_city2_results

    st.divider()

    st.subheader(f"{city1}  vs  {city2}")


    avg1 = city1_results["recalculated_statistics"]["mean"]
    avg2 = city2_results["recalculated_statistics"]["mean"]

    max1 = city1_results["recalculated_statistics"]["maximum"]
    max2 = city2_results["recalculated_statistics"]["maximum"]

    hot1 = city1_results["hotspot_area_km2"]
    hot2 = city2_results["hotspot_area_km2"]

    ndvi1 = city1_results["ndvi_statistics_before_clipping"]["mean"]
    ndvi2 = city2_results["ndvi_statistics_before_clipping"]["mean"]

    risk1 = city1_results["high_risk_percentage"]
    risk2 = city2_results["high_risk_percentage"]

    # ---------------------------------------
    # City Summary Cards
    # ---------------------------------------

    left, right = st.columns(2)

    with left:

        with st.container(border=True):

            st.markdown(f"## 📍 {city1}")

            st.write(f"**Average Temperature:** {avg1:.2f} °C")
            st.write(f"**Maximum Temperature:** {max1:.2f} °C")
            st.write(f"**Mean NDVI:** {ndvi1:.3f}")
            st.write(f"**High Risk Area:** {risk1:.2f}%")

    with right:

        with st.container(border=True):

            st.markdown(f"## 📍 {city2}")

            st.write(f"**Average Temperature:** {avg2:.2f} °C")
            st.write(f"**Maximum Temperature:** {max2:.2f} °C")
            st.write(f"**Mean NDVI:** {ndvi2:.3f}")
            st.write(f"**High Risk Area:** {risk2:.2f}%")

    st.write("")
    st.divider()

    # ---------------------------------------
    # Heatmap Comparison
    # ---------------------------------------

    st.subheader("Urban Heat Comparison🔥")

    left_map, right_map = st.columns(2)

    with left_map:

        st.markdown(f"## 📍 {city1}")

        if city1_results.get("heatmap_figure") is not None:
            st.pyplot(
                city1_results["heatmap_figure"],
                use_container_width=True,
            )

    with right_map:

        st.markdown(f"## 📍 {city2}")

        if city2_results.get("heatmap_figure") is not None:
            st.pyplot(
                city2_results["heatmap_figure"],
                use_container_width=True,
            )

    st.divider()

    # ---------------------------------------
    # Temperature Comparison Chart
    # ---------------------------------------

    st.subheader("Temperature Comparison 🌡️")

    if avg1 >= avg2:
        color1 = "#E53935"   # Red (Hotter)
        color2 = "#FF8C00"   # Orange
    else:
        color1 = "#FF8C00"
        color2 = "#E53935"

    fig = go.Figure()

    fig.add_bar(
        name=city1,
        x=["Average", "Maximum"],
        y=[avg1, max1],
        marker_color=color1,
    )

    fig.add_bar(
        name=city2,
        x=["Average", "Maximum"],
        y=[avg2, max2],
        marker_color=color2,
    )

    fig.update_layout(
        barmode="group",
        height=420,
        xaxis_title="Temperature Metric",
        yaxis_title="Temperature (°C)",
        legend_title="City",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---------------------------------------
    # AI Insights
    # ---------------------------------------

    st.subheader("AI Insights 🤖 ")

    comparison_data = f"""
    {city1}
    - Average Temperature: {avg1:.2f} °C
    - Maximum Temperature: {max1:.2f} °C
    - Mean Vegetation: {ndvi1:.3f}
    - High Risk Area: {risk1:.2f}%
    - Hotspot Area: {hot1:.2f} km²

    {city2}
    - Average Temperature: {avg2:.2f} °C
    - Maximum Temperature: {max2:.2f} °C
    - Mean Vegetation: {ndvi2:.3f}
    - High Risk Area: {risk2:.2f}%
    - Hotspot Area: {hot2:.2f} km²
    """

    with st.spinner("AI is comparing both cities..."):
        ai_response = compare_cities_ai(
            city1,
            city2,
            comparison_data,
        )

    st.markdown(ai_response)