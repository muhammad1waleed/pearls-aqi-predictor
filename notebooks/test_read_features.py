from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group, get_latest_rows

fs = get_feature_store()
fg = get_or_create_aqi_feature_group(fs)

latest = get_latest_rows(fg, n=5)
print(latest)