ANALYTICS_TOOLS = [
    {
        "tool_name": "profile_dataset",
        "description": "Scans the uploaded dataset and summarizes rows, columns, column types, missing values, and duplicate rows.",
        "inputs": [],
        "output": [
            "rows",
            "columns",
            "column_names",
            "numeric_columns",
            "categorical_columns",
            "date_like_columns",
            "missing_values",
            "duplicate_rows"
        ]
    },
    {
        "tool_name": "calculate_kpi_trend",
        "description": "Calculates the monthly trend for Revenue, Orders, or Average Order Value.",
        "inputs": ["date_col", "kpi_name", "revenue_col", "order_col"],
        "output": ["period", "kpi_name", "kpi_value"]
    },
    {
        "tool_name": "compare_periods",
        "description": "Compares a selected KPI between two periods and returns absolute and percent change.",
        "inputs": ["previous_period", "current_period"],
        "output": [
            "previous_period",
            "current_period",
            "previous_value",
            "current_value",
            "absolute_change",
            "percent_change",
            "direction"
        ]
    },
    {
        "tool_name": "analyze_root_cause",
        "description": "Breaks down KPI change by a segment column and identifies biggest positive and negative drivers.",
        "inputs": [
            "date_col",
            "kpi_name",
            "segment_col",
            "previous_period",
            "current_period",
            "revenue_col",
            "order_col"
        ],
        "output": [
            "segment",
            "previous_value",
            "current_value",
            "absolute_change",
            "percent_change",
            "biggest_negative_driver",
            "biggest_positive_driver"
        ]
    },
    {
        "tool_name": "detect_anomalies",
        "description": "Flags unusually high or low KPI periods using z-score based anomaly detection.",
        "inputs": ["z_threshold"],
        "output": [
            "period",
            "kpi_name",
            "kpi_value",
            "mean_value",
            "z_score",
            "is_anomaly",
            "anomaly_direction"
        ]
    },
    {
        "tool_name": "forecast_kpi",
        "description": "Forecasts future KPI values from the monthly KPI trend using a baseline forecasting model.",
        "inputs": ["periods_to_forecast"],
        "output": ["period", "forecast_value"]
    },
    {
        "tool_name": "run_sql_query",
        "description": "Runs a read-only SQL SELECT query on the uploaded dataset using DuckDB.",
        "inputs": ["query"],
        "output": ["SQL result table"]
    },
    {
        "tool_name": "generate_insight_summary",
        "description": "Generates a stakeholder-ready explanation from verified KPI, root-cause, anomaly, and forecast results.",
        "inputs": [
            "kpi_name",
            "comparison_result",
            "root_cause_result",
            "anomaly_result",
            "forecast_result"
        ],
        "output": ["business_summary"]
    }
]
