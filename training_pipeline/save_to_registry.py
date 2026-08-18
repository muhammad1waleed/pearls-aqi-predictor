from training_pipeline.train import load_training_data, train_model
from training_pipeline.registry import save_model_locally, register_model

WINNERS = {
    "target_1d": "random_forest",
    "target_2d": "ridge",
    "target_3d": "ridge",
}


def run():
    print("Loading training data...")
    training_df = load_training_data()

    for target, model_type in WINNERS.items():
        print(f"\nTraining final {model_type} for {target}...")
        result = train_model(training_df, target, model_type)

        print(f"RMSE: {result['rmse']:.4f} | MAE: {result['mae']:.4f} | R2: {result['r2']:.4f}")

        print("Saving model locally...")
        model_path = save_model_locally(result["model"], target)

        print("Registering model in Hopsworks Model Registry...")
        registered = register_model(
            model_path=model_path,
            target=target,
            model_type=model_type,
            metrics={
                "rmse": result["rmse"],
                "mae": result["mae"],
                "r2": result["r2"],
            },
            X_sample=result["X_test"],
        )
        print(f"Registered: {registered.name}, version {registered.version}")


if __name__ == "__main__":
    run()