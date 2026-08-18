import duckdb
import pandas as pd


def quote_identifier(column_name: str) -> str:
    """
    Safely quote a SQL column name for DuckDB.
    Needed for columns like: Order Date, Product Name, Sales Amount.
    """
    escaped = column_name.replace('"', '""')
    return f'"{escaped}"'


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


def get_sample_queries(
    date_col: str,
    revenue_col: str,
    order_col: str,
    segment_col: str
) -> dict:
    """
    Return dataset-aware sample SQL queries.
    """

    q_date = quote_identifier(date_col)
    q_revenue = quote_identifier(revenue_col)
    q_order = quote_identifier(order_col)
    q_segment = quote_identifier(segment_col)

    return {
        "Monthly revenue": f"""
SELECT
    strftime(CAST({q_date} AS DATE), '%Y-%m') AS month,
    ROUND(SUM({q_revenue}), 2) AS total_revenue
FROM sales_data
GROUP BY month
ORDER BY month;
""",
        f"Revenue by {segment_col}": f"""
SELECT
    {q_segment} AS segment,
    ROUND(SUM({q_revenue}), 2) AS total_revenue
FROM sales_data
GROUP BY segment
ORDER BY total_revenue DESC;
""",
        f"Orders by {segment_col}": f"""
SELECT
    {q_segment} AS segment,
    COUNT(DISTINCT {q_order}) AS total_orders
FROM sales_data
GROUP BY segment
ORDER BY total_orders DESC;
""",
        "Preview data": """
SELECT *
FROM sales_data
LIMIT 10;
"""
    }
