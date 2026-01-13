from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd


BRANDS = [
    "Off-White", "Acne Studios", "Jacquemus", "Balenciaga", "Saint Laurent", "Prada", "Gucci",
    "Bottega Veneta", "Loewe", "Maison Margiela", "Rick Owens", "Issey Miyake", "Comme des Garçons",
    "AMI", "A.P.C.", "Stone Island", "Moncler", "The Row", "Celine", "Chloé", "Burberry", "Givenchy",
    "Fendi", "Versace", "Miu Miu", "Alexander McQueen", "VETEMENTS", "Palm Angels", "Dries Van Noten",
    "Marni", "Ganni", "Khaite", "Zimmermann", "Tory Burch", "Tibi", "Kiko Kostadinov",
    "Fear of God", "Totême", "Ralph Lauren", "JW Anderson", "Diesel", "Kenzo", "UGG",
]
REGIONS = ["NA", "EU", "APAC"]
GENDERS = ["W", "M", "U"]
CATEGORIES = ["Outerwear", "Tops", "Bottoms", "Dresses", "Shoes", "Bags", "Accessories"]
SILHOUETTES = [
    "Oversized", "Slim", "Boxy", "Cropped", "Wide-Leg", "Straight", "A-Line", "Slip",
    "Platform", "Minimal", "Tailored", "Sport", "Utility", "Maxi", "Micro",
]
COLORS = ["Black", "White", "Denim Blue", "Navy", "Beige", "Red", "Pink", "Green", "Brown", "Gray", "Metallic"]
COLLECTIONS = ["Pre-Fall", "Fall/Winter", "Resort", "Spring/Summer", "Capsule", "Collab"]


@dataclass(frozen=True)
class GenConfig:
    seed: int
    days: int
    n_users: int
    out_dir: Path


def _seasonality(t: np.ndarray) -> np.ndarray:
    return 1.0 + 0.15 * np.sin(2 * np.pi * t / 7.0) + 0.10 * np.sin(2 * np.pi * t / 365.0)


def _promo_pulses(t: np.ndarray) -> np.ndarray:
    pulses = np.zeros_like(t, dtype=float)
    for center in [35, 80, 120, 165]:
        pulses += 0.40 * np.exp(-0.5 * ((t - center) / 6.0) ** 2)
    return 1.0 + pulses


def _trend_signal(t: np.ndarray, start: int, slope: float, cap: float = 1.8) -> np.ndarray:
    x = np.clip(t - start, 0, None)
    return 1.0 + np.clip(slope * x / 30.0, 0, cap - 1.0)


