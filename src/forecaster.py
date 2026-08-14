import numpy as np
import pandas as pd


def forecast_kpi_trend(
    trend_df: pd.DataFrame,
    periods_to_forecast: int = 3
) -> pd.DataFrame:
    """
    Forecast future KPI values using a simple linear trend.

    This is a lightweight baseline forecast:
    x = month number
    y = KPI value
    """

    if trend_df.empty or trend_df.shape[0] < 2:
        return pd.DataFrame()

    working_df = trend_df.copy()
    working_df = working_df.sort_values("period").reset_index(drop=True)

    x = np.arange(len(working_df))
    y = working_df["kpi_value"].astype(float).values

    slope, intercept = np.polyfit(x, y, 1)

    last_period = pd.Period(working_df["period"].iloc[-1], freq="M")

    forecast_rows = []

    for step in range(1, periods_to_forecast + 1):
        future_x = len(working_df) + step - 1
        forecast_value = slope * future_x + intercept
        future_period = last_period + step

        forecast_rows.append({
            "period": str(future_period),
            "forecast_value": round(float(forecast_value), 2)
        })

    return pd.DataFrame(forecast_rows)
