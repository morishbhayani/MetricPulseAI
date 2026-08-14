import duckdb
import pandas as pd


def run_sql_query(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """
    Run a SQL query against the uploaded dataframe using DuckDB.

    The dataframe is registered as a SQL table named: sales_data
    """

    if not query.strip():
        return pd.DataFrame()

    connection = duckdb.connect(database=":memory:")

    try:
        connection.register("sales_data", df)
        result_df = connection.execute(query).df()
        return result_df

    finally:
        connection.close()


def get_sample_queries() -> dict:
    """
    Return beginner-friendly sample SQL queries for the app.
    """

    return {
        "Monthly revenue": """
SELECT
    strftime(CAST(order_date AS DATE), '%Y-%m') AS month,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales_data
GROUP BY month
ORDER BY month;
""",
        "Revenue by region": """
SELECT
    region,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales_data
GROUP BY region
ORDER BY total_revenue DESC;
""",
        "Revenue by category": """
SELECT
    category,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales_data
GROUP BY category
ORDER BY total_revenue DESC;
""",
        "Orders by channel": """
SELECT
    channel,
    COUNT(DISTINCT order_id) AS total_orders
FROM sales_data
GROUP BY channel
ORDER BY total_orders DESC;
"""
    }
