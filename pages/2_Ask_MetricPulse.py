import streamlit as st
import pandas as pd
import plotly.express as px

from src.profiler import profile_dataframe
from src.column_suggester import suggest_column, get_selectbox_index
from src.question_agent import run_question_agent


st.set_page_config(
    page_title="Ask MetricPulse",
    layout="wide"
)

st.title("Ask MetricPulse")
st.caption("Ask a business question. A rule-based planner chooses which analytics tools to run. No LLM is used yet.")

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

st.sidebar.header("Question Agent Inputs")

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

question = st.text_input(
    "Ask a question",
    value="Why did revenue drop?"
)

run_question = st.button("Ask MetricPulse")

if run_question:
    result = run_question_agent(
        question=question,
        df=df,
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col,
        segment_col=segment_col
    )

    st.write("## Tool Plan")
    st.caption("This is the planner's selected tool list based on your question.")
    st.dataframe(result["plan"])

    st.write("## Tool Trace")
    st.caption("This shows which tools actually ran.")
    st.dataframe(result["tool_trace"])

    if "summary" in result:
        st.write("## Answer")
        st.success(result["summary"])

    if "trend_df" in result:
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

    if "comparison_result" in result:
        st.write("## Period Comparison")
        st.json(result["comparison_result"])

    if "root_cause_result" in result:
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

    if "anomaly_result" in result:
        st.write("## Anomaly Detection")
        st.dataframe(result["anomaly_result"])

    if "forecast_result" in result:
        st.write("## Forecast")
        st.dataframe(result["forecast_result"])

    if "sql_result" in result:
        st.write("## SQL Result")
        st.dataframe(result["sql_result"])
