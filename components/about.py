import streamlit as st


def show_about():

    st.title("ℹ️ About UrbanHeat AI")

    st.markdown("""
Welcome to **UrbanHeat AI!** We built this platform to tackle one of the fastest-growing climate challenges of our time: **Urban Heat Islands (UHI).**

As cities expand, concrete and asphalt trap heat, creating localized pockets of extreme temperatures. Traditionally, analyzing this heat distribution required expensive software, deep technical expertise, and hours of coding to process satellite imagery.

UrbanHeat AI changes that. We’ve simplified the entire process. By combining remote sensing with machine learning, our platform automatically turns raw satellite data into clear, actionable maps and insights in just a few clicks. It takes the heavy lifting out of geospatial analysis so you can focus on finding solutions.
""")

    st.divider()

    st.header("👥 Who is this platform for?")

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.subheader("🏙️ Urban Planners & City Officials")

            st.write(
                "Pinpoint exactly which neighborhoods need immediate interventions, "
                "like planting trees, adding green roofs, or changing zoning laws."
            )

        with st.container(border=True):

            st.subheader("🎓 Environmental Researchers & Students")

            st.write(
                "Fast-track your research. Instead of writing complex code to calculate "
                "environmental indices, use our app to analyze satellite data instantly."
            )

    with col2:

        with st.container(border=True):

            st.subheader("🏗️ Real Estate & Infrastructure Developers")

            st.write(
                "Assess climate risks and heat vulnerability for new construction "
                "projects to design more eco-friendly developments."
            )

        with st.container(border=True):

            st.subheader("🏥 Public Health Officials")

            st.write(
                "Identify vulnerable, high-heat neighborhoods to strategically deploy "
                "cooling centers and emergency resources during extreme heatwaves."
            )

    st.divider()

    st.header("🌟 Why Use UrbanHeat AI?")

    with st.container(border=True):

        st.subheader("🏙️ City-to-City Comparison")

        st.write(
            "Put two different cities side-by-side to compare their heat distribution, "
            "green spaces, and concrete density to see which urban designs work best."
        )

        st.divider()

        st.subheader("🤖 Automated AI Detection")

        st.write(
            "We use machine learning to remove human bias and automatically draw "
            "boundaries around high-risk heat zones."
        )

        st.divider()

        st.subheader("💡 Actionable Recommendations")

        st.write(
            "The platform doesn't just show you the problem—it highlights priority "
            "areas and generates AI-driven strategies for cooling them down."
        )

    st.divider()

    st.header("⚙️ How It Works (Simplified)")

    st.image(
        "assets/images/uhi_workflow.png",
        use_container_width=True,
    )

    st.markdown("""
We’ve streamlined a complex data science workflow into an easy, user-friendly process:
""")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        with st.container(border=True):

            st.subheader("1️⃣ Feed it Satellite Data")

            st.write(
                "Select or upload raw Landsat 8/9 satellite imagery for your target area."
            )

    with c2:

        with st.container(border=True):

            st.subheader("2️⃣ Decode the Environment")

            st.write(
                "Automatically calculates Land Surface Temperature (LST), NDVI, "
                "NDBI and NDWI."
            )

    with c3:

        with st.container(border=True):

            st.subheader("3️⃣ Let AI Find the Heat")

            st.write(
                "K-Means Clustering automatically identifies Urban Heat Island hotspots."
            )

    with c4:

        with st.container(border=True):

            st.subheader("4️⃣ Visualize & Act")

            st.write(
                "View risk maps, environmental insights and AI-powered recommendations."
            )

    st.divider()

    st.header("🌱 What's Next?")

    st.info(
        """
• Temporal Change Detection

• Real-Time Satellite Feeds

• Automated PDF Report Generation

We are constantly working to make UrbanHeat AI even smarter and more useful for planners, researchers and decision makers.
"""
    )