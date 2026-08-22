import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group

sns.set_theme(style="whitegrid")

print("Connecting to feature store...")
fs = get_feature_store()
fg = get_or_create_aqi_feature_group(fs)
df = fg.read()
df = df.sort_values("timestamp").reset_index(drop=True)
print(f"Loaded {len(df)} rows.\n")

# --- 1. AQI over time ---
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df["timestamp"], df["aqi"], linewidth=0.8, color="darkorange")
ax.set_title("Rawalpindi AQI Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("AQI (1-5 scale)")
plt.tight_layout()
plt.savefig("notebooks/eda_aqi_over_time.png", dpi=120)
plt.close()
print("Saved: eda_aqi_over_time.png")

# --- 2. AQI distribution ---
fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(x="aqi", data=df, hue="aqi", palette="YlOrRd", legend=False, ax=ax)
ax.set_title("Distribution of AQI Readings")
ax.set_xlabel("AQI Category (1=Good ... 5=Very Poor)")
ax.set_ylabel("Number of Hourly Readings")
plt.tight_layout()
plt.savefig("notebooks/eda_aqi_distribution.png", dpi=120)
plt.close()
print("Saved: eda_aqi_distribution.png")

# --- 3. Average AQI by month (seasonal pattern) ---
fig, ax = plt.subplots(figsize=(9, 5))
monthly_avg = df.groupby("month")["aqi"].mean().reindex(range(1, 13))
monthly_avg.plot(kind="bar", color="firebrick", ax=ax)
ax.set_title("Average AQI by Month (Seasonal Pattern)")
ax.set_xlabel("Month")
ax.set_ylabel("Average AQI")
plt.tight_layout()
plt.savefig("notebooks/eda_aqi_by_month.png", dpi=120)
plt.close()
print("Saved: eda_aqi_by_month.png")

# --- 4. Average AQI by hour of day ---
fig, ax = plt.subplots(figsize=(9, 5))
hourly_avg = df.groupby("hour")["aqi"].mean().reindex(range(24))
hourly_avg.plot(kind="line", marker="o", color="steelblue", ax=ax)
ax.set_title("Average AQI by Hour of Day")
ax.set_xlabel("Hour (UTC)")
ax.set_ylabel("Average AQI")
ax.set_xticks(range(0, 24, 2))
plt.tight_layout()
plt.savefig("notebooks/eda_aqi_by_hour.png", dpi=120)
plt.close()
print("Saved: eda_aqi_by_hour.png")

# --- 5. Correlation heatmap among pollutants + AQI ---
pollutant_cols = ["aqi", "co", "no2", "so2", "o3", "pm2_5", "pm10", "nh3"]
fig, ax = plt.subplots(figsize=(8, 6))
corr = df[pollutant_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation Between AQI and Pollutants")
plt.tight_layout()
plt.savefig("notebooks/eda_correlation_heatmap.png", dpi=120)
plt.close()
print("Saved: eda_correlation_heatmap.png")

# --- Text summary ---
print("\n--- Summary Statistics ---")
print(df[pollutant_cols].describe().round(2))
print(f"\nMost common AQI category: {df['aqi'].mode()[0]}")
print(f"Highest single AQI reading: {df['aqi'].max()}")
print(f"Percentage of hazardous readings (AQI >= 4): "
      f"{(df['aqi'] >= 4).mean() * 100:.1f}%")