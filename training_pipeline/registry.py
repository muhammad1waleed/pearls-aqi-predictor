import os
import joblib

import hopsworks

from training_pipeline.train import FEATURE_COLUMNS

MODELS_DIR = "saved_models"


def save_model_locally(model, target: str) -> str:
    """
    Serialize a trained model to disk with joblib.

    Args:
        model: trained sklearn model.
        target (str): 'target_1d', 'target_2d', or 'target_3d'.

    Returns:
        str: path to the saved .pkl file.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, f"{target}_model.pkl")
    joblib.dump(model, path)
    return path


def register_model(model_path: str, target: str, model_type: str,
                    metrics: dict, X_sample):
    """
    Upload a saved model to the Hopsworks Model Registry.

    Args:
        model_path (str): path to the local .pkl file.
        target (str): 'target_1d', 'target_2d', or 'target_3d'.
        model_type (str): 'ridge' or 'random_forest'.
        metrics (dict): {"rmse": ..., "mae": ..., "r2": ...}.
        X_sample (pd.DataFrame): a few example input rows, for schema inference.

    Returns:
        The registered model object from Hopsworks.
    """
    project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"))
    mr = project.get_model_registry()

    model_name = f"aqi_{target}_{model_type}"

    aqi_model = mr.sklearn.create_model(
        name=model_name,
        metrics=metrics,
        description=f"AQI forecast model for {target} ({model_type}), "
                     f"features: {', '.join(FEATURE_COLUMNS)}",
        input_example=X_sample.iloc[:3],
    )

    aqi_model.save(model_path)

    return aqi_model