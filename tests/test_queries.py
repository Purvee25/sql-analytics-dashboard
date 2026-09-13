"""
SQL correctness tests.
Run *after* generating data:  python data/generate.py && pytest
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard.query_runner import run, data_loaded


@pytest.fixture(scope="session", autouse=True)
def require_data():
    if not data_loaded():
        pytest.skip("Run `python data/generate.py` first to generate test data.")


class TestRevenueTrends:
    def test_returns_rows(self):
        df = run("01_revenue_trends")
        assert len(df) > 0

    def test_columns_present(self):
        df = run("01_revenue_trends")
        assert {"month", "revenue", "orders", "unique_customers", "mom_growth_pct"}.issubset(df.columns)

    def test_revenue_positive(self):
        df = run("01_revenue_trends")
        assert (df["revenue"] > 0).all()

    def test_orders_positive(self):
        df = run("01_revenue_trends")
        assert (df["orders"] > 0).all()

    def test_months_ordered(self):
        df = run("01_revenue_trends")
        assert list(df["month"]) == sorted(df["month"].tolist())


class TestCustomerSegments:
    def test_returns_rows(self):
        df = run("02_customer_segments")
        assert len(df) > 0

    def test_rfm_labels_valid(self):
        df = run("02_customer_segments")
        valid = {"Champion", "Promising", "Loyal", "Needs Attention", "At-Risk", "Lost"}
        assert set(df["rfm_label"].unique()).issubset(valid)

    def test_monetary_non_negative(self):
        df = run("02_customer_segments")
        assert (df["monetary"] >= 0).all()

    def test_no_duplicate_customers(self):
        df = run("02_customer_segments")
        assert df["customer_id"].is_unique


class TestProductPerformance:
    def test_returns_rows(self):
        df = run("03_product_performance")
        assert len(df) > 0

    def test_margin_reasonable(self):
        df = run("03_product_performance")
        # margins should be positive and under 100%
        assert (df["margin_pct"] >= 0).all()
        assert (df["margin_pct"] < 100).all()

    def test_return_rate_bounded(self):
        df = run("03_product_performance")
        assert (df["return_rate_pct"] >= 0).all()
        assert (df["return_rate_pct"] <= 100).all()

    def test_one_row_per_category(self):
        df = run("03_product_performance")
        assert df["category"].is_unique


class TestCohortRetention:
    def test_returns_rows(self):
        df = run("04_cohort_retention")
        assert len(df) > 0

    def test_month_zero_is_100_pct(self):
        df = run("04_cohort_retention")
        month0 = df[df["month_number"] == 0]
        # cohort size == retained at month 0 → 100%
        assert (month0["retention_pct"] == 100.0).all()

    def test_retention_bounded(self):
        df = run("04_cohort_retention")
        assert (df["retention_pct"] >= 0).all()
        assert (df["retention_pct"] <= 100).all()

    def test_month_number_non_negative(self):
        df = run("04_cohort_retention")
        assert (df["month_number"] >= 0).all()


class TestSellerSLA:
    def test_returns_rows(self):
        df = run("05_seller_sla")
        assert len(df) > 0

    def test_sla_pct_bounded(self):
        df = run("05_seller_sla")
        assert (df["sla_pct"] >= 0).all()
        assert (df["sla_pct"] <= 100).all()

    def test_tiers_valid(self):
        df = run("05_seller_sla")
        assert set(df["tier"].unique()).issubset({1, 2, 3})

    def test_delivered_orders_positive(self):
        df = run("05_seller_sla")
        assert (df["delivered_orders"] > 0).all()
