import shap
import pandas as pd

from training_pipeline.train import FEATURE_COLUMNS


def explain_model(model, model_type: str, X_test: pd.DataFrame, max_samples: int = 200):
    """
    Compute SHAP values for a trained model and return mean absolute
    SHAP value per feature (a global feature-importance ranking).

    Args:
        model: trained sklearn model (Ridge or RandomForestRegressor).
        model_type (str): 'ridge' or 'random_forest'.
        X_test (pd.DataFrame): test features to explain.
        max_samples (int): cap on rows used for SHAP (for speed).

    Returns:
        pd.Series: mean |SHAP value| per feature, sorted descending.
    """
    X_sample = X_test.sample(min(max_samples, len(X_test)), random_state=42)

    if model_type == "random_forest":
        explainer = shap.TreeExplainer(model)
    elif model_type == "ridge":
        explainer = shap.LinearExplainer(model, X_sample)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    shap_values = explainer.shap_values(X_sample)

    importance = pd.Series(
        abs(shap_values).mean(axis=0), index=FEATURE_COLUMNS
    ).sort_values(ascending=False)

    return importance