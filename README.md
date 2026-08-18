# MetricPulseAI

MetricPulseAI is an agentic KPI analytics assistant that helps users analyze business metrics from CSV datasets.

## Demo Video

Watch the 2-minute project walkthrough here:

https://www.loom.com/share/454d8374448d4a7dbd64bfa32f84988e


The system combines KPI dashboards, root-cause analysis, SQL analytics, anomaly detection, forecasting, and an LLM-powered tool-calling agent.

## What It Does

MetricPulseAI helps answer business questions such as:

- Why did revenue drop?
- Which region or category drove the change?
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
- LLM-powered planning agent
- Grounded LLM final answer generation
- Visible tool trace for transparency

## Agentic AI Architecture

MetricPulseAI uses an agentic architecture where the LLM does not calculate metrics directly.

Instead:

```text
LLM = plans and explains
Python = calculates and verifies
EOD