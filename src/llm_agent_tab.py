import streamlit as st
import plotly.express as px

from src.column_suggester import suggest_column, get_selectbox_index
from src.metricpulse_llm_agent import run_metricpulse_llm_agent


def render_metricpulse_llm_agent_tab(
    df,
    profile,
    date_col,
    kpi_name,
    revenue_col,
    order_col
):
    st.write("## MetricPulse LLM Agent")
    st.caption(
        "Ask a business question. The LLM planner chooses tools, Python calculates verified results, "
        "and the LLM explainer writes the final answer."
    )

    categorical_columns = profile["categorical_columns"]

    segment_candidates = [
        col for col in categorical_columns
        if "id" not in col.lower()
    ]

    if not segment_candidates:
        st.warning("No useful segment column detected for root-cause analysis.")
        return

    preferred_segment = suggest_column(
        segment_candidates,
        ["region", "category", "channel", "segment", "department"]
    )

    segment_col = st.selectbox(
        "Segment column for root-cause analysis",
        segment_candidates,
        index=get_selectbox_index(segment_candidates, preferred_segment),
        key="llm_agent_segment_col"
    )

    question = st.text_input(
        "Ask the MetricPulse LLM Agent",
        value="Why did revenue drop?",
        key="llm_agent_question"
    )

    run_agent = st.button("Run LLM Agent", key="run_llm_agent_button")

    if run_agent:
        try:
            with st.spinner("LLM is planning tools and Python is running analysis..."):
                result = run_metricpulse_llm_agent(
                    question=question,
                    df=df,
                    date_col=date_col,
                    kpi_name=kpi_name,
                    revenue_col=revenue_col,
                    order_col=order_col,
                    segment_col=segment_col
                )

            st.write("### LLM Final Answer")
            st.success(result.get("llm_final_answer", "No final answer generated."))

            st.write("### LLM JSON Tool Plan")
            st.code(result["llm_plan_text"], language="json")

            st.write("### Tool Trace")
            st.dataframe(result["tool_trace"])

            if "calculate_kpi_trend" in result:
                st.write("### KPI Trend")
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
                    st.plotly_chart(fig, use_container_width=True, key="llm_agent_plot_1")

            if "compare_periods" in result:
                st.write("### Period Comparison")
                st.json(result["compare_periods"])

            if "analyze_root_cause" in result:
                st.write("### Root-Cause Drivers")
                root_cause_df = result["analyze_root_cause"]
                st.dataframe(root_cause_df)

                if not root_cause_df.empty:
                    fig = px.bar(
                        root_cause_df,
                        x="segment",
                        y="absolute_change",
                        title=f"{kpi_name} Change by {segment_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True, key="llm_agent_plot_2")

            if "detect_anomalies" in result:
                st.write("### Anomaly Detection")
                st.dataframe(result["detect_anomalies"])

            if "forecast_kpi" in result:
                st.write("### Forecast")
                st.dataframe(result["forecast_kpi"])

            if "run_sql_query" in result:
                st.write("### SQL Result")
                st.dataframe(result["run_sql_query"])

            with st.expander("Debug: LLM Planner Prompt"):
                st.code(result["llm_prompt"], language="text")

            if "llm_explainer_prompt" in result:
                with st.expander("Debug: LLM Explainer Prompt"):
                    st.code(result["llm_explainer_prompt"], language="text")

        except Exception as error:
            st.error(f"LLM agent failed: {error}")
