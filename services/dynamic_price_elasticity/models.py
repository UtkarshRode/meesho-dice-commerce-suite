"""
Data models for Econometric Price Elasticity Modeling & Dynamic Revenue Optimizer.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone

class PriceDemandPoint(BaseModel):
    date: str
    price: float
    units_sold: int
    competitor_price: float

class ProductCatalogItem(BaseModel):
    product_id: str
    title: str
    category: str
    unit_cost: float = Field(..., description="Seller manufacturing/procurement cost in INR")
    current_price: float = Field(..., description="Active listing price on Meesho in INR")
    competitor_lowest_price: float = Field(..., description="Lowest competitor price on Flipkart/Amazon in INR")
    historical_sales: List[PriceDemandPoint] = []

class ElasticityResult(BaseModel):
    product_id: str
    elasticity_coefficient: float
    is_price_elastic: bool
    r_squared: float
    optimal_profit_price: float
    current_weekly_profit: float
    projected_optimal_profit: float
    profit_uplift_percentage: float
    smart_price_recommendation: str

class SimulationPoint(BaseModel):
    price: float
    projected_units: int
    projected_revenue: float
    projected_profit: float

class WhatIfSimulationResponse(BaseModel):
    product_id: str
    unit_cost: float
    current_price: float
    tested_price: float
    elasticity: float
    delta_price_pct: float
    delta_volume_pct: float
    delta_profit_pct: float
    curve_points: List[SimulationPoint]
