from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group
from feature_pipeline.training_data import build_training_dataset

fs = get_feature_store()
fg = get_or_create_aqi_feature_group(fs)

raw_df = fg.read()
print(f"Raw rows: {len(raw_df)}")

training_df = build_training_dataset(raw_df)
print(f"Training-ready rows: {len(training_df)}")

print(training_df[["timestamp", "aqi", "aqi_lag_1h", "aqi_lag_24h", "target_1d", "target_2d", "target_3d"]].head(5))