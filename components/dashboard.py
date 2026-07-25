import streamlit as st
import plotly.graph_objects as go
from components.kpi_cards import show_kpi_cards
import numpy as np
from utils.gemini_service import (
    generate_causes,
    generate_recommendations,
    ask_planning_assistant,
    generate_suggested_questions,
)

def show_dashboard():
    """UrbanHeat AI Dashboard"""

    # Get analysis results

    if "results" not in st.session_state:
        st.warning("No analysis found. Please run an analysis first.")
        return

    results = st.session_state.results

    temperature = results["temperature_celsius"]

    stats = results["recalculated_statistics"]

    ndvi = results["ndvi"]

    method = results["method"]
    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    left, right = st.columns([5, 1])

    with left:
        st.title("Dashboard")
        st.caption("Overview of Urban Heat Island Analysis")

    with right:
        st.selectbox(
            "",
            [st.session_state.dataset],
            label_visibility="collapsed",
            disabled=True,
        )


    st.divider()

    # --------------------------------------------------
    # KPI Cards
    # --------------------------------------------------

    show_kpi_cards(results)

    st.write("")

    # --------------------------------------------------
    # First Dashboard Row
    # --------------------------------------------------

    map_col, priority_col, risk_col = st.columns(
        [1.6, 1.05, 1.10]
    )

    # ---------------- Heat Map ----------------

    with map_col:

        with st.container(border=True):

            # ---------- Header ----------
            title_col, action_col = st.columns([5, 1])

            with title_col:
                st.markdown("## Urban Heat Map")

            with action_col:
                pass

            # ---------- Heat Map + Legend ----------
            image_col = st.container()


            with image_col:
                st.pyplot(
                    results["heatmap_figure"],
                    clear_figure=False,
                )

                st.caption("Urban Heat Risk Analysis")


