"""
Generate a small fake e-commerce interactions dataset.

The dataset schema is:
- user_id
- product_id
- product_name
- category
- rating
"""

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd


def _build_product_catalog() -> List[dict]:
    """Create a fixed product catalog used for fake interactions."""
    return [
        {"product_id": 101, "product_name": "Wireless Mouse", "category": "Electronics"},
        {"product_id": 102, "product_name": "Mechanical Keyboard", "category": "Electronics"},
        {"product_id": 103, "product_name": "Noise Cancelling Headphones", "category": "Electronics"},
        {"product_id": 104, "product_name": "USB-C Hub", "category": "Electronics"},
        {"product_id": 105, "product_name": "Gaming Monitor", "category": "Electronics"},
        {"product_id": 201, "product_name": "Running Shoes", "category": "Fashion"},
        {"product_id": 202, "product_name": "Cotton T-Shirt", "category": "Fashion"},
        {"product_id": 203, "product_name": "Slim Fit Jeans", "category": "Fashion"},
        {"product_id": 301, "product_name": "Stainless Steel Bottle", "category": "Home"},
        {"product_id": 302, "product_name": "Desk Lamp", "category": "Home"},
        {"product_id": 303, "product_name": "Air Purifier", "category": "Home"},
        {"product_id": 401, "product_name": "Yoga Mat", "category": "Sports"},
        {"product_id": 402, "product_name": "Dumbbell Set", "category": "Sports"},
        {"product_id": 501, "product_name": "Mystery Novel", "category": "Books"},
        {"product_id": 502, "product_name": "Cookbook", "category": "Books"},
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
