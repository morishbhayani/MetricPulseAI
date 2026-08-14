import pandas as pd


def detect_kpi_anomalies(
    trend_df: pd.DataFrame,
    value_col: str = "kpi_value",
    z_threshold: float = 1.5
) -> pd.DataFrame:
    """
    Detect unusual KPI values using a simple z-score method.

    z-score tells us how far a value is from the average.
    A high positive z-score means unusually high.
    A high negative z-score means unusually low.
    """

    if trend_df.empty or value_col not in trend_df.columns:
        return pd.DataFrame()

    result_df = trend_df.copy()

    mean_value = result_df[value_col].mean()
    std_value = result_df[value_col].std()

    if pd.isna(std_value) or std_value == 0:
        result_df["mean_value"] = round(mean_value, 2)
        result_df["z_score"] = 0.0
        result_df["is_anomaly"] = False
        result_df["anomaly_direction"] = "normal"
        return result_df

    result_df["mean_value"] = round(mean_value, 2)
    result_df["z_score"] = (result_df[value_col] - mean_value) / std_value
    result_df["z_score"] = result_df["z_score"].round(2)

    result_df["is_anomaly"] = result_df["z_score"].abs() >= z_threshold

    result_df["anomaly_direction"] = result_df["z_score"].apply(
        lambda z: "unusually high" if z >= z_threshold
        else "unusually low" if z <= -z_threshold
        else "normal"
    )

    return result_df
