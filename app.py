import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    load_data,
    calculate_summary,
    loan_type_summary,
    search_loans,
)

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="LoanWise AI",
    page_icon="🏦",
    layout="wide",
)

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main{
        padding-top:1rem;
    }
    div[data-testid="metric-container"]{
        border-radius:12px;
        padding:15px;
        border:1px solid #e5e5e5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🏦 LoanWise AI")

st.caption(
    "Analyze loan portfolios, repayments and outstanding balances."
)

st.divider()

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Upload Loan Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV",
    type=["csv"],
)

if uploaded_file is None:

    st.info("Please upload a loan CSV file.")

    st.stop()

# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

try:

    df = load_data(uploaded_file)

except Exception as e:

    st.error(str(e))

    st.stop()

if df.empty:

    st.warning(
        "Dataset contains no valid records."
    )

    st.stop()

st.success(
    f"Loaded {len(df):,} loan records successfully."
)

st.divider()
# --------------------------------------------------
# Dashboard Summary
# --------------------------------------------------

try:

    summary = calculate_summary(df)

except Exception as e:

    st.error(
        "Unable to calculate dashboard summary."
    )

    st.exception(e)

    st.stop()

st.subheader("📊 Loan Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "Total Loans",
        summary["Total Loans"],
    )

with col2:

    st.metric(
        "Total Principal",
        f"₹{summary['Total Principal']:,.2f}",
    )

with col3:

    st.metric(
        "Outstanding Balance",
        f"₹{summary['Outstanding Balance']:,.2f}",
    )

with col4:

    st.metric(
        "Total EMI",
        f"₹{summary['Total EMI']:,.2f}",
    )

with col5:

    st.metric(
        "Average Interest",
        f"{summary['Average Interest']:.2f}%",
    )

st.divider()

# --------------------------------------------------
# Loan Type Summary
# --------------------------------------------------

try:

    loan_summary_df = loan_type_summary(df)

except Exception as e:

    st.error(
        "Unable to generate loan type summary."
    )

    st.exception(e)

    loan_summary_df = pd.DataFrame(
        columns=[
            "Loan Type",
            "Loans",
            "Principal",
            "Outstanding Balance",
        ]
    )

st.subheader("🏦 Loan Type Summary")

