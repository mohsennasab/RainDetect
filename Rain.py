import os
from meteostat import Stations, Hourly, units
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, box
import contextily as ctx
import requests
from functools import partial
import urllib3

# Override requests.get to disable SSL verification for contextily
requests.get = partial(requests.get, verify=False)

# Suppress SSL warnings (optional but cleaner output)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define bounding box (top-left, bottom-right)
top_left = (45.181069, -93.558197)
bottom_right = (44.725272, -92.730103)

# ┌────────────────────────────────────────────────────────────────────┐
# │  📍 INSTRUCTIONS: Get Your Bounding Box Coordinates Using Website  │
# └────────────────────────────────────────────────────────────────────┘
#
# 1. Go to https://bboxfinder.com/
# 2. Use the interactive map to draw a rectangular area by clicking and dragging.
#    This defines the geographic area you're interested in.
# 3. Scroll to the bottom of the page and find the coordinates under:
#       ▶ EPSG:4326 - WGS 84
#    The format will look like this:
#       -95.745850,45.367584,-91.966553,47.189712
#
#    These represent:
#       [min_longitude, min_latitude, max_longitude, max_latitude]
#       ↳ In other words: [west, south, east, north]
#
# 4. To convert to the format used in this script:
#
#       top_left = (max_latitude, min_longitude)
#       bottom_right = (min_latitude, max_longitude)
#
#    📌 Example:
#       Given bbox string from bboxfinder:
#           -93.558197,44.725272,-92.730103,45.181069
#
#       You should define:
#           top_left = (45.181069, -93.558197)
#           bottom_right = (44.725272, -92.730103)


# Create output folder
os.makedirs("Downloads", exist_ok=True)

# Step 1: Get all stations in bounding box
stations = Stations().bounds(top_left, bottom_right).fetch()

# Save station metadata
stations.to_csv("Downloads/all_stations_metadata.csv", index=False)
print("✅ Saved all station metadata to 'all_stations_metadata.csv'")

# Step 2: Download hourly weather data for each station using its own available time range
for index, row in stations.iterrows():
    station_id = row.name
    start = row['hourly_start']
    end = row['hourly_end']

    if pd.isna(start) or pd.isna(end):
        print(f"⚠️ Skipping {station_id} due to missing hourly date range")
        continue

    print(f"📡 Fetching data for station {station_id} from {start.date()} to {end.date()}...")

    # Fetch and convert to imperial units
    ts = Hourly(station_id, start, end).convert(units.imperial)
    df = ts.fetch()

    if not df.empty:
        output_path = f"Downloads/{station_id}_hourly.csv"
        df.to_csv(output_path)
        print(f"✅ Saved hourly data to {output_path}")
    else:
        print(f"⚠️ No data found for station {station_id}")


# Step 3: Generate map of stations and bounding box

# Load the station metadata CSV
metadata_df = pd.read_csv("Downloads/all_stations_metadata.csv")
# Convert date columns to datetime (safe & explicit)
metadata_df["hourly_start"] = pd.to_datetime(metadata_df["hourly_start"])
metadata_df["hourly_end"] = pd.to_datetime(metadata_df["hourly_end"])


# Create GeoDataFrame from lat/lon
geometry = [Point(xy) for xy in zip(metadata_df['longitude'], metadata_df['latitude'])]
gdf = gpd.GeoDataFrame(metadata_df, geometry=geometry, crs="EPSG:4326")

# Convert to Web Mercator for basemap overlay
gdf_web = gdf.to_crs(epsg=3857)

# Create bounding box polygon and convert to GeoDataFrame
minx, miny = bottom_right[1], bottom_right[0]
maxx, maxy = top_left[1], top_left[0]
bbox_geom = box(minx, miny, maxx, maxy)
bbox_gdf = gpd.GeoDataFrame(geometry=[bbox_geom], crs="EPSG:4326").to_crs(epsg=3857)

# Plot
fig, ax = plt.subplots(figsize=(12, 10))
bbox_gdf.boundary.plot(ax=ax, color='black', linewidth=2, label='Bounding Box')
gdf_web.plot(ax=ax, color='red', markersize=60, zorder=5)

# Add labels on top of pins
for x, y, label in zip(gdf_web.geometry.x, gdf_web.geometry.y, gdf_web['name']):
    ax.text(x, y + 1000, label, fontsize=12, ha='center', color='darkblue')

# Add basemap and format
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=10, alpha=0.6)
ax.set_title("Hourly Rainfall Stations", fontsize=16)
ax.set_axis_off()
plt.tight_layout()

# Save
plt.savefig("Downloads/station_map.png", dpi=600)
print("🗺️ Map saved to 'station_map.png'")
