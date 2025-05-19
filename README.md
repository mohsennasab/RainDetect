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

To get started, create a virtual environment and install dependencies using the steps below.

### 1. Create and activate a virtual environment

```bash
python -m venv RainDetect
source RainDetect/bin/activate   # On Windows use: RainDetect\Scripts\activate
```
### 2. Install dependencies
Make sure you are in the root directory (where requirements.txt is located), then run:

```bash
python -m venv RainDetect
source RainDetect/bin/activate   # On Windows use: RainDetect\Scripts\activate
```
---

## 🤝 Contributing

Feel free to fork the repo and submit pull requests. Open an issue if you spot bugs or want to suggest features!

**Developed by:** Mohsen Tahmasebi Nasab, PhD  
🌐 [hydromohsen.com](https://www.hydromohsen.com)


---

## 📄 License

Custom Open-Source License

Copyright (c) 2024 Mohsen Tahmasebi Nasab

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to use, copy, and modify the Software for personal, academic, or internal non-commercial purposes, subject to the following conditions:

1. Commercial use, including but not limited to use in paid services, proprietary software, or as part of any commercial product or package, is not permitted without prior written permission from the copyright holder.

2. Redistribution of the Software, in part or in full, whether modified or unmodified, is also not permitted without prior written permission.

3. This copyright notice and license shall be included in all copies or substantial portions of the Software.

## Disclaimer
The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the author or copyright holder be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software, including but not limited to any direct, indirect, incidental, special, exemplary, or consequential damages.

---
