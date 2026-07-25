"""Reusable processing and plotting utilities for Urban Heat Island detection.

This module is a direct refactor of the supplied Colab notebook. Scientific
constants, formulas, thresholds, sampling, K-Means settings, cluster-to-risk
mapping, and percentage denominators are intentionally unchanged.
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from rasterio.io import MemoryFile
from sklearn.cluster import KMeans
from pathlib import Path


# Landsat 9 thermal calibration constants used by the notebook.
ML = 3.8000e-04
AL = 0.10000
K1 = 799.0284
K2 = 1329.2405


def read_raster_band(file_bytes: bytes) -> np.ndarray:
    """Read band 1 of an uploaded raster as float32."""
    with MemoryFile(file_bytes) as memory_file:
        with memory_file.open() as source:
            return (
                source.read(1).astype(np.float32),
                abs(source.transform.a),
                abs(source.transform.e),
            )


def load_landsat_bands(
    green_bytes: bytes,
    red_bytes: bytes,
    nir_bytes: bytes,
    swir1_bytes: bytes,
    thermal_bytes: bytes,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    """Load and validate Red, NIR, and Thermal Landsat bands."""
    green, pixel_width, pixel_height = read_raster_band(green_bytes)

    red, _, _ = read_raster_band(red_bytes)

    nir, _, _ = read_raster_band(nir_bytes)

    swir1, _, _ = read_raster_band(swir1_bytes)

    thermal, _, _ = read_raster_band(thermal_bytes)

    pixel_area_km2 = (pixel_width * pixel_height) / 1_000_000

    if not (
    green.shape
    == red.shape
    == nir.shape
    == swir1.shape
    == thermal.shape
):
        raise ValueError(
            "All Landsat bands must have identical dimensions."
            f"Received Red {red.shape}, NIR {nir.shape}, Thermal {thermal.shape}."
        )
    return (
    green,
    red,
    nir,
    swir1,
    thermal,
    pixel_area_km2,
)

def load_sample_dataset(city="Lucknow"):
    """
    Load the default sample Landsat dataset from the project.
    """
    dataset_path = Path(f"data/raw/{city}")
    green_path = next(dataset_path.glob("*_B3.TIF"))
    red_path = next(dataset_path.glob("*_B4.TIF"))
    nir_path = next(dataset_path.glob("*_B5.TIF"))
    swir1_path = next(dataset_path.glob("*_B6.TIF"))
    thermal_path = next(dataset_path.glob("*_B10.TIF"))

    with open(green_path, "rb") as f:
        green_bytes = f.read()

    with open(red_path, "rb") as f:
        red_bytes = f.read()

    with open(nir_path, "rb") as f:
        nir_bytes = f.read()

    with open(swir1_path, "rb") as f:
        swir1_bytes = f.read()

    with open(thermal_path, "rb") as f:
        thermal_bytes = f.read()

    return load_landsat_bands(
        green_bytes,
        red_bytes,
        nir_bytes,
        swir1_bytes,
        thermal_bytes,
    )


def calculate_ndvi(red: np.ndarray, nir: np.ndarray) -> dict[str, Any]:
    """Calculate NDVI with the notebook's original operation order."""
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir - red) / (nir + red)

    # Preserve both divide-by-zero steps present in the notebook.
    ndvi = np.where((nir + red) == 0, 0, ndvi)
    ndvi = np.divide(
        nir - red,
        nir + red,
        out=np.zeros_like(nir),
        where=(nir + red) != 0,
    )

    # The notebook reports these statistics before clipping.
    statistics_before_clipping = {
        "minimum": np.nanmin(ndvi),
        "maximum": np.nanmax(ndvi),
        "mean": np.nanmean(ndvi),
    }
    ndvi = np.clip(ndvi, -1, 1)

    return {
        "ndvi": ndvi,
        "statistics_before_clipping": statistics_before_clipping,
    }

