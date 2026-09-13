"""
Generate synthetic Indian e-commerce dataset.

Schema:
  customers   — id, city, state, signup_date, segment
  products    — id, name, category, cost_price, selling_price
  sellers     — id, name, city, tier (1/2/3)
  orders      — id, customer_id, seller_id, order_date, promised_delivery, actual_delivery, status
  order_items — order_id, product_id, quantity, unit_price

Run:  python data/generate.py
"""

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_IN")
rng = random.Random(42)

OUT = Path(__file__).parent

# ── constants ─────────────────────────────────────────────────────────────────

CATEGORIES = {
    "Electronics":    (800,  12000, 0.12),
    "Fashion":        (200,  3000,  0.45),
    "Home & Kitchen": (150,  5000,  0.30),
    "Books":          (80,   800,   0.20),
    "Beauty":         (100,  2500,  0.50),
    "Sports":         (300,  8000,  0.25),
    "Toys":           (150,  2000,  0.35),
    "Grocery":        (50,   500,   0.10),
}

STATES = [
    "Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Telangana",
    "West Bengal", "Gujarat", "Rajasthan", "Uttar Pradesh", "Kerala",
]

SEGMENTS = ["Consumer", "SMB", "Enterprise"]

START = date(2023, 1, 1)
END   = date(2024, 12, 31)


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=rng.randint(0, delta))


# ── generators ────────────────────────────────────────────────────────────────

def make_customers(n: int = 2000) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "customer_id": f"C{i:05d}",
            "city":        fake.city(),
            "state":       rng.choice(STATES),
            "signup_date": random_date(date(2022, 1, 1), date(2023, 6, 30)).isoformat(),
            "segment":     rng.choice(SEGMENTS),
        })
    return pd.DataFrame(rows)


def make_products(n: int = 300) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        cat = rng.choice(list(CATEGORIES))
        lo, hi, margin = CATEGORIES[cat]
        cost = round(rng.uniform(lo, hi), 2)
        price = round(cost * (1 + margin + rng.uniform(-0.05, 0.10)), 2)
        rows.append({
            "product_id":    f"P{i:04d}",
            "name":          fake.catch_phrase()[:60],
            "category":      cat,
            "cost_price":    cost,
            "selling_price": price,
        })
    return pd.DataFrame(rows)


def make_sellers(n: int = 80) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "seller_id": f"S{i:03d}",
            "name":      fake.company()[:50],
            "city":      fake.city(),
            "tier":      rng.choices([1, 2, 3], weights=[20, 50, 30])[0],
        })
    return pd.DataFrame(rows)


def make_orders(customers: pd.DataFrame, sellers: pd.DataFrame, n: int = 12000) -> pd.DataFrame:
    cids = customers["customer_id"].tolist()
    sids = sellers["seller_id"].tolist()
    rows = []

    # simulate growth: later months have more orders
    for i in range(1, n + 1):
        weight = rng.random()
        # skew toward later dates for growth story
        days_in_range = (END - START).days
        day_offset = int(days_in_range * (weight ** 0.6))
        order_date = START + timedelta(days=day_offset)

        # promised delivery: tier-1 sellers promise faster
        seller_id = rng.choice(sids)
        tier = sellers.loc[sellers["seller_id"] == seller_id, "tier"].iat[0]
        promised_days = {1: rng.randint(2, 4), 2: rng.randint(3, 6), 3: rng.randint(5, 10)}[tier]
        promised = order_date + timedelta(days=promised_days)

        # actual delivery: tier-1 reliable, tier-3 often late
        late_prob = {1: 0.05, 2: 0.15, 3: 0.30}[tier]
        extra = rng.randint(1, 5) if rng.random() < late_prob else rng.randint(-1, 1)
        actual = promised + timedelta(days=extra)

        # small % cancelled / returned
        status = rng.choices(
            ["delivered", "cancelled", "returned"],
            weights=[88, 7, 5],
        )[0]
        if status != "delivered":
            actual = None

        rows.append({
            "order_id":           f"O{i:06d}",
            "customer_id":        rng.choice(cids),
            "seller_id":          seller_id,
            "order_date":         order_date.isoformat(),
            "promised_delivery":  promised.isoformat(),
            "actual_delivery":    actual.isoformat() if actual else None,
            "status":             status,
        })
    return pd.DataFrame(rows)


def make_order_items(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    pids = products["product_id"].tolist()
    price_map = products.set_index("product_id")["selling_price"].to_dict()
    rows = []
    for oid in orders["order_id"]:
        n_items = rng.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        chosen = rng.sample(pids, min(n_items, len(pids)))
        for pid in chosen:
            qty = rng.randint(1, 3)
            # small discount on multi-quantity
            unit = round(price_map[pid] * rng.uniform(0.90, 1.00), 2)
            rows.append({
                "order_id":   oid,
                "product_id": pid,
                "quantity":   qty,
                "unit_price": unit,
            })
    return pd.DataFrame(rows)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Generating customers …")
    customers = make_customers(2000)
    customers.to_csv(OUT / "customers.csv", index=False)

    print("Generating products …")
    products = make_products(300)
    products.to_csv(OUT / "products.csv", index=False)

    print("Generating sellers …")
    sellers = make_sellers(80)
    sellers.to_csv(OUT / "sellers.csv", index=False)

    print("Generating orders …")
    orders = make_orders(customers, sellers, 12000)
    orders.to_csv(OUT / "orders.csv", index=False)

    print("Generating order_items …")
    items = make_order_items(orders, products)
    items.to_csv(OUT / "order_items.csv", index=False)

    print(f"Done.  {len(orders):,} orders  |  {len(items):,} line items")


if __name__ == "__main__":
    main()
