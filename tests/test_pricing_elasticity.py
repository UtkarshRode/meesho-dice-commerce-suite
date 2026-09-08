"""
Automated unit tests for Dynamic Price Elasticity Optimizer.
Tests Log-Log OLS regression fitting, negative elasticity validation, and optimal price calculation.
"""
import pytest
import sys
import os

# Add service directory to sys.path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "dynamic_price_elasticity"))
sys.path.insert(0, service_dir)

from pricing_models import PriceDemandPoint
from elasticity_engine import PriceElasticityEngine
from buy_box_recommender import BuyBoxRecommender

def test_elasticity_regression():
    engine = PriceElasticityEngine()

    # Synthetic price-demand points with known inverse relationship: Q increases as P drops
    data = [
        PriceDemandPoint(date="2026-08-01", price=400.0, units_sold=50, competitor_price=380.0),
        PriceDemandPoint(date="2026-08-08", price=350.0, units_sold=75, competitor_price=350.0),
        PriceDemandPoint(date="2026-08-15", price=300.0, units_sold=110, competitor_price=320.0),
        PriceDemandPoint(date="2026-08-22", price=250.0, units_sold=160, competitor_price=290.0)
    ]

    epsilon, alpha, r2 = engine.fit_elasticity(data)

    # Elasticity must be negative (downward sloping demand)
    assert epsilon < 0.0
    # Must have strong correlation
    assert r2 > 0.80

    # Demand prediction: lower price yields higher quantity
    q_high = engine.predict_quantity(380.0, epsilon, alpha)
    q_low = engine.predict_quantity(260.0, epsilon, alpha)
    assert q_low > q_high

def test_optimal_price_profit_maximization():
    engine = PriceElasticityEngine()
    unit_cost = 150.0
    current_price = 350.0
    epsilon = -1.80
    alpha = 14.5

    opt_p, curr_profit, opt_profit = engine.compute_optimal_price(unit_cost, current_price, epsilon, alpha)

    # Optimal price must be above unit cost
    assert opt_p > unit_cost
    # Optimal profit must be greater than or equal to current profit
    assert opt_profit >= curr_profit

def test_buy_box_undercut_recommendation():
    recommender = BuyBoxRecommender()
    rec = recommender.recommend(
        current_price=350.0,
        unit_cost=150.0,
        competitor_price=300.0,
        optimal_profit_price=288.0
    )

    assert rec["status"] == "AT_RISK_OVERPRICED"
    assert rec["suggested_price"] <= 300.0
    assert rec["margin_inr"] > 0
