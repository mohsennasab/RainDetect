# Rainfall Station Explorer + Event Analyzer

<p align="center">
  <img src="Images/Logo.png" alt="Project Logo" width="300"/>
</p>


This two-part Python project helps identify rainfall stations in a user-defined area, download hourly precipitation data, and extract and analyze individual storm events using customizable thresholds. It outputs both data and visuals to support hydrologic and climate analysis workflows.

---

## 🧭 Workflow Summary

### Step 1️⃣ `Rain.py` – Station Discovery & Hourly Data Download
- Accepts a bounding box
- Finds all NOAA stations with hourly data in that area
- Downloads full hourly precipitation records (converted to **Imperial units**)
- Saves a map showing bounding box and station locations

### Step 2️⃣ `EventFinder.py` – Storm Event Identification & Visualization
- Analyzes hourly precipitation CSV from Step 1
- Identifies storm events using:
  - Rainfall intensity threshold
  - Max gap between rainy hours
  - Minimum total rainfall
  - Minimum storm duration
- Generates:
  - Hyetographs
  - Cumulative rainfall plots
  - Normalized comparison charts (with underlying CSV)

---

## 📌 Features

### ✅ `Rain.py` Outputs

- `Downloads/all_stations_metadata.csv`  
- `Downloads/{station_id}_hourly.csv`  
- `Downloads/station_map.png`  

### ✅ `EventFinder.py` Outputs

Saved inside `ProcessedEvents/<station_id>/`:

- `rainfall_events_filtered.csv` – Filtered storm summary  
- `Hyetographs/` – Bar plots of rainfall by hour  
- `Cumulative Plots/` – Line charts of cumulative rain  
- `normalized_event_comparison.png` – Comparison across storms  
- `normalized_event_comparison.csv` – Underlying data  

---

## ⚙️ Configuration

Set these thresholds at the top of `EventFinder.py`:

```python
rainfall_threshold = 0.04        # in/hr to define a wet hour
cumulative_threshold = 2.85      # total inches required
duration_threshold = 6           # hours, minimum duration
gap_hours = 1                    # allowable dry hours between wet hours
```

---

## 🧭 How to Define the Bounding Box (in `Rain.py`)

1. Visit [bboxfinder.com](https://bboxfinder.com)
2. Draw your desired region
3. Copy the EPSG:4326 coordinates:
   ```
   min_lon, min_lat, max_lon, max_lat
   ```
4. Convert to Python format:

```python
top_left = (max_lat, min_lon)
bottom_right = (min_lat, max_lon)
```

---

## 📏 Units Used

This tool converts all data to **Imperial Units** before analysis.

| Parameter        | Unit              |
|------------------|-------------------|
| Rainfall         | inches             |
| Time             | datetime           |
| Temperature      | °F (if used)       |
| Wind speed       | mph (if used)      |

📝 See `hourly_weather_columns_converted.md` for full details.

---

## 🧪 Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install pandas geopandas matplotlib shapely contextily requests meteostat
```

---

## 🚧 Roadmap

- [ ] Add UI for threshold selection and batch upload
- [ ] Event detection summary across multiple stations
- [ ] Export GIS-ready shapefiles of event time ranges
- [ ] Add NOAA gridded rainfall dataset compatibility

---

## 👤 Author

**Mohsen Tahmasebi Nasab**  
Water Resources Engineer | Python Automation Advocate

---

## 📄 License

Open-source. Please cite [Meteostat](https://meteostat.net/) for all meteorological data used in this project.
