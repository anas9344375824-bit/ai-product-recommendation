"""
Collaborative filtering recommender.

This module uses user-user collaborative filtering:
1. Build a user-item ratings matrix.
2. Compute cosine similarity between users.
3. Predict scores for unseen products using weighted ratings from similar users.
"""

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class ProductRecommender:
    """Recommend products based on collaborative filtering."""

    REQUIRED_COLUMNS = {"user_id", "product_id", "product_name", "category", "rating"}

    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)
        self.df = self._load_data()
        self.product_lookup = (
            self.df[["product_id", "product_name", "category"]]
            .drop_duplicates(subset=["product_id"])
            .set_index("product_id")
        )

        # User-item matrix: rows are users, columns are products, values are ratings.
        self.user_item_matrix = (
            self.df.pivot_table(index="user_id", columns="product_id", values="rating", fill_value=0)
            .sort_index()
            .sort_index(axis=1)
        )
        self.user_similarity = self._compute_user_similarity()

    def _load_data(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.data_path}")

        df = pd.read_csv(self.data_path)
        missing_cols = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise ValueError(f"Dataset missing required columns: {sorted(missing_cols)}")
        return df

    def _compute_user_similarity(self) -> pd.DataFrame:
        # Cosine similarity compares users based on the direction of their rating vectors.
        similarity_matrix = cosine_similarity(self.user_item_matrix)
        return pd.DataFrame(
            similarity_matrix,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index,
        )

    def _popular_products(self, exclude_product_ids: set, top_n: int) -> List[Dict]:
        agg = (
            self.df.groupby("product_id")
            .agg(avg_rating=("rating", "mean"), rating_count=("rating", "count"))
            .sort_values(["avg_rating", "rating_count"], ascending=[False, False])
        )

        results = []
        for product_id, row in agg.iterrows():
            if product_id in exclude_product_ids:
                continue

            product_meta = self.product_lookup.loc[product_id]
            results.append(
                {
                    "product_id": int(product_id),
                    "product_name": str(product_meta["product_name"]),
                    "category": str(product_meta["category"]),
                    "score": round(float(row["avg_rating"]), 4),
                }
            )
            if len(results) >= top_n:
                break
        return results

    def recommend(self, user_id: int, top_n: int = 5) -> List[Dict]:
        """
        Recommend top N unseen products for a user.

        For each unseen product, predicted score is a weighted average of ratings
        from similar users:
            pred(u, i) = sum(sim(u, v) * r(v, i)) / sum(|sim(u, v)|)
        """
        if top_n <= 0:
            return []

        # Cold-start fallback: unknown users get popular products.
        if user_id not in self.user_item_matrix.index:
            return self._popular_products(exclude_product_ids=set(), top_n=top_n)

        target_ratings = self.user_item_matrix.loc[user_id]
        seen_products = set(target_ratings[target_ratings > 0].index.tolist())
        unseen_products = [pid for pid in self.user_item_matrix.columns if pid not in seen_products]

        # Similarity scores to other users, excluding self.
        similarities = self.user_similarity.loc[user_id].drop(index=user_id)
        candidate_scores = []

        for product_id in unseen_products:
            other_ratings = self.user_item_matrix[product_id]
            rated_mask = other_ratings > 0
            if not rated_mask.any():
                continue

            sims = similarities[rated_mask.loc[similarities.index]]
            ratings = other_ratings.loc[sims.index]

            denominator = np.abs(sims).sum()
            if denominator == 0:
                continue

            predicted_rating = float(np.dot(sims, ratings) / denominator)
            product_meta = self.product_lookup.loc[product_id]
            candidate_scores.append(
                {
                    "product_id": int(product_id),
                    "product_name": str(product_meta["product_name"]),
                    "category": str(product_meta["category"]),
                    "score": round(predicted_rating, 4),
                }
            )

        # Rank by predicted score and keep top N.
        candidate_scores.sort(key=lambda x: x["score"], reverse=True)
        recommendations = candidate_scores[:top_n]

        # If model-based results are not enough, fill with globally popular items.
        if len(recommendations) < top_n:
            recommended_ids = {item["product_id"] for item in recommendations}
            exclude_ids = seen_products.union(recommended_ids)
            needed = top_n - len(recommendations)
            recommendations.extend(self._popular_products(exclude_product_ids=exclude_ids, top_n=needed))

        return recommendations[:top_n]
