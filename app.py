import streamlit as st
import pandas as pd
import plotly.express as px

from src.profiler import profile_dataframe
from src.kpi_engine import build_monthly_kpi_trend, calculate_period_change
from src.column_suggester import suggest_column, get_selectbox_index
from src.root_cause import analyze_segment_drivers
from src.summary_writer import generate_kpi_summary


st.set_page_config(
    page_title="MetricPulse AI",
    page_icon="📊",
    layout="wide"
)

st.title("MetricPulse AI")
st.subheader("AI-assisted KPI analytics and root-cause analysis")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    profile = profile_dataframe(df)

    tab1, tab2, tab3 = st.tabs(
        ["Dataset Profile", "KPI Analysis", "Root-Cause Analysis"]
    )

    with tab1:
        st.write("### Dataset Preview")
        st.dataframe(df.head())

        st.write("### Dataset Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Rows", profile["rows"])

        with col2:
            st.metric("Columns", profile["columns"])

        with col3:
            st.metric("Duplicate Rows", profile["duplicate_rows"])

        st.write("### Missing Values")
        st.write(profile["missing_values"])

        st.write("### Detected Column Types")
        st.write("**Numeric columns:**")
        st.write(profile["numeric_columns"])

        st.write("**Categorical columns:**")
        st.write(profile["categorical_columns"])

        st.write("**Date-like columns:**")
        st.write(profile["date_like_columns"])

    if not profile["date_like_columns"]:
        st.warning("No date-like column detected. KPI trend analysis needs a date column.")
        st.stop()

    suggested_date_col = suggest_column(
        profile["date_like_columns"],
        ["order_date", "date", "created_at", "timestamp"]
    )

    date_col = st.sidebar.selectbox(
        "Date column",
        profile["date_like_columns"],
        index=get_selectbox_index(profile["date_like_columns"], suggested_date_col)
    )

    kpi_name = st.sidebar.selectbox(
        "KPI",
        ["Revenue", "Orders", "Average Order Value"]
    )

    revenue_col = None

    if kpi_name in ["Revenue", "Average Order Value"]:
        if not profile["numeric_columns"]:
            st.warning("No numeric columns detected. Revenue-based KPIs need a numeric column.")
            st.stop()

        suggested_revenue_col = suggest_column(
            profile["numeric_columns"],
            ["revenue", "sales", "amount", "total", "price", "order_value"]
        )

        revenue_col = st.sidebar.selectbox(
            "Revenue column",
            profile["numeric_columns"],
            index=get_selectbox_index(profile["numeric_columns"], suggested_revenue_col)
        )

    possible_order_columns = profile["categorical_columns"] + profile["numeric_columns"]

    suggested_order_col = suggest_column(
        possible_order_columns,
        ["order_id", "order", "transaction_id", "invoice_id", "purchase_id"]
    )

    order_options = ["Use row count"] + possible_order_columns

    order_col = st.sidebar.selectbox(
        "Order ID column",
        order_options,
        index=get_selectbox_index(order_options, suggested_order_col)
    )

    if order_col == "Use row count":
        order_col = None

    trend_df = build_monthly_kpi_trend(
        df=df,
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col
    )

    change = calculate_period_change(trend_df)

    with tab2:
        st.write("### KPI Trend Table")
        st.dataframe(trend_df)

        if not trend_df.empty:
            fig = px.line(
                trend_df,
                x="period",
                y="kpi_value",
                markers=True,
                title=f"Monthly {kpi_name} Trend"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.write("### Latest Period Change")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current Period", change["current_period"])

        with col2:
            st.metric("Previous Period", change["previous_period"])

        with col3:
            st.metric(
                "Percent Change",
                f"{change['percent_change']}%" if change["percent_change"] is not None else "N/A"
            )

        st.write(change)

    with tab3:
        st.write("### Root-Cause Analysis")

        if trend_df.shape[0] < 2:
            st.warning("Root-cause analysis needs at least two periods.")
        else:
            available_periods = trend_df["period"].tolist()

            comparison_mode = st.selectbox(
                "Select comparison mode",
                ["Latest vs previous", "First vs latest", "Custom"]
            )

            if comparison_mode == "Latest vs previous":
                previous_period = available_periods[-2]
                current_period = available_periods[-1]

            elif comparison_mode == "First vs latest":
                previous_period = available_periods[0]
                current_period = available_periods[-1]

            else:
                previous_period = st.selectbox(
                    "Previous period",
                    available_periods,
                    index=0
                )

                current_period = st.selectbox(
                    "Current period",
                    available_periods,
                    index=len(available_periods) - 1
                )

            st.info(f"Comparing **{previous_period}** vs **{current_period}**")

            previous_value = float(
                trend_df.loc[trend_df["period"] == previous_period, "kpi_value"].iloc[0]
            )
            current_value = float(
                trend_df.loc[trend_df["period"] == current_period, "kpi_value"].iloc[0]
            )

            absolute_change = current_value - previous_value

            if previous_value == 0:
                percent_change = None
            else:
                percent_change = (absolute_change / previous_value) * 100

            comparison_change = {
                "previous_period": previous_period,
                "current_period": current_period,
                "previous_value": round(previous_value, 2),
                "current_value": round(current_value, 2),
                "absolute_change": round(absolute_change, 2),
                "percent_change": round(percent_change, 2) if percent_change is not None else None
            }

            segment_options = [
                col for col in profile["categorical_columns"]
                if col not in [date_col, order_col]
                and not col.lower().endswith("_id")
                and col.lower() != "id"
            ]

            if not segment_options:
                st.warning("No useful categorical segment columns found for root-cause analysis.")
            else:
                suggested_segment_col = suggest_column(
                    segment_options,
                    ["region", "category", "channel", "segment", "market", "country", "state", "city", "product"]
                )

                segment_col = st.selectbox(
                    "Select segment column",
                    segment_options,
                    index=get_selectbox_index(segment_options, suggested_segment_col)
                )

                driver_df = analyze_segment_drivers(
                    df=df,
                    date_col=date_col,
                    segment_col=segment_col,
                    kpi_name=kpi_name,
                    revenue_col=revenue_col,
                    order_col=order_col,
                    previous_period=previous_period,
                    current_period=current_period
                )

                st.write("### Segment Driver Table")
                st.dataframe(driver_df)

                if not driver_df.empty:
                    fig = px.bar(
                        driver_df,
                        x="segment",
                        y="absolute_change",
                        title=f"{kpi_name} Change by {segment_col}: {previous_period} vs {current_period}"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    biggest_drop = driver_df.iloc[0]
                    biggest_gain = driver_df.iloc[-1]

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("### Biggest Negative Driver")
                        st.write(
                            f"**{biggest_drop['segment']}** changed by "
                            f"**{biggest_drop['absolute_change']}**."
                        )

                    with col2:
                        st.write("### Biggest Positive Driver")
                        st.write(
                            f"**{biggest_gain['segment']}** changed by "
                            f"**{biggest_gain['absolute_change']}**."
                        )

                    st.write("### Insight Summary")

                    summary = generate_kpi_summary(
                        change=comparison_change,
                        driver_df=driver_df,
                        kpi_name=kpi_name,
                        segment_col=segment_col
                    )

                    st.success(summary)

else:
    st.info("Upload a CSV file to begin.")
