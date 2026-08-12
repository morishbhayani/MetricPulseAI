def suggest_column(columns: list[str], keywords: list[str]) -> str | None:
    """
    Suggest the best matching column based on common business keywords.
    """

    normalized_columns = {
        col: col.lower().replace(" ", "_").replace("-", "_")
        for col in columns
    }

    # First try exact matches
    for keyword in keywords:
        for original_col, normalized_col in normalized_columns.items():
            if normalized_col == keyword:
                return original_col

    # Then try partial matches
    for keyword in keywords:
        for original_col, normalized_col in normalized_columns.items():
            if keyword in normalized_col:
                return original_col

    return None


def get_selectbox_index(options: list[str], preferred_value: str | None) -> int:
    """
    Return the index of the preferred value for a Streamlit selectbox.
    """

    if preferred_value in options:
        return options.index(preferred_value)

    return 0
