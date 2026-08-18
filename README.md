# MetricPulseAI

MetricPulseAI is an AI-ready KPI analytics assistant for analyzing business metrics from CSV datasets.

It combines KPI dashboards, root-cause analysis, SQL analytics, anomaly detection, baseline forecasting, report generation, and an LLM-ready tool-calling architecture.

## Demo Video

Watch the 2-minute project walkthrough:

https://www.loom.com/share/454d8374448d4a7dbd64bfa32f84988e

## What It Does

MetricPulseAI helps answer business questions such as:

- Why did revenue drop?
- Which region, category, or channel drove the change?
- Are there unusual KPI periods?
- What is the forecast for the next few months?
- Can I query the uploaded dataset using SQL?

## Key Features

- CSV upload and dataset profiling
- Automatic column detection
- KPI tracking for Revenue, Orders, and Average Order Value
- Monthly KPI trend analysis
- Period-over-period comparison
- Root-cause driver analysis by segment
- DuckDB-powered SQL Lab
- Z-score anomaly detection
- Baseline KPI forecasting
- Markdown report generation
- Tool registry and tool executor
- Rule-based question planner
- LLM-ready planned agent workflow
- Visible tool trace for transparency

## Agentic AI Architecture

MetricPulseAI separates planning from calculation.

LLM / planner:
- Chooses which tools should be used
- Produces a structured tool plan
- Explains verified outputs

Python analytics tools:
- Profile the dataset
- Calculate KPIs
- Compare periods
- Analyze root-cause drivers
- Detect anomalies
- Forecast future KPI values
- Run SQL queries
- Generate business summaries

This reduces hallucination risk because the LLM does not calculate metrics directly. Python and DuckDB produce the verified numbers.

## Current LLM Status

The current LLM Agent tab simulates an LLM-generated JSON tool plan.

This means the project already has the architecture for LLM tool-calling:

User question
→ planner prompt
→ JSON tool plan
→ parser
→ executor
→ analytics tools
→ final answer

A real LLM API can be connected later by replacing the pasted JSON plan with an API response.

## Tech Stack

- Python
- Streamlit
- pandas
- DuckDB
- Plotly
- NumPy
- Markdown report export

## Project Structure

- app.py: Main Streamlit application
- src/profiler.py: Dataset profiling
- src/kpi_engine.py: KPI calculation and period comparison
- src/root_cause.py: Segment-level driver analysis
- src/sql_engine.py: DuckDB SQL query execution
- src/anomaly_detector.py: Z-score anomaly detection
- src/forecaster.py: Baseline KPI forecasting
- src/summary_writer.py: Business summary generation
- src/report_exporter.py: Markdown report generation
- src/tool_registry.py: Tool definitions
- src/tool_executor.py: Tool execution layer
- src/agent_runner.py: Fixed tool-calling workflow
- src/question_planner.py: Rule-based question-to-tool planner
- src/question_agent.py: Question-based analytics agent
- src/llm_prompt_builder.py: LLM planner prompt builder
- src/llm_plan_parser.py: Safe JSON plan parser
- src/llm_plan_executor.py: LLM tool plan executor
- src/llm_agent.py: LLM-planned agent pipeline
- src/llm_planned_agent_tab.py: Streamlit UI for the LLM-planned agent

## How to Run Locally

Create and activate a virtual environment:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Run the app:

streamlit run app.py

## Example Questions

Try these in the MetricPulse LLM Agent tab:

- Why did revenue drop?
- Which region drove the change?
- Are there any unusual revenue anomalies?
- Forecast revenue for the next few months.
- Give me a business summary of performance.

## Notes

MetricPulseAI is designed as a portfolio project for AI Engineer, Data Analyst, and Data Scientist / ML Engineer roles.

It demonstrates analytics engineering, KPI reasoning, SQL analysis, agent-style architecture, tool calling, and explainable AI workflow design.
