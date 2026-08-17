from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score

from feature_pipeline.feature_store import get_feature_store, get_or_create_aqi_feature_group
from feature_pipeline.training_data import build_training_dataset
from feature_pipeline.train_test_split import time_based_split

FEATURE_COLUMNS = [
    "aqi", "co", "no2", "so2", "o3", "pm2_5", "pm10", "nh3",
    "hour", "day_of_week", "month",
    "aqi_lag_1h", "aqi_lag_24h", "aqi_change_rate",
]

TARGET_COLUMN = "target_1d"


def train_random_forest():
    """
    Train a Random Forest Regressor to predict target_1d,
    and report evaluation metrics on the held-out test set.
    """
    print("Connecting to feature store...")
    fs = get_feature_store()
    fg = get_or_create_aqi_feature_group(fs)

    raw_df = fg.read()
    training_df = build_training_dataset(raw_df)
    train_df, test_df = time_based_split(training_df, train_ratio=0.8)

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    print(f"Training on {len(X_train)} rows, testing on {len(X_test)} rows...")

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    rmse = root_mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print(f"RMSE: {rmse:.4f}")
    print(f"MAE:  {mae:.4f}")
    print(f"R2:   {r2:.4f}")

    return model, {"rmse": rmse, "mae": mae, "r2": r2}


if __name__ == "__main__":
    train_random_forest()