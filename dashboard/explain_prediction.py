import shap
import pandas as pd

from predict import get_latest_feature_row
from load_models import load_latest_models


def explain_single_prediction(model, model_type: str, row: pd.DataFrame,
                               background: pd.DataFrame) -> pd.Series:
    """
    Compute SHAP values for a single feature row and return the signed
    contribution of each feature to that specific prediction.

    Args:
        model: trained sklearn model.
        model_type (str): 'ridge' or 'random_forest'.
        row (pd.DataFrame): single-row DataFrame of feature values to explain.
        background (pd.DataFrame): a diverse sample of historical rows,
            used as the reference point for linear explanations.

    Returns:
        pd.Series: signed SHAP value per feature, sorted by absolute
            magnitude (most influential first).
    """
    if model_type == "random_forest":
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(row)
    elif model_type == "ridge":
        explainer = shap.LinearExplainer(model, background)
        shap_values = explainer.shap_values(row)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    contributions = pd.Series(shap_values[0], index=row.columns)
    return contributions.reindex(contributions.abs().sort_values(ascending=False).index)