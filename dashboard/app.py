"""
SQL Analytics Dashboard
Run:  streamlit run dashboard/app.py
"""

import subprocess
import sys
from pathlib import Path

import streamlit as st

# Resolve imports when run from any working directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard import charts, query_runner

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
)

# ── sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.title("📊 E-Commerce Analytics")
st.sidebar.caption("Indian e-commerce · 2023–2024 · DuckDB")

if not query_runner.data_loaded():
    st.warning("Data not found. Generating synthetic dataset…")
    with st.spinner("Running data/generate.py …"):
        subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "data" / "generate.py")],
            check=True,
        )
    st.rerun()

tab = st.sidebar.radio(
    "View",
    ["Revenue Trends", "Customer Segments", "Product Performance", "Cohort Retention", "Seller SLA"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Stack:** DuckDB · Streamlit · Plotly")
st.sidebar.markdown("[Source](https://github.com/Purvee25/sql-analytics-dashboard)")


# ── tabs ──────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load(query_name: str):
    return query_runner.run(query_name)


if tab == "Revenue Trends":
    st.header("Revenue Trends")
    df = load("01_revenue_trends")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"₹{df['revenue'].sum():,.0f}")
    col2.metric("Total Orders", f"{df['orders'].sum():,}")
    col3.metric(
        "Avg MoM Growth",
        f"{df['mom_growth_pct'].dropna().mean():.1f}%",
    )

    st.plotly_chart(charts.revenue_trend(df), use_container_width=True)
    with st.expander("SQL"):
        st.code((Path(__file__).parent.parent / "queries" / "01_revenue_trends.sql").read_text(), language="sql")
    with st.expander("Raw data"):
        st.dataframe(df, use_container_width=True)

elif tab == "Customer Segments":
    st.header("Customer Segmentation (RFM)")
    df = load("02_customer_segments")

    col1, col2, col3 = st.columns(3)
    col1.metric("Customers Analysed", f"{len(df):,}")
    col2.metric("Champions", f"{(df['rfm_label'] == 'Champion').sum():,}")
    col3.metric("At-Risk / Lost", f"{df['rfm_label'].isin(['At-Risk', 'Lost']).sum():,}")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.rfm_distribution(df), use_container_width=True)
    with c2:
        st.plotly_chart(charts.rfm_scatter(df), use_container_width=True)

    with st.expander("SQL"):
        st.code((Path(__file__).parent.parent / "queries" / "02_customer_segments.sql").read_text(), language="sql")
    with st.expander("Raw data"):
        st.dataframe(df, use_container_width=True)

elif tab == "Product Performance":
    st.header("Product & Category Performance")
    df = load("03_product_performance")

    col1, col2, col3 = st.columns(3)
    col1.metric("Top Category by Revenue", df.loc[df["revenue"].idxmax(), "category"])
    col2.metric("Highest Margin Category", df.loc[df["margin_pct"].idxmax(), "category"])
    col3.metric("Highest Return Rate", df.loc[df["return_rate_pct"].idxmax(), "category"])

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.category_revenue_margin(df), use_container_width=True)
    with c2:
        st.plotly_chart(charts.return_rates(df), use_container_width=True)

    with st.expander("SQL"):
        st.code((Path(__file__).parent.parent / "queries" / "03_product_performance.sql").read_text(), language="sql")
    with st.expander("Raw data"):
        st.dataframe(df, use_container_width=True)

elif tab == "Cohort Retention":
    st.header("Cohort Retention Analysis")
    df = load("04_cohort_retention")

    month0 = df[df["month_number"] == 0]
    month1 = df[df["month_number"] == 1]
    month3 = df[df["month_number"] == 3]

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Month-1 Retention", f"{month1['retention_pct'].mean():.1f}%")
    col2.metric("Avg Month-3 Retention", f"{month3['retention_pct'].mean():.1f}%")
    col3.metric("Cohorts Tracked", f"{month0['cohort_month'].nunique()}")

    st.plotly_chart(charts.cohort_heatmap(df), use_container_width=True)
    st.caption("Each row = cohort (month of first purchase). Each column = months since first order. Value = % of cohort still active.")

    with st.expander("SQL"):
        st.code((Path(__file__).parent.parent / "queries" / "04_cohort_retention.sql").read_text(), language="sql")
    with st.expander("Raw data"):
        st.dataframe(df, use_container_width=True)

elif tab == "Seller SLA":
    st.header("Seller SLA Compliance")
    df = load("05_seller_sla")

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall On-Time Rate", f"{df['sla_pct'].mean():.1f}%")
    col2.metric("Best Seller SLA", f"{df['sla_pct'].max():.1f}%")
    col3.metric("Avg Delay (late orders)", f"{df.loc[df['avg_delay_days'] > 0, 'avg_delay_days'].mean():.1f} days")

    st.plotly_chart(charts.seller_sla(df), use_container_width=True)

    tier_filter = st.selectbox("Filter by tier", ["All", 1, 2, 3])
    display = df if tier_filter == "All" else df[df["tier"] == tier_filter]
    st.dataframe(
        display[["seller_name", "tier", "city", "delivered_orders", "sla_pct", "avg_delay_days"]],
        use_container_width=True,
    )

    with st.expander("SQL"):
        st.code((Path(__file__).parent.parent / "queries" / "05_seller_sla.sql").read_text(), language="sql")
