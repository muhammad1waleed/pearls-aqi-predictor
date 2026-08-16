from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group
from feature_pipeline.training_data import build_training_dataset
from feature_pipeline.train_test_split import time_based_split

fs = get_feature_store()
fg = get_or_create_aqi_feature_group(fs)

raw_df = fg.read()
training_df = build_training_dataset(raw_df)

train_df, test_df = time_based_split(training_df, train_ratio=0.8)

print(f"Train rows: {len(train_df)} | {train_df['timestamp'].min()} to {train_df['timestamp'].max()}")
print(f"Test rows:  {len(test_df)} | {test_df['timestamp'].min()} to {test_df['timestamp'].max()}")