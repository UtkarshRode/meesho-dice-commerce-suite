"""
FastAPI Microservice for Dynamic Price Elasticity & Revenue Optimizer.
Provides econometric price regression, What-If profit simulations,
and Buy-Box competitor pricing intelligence for marketplace sellers.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
import os

try:
    from pricing_models import (
        ProductCatalogItem, PriceDemandPoint, ElasticityResult,
        WhatIfSimulationResponse
    )
except ImportError:
    from .pricing_models import (
        ProductCatalogItem, PriceDemandPoint, ElasticityResult,
        WhatIfSimulationResponse
    )
try:
    from elasticity_engine import PriceElasticityEngine
    from buy_box_recommender import BuyBoxRecommender
except ImportError:
    from .elasticity_engine import PriceElasticityEngine
    from .buy_box_recommender import BuyBoxRecommender

app = FastAPI(
    title="Meesho DICE 3.0: Dynamic Price Elasticity Optimizer",
    description="Econometric Constant-Elasticity Modeling and Margin-Maximizing Seller Simulator",
    version="1.0.0"
)

engine = PriceElasticityEngine()
recommender = BuyBoxRecommender()

# Seed catalog items with realistic Indian apparel/accessory pricing data
DEMO_PRODUCTS = [
    ProductCatalogItem(
        product_id="prod_bandhani_saree_01",
        title="Jaipuri Bandhani Georgette Saree (Yellow)",
        category="ethnic_wear",
        unit_cost=180.0,
        current_price=349.0,
        competitor_lowest_price=319.0,
        historical_sales=[
            PriceDemandPoint(date="2026-08-01", price=380.0, units_sold=42, competitor_price=340.0),
            PriceDemandPoint(date="2026-08-08", price=360.0, units_sold=58, competitor_price=330.0),
            PriceDemandPoint(date="2026-08-15", price=349.0, units_sold=72, competitor_price=325.0),
            PriceDemandPoint(date="2026-08-22", price=320.0, units_sold=110, competitor_price=320.0),
            PriceDemandPoint(date="2026-08-29", price=299.0, units_sold=155, competitor_price=315.0),
            PriceDemandPoint(date="2026-09-05", price=279.0, units_sold=198, competitor_price=310.0)
        ]
    ),
    ProductCatalogItem(
        product_id="prod_cotton_kurti_02",
        title="Pure Cotton Floral Printed Straight Kurti",
        category="ethnic_wear",
        unit_cost=120.0,
        current_price=249.0,
        competitor_lowest_price=229.0,
        historical_sales=[
            PriceDemandPoint(date="2026-08-01", price=279.0, units_sold=65, competitor_price=249.0),
            PriceDemandPoint(date="2026-08-08", price=259.0, units_sold=88, competitor_price=239.0),
            PriceDemandPoint(date="2026-08-15", price=249.0, units_sold=104, competitor_price=235.0),
            PriceDemandPoint(date="2026-08-22", price=229.0, units_sold=140, competitor_price=229.0),
            PriceDemandPoint(date="2026-08-29", price=210.0, units_sold=192, competitor_price=225.0)
        ]
    ),
    ProductCatalogItem(
        product_id="prod_kundan_earrings_03",
        title="Handcrafted Kundan Meenakari Jhumka Earrings",
        category="jewellery",
        unit_cost=65.0,
        current_price=179.0,
        competitor_lowest_price=169.0,
        historical_sales=[
            PriceDemandPoint(date="2026-08-01", price=199.0, units_sold=50, competitor_price=180.0),
            PriceDemandPoint(date="2026-08-08", price=189.0, units_sold=62, competitor_price=175.0),
            PriceDemandPoint(date="2026-08-15", price=179.0, units_sold=80, competitor_price=169.0),
            PriceDemandPoint(date="2026-08-22", price=159.0, units_sold=125, competitor_price=165.0)
        ]
    )
]

catalog: Dict[str, ProductCatalogItem] = {p.product_id: p for p in DEMO_PRODUCTS}

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

class SimulationRequest(BaseModel):
    tested_price: float

@app.get("/api/products", response_model=List[ProductCatalogItem])
def list_products():
    return list(catalog.values())

@app.get("/api/products/{product_id}/elasticity", response_model=ElasticityResult)
def get_product_elasticity(product_id: str):
    if product_id not in catalog:
        raise HTTPException(status_code=404, detail="Product not found")

    prod = catalog[product_id]
    epsilon, alpha, r2 = engine.fit_elasticity(prod.historical_sales)
    opt_p, curr_profit, opt_profit = engine.compute_optimal_price(
        prod.unit_cost, prod.current_price, epsilon, alpha
    )

    profit_uplift = ((opt_profit - curr_profit) / curr_profit) * 100.0 if curr_profit > 0 else 0.0

    rec = recommender.recommend(
        prod.current_price, prod.unit_cost, prod.competitor_lowest_price, opt_p
    )

    return ElasticityResult(
        product_id=prod.product_id,
        elasticity_coefficient=epsilon,
        is_price_elastic=(abs(epsilon) > 1.0),
        r_squared=r2,
        optimal_profit_price=opt_p,
        current_weekly_profit=curr_profit,
        projected_optimal_profit=opt_profit,
        profit_uplift_percentage=round(profit_uplift, 1),
        smart_price_recommendation=rec["action_recommendation"]
    )

@app.post("/api/products/{product_id}/simulate", response_model=WhatIfSimulationResponse)
def simulate_price(product_id: str, payload: SimulationRequest):
    if product_id not in catalog:
        raise HTTPException(status_code=404, detail="Product not found")

    prod = catalog[product_id]
    epsilon, alpha, r2 = engine.fit_elasticity(prod.historical_sales)
    return engine.generate_simulation_curve(
        prod.unit_cost, prod.current_price, payload.tested_price, epsilon, alpha, product_id
    )

@app.get("/", response_class=HTMLResponse)
def index_view():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Price Elasticity Engine Running</h1>"
