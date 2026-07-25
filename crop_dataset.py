from pathlib import Path
import rasterio
from rasterio.windows import Window

# -----------------------------
# CHANGE THESE IF NEEDED
# -----------------------------

INPUT_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/cropped")

# Percentage of image to keep
KEEP_PERCENT = 50      # try 50 first

# -----------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

cities = ["Lucknow", "Delhi", "Bengaluru"]

for city in cities:

    city_input = INPUT_DIR / city
    city_output = OUTPUT_DIR / city
    city_output.mkdir(parents=True, exist_ok=True)

    print(f"\nProcessing {city}")

    for tif in city_input.glob("*.TIF"):

        with rasterio.open(tif) as src:

            width = src.width
            height = src.height

            crop_w = int(width * KEEP_PERCENT / 100)
            crop_h = int(height * KEEP_PERCENT / 100)

            x0 = (width - crop_w) // 2
            y0 = (height - crop_h) // 2

            window = Window(x0, y0, crop_w, crop_h)

            image = src.read(window=window)

            transform = src.window_transform(window)

            profile = src.profile

            profile.update(
                width=crop_w,
                height=crop_h,
                transform=transform,
                compress="lzw"
            )

            out_file = city_output / tif.name

            with rasterio.open(out_file, "w", **profile) as dst:
                dst.write(image)

        print(f"Saved {out_file}")

print("\nFinished!")