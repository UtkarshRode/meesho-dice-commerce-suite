"""
Automated unit tests for the Real-Time Ad-Auction Engine.
Verifies GSP pricing logic, budget pacing, and fraud detection.
"""
import pytest
import sys
import os

# Add service directory to sys.path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "realtime_ad_auction"))
sys.path.insert(0, service_dir)

from auction_models import SellerCampaign, AuctionRequest, AdPlacement
from auction_server import GSPAuctionServer
from budget_pacer import BudgetPacer
from click_fraud import ClickFraudDetector

def test_gsp_second_price_discount():
    server = GSPAuctionServer()

    # Seller 1: high bid
    server.register_campaign(SellerCampaign(
        campaign_id="camp_high",
        seller_id="seller_1",
        product_id="prod_1",
        product_title="Silk Saree",
        category="ethnic",
        max_cpc_bid=10.0,
        daily_budget=500.0,
        spent_today=10.0,
        seller_rating=4.5,
        historical_ctr=0.05
    ))

    # Seller 2: medium bid
    server.register_campaign(SellerCampaign(
        campaign_id="camp_runner_up",
        seller_id="seller_2",
        product_id="prod_2",
        product_title="Cotton Saree",
        category="ethnic",
        max_cpc_bid=6.0,
        daily_budget=500.0,
        spent_today=10.0,
        seller_rating=4.5,
        historical_ctr=0.05
    ))

    req = AuctionRequest(
        request_id="req_test_1",
        query="Saree",
        category="ethnic",
        user_id="user_123",
        slot_count=1
    )

    resp = server.run_auction(req, current_hour=14)
    assert len(resp.winning_ads) == 1
    winner = resp.winning_ads[0]
    assert winner.campaign_id == "camp_high"
    # GSP: Charged CPC must be LESS than or equal to raw max bid
    assert winner.charged_cpc < winner.raw_bid_cpc
    assert winner.charged_cpc >= server.RESERVE_PRICE_CPC

def test_budget_pacing_exhaustion():
    pacer = BudgetPacer()
    participate, rho, status = pacer.get_pacing_decision(
        daily_budget=500.0,
        spent_today=500.0,
        current_hour=10
    )
    assert participate is False
    assert rho == 0.0
    assert status == "DAILY_BUDGET_EXHAUSTED"

def test_click_fraud_burst_rejection():
    detector = ClickFraudDetector(window_seconds=60, max_clicks_per_window=3)
    ip = "203.0.113.195"

    # Click 1: valid
    assert detector.is_valid_click(ip, "user_a", "camp_1")[0] is True
    # Click 2: valid
    assert detector.is_valid_click(ip, "user_a", "camp_1")[0] is True
    # Click 3: duplicate spam on same campaign rejected!
    valid, reason = detector.is_valid_click(ip, "user_a", "camp_1")
    assert valid is False
    assert reason == "FRAUD_REPEAT_CAMPAIGN_SPAM"
