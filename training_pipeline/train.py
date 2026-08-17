from sklearn.linear_model import Ridge
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

MODEL_BUILDERS = {
    "ridge": lambda: Ridge(alpha=1.0),
    "random_forest": lambda: RandomForestRegressor(
        n_estimators=200, max_depth=8, random_state=42
    ),
}


def load_training_data():
    """
    Connect to the feature store, read all data, and build the full
    training-ready dataset (with lag features and targets).

    Returns:
        pd.DataFrame: training-ready dataset.
    """
    fs = get_feature_store()
    fg = get_or_create_aqi_feature_group(fs)
    raw_df = fg.read()
    return build_training_dataset(raw_df)


def train_model(training_df, target_column: str, model_type: str):
    """
    Train a single model for a single target column and evaluate it
    on a time-based held-out test set.

    Args:
        training_df (pd.DataFrame): full training-ready dataset
            (output of load_training_data()).
        target_column (str): one of 'target_1d', 'target_2d', 'target_3d'.
        model_type (str): one of 'ridge', 'random_forest'.

    Returns:
        dict: {"target": ..., "model_type": ..., "rmse": ..., "mae": ..., "r2": ...}
    """
    if model_type not in MODEL_BUILDERS:
        raise ValueError(f"Unknown model_type: {model_type}")

    train_df, test_df = time_based_split(training_df, train_ratio=0.8)

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[target_column]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[target_column]

    model = MODEL_BUILDERS[model_type]()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    return {
        "target": target_column,
        "model_type": model_type,
        "model": model,
        "rmse": root_mean_squared_error(y_test, predictions),
        "mae": mean_absolute_error(y_test, predictions),
        "r2": r2_score(y_test, predictions),
    }