import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# === CONFIGURATION ===
rainfall_threshold = 0.04  # inches/hour to define a "wet" hour
cumulative_threshold = 2.85  # inches total to keep an event
duration_threshold = 6  # hours, minimum event duration to include
gap_hours = 1  # number of dry hours allowed between wet hours


# Input file
input_file = r"Downloads\72658_hourly.csv"  # your rainfall CSV file

# Create output folder based on input file name (without extension)
base_name = os.path.splitext(os.path.basename(input_file))[0]
output_root = os.path.join("ProcessedEvents", base_name)
os.makedirs(output_root, exist_ok=True)

# Output paths
output_events_csv = os.path.join(output_root, "rainfall_events_filtered.csv")
hyetograph_dir = os.path.join(output_root, "Hyetographs")
cumulative_dir = os.path.join(output_root, "Cumulative Plots")
comparison_plot_path = os.path.join(output_root, "normalized_event_comparison.png")

# Create subfolders
os.makedirs(hyetograph_dir, exist_ok=True)
os.makedirs(cumulative_dir, exist_ok=True)


# === STEP 1: LOAD AND PREPARE DATA ===
def load_rainfall_data(file_path):
    df = pd.read_csv(file_path)
    df['time'] = pd.to_datetime(df['time'])
    df['prcp'] = pd.to_numeric(df['prcp'], errors='coerce').fillna(0)
    df = df.sort_values('time')
    return df


# === STEP 2: IDENTIFY RAINFALL EVENTS ===
def identify_events(df, rainfall_thresh, gap_thresh):
    df['is_wet'] = df['prcp'] >= rainfall_thresh
    event_id = 0
    gap_counter = 0
    event_ids = []

    for i in range(len(df)):
        if df.iloc[i]['is_wet']:
            if gap_counter > gap_thresh:
                event_id += 1
            gap_counter = 0
            event_ids.append(event_id)
        else:
            gap_counter += 1
            if gap_counter <= gap_thresh:
                event_ids.append(event_id)
            else:
                event_ids.append(None)

    df['event_id'] = event_ids
    return df


# === STEP 3: FILTER EVENTS ===
def get_filtered_events(df, cumulative_thresh):
    events = (
        df.dropna(subset=['event_id'])
        .groupby('event_id')
        .agg(
            start_time=('time', 'min'),
            end_time=('time', 'max'),
            duration_hr=('time', lambda x: (x.max() - x.min()).total_seconds() / 3600 + 1),
            total_rainfall_in=('prcp', 'sum')
        )
        .reset_index()
    )
    return events[
        (events['total_rainfall_in'] >= cumulative_thresh) &
        (events['duration_hr'] >= duration_threshold)
    ]


# === STEP 4A: PLOT HYETOGRAPH ===
def plot_hyetograph(event_df, event_id):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(event_df['time'], event_df['prcp'], width=0.03, color='blue')
    ax.set_title(f"Hyetograph - Event {event_id}")

    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.set_xlabel("Time (YYYY-MM-DD HH:MM)")

    ax.set_ylabel("Rainfall (in/hr)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(os.path.join(hyetograph_dir, f"event_{event_id}_hyetograph.png"))
    event_df.to_csv(os.path.join(hyetograph_dir, f"event_{event_id}_data.csv"), index=False)
    plt.close(fig)


# === STEP 4B: PLOT CUMULATIVE ===
def plot_cumulative(event_df, event_id):
    event_df = event_df.copy()
    event_df['cumulative'] = event_df['prcp'].cumsum()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(event_df['time'], event_df['cumulative'], marker='o', color='green')
    ax.set_title(f"Cumulative Rainfall - Event {event_id}")

    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.set_xlabel("Time (YYYY-MM-DD HH:MM)")

    ax.set_ylabel("Cumulative Rainfall (in)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig.savefig(os.path.join(cumulative_dir, f"event_{event_id}_cumulative.png"))
    event_df.to_csv(os.path.join(cumulative_dir, f"event_{event_id}_cumulative.csv"), index=False)
    plt.close(fig)


# === STEP 4C: NORMALIZED COMPARISON PLOT ===
def plot_normalized_comparison(events_data, output_file):
    plt.figure(figsize=(8, 6))
    for event_id, df in events_data:
        df = df.copy()
        df['cumulative'] = df['prcp'].cumsum()
        df['pct_time'] = ((df['time'] - df['time'].min()) /
                          (df['time'].max() - df['time'].min())).fillna(0)
        df['pct_rain'] = df['cumulative'] / df['cumulative'].iloc[-1]
        plt.plot(df['pct_time'] * 100, df['pct_rain'] * 100, label=f"Event {event_id}")
    plt.xlabel("Percent Duration (%)")
    plt.ylabel("Percent Cumulative Rainfall (%)")
    plt.title("Normalized Rainfall Events")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# === STEP 4D: SAVE NORMALIZED EVENT DATA TO CSV ===
def save_normalized_comparison_data(events_data, output_csv):
    normalized_rows = []
    for event_id, df in events_data:
        df = df.copy()
        df['cumulative'] = df['prcp'].cumsum()
        duration = (df['time'].max() - df['time'].min()).total_seconds()
        if duration == 0 or df['cumulative'].iloc[-1] == 0:
            continue  # skip degenerate cases
        df['pct_time'] = ((df['time'] - df['time'].min()) / (df['time'].max() - df['time'].min())) * 100
        df['pct_rain'] = (df['cumulative'] / df['cumulative'].iloc[-1]) * 100

        for _, row in df.iterrows():
            normalized_rows.append({
                "event_id": event_id,
                "percent_duration": round(row['pct_time'], 2),
                "percent_cumulative_rainfall": round(row['pct_rain'], 2)
            })

    pd.DataFrame(normalized_rows).to_csv(output_csv, index=False)
    print(f"📄 Normalized comparison data saved to {output_csv}")



# === MAIN WORKFLOW ===
if __name__ == "__main__":
    df = load_rainfall_data(input_file)
    print("⏳ Please wait while the code identifies and separates rainfall events...")
    df = identify_events(df, rainfall_threshold, gap_hours)
    filtered_events = get_filtered_events(df, cumulative_threshold)
    print(f"✅ Identified {len(filtered_events)} rainfall events that meet the thresholds.")
    filtered_events.to_csv(output_events_csv, index=False)

    all_event_data = []
    for _, row in filtered_events.iterrows():
        eid = int(row['event_id'])
        event_df = df[df['event_id'] == eid][['time', 'prcp']]
        plot_hyetograph(event_df, eid)
        plot_cumulative(event_df, eid)
        all_event_data.append((eid, event_df))

    plot_normalized_comparison(all_event_data, comparison_plot_path)
    normalized_csv_path = os.path.join(output_root, "normalized_event_comparison.csv")
    save_normalized_comparison_data(all_event_data, normalized_csv_path)

    print("✅ All plots and data saved.")
