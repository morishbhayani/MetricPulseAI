import json
import streamlit as st
import plotly.express as px

from src.column_suggester import suggest_column, get_selectbox_index
from src.llm_prompt_builder import build_llm_planner_prompt
from src.llm_agent import run_llm_planned_agent


def render_llm_planned_agent_tab(
    df,
    categorical_columns,
    date_col,
    kpi_name,
    revenue_col,
    order_col
):
    st.write("## MetricPulse LLM Agent")
    st.caption("This simulates an LLM tool-calling planner. No real LLM API is used yet.")

    question = st.text_input(
        "Ask a business question",
        value="Why did revenue drop?",
        key="llm_agent_question"
    )

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
        "Segment column for LLM agent",
        segment_candidates,
        index=get_selectbox_index(segment_candidates, preferred_segment),
        key="llm_agent_segment_col"
    )

    planner_prompt = build_llm_planner_prompt(
        question=question,
        available_columns=df.columns.tolist(),
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col,
        segment_col=segment_col
    )

    with st.expander("View LLM Planner Prompt"):
        st.text_area(
            "Prompt that would be sent to the LLM",
            value=planner_prompt,
            height=350,
            key="llm_planner_prompt_view"
        )

    default_plan = {
        "tool_plan": [
            {
                "tool_name": "profile_dataset",
                "args": {},
                "reason": "Understand the dataset structure."
            },
            {
                "tool_name": "calculate_kpi_trend",
                "args": {
                    "date_col": date_col,
                    "kpi_name": kpi_name,
                    "revenue_col": revenue_col,
                    "order_col": order_col
                },
                "reason": "Calculate the KPI trend."
            },
            {
                "tool_name": "compare_periods",
                "args": {},
                "reason": "Compare the latest period against the previous period."
            },
            {
                "tool_name": "analyze_root_cause",
                "args": {
                    "segment_col": segment_col
                },
                "reason": "Identify which segment drove the KPI change."
            },
            {
                "tool_name": "generate_insight_summary",
                "args": {},
                "reason": "Explain the verified results in business language."
            }
        ]
    }

    llm_response_text = st.text_area(
        "Paste LLM JSON tool plan here",
        value=json.dumps(default_plan, indent=2),
        height=300,
        key="llm_json_tool_plan"
    )

    if st.button("Run LLM-Planned Agent", key="run_llm_planned_agent"):
        try:
            result = run_llm_planned_agent(
                question=question,
                llm_response_text=llm_response_text,
                df=df,
                date_col=date_col,
                kpi_name=kpi_name,
                revenue_col=revenue_col,
                order_col=order_col,
                segment_col=segment_col
            )

            context = result["context"]

            st.write("### Parsed Tool Plan")
            st.dataframe(result["tool_plan"])

            st.write("### Tool Trace")
            st.dataframe(result["tool_trace"])

            if context.get("business_summary") is not None:
                st.write("### Final Answer")
                st.success(context["business_summary"])

            if context.get("trend_df") is not None:
                st.write("### KPI Trend")
                trend_df = context["trend_df"]
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

            if context.get("comparison_result") is not None:
                st.write("### Period Comparison")
                st.json(context["comparison_result"])

            if context.get("root_cause_result") is not None:
                st.write("### Root-Cause Drivers")
                root_cause_result = context["root_cause_result"]
                st.dataframe(root_cause_result)

                if not root_cause_result.empty:
                    fig = px.bar(
                        root_cause_result,
                        x="segment",
                        y="absolute_change",
                        title=f"{kpi_name} Change by {segment_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            if context.get("anomaly_result") is not None:
                st.write("### Anomaly Detection")
                st.dataframe(context["anomaly_result"])

            if context.get("forecast_result") is not None:
                st.write("### Forecast")
                st.dataframe(context["forecast_result"])

            if context.get("sql_result") is not None:
                st.write("### SQL Result")
                st.dataframe(context["sql_result"])

        except Exception as error:
            st.error(f"LLM-planned agent failed: {error}")
