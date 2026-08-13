from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group

fs = get_feature_store()
fg = get_or_create_aqi_feature_group(fs)

print("Feature group name:", fg.name)
print("Feature group version:", fg.version)