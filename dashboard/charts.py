"""Plotly chart builders — each function takes a DataFrame and returns a Figure."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_PALETTE = px.colors.qualitative.Set2


def revenue_trend(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=df["month"], y=df["revenue"], name="Revenue (₹)", marker_color=_PALETTE[0]),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df["month"], y=df["mom_growth_pct"],
            name="MoM Growth %", mode="lines+markers",
            line={"color": _PALETTE[1], "width": 2},
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="Monthly Revenue & MoM Growth",
        xaxis_title="Month",
        legend={"orientation": "h", "y": -0.2},
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Revenue (₹)", secondary_y=False)
    fig.update_yaxes(title_text="MoM Growth %", secondary_y=True)
    return fig


def rfm_scatter(df: pd.DataFrame) -> go.Figure:
    return px.scatter(
        df,
        x="recency_days",
        y="monetary",
        size="frequency",
        color="rfm_label",
        hover_data=["customer_id", "state", "biz_segment"],
        title="Customer RFM Segmentation",
        labels={"recency_days": "Recency (days)", "monetary": "Total Spend (₹)", "rfm_label": "Segment"},
        color_discrete_sequence=_PALETTE,
    )


def rfm_distribution(df: pd.DataFrame) -> go.Figure:
    counts = df["rfm_label"].value_counts().reset_index()
    counts.columns = ["Segment", "Count"]
    return px.pie(
        counts, names="Segment", values="Count",
        title="Customer Distribution by RFM Segment",
        color_discrete_sequence=_PALETTE,
        hole=0.4,
    )


def category_revenue_margin(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=df["category"], y=df["revenue"], name="Revenue (₹)", marker_color=_PALETTE[0]),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df["category"], y=df["margin_pct"],
            name="Margin %", mode="markers",
            marker={"size": 12, "color": _PALETTE[2]},
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="Category Revenue vs. Gross Margin",
        xaxis_tickangle=-30,
        legend={"orientation": "h", "y": -0.3},
    )
    fig.update_yaxes(title_text="Revenue (₹)", secondary_y=False)
    fig.update_yaxes(title_text="Margin %", secondary_y=True)
    return fig


def return_rates(df: pd.DataFrame) -> go.Figure:
    df_sorted = df.sort_values("return_rate_pct", ascending=True)
    return px.bar(
        df_sorted, x="return_rate_pct", y="category",
        orientation="h",
        title="Return Rate by Category (%)",
        labels={"return_rate_pct": "Return Rate (%)", "category": ""},
        color="return_rate_pct",
        color_continuous_scale="RdYlGn_r",
    )


def cohort_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot(index="cohort_month", columns="month_number", values="retention_pct")
    pivot.index = pivot.index.astype(str).str[:7]  # YYYY-MM

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"Month {n}" for n in pivot.columns],
        y=pivot.index.tolist(),
        colorscale="Blues",
        text=[[f"{v:.0f}%" if v == v else "" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        hoverongaps=False,
    ))
    fig.update_layout(title="Cohort Retention Heatmap", xaxis_title="Month since first order")
    return fig


def seller_sla(df: pd.DataFrame) -> go.Figure:
    tier_summary = (
        df.groupby("tier")
        .agg(avg_sla=("sla_pct", "mean"), avg_delay=("avg_delay_days", "mean"), sellers=("seller_id", "count"))
        .reset_index()
    )
    fig = px.bar(
        tier_summary,
        x="tier", y="avg_sla",
        text="avg_sla",
        color="tier",
        title="Average SLA Compliance by Seller Tier (%)",
        labels={"tier": "Seller Tier", "avg_sla": "Avg On-Time Delivery (%)"},
        color_discrete_sequence=_PALETTE,
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    return fig