def calculate_ndbi(
    nir: np.ndarray,
    swir1: np.ndarray,
) -> dict[str, Any]:
    """Calculate NDBI."""

    with np.errstate(divide="ignore", invalid="ignore"):
        ndbi = (swir1 - nir) / (swir1 + nir)

    ndbi = np.divide(
        swir1 - nir,
        swir1 + nir,
        out=np.zeros_like(swir1),
        where=(swir1 + nir) != 0,
    )

    ndbi = np.clip(ndbi, -1, 1)

    return {
        "ndbi": ndbi,
        "statistics": {
            "minimum": np.nanmin(ndbi),
            "maximum": np.nanmax(ndbi),
            "mean": np.nanmean(ndbi),
        },
    }

def calculate_ndwi(
    green: np.ndarray,
    nir: np.ndarray,
) -> dict[str, Any]:
    """Calculate NDWI."""

    with np.errstate(divide="ignore", invalid="ignore"):
        ndwi = (green - nir) / (green + nir)

    ndwi = np.divide(
        green - nir,
        green + nir,
        out=np.zeros_like(green),
        where=(green + nir) != 0,
    )

    ndwi = np.clip(ndwi, -1, 1)

    return {
        "ndwi": ndwi,
        "statistics": {
            "minimum": np.nanmin(ndwi),
            "maximum": np.nanmax(ndwi),
            "mean": np.nanmean(ndwi),
        },
    }


def estimate_land_surface_temperature(thermal: np.ndarray) -> dict[str, Any]:
    """Convert thermal DN values to brightness temperature in Celsius."""
    # Initial calculation before invalid thermal pixels are masked.
    initial_radiance = ML * thermal + AL
    initial_bt = K2 / np.log((K1 / initial_radiance) + 1)
    initial_bt_celsius = initial_bt - 273.15
    initial_statistics = {
        "minimum": np.nanmin(initial_bt_celsius),
        "maximum": np.nanmax(initial_bt_celsius),
        "mean": np.nanmean(initial_bt_celsius),
    }

    # Mask invalid pixels and repeat the calculation, exactly as in the notebook.
    masked_thermal = thermal.copy()
    masked_thermal[masked_thermal == 0] = np.nan
    radiance = ML * masked_thermal + AL
    bt = K2 / np.log((K1 / radiance) + 1)
    bt_celsius = bt - 273.15

    recalculated_statistics = {
        "minimum": np.nanmin(bt_celsius),
        "maximum": np.nanmax(bt_celsius),
        "mean": np.nanmean(bt_celsius),
        "standard_deviation": np.nanstd(bt_celsius),
    }
    diagnostics = {
        "pixels_below_20_celsius": np.sum(bt_celsius < 20),
        "total_pixels": bt_celsius.size,
        "1st_percentile": np.nanpercentile(bt_celsius, 1),
        "5th_percentile": np.nanpercentile(bt_celsius, 5),
        "95th_percentile": np.nanpercentile(bt_celsius, 95),
        "99th_percentile": np.nanpercentile(bt_celsius, 99),
    }

    return {
        "masked_thermal": masked_thermal,
        "radiance": radiance,
        "brightness_temperature_kelvin": bt,
        "temperature_celsius": bt_celsius,
        "initial_statistics": initial_statistics,
        "recalculated_statistics": recalculated_statistics,
        "diagnostics": diagnostics,
    }


def run_common_processing(
    green: np.ndarray,
    red: np.ndarray,
    nir: np.ndarray,
    swir1: np.ndarray,
    thermal: np.ndarray,
) -> dict[str, Any]:
    """Run calculations shared by both detection approaches."""

    ndvi_result = calculate_ndvi(red, nir)

    ndbi_result = calculate_ndbi(nir, swir1)

    ndwi_result = calculate_ndwi(green, nir)

    temperature_result = estimate_land_surface_temperature(thermal)

    return {
    "green": green,
    "red": red,
    "nir": nir,
    "swir1": swir1,
    "thermal": thermal,

    "ndvi": ndvi_result["ndvi"],
    "ndvi_statistics_before_clipping": ndvi_result[
        "statistics_before_clipping"
    ],

    "ndbi": ndbi_result["ndbi"],
    "ndbi_statistics": ndbi_result["statistics"],

    "ndwi": ndwi_result["ndwi"],
    "ndwi_statistics": ndwi_result["statistics"],

    **temperature_result,
}


