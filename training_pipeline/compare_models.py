from training_pipeline.train import load_training_data, train_model

TARGETS = ["target_1d", "target_2d", "target_3d"]
MODEL_TYPES = ["ridge", "random_forest"]


def run_comparison():
    """
    Train every combination of target x model_type, and print a
    comparison table of RMSE, MAE, R2.
    """
    print("Loading training data from feature store (once)...")
    training_df = load_training_data()
    print(f"Loaded {len(training_df)} training-ready rows.\n")

    results = []
    for target in TARGETS:
        for model_type in MODEL_TYPES:
            print(f"Training {model_type} for {target}...")
            result = train_model(training_df, target, model_type)
            results.append(result)

    print("\n" + "=" * 60)
    print(f"{'Target':<12}{'Model':<16}{'RMSE':<10}{'MAE':<10}{'R2':<10}")
    print("=" * 60)
    for r in results:
        print(f"{r['target']:<12}{r['model_type']:<16}{r['rmse']:<10.4f}{r['mae']:<10.4f}{r['r2']:<10.4f}")

    return results


if __name__ == "__main__":
    run_comparison()