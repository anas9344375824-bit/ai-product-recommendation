# AI Product Recommendation System

A full example recommendation API using:
- `pandas`
- `scikit-learn`
- `FastAPI`

It generates a fake e-commerce ratings dataset and serves top product recommendations with collaborative filtering.

## Project Structure

```text
ai-recommendation-system/
|-- app/
|   |-- __init__.py
|   |-- main.py
|   |-- recommender.py
|   |-- dataset_generator.py
|   |-- static/
|   |   |-- index.html
|   |   |-- styles.css
|   |   `-- app.js
|   `-- requirements.txt
|-- data/
`-- README.md
```

## ML Approach (Collaborative Filtering)

`app/recommender.py` uses **user-user collaborative filtering**:
1. Build a user-item rating matrix from the dataset.
2. Compute cosine similarity between users.
3. Predict unseen product scores using weighted ratings from similar users.
4. Return top 5 products.
5. For unknown users (cold start), fallback to globally popular products.

## Setup

From project root:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r app/requirements.txt
```

## Generate Dataset

Run:

```bash
python app/dataset_generator.py
```

This creates:

`data/interactions.csv`

Columns:
- `user_id`
- `product_id`
- `product_name`
- `category`
- `rating`

## Run API

Windows PowerShell:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8001
```

macOS/Linux:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

## UI URL

Open:

`http://127.0.0.1:8001/`

Health endpoint:

`http://127.0.0.1:8001/health`

## API Endpoint

### `GET /recommend/{user_id}`

Example:

```bash
curl http://127.0.0.1:8001/recommend/1
```

Example JSON response:

```json
{
  "user_id": 1,
  "recommended_products": [
    {
      "product_id": 302,
      "product_name": "Desk Lamp",
      "category": "Home",
      "score": 3.9912
    }
  ]
}
```

Note: The API always returns up to top 5 recommendations.