st.dataframe(
    loan_summary_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# --------------------------------------------------
# Loan Statistics
# --------------------------------------------------

st.subheader("📈 Loan Statistics")

left, right = st.columns(2)

with left:

    st.write(
        f"**Loan Types:** {df['Loan Type'].nunique()}"
    )

    st.write(
        f"**Customers:** {df['Customer'].nunique()}"
    )

    st.write(
        f"**Statuses:** {df['Status'].nunique()}"
    )

with right:

    st.write(
        f"**Earliest Loan:** {df['Start Date'].min().date()}"
    )

    st.write(
        f"**Latest Loan:** {df['Start Date'].max().date()}"
    )

    st.write(
        f"**Records:** {len(df)}"
    )

st.divider()
# --------------------------------------------------
# Loan Search
# --------------------------------------------------

st.subheader("🔍 Search Loans")

search_text = st.text_input(
    "Search by Loan ID, Customer, Loan Type or Status",
    placeholder="Example: Rahul, Home Loan, Active",
)

try:

    filtered_df = search_loans(
        df,
        search_text,
    ).reset_index(drop=True)

except Exception as e:

    st.error(
        "Unable to search loans."
    )

    st.exception(e)

    filtered_df = df.copy().reset_index(drop=True)

# --------------------------------------------------
# Loan Table
# --------------------------------------------------

st.subheader("📋 Loan Records")

loan_df = filtered_df.copy()

st.write(
    f"Showing **{len(loan_df):,}** loan record(s)."
)

if loan_df.empty:

    st.warning(
        "No matching loans found."
    )

else:

    st.dataframe(
        loan_df,
        use_container_width=True,
        hide_index=True,
    )

# --------------------------------------------------
# Download CSV
# --------------------------------------------------

try:

    csv = loan_df.to_csv(
        index=False,
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Loan Data",
        data=csv,
        file_name="loanwise_results.csv",
        mime="text/csv",
    )

except Exception as e:

    st.error(
        "Unable to prepare CSV download."
    )

    st.exception(e)

st.divider()

# --------------------------------------------------
# Largest Loans
# --------------------------------------------------

st.subheader("💰 Largest Loans")

if not loan_df.empty:

    largest_loans = (
        loan_df.sort_values(
            by="Principal",
            ascending=False,
        )
        .head(10)
    )

    st.dataframe(
        largest_loans,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No loans available."
    )

st.divider()

# --------------------------------------------------
# Dataset Preview
# --------------------------------------------------

st.subheader("📄 Dataset Preview")

preview_rows = st.slider(
    "Rows to Preview",
    min_value=5,
    max_value=50,
    value=10,
)

st.dataframe(
    loan_df.head(preview_rows),
    use_container_width=True,
    hide_index=True,
)

st.divider()
# --------------------------------------------------
# Loan Analytics
# --------------------------------------------------

st.subheader("📊 Loan Analytics")

# --------------------------------------------------
# Loan Type Distribution
# --------------------------------------------------

try:

    if not loan_summary_df.empty:

        fig = px.pie(
            loan_summary_df,
            names="Loan Type",
            values="Principal",
            hole=0.45,
            title="Principal Distribution by Loan Type",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

except Exception as e:

    st.error(
        "Unable to generate loan type chart."
    )

    st.exception(e)

# --------------------------------------------------
# Outstanding Balance
# --------------------------------------------------

try:

    if not loan_summary_df.empty:

        fig = px.bar(
            loan_summary_df,
            x="Loan Type",
            y="Outstanding Balance",
            title="Outstanding Balance by Loan Type",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

except Exception as e:

    st.error(
        "Unable to generate outstanding balance chart."
    )

    st.exception(e)

# --------------------------------------------------
# EMI Distribution
# --------------------------------------------------

try:

    fig = px.histogram(
        loan_df,
        x="EMI",
        nbins=20,
        title="EMI Distribution",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate EMI distribution."
    )

    st.exception(e)

# --------------------------------------------------
# Interest Rate Distribution
# --------------------------------------------------

try:

    fig = px.histogram(
        loan_df,
        x="Interest Rate",
        nbins=20,
        title="Interest Rate Distribution",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate interest rate chart."
    )

    st.exception(e)

# --------------------------------------------------
# Loan Status Distribution
# --------------------------------------------------

try:

    status_df = (
        loan_df.groupby(
            "Status",
            dropna=False,
        )
        .size()
        .reset_index(name="Loans")
    )

    fig = px.bar(
        status_df,
        x="Status",
        y="Loans",
        title="Loan Status Distribution",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate status chart."
    )

    st.exception(e)

# --------------------------------------------------
# Loan Timeline
# --------------------------------------------------

try:

    timeline_df = (
        loan_df.copy()
        .sort_values("Start Date")
    )

    fig = px.line(
        timeline_df,
        x="Start Date",
        y="Outstanding Balance",
        color="Loan Type",
        markers=True,
        title="Outstanding Balance Timeline",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

except Exception as e:

    st.error(
        "Unable to generate timeline."
    )

    st.exception(e)

st.divider()
# --------------------------------------------------
# Loan Insights
# --------------------------------------------------

st.subheader("🔍 Loan Insights")

display_df = loan_df.reset_index(
    drop=True
)

if display_df.empty:

    st.info(
        "No loans available."
    )

else:

    selected_index = st.selectbox(
        "Select Loan",
        options=range(len(display_df)),
        format_func=lambda x:
            f"{display_df.iloc[x]['Loan ID']} | "
            f"{display_df.iloc[x]['Customer']}",
    )

    loan = display_df.iloc[selected_index]

    col1, col2 = st.columns(2)

    with col1:

        st.write("### Customer Details")

        st.write(
            f"**Loan ID:** {loan['Loan ID']}"
        )

        st.write(
            f"**Customer:** {loan['Customer']}"
        )

        st.write(
            f"**Loan Type:** {loan['Loan Type']}"
        )

        st.write(
            f"**Status:** {loan['Status']}"
        )

        st.write(
            f"**Start Date:** "
            f"{loan['Start Date'].date()}"
        )

    with col2:

        st.write("### Financial Details")

        st.write(
            f"**Principal:** ₹{loan['Principal']:,.2f}"
        )

        st.write(
            f"**Outstanding Balance:** "
            f"₹{loan['Outstanding Balance']:,.2f}"
        )

        st.write(
            f"**Monthly EMI:** ₹{loan['EMI']:,.2f}"
        )

        st.write(
            f"**Interest Rate:** "
            f"{loan['Interest Rate']:.2f}%"
        )

        st.write(
            f"**Tenure:** "
            f"{int(loan['Tenure (Months)'])} months"
        )

        repayment_percent = 0.0

        if loan["Principal"] > 0:

            repayment_percent = (
                (
                    loan["Principal"]
                    - loan["Outstanding Balance"]
                )
                / loan["Principal"]
            ) * 100

        st.write(
            f"**Loan Repaid:** "
            f"{repayment_percent:.2f}%"
        )

        if repayment_percent >= 80:

            st.success(
                "Loan is nearing completion."
            )

        elif repayment_percent >= 40:

            st.info(
                "Loan is progressing well."
            )

        else:

            st.warning(
                "Large outstanding balance remains."
            )

st.divider()

# --------------------------------------------------
# Highest Outstanding Loans
# --------------------------------------------------

st.subheader("🏆 Highest Outstanding Loans")

ranking_df = loan_df.sort_values(
    by="Outstanding Balance",
    ascending=False,
)

st.dataframe(
    ranking_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()
# --------------------------------------------------
# Dataset Health Report
# --------------------------------------------------

st.subheader("🩺 Dataset Health Report")

total_records = len(df)

missing_values = int(df.isna().sum().sum())

duplicate_rows = int(df.duplicated().sum())

health_score = max(
    0,
    100 - (
        missing_values
        + duplicate_rows
    ),
)

health_score = min(
    100,
    health_score,
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Records",
        total_records,
    )

    st.metric(
        "Missing Values",
        missing_values,
    )

with col2:

    st.metric(
        "Duplicate Rows",
        duplicate_rows,
    )

    st.metric(
        "Loan Types",
        df["Loan Type"].nunique(),
    )

with col3:

    st.metric(
        "Customers",
        df["Customer"].nunique(),
    )

    st.metric(
        "Dataset Quality",
        f"{health_score}%",
    )

st.divider()

# --------------------------------------------------
# Loan Summary
# --------------------------------------------------

st.subheader("📋 Loan Summary")

summary_df = pd.DataFrame(
    {
        "Metric": [
            "Rows",
            "Columns",
            "Customers",
            "Loan Types",
            "Total Loans",
            "Total Principal",
            "Outstanding Balance",
            "Total EMI",
            "Average Interest",
        ],
        "Value": [
            len(df),
            len(df.columns),
            df["Customer"].nunique(),
            df["Loan Type"].nunique(),
            summary["Total Loans"],
            f"₹{summary['Total Principal']:,.2f}",
            f"₹{summary['Outstanding Balance']:,.2f}",
            f"₹{summary['Total EMI']:,.2f}",
            f"{summary['Average Interest']:.2f}%",
        ],
    }
)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.caption(
    "LoanWise AI • Built with Streamlit, Pandas and Plotly"
    )






