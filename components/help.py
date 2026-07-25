import streamlit as st


def show_help():

    st.title("❓ Help Center")

    st.write(
        "Everything you need to use UrbanHeat AI efficiently."
    )

    st.divider()

    st.header("🚀 Getting Started")

    with st.expander("1. How do I analyze a city?"):

        st.write("""
1. Go to the **Home** page.
2. Select a sample city or upload your own Landsat dataset.
3. Click **Start Analysis**.
4. Wait for processing to complete.
5. Explore the Dashboard for results.
""")

    with st.expander("2. Which satellite data is supported?"):

        st.write("""
UrbanHeat AI currently supports:

- Landsat 8
- Landsat 9

Required bands include:

- Red (B4)
- Near Infrared (B5)
- Thermal (B10)
""")

    with st.expander("3. What file format should I upload?"):

        st.write("""
Upload GeoTIFF (.TIF) satellite bands.

Ensure all required bands belong to the same acquisition date.
""")

    st.divider()

    st.header("📊 Understanding the Results")

    with st.expander("🌡️ Land Surface Temperature (LST)"):

        st.write("""
Shows how hot the land surface is.

Higher temperatures generally indicate stronger Urban Heat Island effects.
""")

    with st.expander("🌿 NDVI"):

        st.write("""
Normalized Difference Vegetation Index.

Higher NDVI means healthier vegetation.

Lower NDVI usually indicates built-up or barren land.
""")

    with st.expander("🏢 NDBI"):

        st.write("""
Normalized Difference Built-up Index.

Higher values represent urban or concrete areas.
""")

    with st.expander("💧 NDWI"):

        st.write("""
Normalized Difference Water Index.

Used to identify rivers, lakes and other water bodies.
""")

    with st.expander("🤖 AI Risk Map"):

        st.write("""
The AI Risk Map is generated using K-Means Clustering.

It automatically groups areas into different heat-risk zones based on environmental characteristics.
""")

    st.divider()

    st.header("⚠ Frequently Asked Questions")

    with st.expander("Analysis takes a long time"):

        st.write("""
Large satellite datasets require additional processing time.

Please wait until processing is complete before leaving the page.
""")

    with st.expander("Why are temperatures different from weather apps?"):

        st.write("""
UrbanHeat AI measures **Land Surface Temperature (LST)**.

Weather apps report **Air Temperature**.

These are different measurements.
""")

    with st.expander("Can I compare two cities?"):

        st.write("""
Yes.

Open the **Compare Cities** page and select two available cities for comparison.
""")

    with st.expander("Which AI model is used?"):

        st.write("""
UrbanHeat AI currently uses K-Means Clustering to identify Urban Heat Island zones automatically.
""")

    st.divider()

    st.header("📌 Tips")

    st.info("""
• Use cloud-free satellite images.

• Compare cities captured during similar seasons.

• Higher NDVI generally indicates cooler regions.

• Higher NDBI generally indicates hotter urban regions.

• Review AI recommendations before planning interventions.
""")

    st.divider()

    st.success(
        "Need more assistance? Future versions of UrbanHeat AI will include an integrated AI Planning Assistant."
    )