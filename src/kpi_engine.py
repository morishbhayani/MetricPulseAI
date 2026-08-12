import pandas as pd


def calculate_kpi_value(
    df: pd.DataFrame,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None
) -> float:
    """
    Calculate one KPI value for the given dataframe.
    """

    if kpi_name == "Revenue":
        if revenue_col is None:
            raise ValueError("Revenue column is required for Revenue KPI.")

        return float(df[revenue_col].sum())

    if kpi_name == "Orders":
        if order_col is not None:
            return float(df[order_col].nunique())

        return float(len(df))

    if kpi_name == "Average Order Value":
        if revenue_col is None:
            raise ValueError("Revenue column is required for Average Order Value KPI.")

        revenue = df[revenue_col].sum()

        if order_col is not None:
            orders = df[order_col].nunique()
        else:
            orders = len(df)

        if orders == 0:
            return 0.0

        return float(revenue / orders)

    raise ValueError(f"Unsupported KPI: {kpi_name}")


def build_monthly_kpi_trend(
    df: pd.DataFrame,
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None
) -> pd.DataFrame:
    """
    Build a monthly KPI trend table.
    """

    working_df = df.copy()
    working_df[date_col] = pd.to_datetime(working_df[date_col], errors="coerce")
    working_df = working_df.dropna(subset=[date_col])

    working_df["period"] = working_df[date_col].dt.to_period("M").astype(str)

    rows = []

    for period, group in working_df.groupby("period"):
        value = calculate_kpi_value(
            group,
            kpi_name=kpi_name,
            revenue_col=revenue_col,
            order_col=order_col
        )

        rows.append({
            "period": period,
            "kpi_name": kpi_name,
            "kpi_value": round(value, 2)
        })

    trend_df = pd.DataFrame(rows)

    if not trend_df.empty:
        trend_df = trend_df.sort_values("period")

    return trend_df


def calculate_period_change(trend_df: pd.DataFrame) -> dict:
    """
    Compare the latest period against the previous period.
    """

    if trend_df.shape[0] < 2:
        return {
            "current_period": None,
            "previous_period": None,
            "current_value": None,
            "previous_value": None,
            "absolute_change": None,
            "percent_change": None
        }

    previous_row = trend_df.iloc[-2]
    current_row = trend_df.iloc[-1]

    previous_value = float(previous_row["kpi_value"])
    current_value = float(current_row["kpi_value"])

    absolute_change = current_value - previous_value

    if previous_value == 0:
        percent_change = None
    else:
        percent_change = (absolute_change / previous_value) * 100

    return {
        "current_period": current_row["period"],
        "previous_period": previous_row["period"],
        "current_value": round(current_value, 2),
        "previous_value": round(previous_value, 2),
        "absolute_change": round(absolute_change, 2),
        "percent_change": round(percent_change, 2) if percent_change is not None else None
    }
