import streamlit as st


def show_kpi_cards(results):

    stats = results["recalculated_statistics"]

    ndvi_stats = results["ndvi_statistics_before_clipping"]

    method = results["method"]

    if method == "AI":

        hotspot_value = f'{results["hotspot_area_km2"]:.2f} km²'
        coverage_value = f'{results["high_risk_percentage"]:.1f}%'

    else:

        hotspot_value = f'{results["hotspot_area_km2"]:.2f} km²'
        coverage_value = f'{results["uhi_percentage"]:.2f}%'

    metrics = [

    (
        "assets/icons/urbanheat.svg",
        "Heat Affected Area",
        coverage_value,
        method,
    ),

    (
        "assets/icons/temperature.svg",
        "Avg Surface Temp.",
        f'{stats["mean"]:.2f}°C',
        f'Max {stats["maximum"]:.2f}°C',
    ),

    (
        "assets/icons/hotspots.svg",
        "Hotspot Area",
        hotspot_value,
        "",
    ),

    (
        "assets/icons/recommends.svg",
        "Mean NDVI",
        f'{ndvi_stats["mean"]:.3f}',
        "",
    ),

    (
        "assets/icons/detect.svg",
        "Detection Method",
        method,
        "",
    ),
]

    cols = st.columns(5)

    for col, metric in zip(cols, metrics):

        icon, title, value, delta = metric

        with col:

            with st.container(border=True):

                title_col, icon_col = st.columns([4.5, 2])

                with title_col:
                    st.markdown(title)

                with icon_col:
                    st.image(icon, width=60)

                st.metric(
                    label=" ",
                    value=value,
                    delta=delta,
                )