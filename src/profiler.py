import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict:
    """
    Create a basic profile of the dataset.
    """

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()

    profile = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "date_like_columns": [],
    }

    date_keywords = ["date", "time", "created_at", "updated_at", "timestamp"]

    for col in df.columns:
        col_lower = col.lower()

        # Real datetime columns are always accepted
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            profile["date_like_columns"].append(col)
            continue

        # Do not treat numeric columns as dates
        if col in numeric_columns:
            continue

        # Prefer columns whose names sound date-like
        has_date_keyword = any(keyword in col_lower for keyword in date_keywords)

        if not has_date_keyword:
            continue

        try:
            parsed = pd.to_datetime(df[col], errors="coerce")
            valid_ratio = parsed.notna().mean()

            if valid_ratio > 0.7:
                profile["date_like_columns"].append(col)
        except Exception:
            pass

    return profile
