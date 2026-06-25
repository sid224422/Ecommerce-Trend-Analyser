"""
Generate fashion / apparel test CSV (INR) for TrendScanner AI demos.

Exercises: brand share, pricing stats, comma/pipe/semicolon features,
gap signals, dedup, optional model column — same coverage as biscuit CSV.
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

random.seed(2027)

# brand, weight, category, (price_lo, price_hi) INR
BRANDS = [
    ("Zara", 22, "Women's Dress", (1299, 5999)),
    ("H&M", 20, "Casual Wear", (399, 3499)),
    ("Levi's", 18, "Denim", (1499, 5499)),
    ("Allen Solly", 16, "Men's Shirt", (899, 3999)),
    ("Van Heusen", 14, "Formal Wear", (999, 4499)),
    ("Peter England", 14, "Men's Shirt", (699, 2999)),
    ("Biba", 12, "Ethnic Wear", (999, 4999)),
    ("FabIndia", 11, "Ethnic Wear", (799, 3999)),
    ("Manyavar", 10, "Ethnic Wear", (2499, 8999)),
    ("W for Woman", 9, "Women's Kurti", (499, 2499)),
    ("Pantaloons", 8, "Casual Wear", (399, 1999)),
    ("Mufti", 7, "Streetwear", (799, 3499)),
    ("United Colors of Benetton", 6, "Casual Wear", (999, 3999)),
    ("Marks & Spencer", 5, "Formal Wear", (1499, 5999)),
    ("Lifestyle", 5, "Footwear", (799, 4999)),
]

CASUAL_FEATURES = [
    "Cotton,Regular Fit,Breathable",
    "Linen Blend,Relaxed Fit,Summer Wear",
    "Poly Cotton,Easy Care,Wrinkle Resistant",
    "Oversized Fit,Street Style,Unisex",
    "Crop Top,Stretch Fabric,Lightweight",
]

DENIM_FEATURES = [
    "Stretch Denim,Slim Fit,Fade Wash",
    "High Rise,Skinny Fit,Dark Indigo",
    "Straight Fit,Mid Rise,Comfort Stretch",
    "Bootcut,Classic Blue,Heavy Stitch",
]

FORMAL_FEATURES = [
    "Non Iron,Spread Collar,Office Wear",
    "Slim Fit,Cotton Rich,Full Sleeves",
    "Wrinkle Free,Formal Cut,Pocket Square Ready",
    "Tailored Fit,Premium Cotton,Business Casual",
]

ETHNIC_FEATURES = [
    "Silk Blend,Embroidered,Festive Wear",
    "Cotton Handloom,Block Print,Sustainable",
    "Chikankari,Lightweight,Party Wear",
    "Banarasi Weave,Gold Zari,Wedding Collection",
]

FOOTWEAR_FEATURES = [
    "Cushioned Sole,Running,Lightweight",
    "Leather Upper,Formal Lace Up,Anti Slip",
    "Memory Foam,Casual Sneaker,Breathable Mesh",
    "Slip On,Everyday Comfort,Rubber Outsole",
]

ACTIVE_FEATURES = [
    "Moisture Wicking,Quick Dry,Gym Wear",
    "4-Way Stretch,Yoga Fit,High Waist",
    "Reflective Trim,Running Jacket,Wind Resistant",
]

GAP_RARE = [
    ("Zara", "Organic Hemp,Vegan Dye,Zero Waste Line"),
    ("H&M", "Recycled Ocean Plastic,Waterless Dye,Carbon Neutral"),
    ("Levi's", "Selvedge Denim,Japanese Mill,Raw Unsanforized"),
    ("Allen Solly", "Cooling Tech,UV Protection,Anti Odour"),
    ("Biba", "Plus Size Inclusive,Adaptive Fasteners,Easy Wear"),
    ("FabIndia", "Hand Spun Khadi,Natural Indigo,Artisan Co-op"),
    ("Manyavar", "Rentable Groom Set,Eco Packaging,Rental Ready"),
    ("Mufti", "Heated Jacket,Battery Pack,Winter Tech"),
    ("Lifestyle", "3D Printed Sole,Custom Fit Scan,Smart Insole"),
    ("W for Woman", "Maternity Friendly,Nursing Access,Soft Bamboo"),
]

DELIMITER_SAMPLES = [
    ("H&M", "Cotton|Regular Fit|Breathable"),
    ("Peter England", "Non Iron;Spread Collar;Office Wear"),
    ("Biba", "Silk Blend|Embroidered|Festive Wear"),
]

POPULAR_GAP_FEATURE = "Sustainable Cotton,Regular Fit,Breathable,Machine Washable"

VARIANT = ["Classic", "Essential", "Premium", "Limited", "Seasonal", "Studio"]
PACK_SUFFIX = ["Collection", "Line", "Edition", "Series", "Drop"]


def _price(lo: float, hi: float, *, premium: bool = False) -> float:
    x = random.uniform(lo, hi)
    if premium:
        x *= random.uniform(1.08, 1.35)
    x = round(x / 99) * 99
    if x < 199:
        x = 199.0
    return round(x, 2)


def _model(brand: str, category: str) -> str:
    size = random.choice(["S", "M", "L", "XL", "32", "34", "36", "38"])
    return (
        f"{brand} {category} {random.choice(VARIANT)} "
        f"Size {size} {random.choice(PACK_SUFFIX)}"
    )


def _feature_pool(category: str) -> list[str]:
    pools = {
        "Women's Dress": CASUAL_FEATURES + ACTIVE_FEATURES[:2],
        "Casual Wear": CASUAL_FEATURES,
        "Denim": DENIM_FEATURES,
        "Men's Shirt": FORMAL_FEATURES + CASUAL_FEATURES[:2],
        "Formal Wear": FORMAL_FEATURES,
        "Ethnic Wear": ETHNIC_FEATURES,
        "Women's Kurti": ETHNIC_FEATURES + CASUAL_FEATURES[:3],
        "Streetwear": CASUAL_FEATURES + DENIM_FEATURES[:2],
        "Footwear": FOOTWEAR_FEATURES,
    }
    return pools.get(category, CASUAL_FEATURES)


def build_rows() -> list[dict]:
    rows: list[dict] = []

    for brand, weight, category, (plo, phi) in BRANDS:
        pool = _feature_pool(category)
        for _ in range(weight):
            feat = random.choice(pool)
            premium = any(
                k in feat
                for k in ("Silk", "Embroidered", "Leather", "Banarasi", "Premium")
            )
            rows.append(
                {
                    "brand": brand,
                    "price": _price(plo, phi, premium=premium),
                    "feature": feat,
                    "category": category,
                    "model": _model(brand, category),
                }
            )

    for brand, feat in DELIMITER_SAMPLES:
        cat = next(c for b, _, c, _ in BRANDS if b == brand)
        plo, phi = next(p for b, _, _, p in BRANDS if b == brand)
        rows.append(
            {
                "brand": brand,
                "price": _price(plo, phi),
                "feature": feat,
                "category": cat,
                "model": _model(brand, cat),
            }
        )

    for brand in ("Zara", "Levi's", "Manyavar", "Marks & Spencer"):
        cat = next(c for b, _, c, _ in BRANDS if b == brand)
        plo, phi = next(p for b, _, _, p in BRANDS if b == brand)
        rows.append(
            {
                "brand": brand,
                "price": _price(plo, phi),
                "feature": POPULAR_GAP_FEATURE,
                "category": cat,
                "model": _model(brand, cat),
            }
        )

    for brand in ("H&M", "Allen Solly", "Peter England", "Biba", "FabIndia", "Pantaloons"):
        cat = next(c for b, _, c, _ in BRANDS if b == brand)
        plo, phi = next(p for b, _, _, p in BRANDS if b == brand)
        for _ in range(6):
            rows.append(
                {
                    "brand": brand,
                    "price": _price(plo, phi),
                    "feature": POPULAR_GAP_FEATURE,
                    "category": cat,
                    "model": _model(brand, cat),
                }
            )

    for brand, feat in GAP_RARE:
        cat = next((c for b, _, c, _ in BRANDS if b == brand), "Casual Wear")
        plo, phi = next((p for b, _, _, p in BRANDS if b == brand), (499, 2999))
        rows.append(
            {
                "brand": brand,
                "price": _price(phi * 0.85, phi * 1.25, premium=True),
                "feature": feat,
                "category": cat,
                "model": _model(brand, cat),
            }
        )

    outliers = [
        ("Pantaloons", 199.0, "Basic Tee,Cotton,Regular Fit", "Casual Wear"),
        ("H&M", 299.0, "Poly Cotton,Easy Care,Wrinkle Resistant", "Casual Wear"),
        ("Manyavar", 8999.0, "Wedding Sherwani,Silk Blend,Gold Embroidery", "Ethnic Wear"),
        ("Zara", 7499.0, "Evening Gown,Satin Finish,Limited Edition", "Women's Dress"),
        ("Levi's", 5499.0, "Premium Denim,Japanese Selvedge,Collector Edition", "Denim"),
        ("Lifestyle", 4999.0, "Leather Boots,Formal Lace Up,Anti Slip", "Footwear"),
    ]
    for brand, price, feat, cat in outliers:
        rows.append(
            {
                "brand": brand,
                "price": price,
                "feature": feat,
                "category": cat,
                "model": _model(brand, cat),
            }
        )

    for brand in ("H&M", "Allen Solly", "Biba"):
        cat = next(c for b, _, c, _ in BRANDS if b == brand)
        plo, phi = next(p for b, _, _, p in BRANDS if b == brand)
        rows.append(
            {
                "brand": brand,
                "price": _price(plo, phi),
                "feature": random.choice(_feature_pool(cat)),
                "category": "",
                "model": "",
            }
        )

    return rows


def main() -> None:
    import sys

    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    rows = build_rows()
    dup_sources = random.sample(rows, min(12, len(rows)))
    rows.extend(dup_sources)

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=2027).reset_index(drop=True)

    out = root / "test_trendscanner_fashion_inr.csv"
    df.to_csv(out, index=False, encoding="utf-8")

    from core.ingestion import read_csv_file
    from core.validator import validate_and_clean
    from core.orchestrator import run_all_agents

    raw = read_csv_file(str(out))
    cleaned = validate_and_clean(raw, cleaning_strategy="drop_rows", remove_dupes=True)
    results = run_all_agents(
        cleaned,
        brand_column="brand",
        price_column="price",
        feature_column="feature",
        top_n_brands=12,
        top_n_features=15,
        gap_threshold=-0.5,
    )

    stats = results["agents"]["pricing"]["results"]["price_statistics"]
    gaps = results["agents"]["gap"]["results"]

    print(f"Wrote: {out}")
    print(f"  Raw rows: {len(df)} | After clean: {len(cleaned)}")
    print(f"  Brands: {results['agents']['brand']['results']['total_unique_brands']}")
    print(
        f"  Unique feature tokens: "
        f"{results['agents']['feature']['results']['total_unique_features']}"
    )
    print(f"  Price INR range: {stats['min_price']:,.2f} – {stats['max_price']:,.2f}")
    print(f"  Gap pairs flagged: {gaps['identified_gaps_count']}")


if __name__ == "__main__":
    main()
