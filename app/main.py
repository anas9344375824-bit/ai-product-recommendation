from pathlib import Path
from typing import Any, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.dataset_generator import generate_fake_dataset
from app.recommender import ProductRecommender


class ProductRecommendation(BaseModel):
    product_id: int = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product display name")
    category: str = Field(..., description="Product category")
    brand: str = Field(..., description="Product brand")
    price: int = Field(..., description="Product price in INR")
    features: List[str] = Field(..., description="Product feature tags")
    image_url: str = Field(..., description="Product image URL")
    score: float = Field(..., description="Predicted relevance score")


class RecommendationResponse(BaseModel):
    user_id: int = Field(..., description="Requested user ID")
    recommended_products: List[ProductRecommendation]


class ProductCatalogItem(BaseModel):
    product_id: int = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product display name")
    category: str = Field(..., description="Product category")
    brand: str = Field(..., description="Product brand")
    price: int = Field(..., description="Product price in INR")
    features: List[str] = Field(..., description="Product feature tags")
    image_url: str = Field(..., description="Product image URL")


app = FastAPI(title="AI Product Recommendation System")

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
DATA_PATH = PROJECT_ROOT / "data" / "interactions.csv"
STATIC_DIR = APP_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def initialize_recommender() -> None:
    """
    Initialize dataset and recommender once at startup.
    """
    if getattr(app.state, "recommender", None) is not None:
        return

    try:
        if not DATA_PATH.exists():
            generate_fake_dataset(DATA_PATH)
        try:
            app.state.recommender = ProductRecommender(DATA_PATH)
        except ValueError:
            generate_fake_dataset(DATA_PATH)
            app.state.recommender = ProductRecommender(DATA_PATH)
        app.state.init_error = None
    except Exception as exc:  # pragma: no cover - safety net for startup failures
        app.state.recommender = None
        app.state.init_error = str(exc)


@app.on_event("startup")
def startup_event() -> None:
    initialize_recommender()


@app.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check() -> dict[str, str]:
    if getattr(app.state, "init_error", None):
        return {"status": "degraded", "message": app.state.init_error}
    return {"status": "ok", "message": "Recommendation API is running"}


@app.get("/products", response_model=List[ProductCatalogItem])
def list_products() -> List[ProductCatalogItem]:
    recommender: ProductRecommender | None = getattr(app.state, "recommender", None)
    if recommender is None:
        initialize_recommender()
        recommender = getattr(app.state, "recommender", None)

    if recommender is None:
        init_error = getattr(app.state, "init_error", "Model initialization failed")
        raise HTTPException(status_code=500, detail=f"Recommender unavailable: {init_error}")

    return recommender.get_catalog()


@app.get("/recommend/{user_id}", response_model=RecommendationResponse)
def recommend_products(
    user_id: int, top_n: int = Query(5, ge=1, le=20)
) -> RecommendationResponse:
    """
    Return top 5 product recommendations for a user.
    """
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="user_id must be a positive integer")

    recommender: ProductRecommender | None = getattr(app.state, "recommender", None)
    if recommender is None:
        initialize_recommender()
        recommender = getattr(app.state, "recommender", None)

    if recommender is None:
        init_error = getattr(app.state, "init_error", "Model initialization failed")
        raise HTTPException(status_code=500, detail=f"Recommender unavailable: {init_error}")

    recommendations: List[dict[str, Any]] = recommender.recommend(user_id=user_id, top_n=top_n)
    return RecommendationResponse(user_id=user_id, recommended_products=recommendations)
