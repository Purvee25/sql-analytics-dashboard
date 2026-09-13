"""DuckDB query runner — reads named .sql files and substitutes CSV paths."""

from pathlib import Path

import duckdb
import pandas as pd

QUERIES_DIR = Path(__file__).parent.parent / "queries"
DATA_DIR    = Path(__file__).parent.parent / "data"

# Paths substituted into every query via {table_name} placeholders
_CSV_PATHS = {
    "customers":   str(DATA_DIR / "customers.csv"),
    "products":    str(DATA_DIR / "products.csv"),
    "sellers":     str(DATA_DIR / "sellers.csv"),
    "orders":      str(DATA_DIR / "orders.csv"),
    "order_items": str(DATA_DIR / "order_items.csv"),
}


def run(query_name: str, **extra_params: str) -> pd.DataFrame:
    """Load queries/<query_name>.sql, substitute CSV paths, execute, return DataFrame."""
    sql_file = QUERIES_DIR / f"{query_name}.sql"
    if not sql_file.exists():
        raise FileNotFoundError(f"Query file not found: {sql_file}")

    sql = sql_file.read_text()
    params = {**_CSV_PATHS, **extra_params}
    sql = sql.format(**params)

    con = duckdb.connect(database=":memory:")
    return con.execute(sql).df()


def data_loaded() -> bool:
    """Return True if all CSV files exist (i.e. generate.py has been run)."""
    return all(Path(p).exists() for p in _CSV_PATHS.values())
