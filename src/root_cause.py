import pandas as pd

from src.kpi_engine import calculate_kpi_value


def analyze_segment_drivers(
    df: pd.DataFrame,
    date_col: str,
    segment_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    previous_period: str | None = None,
    current_period: str | None = None
) -> pd.DataFrame:
    """
    Compare two periods by segment.
    Example: revenue change by region/category/channel.
    """

    working_df = df.copy()
    working_df[date_col] = pd.to_datetime(working_df[date_col], errors="coerce")
    working_df = working_df.dropna(subset=[date_col])

    working_df["period"] = working_df[date_col].dt.to_period("M").astype(str)

    periods = sorted(working_df["period"].dropna().unique())

    if len(periods) < 2:
        return pd.DataFrame()

    if previous_period is None:
        previous_period = periods[-2]

    if current_period is None:
        current_period = periods[-1]

    previous_df = working_df[working_df["period"] == previous_period]
    current_df = working_df[working_df["period"] == current_period]

    all_segments = sorted(
        set(previous_df[segment_col].dropna().unique())
        | set(current_df[segment_col].dropna().unique())
    )

    rows = []

    for segment in all_segments:
        previous_segment_df = previous_df[previous_df[segment_col] == segment]
        current_segment_df = current_df[current_df[segment_col] == segment]

        previous_value = calculate_kpi_value(
            previous_segment_df,
            kpi_name=kpi_name,
            revenue_col=revenue_col,
            order_col=order_col
        )

        current_value = calculate_kpi_value(
            current_segment_df,
            kpi_name=kpi_name,
            revenue_col=revenue_col,
            order_col=order_col
        )

        absolute_change = current_value - previous_value

        if previous_value == 0:
            percent_change = None
        else:
            percent_change = (absolute_change / previous_value) * 100

        rows.append({
            "segment_column": segment_col,
            "segment": segment,
            "previous_period": previous_period,
            "current_period": current_period,
            "previous_value": round(previous_value, 2),
            "current_value": round(current_value, 2),
            "absolute_change": round(absolute_change, 2),
            "percent_change": round(percent_change, 2) if percent_change is not None else None
        })

    result_df = pd.DataFrame(rows)

    if not result_df.empty:
        result_df = result_df.sort_values("absolute_change")

    return result_df
