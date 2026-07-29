import pandas as pd
import numpy as np

# =====================================================
# Expected CSV Columns
# =====================================================

REQUIRED_COLUMNS = [
    "Loan ID",
    "Customer",
    "Loan Type",
    "Principal",
    "Interest Rate",
    "Tenure (Months)",
    "EMI",
    "Outstanding Balance",
    "Status",
    "Start Date",
]

# =====================================================
# Load & Clean Dataset
# =====================================================

def load_data(uploaded_file):
    """
    Load and clean the uploaded loan CSV.
    Raises ValueError if validation fails.
    """

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        raise ValueError(f"Unable to read CSV: {e}")

    if df.empty:
        raise ValueError("Uploaded CSV is empty.")

    # Remove accidental whitespace
    df.columns = df.columns.str.strip()

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    # Date conversion
    df["Start Date"] = pd.to_datetime(
        df["Start Date"],
        errors="coerce",
    )

    # Numeric conversion
    numeric_columns = [
        "Principal",
        "Interest Rate",
        "Tenure (Months)",
        "EMI",
        "Outstanding Balance",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    # Clean text columns
    text_columns = [
        "Loan ID",
        "Customer",
        "Loan Type",
        "Status",
    ]

    for col in text_columns:
        df[col] = (
            df[col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "Start Date",
            "Principal",
            "Interest Rate",
            "Tenure (Months)",
            "EMI",
            "Outstanding Balance",
        ]
    )

    if df.empty:
        raise ValueError(
            "No valid records remain after cleaning."
        )

    # Prevent negative values
    df["Principal"] = df["Principal"].clip(lower=0)
    df["Interest Rate"] = df["Interest Rate"].clip(lower=0)
    df["Tenure (Months)"] = df["Tenure (Months)"].clip(lower=1)
    df["EMI"] = df["EMI"].clip(lower=0)
    df["Outstanding Balance"] = (
        df["Outstanding Balance"].clip(lower=0)
    )

    return df.reset_index(drop=True)


# =====================================================
# Dashboard Summary
# =====================================================

def calculate_summary(df):
    """
    Returns dashboard statistics.
    """

    if df.empty:
        return {
            "Total Loans": 0,
            "Total Principal": 0.0,
            "Outstanding Balance": 0.0,
            "Total EMI": 0.0,
            "Average Interest": 0.0,
        }

    return {
        "Total Loans": int(len(df)),
        "Total Principal": float(df["Principal"].sum()),
        "Outstanding Balance": float(
            df["Outstanding Balance"].sum()
        ),
        "Total EMI": float(df["EMI"].sum()),
        "Average Interest": float(
            df["Interest Rate"].mean()
        ),
    }


# =====================================================
# Loan Type Summary
# =====================================================

def loan_type_summary(df):
    """
    Summary grouped by loan type.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Loan Type",
                "Loans",
                "Principal",
                "Outstanding Balance",
            ]
        )

    summary = (
        df.groupby("Loan Type", dropna=False)
        .agg(
            Loans=("Loan ID", "count"),
            Principal=("Principal", "sum"),
            Outstanding_Balance=(
                "Outstanding Balance",
                "sum",
            ),
        )
        .reset_index()
    )

    summary.rename(
        columns={
            "Outstanding_Balance":
            "Outstanding Balance"
        },
        inplace=True,
    )

    return summary.sort_values(
        "Principal",
        ascending=False,
    )


# =====================================================
# Search
# =====================================================

def search_loans(df, query):
    """
    Search loans safely.
    """

    if df.empty:
        return df.copy()

    if not query:
        return df.copy()

    query = str(query).strip()

    mask = (
        df["Loan ID"].str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
        |
        df["Customer"].str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
        |
        df["Loan Type"].str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
        |
        df["Status"].str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
    )

    return df.loc[mask].copy()
