import pandas as pd


def format_value(value, kpi_name: str) -> str:
    """
    Format KPI values for readable business summaries.
    """

    if value is None:
        return "N/A"

    if kpi_name in ["Revenue", "Average Order Value"]:
        return f"${value:,.2f}"

    return f"{value:,.0f}"


def generate_kpi_summary(
    change: dict,
    driver_df: pd.DataFrame,
    kpi_name: str,
    segment_col: str | None = None
) -> str:
    """
    Generate a simple stakeholder-style summary from verified KPI outputs.
    """

    if not change or change.get("current_period") is None:
        return "Not enough period data is available to generate a KPI summary."

    current_period = change["current_period"]
    previous_period = change["previous_period"]
    current_value = change["current_value"]
    previous_value = change["previous_value"]
    absolute_change = change["absolute_change"]
    percent_change = change["percent_change"]

    direction = "increased" if absolute_change > 0 else "decreased" if absolute_change < 0 else "stayed flat"

    summary = (
        f"{kpi_name} {direction} from "
        f"{format_value(previous_value, kpi_name)} in {previous_period} "
        f"to {format_value(current_value, kpi_name)} in {current_period}."
    )

    if percent_change is not None:
        summary += f" This represents a {percent_change:.2f}% change."

    if driver_df is not None and not driver_df.empty and segment_col is not None:
        biggest_drop = driver_df.iloc[0]
        biggest_gain = driver_df.iloc[-1]

        summary += (
            f" By {segment_col}, the biggest negative driver was "
            f"{biggest_drop['segment']} with a change of "
            f"{format_value(biggest_drop['absolute_change'], kpi_name)}."
        )

        summary += (
            f" The biggest positive driver was "
            f"{biggest_gain['segment']} with a change of "
            f"{format_value(biggest_gain['absolute_change'], kpi_name)}."
        )

    return summary
