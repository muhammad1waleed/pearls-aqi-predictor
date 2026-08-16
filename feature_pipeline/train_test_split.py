import pandas as pd


def time_based_split(df: pd.DataFrame, train_ratio: float = 0.8):
    """
    Split a time-ordered DataFrame into train/test sets by time,
    NOT randomly — preserves chronological order to avoid data leakage.

    Args:
        df (pd.DataFrame): Training-ready data, must contain 'timestamp'.
        train_ratio (float): Proportion of (chronologically earliest) rows
            to use for training. Remainder is used for testing.

    Returns:
        (pd.DataFrame, pd.DataFrame): (train_df, test_df)
    """
    df = df.sort_values("timestamp").reset_index(drop=True)

    split_index = int(len(df) * train_ratio)

    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]

    return train_df, test_df