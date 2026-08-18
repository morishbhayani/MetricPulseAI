import streamlit as st
import pandas as pd
import plotly.express as px

from src.profiler import profile_dataframe
from src.column_suggester import suggest_column, get_selectbox_index
from src.agent_runner import run_tool_calling_investigation


st.set_page_config(
    page_title="MetricPulse AI - Tool Calling Agent",
    layout="wide"
)

st.title("MetricPulse AI - Tool Calling Agent")
st.caption("This page runs a tool-calling analytics workflow. No LLM is used yet.")

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
    st.error("No date-like column detected. Please upload a dataset with a date column.")
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
    st.error("No useful segment column detected. Try a dataset with region, category, channel, etc.")
    st.stop()

preferred_segment = suggest_column(
    segment_candidates,
    ["region", "category", "channel", "segment", "department"]
)

st.sidebar.header("Agent Inputs")

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

run_agent = st.button("Run Tool-Calling Investigation")

if run_agent:
    result = run_tool_calling_investigation(
        df=df,
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col,
        segment_col=segment_col
    )

    st.write("## Tool Trace")
    st.caption("This shows which tools were called and what arguments were passed.")
    st.dataframe(result["tool_trace"])

    st.write("## Business Summary")
    st.success(result["summary"])

    st.write("## KPI Trend")
    trend_df = result["trend_df"]
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

    st.write("## Period Comparison")
    st.json(result["comparison_result"])

    st.write("## Root-Cause Drivers")
    root_cause_result = result["root_cause_result"]
    st.dataframe(root_cause_result)

    if not root_cause_result.empty:
        fig = px.bar(
            root_cause_result,
            x="segment",
            y="absolute_change",
            title=f"{kpi_name} Change by {segment_col}"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.write("## Anomaly Detection")
    st.dataframe(result["anomaly_result"])

    st.write("## Forecast")
    st.dataframe(result["forecast_result"])
