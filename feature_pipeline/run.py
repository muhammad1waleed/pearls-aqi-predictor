from feature_pipeline.fetch_data import fetch_current_features
from feature_pipeline.feature_store import (
    get_feature_store,
    get_or_create_aqi_feature_group,
    insert_row,
)


def run_feature_pipeline():
    """
    Fetch current weather + pollution data for the configured city,
    and write it to the Hopsworks feature store.
    """
    print("Fetching current features...")
    row = fetch_current_features()
    print("Fetched row:", row)

    print("Connecting to feature store...")
    fs = get_feature_store()
    fg = get_or_create_aqi_feature_group(fs)

    print("Inserting row...")
    insert_row(fg, row)

    print("Done.")


if __name__ == "__main__":
    run_feature_pipeline()