def run_threshold_detection(
    ndvi: np.ndarray,
    bt_celsius: np.ndarray,
    pixel_area_km2: float,
) -> dict[str, Any]:
    """Run the notebook's threshold-based UHI calculations."""
    mean_temp = np.nanmean(bt_celsius)
    std_temp = np.nanstd(bt_celsius)
    threshold = mean_temp + std_temp

    uhi = np.where(
        (bt_celsius > threshold) & (ndvi < 0.2),
        1,
        0,
    )

    rows, cols = uhi.shape
    row_slice = slice(rows // 4, 3 * rows // 4)
    col_slice = slice(cols // 4, 3 * cols // 4)
    crop = uhi[row_slice, col_slice]
    crop_temp = bt_celsius[row_slice, col_slice]
    crop_ndvi = ndvi[row_slice, col_slice]

    uhi_pixels = np.sum(uhi == 1)
    hotspot_area_km2 = uhi_pixels * pixel_area_km2
    total_pixels = uhi.size
    north = uhi[: rows // 2, :]
    south = uhi[rows // 2 :, :]
    north_percent = (np.sum(north == 1) / north.size) * 100
    south_percent = (np.sum(south == 1) / south.size) * 100

    # Preserve the independently rebuilt threshold risk map.
    risk_map = np.zeros_like(bt_celsius)
    risk_map[bt_celsius < mean_temp] = 1
    risk_map[
        (bt_celsius >= mean_temp)
        & (bt_celsius <= mean_temp + std_temp)
    ] = 2
    risk_map[bt_celsius > mean_temp + std_temp] = 3

    low_risk_percentage = np.sum(risk_map == 1) / total_pixels * 100

    moderate_risk_percentage = (
        np.sum(risk_map == 2) / total_pixels * 100
    )

    high_risk_percentage = (
        np.sum(risk_map == 3) / total_pixels * 100
    )

    return {
        "mean_temperature": mean_temp,
        "standard_deviation": std_temp,
        "uhi_threshold": threshold,
        "uhi": uhi,
        "crop_uhi": crop,
        "crop_temperature": crop_temp,
        "crop_ndvi": crop_ndvi,
        "uhi_pixels": uhi_pixels,
        "total_pixels": total_pixels,
        "uhi_percentage": (uhi_pixels / total_pixels) * 100,
        "hotspot_area_km2": hotspot_area_km2,
        "north_uhi_percentage": north_percent,
        "south_uhi_percentage": south_percent,
        "risk_map": risk_map,
        "low_risk_percentage": low_risk_percentage,
        "moderate_risk_percentage": moderate_risk_percentage,
        "high_risk_percentage": high_risk_percentage,
    }


def run_ai_detection(
    ndvi: np.ndarray,
    bt_celsius: np.ndarray,
    pixel_area_km2,
) -> dict[str, Any]:
    """Run the notebook's K-Means UHI risk analysis unchanged."""
    temp_flat = bt_celsius.ravel()
    ndvi_flat = ndvi.ravel()

    # The original mask is based only on temperature NaN values.
    mask = ~np.isnan(temp_flat)
    temp_clean = temp_flat[mask]
    ndvi_clean = ndvi_flat[mask]
    features = np.column_stack((temp_clean, ndvi_clean))

    sample_size = min(100000, features.shape[0])
    if sample_size < 3:
        raise ValueError(
            "At least three valid thermal pixels are required for "
            "three-cluster K-Means detection."
        )

    # Intentionally no NumPy sampling seed: the notebook does not set one.
    indices = np.random.choice(
        features.shape[0],
        sample_size,
        replace=False,
    )
    sample = features[indices]

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(sample)

    labels_full = np.full(temp_flat.shape, -1)
    labels_full[mask] = kmeans.predict(features)
    ai_risk_map = labels_full.reshape(bt_celsius.shape)

    # Preserve the notebook's fixed cluster-ID-to-risk mapping.
    # Order clusters by their average temperature
    cluster_temperatures = {}

    for cluster in range(3):
        cluster_pixels = temp_clean[labels_full[mask] == cluster]
        cluster_temperatures[cluster] = np.mean(cluster_pixels)

    sorted_clusters = sorted(
        cluster_temperatures,
        key=cluster_temperatures.get,
    )

    cluster_to_risk = {
        sorted_clusters[0]: 1,   # Low
        sorted_clusters[1]: 2,   # Moderate
        sorted_clusters[2]: 3,   # High
    }

    ai_ordered = np.zeros_like(ai_risk_map)

    for cluster, risk in cluster_to_risk.items():
        ai_ordered[ai_risk_map == cluster] = risk

    total = ai_ordered.size

    high_risk_pixels = np.sum(ai_ordered == 3)
    hotspot_area_km2 = high_risk_pixels * pixel_area_km2

    low = np.sum(ai_ordered == 1) / total * 100
    moderate = np.sum(ai_ordered == 2) / total * 100
    high = np.sum(ai_ordered == 3) / total * 100

    return {
        "feature_matrix_shape": features.shape,
        "sample_shape": sample.shape,
        "cluster_centers": kmeans.cluster_centers_,
        "ai_risk_map": ai_risk_map,
        "ai_ordered": ai_ordered,
        "low_risk_percentage": low,
        "moderate_risk_percentage": moderate,
        "high_risk_percentage": high,
        "hotspot_area_km2": hotspot_area_km2,
    }


def plot_ndvi_map(
    ndvi: np.ndarray,
    title: str = "NDVI Map",
    colorbar_label: str | None = "NDVI",
    figsize: tuple[int, int] = (8, 6),
) -> plt.Figure:
    """Create an NDVI visualization with the notebook's styling."""
    figure, axis = plt.subplots(figsize=figsize)
    image = axis.imshow(ndvi, cmap="RdYlGn")
    colorbar = figure.colorbar(image, ax=axis)
    if colorbar_label is not None:
        colorbar.set_label(colorbar_label)
    axis.set_title(title)
    return figure


def plot_temperature_distribution(bt_celsius: np.ndarray) -> plt.Figure:
    """Create the notebook's 100-bin temperature histogram."""
    figure, axis = plt.subplots()
    axis.hist(bt_celsius.flatten(), bins=100)
    axis.set_title("Temperature Distribution")
    axis.set_xlabel("Temperature (°C)")
    axis.set_ylabel("Frequency")
    return figure


def plot_uhi_map(uhi: np.ndarray) -> plt.Figure:
    """Create the threshold UHI map."""
    figure, axis = plt.subplots(figsize=(8, 6))
    image = axis.imshow(uhi, cmap="Reds")
    figure.colorbar(image, ax=axis, label="UHI Zones")
    axis.set_title("Urban Heat Island Map")
    return figure


def plot_uhi_overlay(
    bt_celsius: np.ndarray,
    uhi: np.ndarray,
) -> plt.Figure:
    """Overlay threshold UHI zones on grayscale temperature."""
    figure, axis = plt.subplots(figsize=(10, 8))
    axis.imshow(bt_celsius, cmap="gray")
    image = axis.imshow(uhi, cmap="Reds", alpha=0.6)
    figure.colorbar(image, ax=axis, label="UHI Zones")
    axis.set_title("Urban Heat Island Overlay")
    return figure


def plot_zoomed_uhi(
    crop_temperature: np.ndarray,
    crop_uhi: np.ndarray,
) -> plt.Figure:
    """Create the center-cropped UHI overlay."""
    figure, axis = plt.subplots(figsize=(8, 6))
    axis.imshow(crop_temperature, cmap="gray")
    axis.imshow(crop_uhi, cmap="Reds", alpha=0.6)
    axis.set_title("Zoomed Urban Heat Island")
    return figure


def plot_temperature_map(bt_celsius: np.ndarray) -> plt.Figure:
    """Create the land surface temperature map."""
    figure, axis = plt.subplots(figsize=(8, 6))
    image = axis.imshow(bt_celsius, cmap="hot")
    figure.colorbar(image, ax=axis, label="Temperature (°C)")
    axis.set_title("Land Surface Temperature Map")
    return figure


def plot_risk_map(risk_map: np.ndarray, title: str) -> plt.Figure:
    """Create a threshold or AI risk-level map."""
    figure, axis = plt.subplots(figsize=(8, 6))
    display_map = risk_map

    max_dimension = 1000

    height, width = display_map.shape

    step = max(1, max(height, width) // max_dimension)

    display_map = display_map[::step, ::step]
    image = axis.imshow(
    display_map,
    cmap="RdYlGn_r",
    vmin=1,
    vmax=3,
)
    colorbar = figure.colorbar(image, ax=axis)

    colorbar.set_ticks([1, 2, 3])

    colorbar.set_ticklabels([
        "Low",
        "Moderate",
        "High",
    ])

    colorbar.set_label("Risk Level")
    axis.set_title(title)
    return figure


def generate_cause_analysis(
    ndvi_stats,
    ndbi_stats,
    ndwi_stats,
    temperature_stats,
):
    """
    Generate a human-readable explanation of why
    Urban Heat Islands are present.
    """

    causes = []

    if ndvi_stats["mean"] < 0.2:
        causes.append(
            "Sparse vegetation detected, reducing natural cooling."
        )

    if ndbi_stats["mean"] > 0.2:
        causes.append(
            "Dense built-up surfaces are increasing heat absorption."
        )

    if ndwi_stats["mean"] < 0:
        causes.append(
            "Low water presence limits evaporative cooling."
        )

    if temperature_stats["mean"] > 35:
        causes.append(
            "High land surface temperatures indicate severe heat accumulation."
        )

    if not causes:
        causes.append(
            "No dominant environmental cause was identified."
        )

    return causes


def run_analysis(
    green_path,
    red_path,
    nir_path,
    swir1_path,
    thermal_path,
    method="AI",
):
    """
    Runs the complete Urban Heat Island analysis pipeline.

    Parameters:
        red_path (str): Path to Landsat Band 4 (Red)
        nir_path (str): Path to Landsat Band 5 (NIR)
        thermal_path (str): Path to Landsat Band 10 (Thermal)
        method (str): "AI" or "Threshold"

    Returns:
        dict: All analysis results
    """

    results = {}

    # Step 1: Load Landsat Bands

    # Load Sample Dataset
    if red_path is None:
        city = green_path if green_path else "Lucknow"
        green, red, nir, swir1, thermal,pixel_area_km2 = load_sample_dataset(city)

    # Load Uploaded Dataset
    else:

        green_bytes = green_path.read()
        red_bytes = red_path.read()
        nir_bytes = nir_path.read()
        swir1_bytes = swir1_path.read()
        thermal_bytes = thermal_path.read()

        green, red, nir, swir1, thermal, pixel_area_km2 = load_landsat_bands(
            green_bytes,
            red_bytes,
            nir_bytes,
            swir1_bytes,
            thermal_bytes,
        )

    # Step 2 & 3: Run Common Processing (NDVI + LST)

    common = run_common_processing(
        green,
        red,
        nir,
        swir1,
        thermal,
    )

    results.update(common)
    results["pixel_area_km2"] = pixel_area_km2

    # Step 4: Detect Urban Heat Islands

    if method.upper() == "AI":

        detection = run_ai_detection(
            common["ndvi"],
            common["temperature_celsius"],
            pixel_area_km2,
        )

    else:

        detection = run_threshold_detection(
            common["ndvi"],
            common["temperature_celsius"],
            pixel_area_km2,
        )

    results.update(detection)

    
    print("Heatmap array shape:", detection["ai_ordered"].shape if method.upper() == "AI" else detection["risk_map"].shape)
    heatmap = detection["ai_ordered"] if method.upper() == "AI" else detection["risk_map"]

    print("Heatmap array shape:", heatmap.shape)
    print("Pixels:", heatmap.size)

    if method.upper() == "AI":
        if "heatmap_figure" not in results:

            results["heatmap_figure"] = plot_risk_map(
                detection["ai_ordered"],
                "Urban Heat Map",
            )

    else:
        if "heatmap_figure" not in results:

            results["heatmap_figure"] = plot_risk_map(
                detection["risk_map"],
                "Urban Heat Map",
            )

    results["method"] = method

    # Step 5: Cause Analysis

    results["causes"] = generate_cause_analysis(
        results["ndvi_statistics_before_clipping"],
        results["ndbi_statistics"],
        results["ndwi_statistics"],
        results["recalculated_statistics"],
    )

    # Step 6-7
    # Will be implemented later.

    results["priority"] = None
    results["recommendations"] = None

    return results

    return results
