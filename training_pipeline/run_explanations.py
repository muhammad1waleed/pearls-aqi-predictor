from training_pipeline.train import load_training_data, train_model
from training_pipeline.explain import explain_model

# Our chosen winners per target, from Step 20's comparison
WINNERS = {
    "target_1d": "random_forest",
    "target_2d": "ridge",
    "target_3d": "ridge",
}


def run_explanations():
    print("Loading training data...")
    training_df = load_training_data()

    for target, model_type in WINNERS.items():
        print(f"\nTraining {model_type} for {target} and computing SHAP values...")
        result = train_model(training_df, target, model_type)

        importance = explain_model(
            result["model"], model_type, result["X_test"]
        )

        print(f"\nTop 5 features for {target} ({model_type}):")
        print(importance.head(5).to_string())


if __name__ == "__main__":
    run_explanations()