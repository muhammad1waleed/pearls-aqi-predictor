from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group
from feature_pipeline.lag_features import add_lag_features

fs = get_feature_store()
fg = get_or_create_aqi_feature_group(fs)

df = fg.read()
df = add_lag_features(df)

# Show a slice so we can visually verify the lag logic makes sense
print(df[["timestamp", "aqi", "aqi_lag_1h", "aqi_lag_24h", "aqi_change_rate"]].tail(10))