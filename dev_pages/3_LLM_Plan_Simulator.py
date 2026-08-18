import json

import streamlit as st
import pandas as pd
import plotly.express as px

from src.profiler import profile_dataframe
from src.column_suggester import suggest_column, get_selectbox_index
from src.llm_plan_runner import run_llm_tool_plan


st.set_page_config(
    page_title="LLM Plan Simulator",
    layout="wide"
)

st.title("LLM Plan Simulator")
st.caption("Simulates an LLM-generated JSON tool plan. No real LLM is called yet.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("data/sample_ecommerce.csv")
    st.info("Using sample ecommerce dataset. Upload your own CSV to test another dataset.")

profile = profile_dataframe(df)

st.write("### Dataset Preview")
st.dataframe(df.head())

date_columns = profile["date_like_columns"]
numeric_columns = profile["numeric_columns"]
categorical_columns = profile["categorical_columns"]

if not date_columns:
    st.error("No date-like column detected.")
    st.stop()

revenue_guess = suggest_column(
    numeric_columns,
    ["revenue", "sales", "amount", "total", "price", "order_value"]
)

order_guess = suggest_column(
    df.columns.tolist(),
    ["order_id", "order", "transaction_id", "transaction"]
)

segment_candidates = [
    col for col in categorical_columns
    if "id" not in col.lower()
]

if not segment_candidates:
    st.error("No useful segment column detected.")
    st.stop()

preferred_segment = suggest_column(
    segment_candidates,
    ["region", "category", "channel", "segment", "department"]
)

st.sidebar.header("Plan Defaults")

date_col = st.sidebar.selectbox(
    "Date column",
    date_columns
)

kpi_name = st.sidebar.selectbox(
    "KPI",
    ["Revenue", "Orders", "Average Order Value"]
)

revenue_col = st.sidebar.selectbox(
    "Revenue column",
    numeric_columns,
    index=get_selectbox_index(numeric_columns, revenue_guess)
)

order_col = st.sidebar.selectbox(
    "Order ID column",
    df.columns.tolist(),
    index=get_selectbox_index(df.columns.tolist(), order_guess)
)

segment_col = st.sidebar.selectbox(
    "Segment column",
    segment_candidates,
    index=get_selectbox_index(segment_candidates, preferred_segment)
)

default_plan = {
    "tool_calls": [
        {
            "tool_name": "profile_dataset",
            "args": {}
        },
        {
            "tool_name": "calculate_kpi_trend",
            "args": {
                "date_col": date_col,
                "kpi_name": kpi_name,
                "revenue_col": revenue_col,
                "order_col": order_col
            }
        },
        {
            "tool_name": "compare_periods",
            "args": {
                "previous_period": "2026-05",
                "current_period": "2026-06"
            }
        },
        {
            "tool_name": "analyze_root_cause",
            "args": {
                "date_col": date_col,
                "kpi_name": kpi_name,
                "segment_col": segment_col,
                "previous_period": "2026-05",
                "current_period": "2026-06",
                "revenue_col": revenue_col,
                "order_col": order_col
            }
        },
        {
            "tool_name": "detect_anomalies",
            "args": {
                "z_threshold": 1.5
            }
        },
        {
            "tool_name": "forecast_kpi",
            "args": {
                "periods_to_forecast": 3
            }
        },
        {
            "tool_name": "generate_insight_summary",
            "args": {
                "kpi_name": kpi_name,
                "segment_col": segment_col
            }
        }
    ]
}

st.write("## Simulated LLM JSON Plan")
st.caption("This is what a real LLM planner will eventually generate automatically.")

plan_text = st.text_area(
    "Edit JSON tool plan",
    value=json.dumps(default_plan, indent=2),
    height=500
)

run_plan = st.button("Run Simulated LLM Plan")

if run_plan:
    try:
        result = run_llm_tool_plan(
            response_text=plan_text,
            df=df
        )

        st.write("## Tool Trace")
        st.dataframe(result["tool_trace"])

        if "generate_insight_summary" in result:
            st.write("## Business Summary")
            st.success(result["generate_insight_summary"])

        if "calculate_kpi_trend" in result:
            st.write("## KPI Trend")
            trend_df = result["calculate_kpi_trend"]
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

        if "compare_periods" in result:
            st.write("## Period Comparison")
            st.json(result["compare_periods"])

        if "analyze_root_cause" in result:
            st.write("## Root-Cause Drivers")
            root_cause_df = result["analyze_root_cause"]
            st.dataframe(root_cause_df)

            if not root_cause_df.empty:
                fig = px.bar(
                    root_cause_df,
                    x="segment",
                    y="absolute_change",
                    title=f"{kpi_name} Change by {segment_col}"
                )
                st.plotly_chart(fig, use_container_width=True)

        if "detect_anomalies" in result:
            st.write("## Anomaly Detection")
            st.dataframe(result["detect_anomalies"])

        if "forecast_kpi" in result:
            st.write("## Forecast")
            st.dataframe(result["forecast_kpi"])

        if "run_sql_query" in result:
            st.write("## SQL Result")
            st.dataframe(result["run_sql_query"])

    except Exception as error:
        st.error(f"Plan failed validation or execution: {error}")