# ---------------- Priority Zones ----------------

    with priority_col:

        with st.container(border=True):

            st.markdown("## Priority Zones")

            temperature_raster = np.asarray(
                results["temperature_celsius"],
                dtype=float,
            )
            risk_raster = np.asarray(
                results["ai_ordered"]
                if results["method"].upper() == "AI"
                else results["risk_map"],
                dtype=float,
            )

            row_midpoint = temperature_raster.shape[0] // 2
            column_midpoint = temperature_raster.shape[1] // 2

            regions = [
                (
                    "North-West",
                    temperature_raster[:row_midpoint, :column_midpoint],
                    risk_raster[:row_midpoint, :column_midpoint],
                ),
                (
                    "North-East",
                    temperature_raster[:row_midpoint, column_midpoint:],
                    risk_raster[:row_midpoint, column_midpoint:],
                ),
                (
                    "South-West",
                    temperature_raster[row_midpoint:, :column_midpoint],
                    risk_raster[row_midpoint:, :column_midpoint],
                ),
                (
                    "South-East",
                    temperature_raster[row_midpoint:, column_midpoint:],
                    risk_raster[row_midpoint:, column_midpoint:],
                ),
            ]

            priority_zones = []

            for region_name, region_temperature, region_risk in regions:
                valid_pixels = (
                    np.isfinite(region_temperature)
                    & np.isfinite(region_risk)
                    & (region_risk > 0)
                )

                average_temperature = float(
                    np.mean(region_temperature[valid_pixels])
                )
                highest_temperature = float(
                    np.max(region_temperature[valid_pixels])
                )
                average_risk = float(np.mean(region_risk[valid_pixels]))

                if average_risk >= 2.5:
                    risk_level = "High"
                    icon = "🔴"
                elif average_risk >= 1.5:
                    risk_level = "Moderate"
                    icon = "🟠"
                else:
                    risk_level = "Low"
                    icon = "🟢"

                priority_zones.append(
                    {
                        "name": region_name,
                        "average_temperature": average_temperature,
                        "maximum_temperature": highest_temperature,
                        "risk": average_risk,
                        "risk_level": risk_level,
                        "icon": icon,
                    }
                )

            priority_zones.sort(
                key=lambda zone: zone["risk"],
                reverse=True,
            )

            for priority_number, zone in enumerate(priority_zones[:3], start=1):

                st.markdown(
                    f"""
            **{zone['icon']} Priority {priority_number}**  
            **Region:** {zone['name']}  
            **Risk:** {zone['risk_level']}   
            **Avg Temp:** {zone['average_temperature']:.1f} °C   
            **Max Temp:** {zone['maximum_temperature']:.1f} °C
            """
                )

                if priority_number < len(priority_zones[:3]):
                    st.divider()


    # ---------------- Risk ----------------

    with risk_col:

        with st.container(border=True):

            title_col, action_col = st.columns([5.5, 1])

            with title_col:
                st.markdown("## Risk Distribution")

            with action_col:
                pass

            results = st.session_state.results

            if results["method"] == "AI":

                values = [
                    results["high_risk_percentage"],
                    results["moderate_risk_percentage"],
                    results["low_risk_percentage"],
                ]

            else:

                values = [
                    results["high_risk_percentage"],
                    results["moderate_risk_percentage"],
                    results["low_risk_percentage"],
                ]

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=[
                            "High",
                            "Moderate",
                            "Low",
                        ],
                        values=values,

                        hole=0.62,

                        textinfo="percent",

                        textfont=dict(
                            size=12,
                            color="white",
                        ),

                        marker=dict(
                            colors=[
                                "#FF4B4B",   # Very High
                                "#FFE53BEE",   # Moderate
                                "#30B842",   # Low
                            ],

                            line=dict(
                                color="#111827",
                                width=2,
                            ),
                        ),
                    )
                ]
            )

            fig.update_layout(
                height=290,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )   
    
                
    st.write("")

    # --------------------------------------------------
    # Second Dashboard Row
    # --------------------------------------------------

    left, middle, right = st.columns(
        [1.35, 1.35, 1.25]
    )

    # ---------------- Cause ----------------

    results = st.session_state.results

    analysis_data = {
        "Detection Method": results["method"],
        "Mean Temperature": round(results["recalculated_statistics"]["mean"], 2),
        "Maximum Temperature": round(results["recalculated_statistics"]["maximum"], 2),
        "Minimum Temperature": round(results["recalculated_statistics"]["minimum"], 2),
        "Mean NDVI": round(results["ndvi_statistics_before_clipping"]["mean"], 3),
        "Mean NDBI": round(results["ndbi_statistics"]["mean"], 3),
        "Mean NDWI": round(results["ndwi_statistics"]["mean"], 3),
        "High Risk Percentage": round(results["high_risk_percentage"], 2),
        "Moderate Risk Percentage": round(results["moderate_risk_percentage"], 2),
        "Low Risk Percentage": round(results["low_risk_percentage"], 2),
    }

    analysis_signature = tuple(analysis_data.items())

    if st.session_state.get("ai_analysis_signature") != analysis_signature:
        st.session_state.ai_analysis_signature = analysis_signature
        st.session_state.ai_causes = None
        st.session_state.ai_recommendations = None
        st.session_state.suggested_questions = None
        st.session_state.chat_history = []
        st.session_state.show_suggestions = True

    if st.session_state.get("ai_causes") is None:
        with st.spinner("Generating AI insights..."):
            st.session_state.ai_causes = generate_causes(analysis_data)


    if st.session_state.get("ai_recommendations") is None:
        with st.spinner("Generating AI recommendations..."):
            st.session_state.ai_recommendations = generate_recommendations(
                analysis_data
            )

    if st.session_state.get("suggested_questions") is None:

        with st.spinner("Preparing suggested questions..."):
            st.session_state.suggested_questions = [
                question.strip()
                for question in generate_suggested_questions(analysis_data).split("\n")
                if question.strip()
            ]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "show_suggestions" not in st.session_state:
        st.session_state.show_suggestions = True

    ai_recommendations = st.session_state.ai_recommendations

    mean_temp = results["recalculated_statistics"]["mean"]
    mean_ndvi = results["ndvi_statistics_before_clipping"]["mean"]
    
    with left:

        with st.container(border=True):

            title_col, action_col = st.columns([4.5, 1.2])

            with title_col:
                st.markdown("## Cause Analysis")

            with action_col:
                pass
                    
            st.write("### Major Contributors")

            mean_ndbi = results["ndbi_statistics"]["mean"]
            mean_ndwi = results["ndwi_statistics"]["mean"]

            built_up = max(
                0,
                min(100, int((mean_ndbi + 1) / 2 * 100))
            )

            vegetation = max(
                0,
                min(100, int((1 - mean_ndvi) * 100))
            )

            surface_heat = max(
                0,
                min(100, int(mean_temp * 2))
            )

            water = max(
                0,
                min(100, int((1 - (mean_ndwi + 1) / 2) * 100))
            )

            st.progress(built_up, text="🏙 High Built-up Area")

            st.progress(vegetation, text="🌿 Low Vegetation")

            st.progress(surface_heat, text="🛣 Surface Heat")

            st.progress(water, text="💧 Limited Water Bodies")

            st.divider()

            scores = {
                "High Built-up Density": built_up,
                "Low Vegetation": vegetation,
                "Limited Water Availability": water,
                "High Surface Temperature": surface_heat,
            }

            overall_cause = max(
                scores,
                key=scores.get,
            )

            st.metric(
                "Primary Cause",
                overall_cause,
            )

            st.divider()

            st.write("### AI Insights")

            st.markdown(st.session_state.ai_causes)

    # ---------------- Recommendation ----------------

    with middle:

        with st.container(border=True):

            title_col, action_col = st.columns([4.5, 1.2])

            with title_col:
                st.markdown("## Recommendations")

            with action_col:
                pass

            recommendations = [
                line.strip()
                for line in ai_recommendations.split("\n")
                if line.strip()
            ]

            cards = [
                st.success,
                st.info,
                st.warning,
            ]

            for card, recommendation in zip(cards, recommendations):
                card(recommendation)

            st.divider()




    # ---------------- AI Assistant ----------------

    with right:

        with st.container(border=True):

            title_col, action_col = st.columns([4.5, 1.2])

            with title_col:
                st.markdown("## AI Planning Assistant")

            with action_col:
                pass

            st.caption("AI-powered planning support")

            if st.button("🗑 Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.show_suggestions = True

            selected_question = None

            if st.session_state.show_suggestions:
                st.write("### 💡 Suggested Questions")

                icons = ["🔥", "🌳", "🏗", "📈"]

                for index, suggested_question in enumerate(
                    st.session_state.suggested_questions
                ):
                    label = (
                        f"{icons[index]} {suggested_question}"
                        if index < len(icons)
                        else suggested_question
                    )

                    if st.button(
                        label,
                        key=f"suggested_question_{index}",
                        use_container_width=True,
                    ):
                        selected_question = suggested_question
                        st.session_state.show_suggestions = False

            chat_messages = st.container()

            typed_question = st.chat_input(
                "Ask about hotspots, causes or recommendations..."
            )

            question = selected_question or (
                typed_question.strip() if typed_question else None
            )

            if question:
                st.session_state.show_suggestions = False
                st.session_state.chat_history = [
                    {"role": "user", "content": question}
                ]

                with chat_messages:
                    with st.chat_message("user"):
                        st.write(question)

                    with st.status(
                        "🤖 Analyzing your question...",
                        expanded=False,
                    ) as status:
                        ai_answer = ask_planning_assistant(analysis_data, question)
                        status.update(
                            label="Response generated",
                            state="complete",
                        )

                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": ai_answer}
                    )

                    with st.chat_message("assistant"):
                        st.write(ai_answer)

            else:
                with chat_messages:
                    for message in st.session_state.chat_history[-2:]:
                        with st.chat_message(message["role"]):
                            st.write(message["content"])

                