def generate_synthetic_data(cfg: GenConfig) -> dict[str, Path]:
    """Generate realistic synthetic retail data for demo + portfolio purposes."""
    rng = np.random.default_rng(cfg.seed)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    end = pd.Timestamp.today().normalize()
    start = end - pd.Timedelta(days=cfg.days)
    dates = pd.date_range(start, end, freq="D")
    t = np.arange(len(dates))

    # Product catalog
    n_products = 12000
    products = pd.DataFrame(
        {
            "product_id": np.arange(1, n_products + 1),
            "brand": rng.choice(BRANDS, size=n_products),
            "category": rng.choice(CATEGORIES, size=n_products, p=[0.16, 0.18, 0.16, 0.10, 0.16, 0.12, 0.12]),
            "gender": rng.choice(GENDERS, size=n_products, p=[0.46, 0.38, 0.16]),
            "collection": rng.choice(COLLECTIONS, size=n_products, p=[0.16, 0.22, 0.12, 0.26, 0.14, 0.10]),
            "silhouette": rng.choice(SILHOUETTES, size=n_products),
            "color": rng.choice(COLORS, size=n_products, p=[0.18, 0.09, 0.10, 0.09, 0.10, 0.06, 0.06, 0.06, 0.09, 0.11, 0.06]),
            "list_price": rng.normal(loc=420, scale=220, size=n_products).clip(35, 2600).round(2),
        }
    )

    # Inject known emerging style buckets (for backtest / demo)
    emerging_rules = [
        ("Jacquemus", "Bags", "U", "Micro", "Pink"),
        ("Acne Studios", "Outerwear", "W", "Oversized", "Denim Blue"),
        ("Off-White", "Tops", "M", "Utility", "Green"),
    ]
    for (b, c, g, s, col) in emerging_rules:
        idx = products.sample(frac=0.015, random_state=cfg.seed).index
        products.loc[idx, "brand"] = b
        products.loc[idx, "category"] = c
        products.loc[idx, "gender"] = g
        products.loc[idx, "silhouette"] = s
        products.loc[idx, "color"] = col

    products_path = cfg.out_dir / "products.csv"
    products.to_csv(products_path, index=False)

    # Inventory receipts (weekly)
    receipts_rows = []
    for pid in products["product_id"].to_numpy():
        base = rng.integers(8, 80)
        for d in pd.date_range(start, end, freq="W-MON"):
            units = max(0, int(rng.normal(loc=base, scale=base * 0.25)))
            receipts_rows.append((int(pid), d.date().isoformat(), units))
    inv = pd.DataFrame(receipts_rows, columns=["product_id", "week_start", "units_received"])
    inv_path = cfg.out_dir / "inventory_receipts.csv"
    inv.to_csv(inv_path, index=False)

    # Sessions per day (bounded for runtime)
    n_sessions_per_day = int(cfg.n_users * 0.11)
    sessions = []
    for day_i, day in enumerate(dates):
        season = float(_seasonality(np.array([day_i]))[0] * _promo_pulses(np.array([day_i]))[0])
        n_sessions = int(min(n_sessions_per_day * season, 120000))
        user_ids = rng.integers(1, cfg.n_users + 1, size=n_sessions)
        region = rng.choice(REGIONS, size=n_sessions, p=[0.46, 0.34, 0.20])
        session_ids = [f"s{day_i:04d}_{j:06d}" for j in range(n_sessions)]
        sessions.append(pd.DataFrame({"date": day.date().isoformat(), "user_id": user_ids, "region": region, "session_id": session_ids}))
    sessions_df = pd.concat(sessions, ignore_index=True)

    # Trend lift after ~midpoint
    lift = pd.DataFrame({"date": dates.date.astype(str), "lift": _trend_signal(t, start=int(cfg.days * 0.45), slope=0.9)})
    sessions_df = sessions_df.merge(lift, on="date", how="left")

    # Page views 1–6 per session
    pv_counts = rng.integers(1, 7, size=len(sessions_df))
    session_rep = sessions_df.loc[sessions_df.index.repeat(pv_counts)].reset_index(drop=True)

    # Weighted product sampling: lift boosts emerging buckets
    prod = products[["product_id", "brand", "category", "gender", "silhouette", "color"]].copy()
    prod["is_emerging_bucket"] = 0
    for (b, c, g, s, col) in emerging_rules:
        mask = (
            (prod["brand"] == b)
            & (prod["category"] == c)
            & (prod["gender"] == g)
            & (prod["silhouette"] == s)
            & (prod["color"] == col)
        )
        prod.loc[mask, "is_emerging_bucket"] = 1
    weights = np.where(prod["is_emerging_bucket"].to_numpy() == 1, 1.4, 1.0).astype(float)
    weights = weights / weights.sum()

    page_view_products = rng.choice(prod["product_id"].to_numpy(), size=len(session_rep), replace=True, p=weights)
    page_views = session_rep[["date", "user_id", "region", "session_id"]].copy()
    page_views["event_type"] = "page_view"
    page_views["product_id"] = page_view_products
    page_views["ts"] = pd.to_datetime(page_views["date"]) + pd.to_timedelta(rng.integers(0, 24 * 3600, size=len(page_views)), unit="s")

    # Add-to-cart probability increases with lift
    atc_prob = (0.075 + 0.030 * (sessions_df["lift"].to_numpy() - 1.0)).clip(0.04, 0.16)
    atc_flags = rng.random(len(sessions_df)) < atc_prob
    atc_sessions = sessions_df.loc[atc_flags].copy()
    atc_sessions["event_type"] = "add_to_cart"
    atc_sessions["product_id"] = rng.choice(prod["product_id"].to_numpy(), size=len(atc_sessions), replace=True, p=weights)
    atc_sessions["ts"] = pd.to_datetime(atc_sessions["date"]) + pd.to_timedelta(rng.integers(0, 24 * 3600, size=len(atc_sessions)), unit="s")

    # Purchases conditional on ATC + promo intensity
    day_index = (pd.to_datetime(sessions_df["date"]) - pd.to_datetime(start.date())).dt.days.to_numpy()
    promo = _promo_pulses(day_index)
    purchase_prob = (0.18 + 0.10 * (promo - 1.0)).clip(0.12, 0.35)
    purchase_flags = atc_flags & (rng.random(len(sessions_df)) < purchase_prob)
    purchase_sessions = sessions_df.loc[purchase_flags].copy()
    purchase_sessions["event_type"] = "purchase"
    purchase_sessions["product_id"] = rng.choice(prod["product_id"].to_numpy(), size=len(purchase_sessions), replace=True, p=weights)
    purchase_sessions["ts"] = pd.to_datetime(purchase_sessions["date"]) + pd.to_timedelta(rng.integers(0, 24 * 3600, size=len(purchase_sessions)), unit="s")

    web_events = pd.concat(
        [
            page_views[["ts", "date", "user_id", "session_id", "region", "event_type", "product_id"]],
            atc_sessions[["ts", "date", "user_id", "session_id", "region", "event_type", "product_id"]],
            purchase_sessions[["ts", "date", "user_id", "session_id", "region", "event_type", "product_id"]],
        ],
        ignore_index=True,
    ).sort_values("ts")
    web_path = cfg.out_dir / "web_events.csv"
    web_events.to_csv(web_path, index=False)

    # Orders + items
    purchase_sessions = purchase_sessions.reset_index(drop=True)
    n_orders = len(purchase_sessions)
    order_ids = np.arange(1, n_orders + 1)
    items_per_order = rng.integers(1, 4, size=n_orders)

    day_index_orders = (pd.to_datetime(purchase_sessions["date"]) - pd.to_datetime(start.date())).dt.days.to_numpy()
    promo_o = _promo_pulses(day_index_orders)
    markdown = (0.05 + 0.28 * (promo_o - 1.0) + rng.normal(0, 0.03, size=n_orders)).clip(0.0, 0.55)

    orders = pd.DataFrame(
        {
            "order_id": order_ids,
            "order_ts": pd.to_datetime(purchase_sessions["ts"]),
            "user_id": purchase_sessions["user_id"].to_numpy(),
            "region": purchase_sessions["region"].to_numpy(),
            "discount_pct": markdown.round(3),
        }
    )

    prod_price = products.set_index("product_id")["list_price"].to_dict()
    prod_cat = products.set_index("product_id")["category"].to_dict()

    item_rows = []
    for oid, n_items, disc in zip(order_ids, items_per_order, markdown):
        pids = rng.choice(products["product_id"].to_numpy(), size=n_items, replace=True, p=weights)
        for pid in pids:
            list_price = float(prod_price[int(pid)])
            unit_price = float(list_price * (1.0 - disc))
            qty = int(rng.integers(1, 3))
            item_rows.append((int(oid), int(pid), qty, round(unit_price, 2), round(disc, 3)))
    order_items = pd.DataFrame(item_rows, columns=["order_id", "product_id", "quantity", "unit_price", "markdown_pct"])

    # Returns correlate with category + markdown (proxy for fit issues / final sale)
    cat_return_base = {
        "Outerwear": 0.10,
        "Tops": 0.12,
        "Bottoms": 0.14,
        "Dresses": 0.16,
        "Shoes": 0.18,
        "Bags": 0.08,
        "Accessories": 0.09,
    }
    probs = []
    for _, row in order_items.iterrows():
        base = cat_return_base.get(prod_cat[int(row["product_id"])], 0.12)
        probs.append(base + 0.25 * float(row["markdown_pct"]))
    probs = np.array(probs).clip(0, 0.6)
    order_items["is_returned"] = (rng.random(len(order_items)) < probs).astype(int)

    orders_path = cfg.out_dir / "orders.csv"
    items_path = cfg.out_dir / "order_items.csv"
    orders.to_csv(orders_path, index=False)
    order_items.to_csv(items_path, index=False)

    return {
        "products": products_path,
        "inventory_receipts": inv_path,
        "web_events": web_path,
        "orders": orders_path,
        "order_items": items_path,
    }
