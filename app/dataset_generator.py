"""
Generate a small fake e-commerce interactions dataset.

The dataset schema is:
- user_id
- product_id
- product_name
- category
- brand
- price
- features
- image_url
- rating
"""

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd


def _build_product_catalog() -> List[dict]:
    """Create a fixed product catalog used for fake interactions."""
    return [
        {
            "product_id": 101,
            "product_name": "iPhone 14",
            "category": "Smartphones",
            "brand": "Apple",
            "price": 79999,
            "features": ["Good Camera", "Long Battery", "Fast Charging"],
            "image_url": "/static/images/smartphone.svg",
        },
        {
            "product_id": 102,
            "product_name": "Samsung Galaxy S23",
            "category": "Smartphones",
            "brand": "Samsung",
            "price": 74999,
            "features": ["Good Camera", "Gaming Performance", "Fast Charging"],
            "image_url": "/static/images/smartphone.svg",
        },
        {
            "product_id": 103,
            "product_name": "OnePlus 11",
            "category": "Smartphones",
            "brand": "OnePlus",
            "price": 57999,
            "features": ["Fast Charging", "Gaming Performance", "Long Battery"],
            "image_url": "/static/images/smartphone.svg",
        },
        {
            "product_id": 104,
            "product_name": "Pixel 8",
            "category": "Smartphones",
            "brand": "Google",
            "price": 69999,
            "features": ["Good Camera", "Long Battery", "Fast Charging"],
            "image_url": "/static/images/smartphone.svg",
        },
        {
            "product_id": 105,
            "product_name": "Xiaomi 13",
            "category": "Smartphones",
            "brand": "Xiaomi",
            "price": 49999,
            "features": ["Fast Charging", "Gaming Performance"],
            "image_url": "/static/images/smartphone.svg",
        },
        {
            "product_id": 106,
            "product_name": "Samsung Galaxy A54",
            "category": "Smartphones",
            "brand": "Samsung",
            "price": 39999,
            "features": ["Good Camera", "Long Battery"],
            "image_url": "/static/images/smartphone.svg",
        },
        {
            "product_id": 107,
            "product_name": "Redmi Note 13 Pro",
            "category": "Smartphones",
            "brand": "Xiaomi",
            "price": 27999,
            "features": ["Good Camera", "Fast Charging"],
            "image_url": "/static/images/smartphone.svg",
        },
        {
            "product_id": 108,
            "product_name": "Realme 12 Pro",
            "category": "Smartphones",
            "brand": "Realme",
            "price": 29999,
            "features": ["Gaming Performance", "Fast Charging"],
            "image_url": "/static/images/smartphone.svg",
        },
        {
            "product_id": 201,
            "product_name": "MacBook Air M2",
            "category": "Laptops",
            "brand": "Apple",
            "price": 89999,
            "features": ["Long Battery", "Fast Charging"],
            "image_url": "/static/images/laptop.svg",
        },
        {
            "product_id": 202,
            "product_name": "Dell XPS 13",
            "category": "Laptops",
            "brand": "Dell",
            "price": 99999,
            "features": ["Long Battery", "Gaming Performance", "Fast Charging"],
            "image_url": "/static/images/laptop.svg",
        },
        {
            "product_id": 203,
            "product_name": "HP Spectre x360",
            "category": "Laptops",
            "brand": "HP",
            "price": 95999,
            "features": ["Long Battery", "Fast Charging"],
            "image_url": "/static/images/laptop.svg",
        },
        {
            "product_id": 301,
            "product_name": "Sony WH-1000XM5",
            "category": "Headphones",
            "brand": "Sony",
            "price": 29999,
            "features": ["Long Battery", "Fast Charging"],
            "image_url": "/static/images/headphones.svg",
        },
        {
            "product_id": 302,
            "product_name": "Bose QuietComfort 45",
            "category": "Headphones",
            "brand": "Bose",
            "price": 26999,
            "features": ["Long Battery"],
            "image_url": "/static/images/headphones.svg",
        },
        {
            "product_id": 303,
            "product_name": "AirPods Max",
            "category": "Headphones",
            "brand": "Apple",
            "price": 49999,
            "features": ["Long Battery", "Fast Charging"],
            "image_url": "/static/images/headphones.svg",
        },
        {
            "product_id": 401,
            "product_name": "Canon EOS R10",
            "category": "Cameras",
            "brand": "Canon",
            "price": 74999,
            "features": ["Good Camera"],
            "image_url": "/static/images/camera.svg",
        },
        {
            "product_id": 402,
            "product_name": "Sony Alpha ZV-E10",
            "category": "Cameras",
            "brand": "Sony",
            "price": 67999,
            "features": ["Good Camera"],
            "image_url": "/static/images/camera.svg",
        },
        {
            "product_id": 403,
            "product_name": "Nikon Z50",
            "category": "Cameras",
            "brand": "Nikon",
            "price": 71999,
            "features": ["Good Camera"],
            "image_url": "/static/images/camera.svg",
        },
    ]


def generate_fake_dataset(
    output_path: Path,
    num_users: int = 20,
    min_interactions: int = 5,
    max_interactions: int = 10,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Build user-product rating interactions and save them as CSV.

    We intentionally keep the data sparse so collaborative filtering has to
    infer missing preferences from similar users.
    """
    rng = np.random.default_rng(seed)
    products = _build_product_catalog()

    rows = []
    for user_id in range(1, num_users + 1):
        interactions_count = int(rng.integers(min_interactions, max_interactions + 1))
        chosen_indices = rng.choice(len(products), size=interactions_count, replace=False)

        for idx in chosen_indices:
            product = products[int(idx)]
            rows.append(
                {
                    "user_id": user_id,
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "brand": product["brand"],
                    "price": product["price"],
                    "features": ";".join(product["features"]),
                    "image_url": product["image_url"],
                    "rating": int(rng.integers(1, 6)),  # Ratings from 1 to 5
                }
            )

    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    csv_path = project_root / "data" / "interactions.csv"
    generated_df = generate_fake_dataset(csv_path)
    print(f"Dataset generated at: {csv_path}")
    print(f"Rows: {len(generated_df)}")
