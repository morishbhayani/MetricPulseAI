import streamlit as st
import pandas as pd
import plotly.express as px

from src.profiler import profile_dataframe
from src.kpi_engine import build_monthly_kpi_trend, calculate_period_change
from src.column_suggester import suggest_column, get_selectbox_index
from src.root_cause import analyze_segment_drivers
from src.summary_writer import generate_kpi_summary
from src.sql_engine import run_sql_query, get_sample_queries
from src.anomaly_detector import detect_kpi_anomalies
from src.forecaster import forecast_kpi_trend
from src.report_exporter import generate_markdown_report
from src.agent_workflow import run_agentic_investigation
from src.tool_registry import ANALYTICS_TOOLS
from src.llm_agent_tab import render_metricpulse_llm_agent_tab


st.set_page_config(
    page_title="MetricPulse AI",
    page_icon="📊",
    layout="wide"
)

st.title("MetricPulse AI")
st.subheader("Agentic KPI analytics and root-cause analysis")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("data/sample_ecommerce.csv")
    st.info("Using sample ecommerce dataset. Upload your own CSV to test another dataset.")

profile = profile_dataframe(df)

if not profile["date_like_columns"]:
    st.warning("No date-like column detected. KPI trend analysis needs a date column.")
    st.stop()

suggested_date_col = suggest_column(
    profile["date_like_columns"],
    ["order_date", "date", "created_at", "timestamp"]
)

suggested_revenue_col = suggest_column(
    profile["numeric_columns"],
    ["revenue", "sales", "amount", "total", "price", "order_value"]
)

suggested_order_col = suggest_column(
    profile["column_names"],
    ["order_id", "transaction_id", "invoice_id", "receipt_id"]
)

if suggested_order_col is None:
    non_date_columns = [
        col for col in profile["column_names"]
        if col != suggested_date_col
    ]
    suggested_order_col = non_date_columns[0] if non_date_columns else profile["column_names"][0]

st.sidebar.header("KPI Settings")

date_col = st.sidebar.selectbox(
    "Date column",
    profile["date_like_columns"],
    index=get_selectbox_index(profile["date_like_columns"], suggested_date_col)
)

kpi_name = st.sidebar.selectbox(
    "KPI",
    ["Revenue", "Orders", "Average Order Value"]
)

revenue_col = st.sidebar.selectbox(
    "Revenue column",
    profile["numeric_columns"],
    index=get_selectbox_index(profile["numeric_columns"], suggested_revenue_col)
)

order_col = st.sidebar.selectbox(
    "Order ID column",
    profile["column_names"],
    index=get_selectbox_index(profile["column_names"], suggested_order_col)
)

trend_df = build_monthly_kpi_trend(
    df=df,
    date_col=date_col,
    kpi_name=kpi_name,
    revenue_col=revenue_col,
    order_col=order_col
)

change = calculate_period_change(trend_df)

anomaly_df = detect_kpi_anomalies(
    trend_df,
    value_col="kpi_value",
    z_threshold=1.5
)

forecast_df = forecast_kpi_trend(
    trend_df,
    periods_to_forecast=3
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dataset Profile",
    "KPI Analysis",
    "Root-Cause Analysis",
    "SQL Lab",
    "Agent Workflow",
    "MetricPulse LLM Agent"
])

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

with tab2:
    st.write("### KPI Trend")
    st.dataframe(trend_df)

    if not trend_df.empty:
        fig = px.line(
            trend_df,
            x="period",
            y="kpi_value",
            markers=True,
            title=f"Monthly {kpi_name} Trend"
        )
        st.plotly_chart(fig, use_container_width=True, key="app_plot_1")

    st.write("### Latest Period Change")
    st.json(change)

    st.write("### Anomaly Detection")
    st.dataframe(anomaly_df)

    st.write("### Forecast")
    st.dataframe(forecast_df)

with tab3:
    st.write("### Root-Cause Driver Analysis")

    segment_candidates = [
        col for col in profile["categorical_columns"]
        if "id" not in col.lower()
    ]

    if not segment_candidates:
        st.warning("No useful segment columns detected.")
    else:
        preferred_segment = suggest_column(
            segment_candidates,
            ["region", "category", "channel", "segment", "department"]
        )

        segment_col = st.selectbox(
            "Segment column",
            segment_candidates,
            index=get_selectbox_index(segment_candidates, preferred_segment)
        )

        periods = trend_df["period"].tolist()

        if len(periods) < 2:
            st.warning("Need at least two periods for root-cause analysis.")
        else:
            comparison_mode = st.selectbox(
                "Comparison mode",
                ["Latest vs previous", "First vs latest", "Custom"]
            )

            if comparison_mode == "Latest vs previous":
                previous_period = periods[-2]
                current_period = periods[-1]

            elif comparison_mode == "First vs latest":
                previous_period = periods[0]
                current_period = periods[-1]

            else:
                previous_period = st.selectbox(
                    "Previous period",
                    periods,
                    index=max(0, len(periods) - 2)
                )
                current_period = st.selectbox(
                    "Current period",
                    periods,
                    index=len(periods) - 1
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

            st.dataframe(driver_df)

            if not driver_df.empty:
                fig = px.bar(
                    driver_df,
                    x="segment",
                    y="absolute_change",
                    title=f"{kpi_name} Change by {segment_col}"
                )
                st.plotly_chart(fig, use_container_width=True, key="app_plot_2")

                insight_summary = generate_kpi_summary(
                    change=change,
                    driver_df=driver_df,
                    kpi_name=kpi_name,
                    segment_col=segment_col
                )

                st.write("### Business Summary")
                st.success(insight_summary)

                report = generate_markdown_report(
                    kpi_name=kpi_name,
                    trend_df=trend_df,
                    change=change,
                    driver_df=driver_df,
                    anomaly_df=anomaly_df,
                    forecast_df=forecast_df,
                    insight_summary=insight_summary
                )

                st.download_button(
                    label="Download Markdown Report",
                    data=report,
                    file_name="metricpulse_report.md",
                    mime="text/markdown"
                )

with tab4:
    st.write("### SQL Lab")
    st.caption("The uploaded dataset is available as a SQL table named sales_data.")

    sample_queries = get_sample_queries()

    selected_query_name = st.selectbox(
        "Sample query",
        list(sample_queries.keys())
    )

    query = st.text_area(
        "SQL query",
        value=sample_queries[selected_query_name],
        height=220
    )

    if st.button("Run SQL Query"):
        try:
            result_df = run_sql_query(df, query)
            st.dataframe(result_df)
        except Exception as error:
            st.error(f"SQL query failed: {error}")

with tab5:
    st.write("### Available Agent Tools")
    st.dataframe(pd.DataFrame(ANALYTICS_TOOLS))

    st.write("### Agent Workflow")
    agent_result = run_agentic_investigation(
        df=df,
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col
    )

    st.write("### Investigation Steps")
    st.dataframe(pd.DataFrame(agent_result["agent_steps"]))

    st.write("### Agent Outputs")
    st.write("**KPI trend:**")
    st.dataframe(agent_result["trend_df"])

    st.write("**Change:**")
    st.json(agent_result["change"])

    st.write("**Anomalies:**")
    st.dataframe(agent_result["anomaly_df"])

    st.write("**Forecast:**")
    st.dataframe(agent_result["forecast_df"])

with tab6:
    render_metricpulse_llm_agent_tab(
        df=df,
        profile=profile,
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col
    )
