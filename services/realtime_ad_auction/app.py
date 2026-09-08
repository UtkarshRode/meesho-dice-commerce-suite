"""
FastAPI Microservice for Real-Time Sponsored Product Bidding Engine.
Provides REST endpoints for auction clearing, campaign registration,
click attribution with fraud detection, and budget reporting.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Dict
import os
import uuid

try:
    from auction_models import (
        SellerCampaign, AuctionRequest, AuctionResponse,
        ClickEvent, AdPlacement
    )
    from auction_server import GSPAuctionServer
    from click_fraud import ClickFraudDetector
except ImportError:
    from .auction_models import (
        SellerCampaign, AuctionRequest, AuctionResponse,
        ClickEvent, AdPlacement
    )
    from .auction_server import GSPAuctionServer
    from .click_fraud import ClickFraudDetector

app = FastAPI(
    title="Meesho DICE 3.0: Real-Time Ad-Auction Engine",
    description="Generalized Second-Price (GSP) Sponsored Product Auction with Diurnal Budget Pacing and pCTR Scoring",
    version="1.0.0"
)

server = GSPAuctionServer()
fraud_detector = ClickFraudDetector()

# Seed default mock campaigns from realistic Indian apparel/electronics sellers
DEFAULT_CAMPAIGNS = [
    SellerCampaign(
        campaign_id="camp_surat_saree_01",
        seller_id="seller_surat_textiles",
        product_id="prod_saree_101",
        product_title="Surat Pure Georgette Bandhani Printed Saree (Yellow)",
        category="ethnic_wear",
        max_cpc_bid=4.50,
        daily_budget=500.0,
        spent_today=120.50,
        seller_rating=4.7,
        historical_ctr=0.048
    ),
    SellerCampaign(
        campaign_id="camp_jaipur_kurti_02",
        seller_id="seller_jaipur_crafts",
        product_id="prod_kurti_202",
        product_title="Jaipuri Cotton Anarkali Kurti with Dupatta",
        category="ethnic_wear",
        max_cpc_bid=3.80,
        daily_budget=300.0,
        spent_today=295.00,  # Near exhaustion to demo budget throttling
        seller_rating=4.3,
        historical_ctr=0.032
    ),
    SellerCampaign(
        campaign_id="camp_ludhiana_knit_03",
        seller_id="seller_punjab_hosiery",
        product_id="prod_kurti_303",
        product_title="Designer Embroidered Rayon Kurti (Yellow Floral)",
        category="ethnic_wear",
        max_cpc_bid=5.20,
        daily_budget=800.0,
        spent_today=85.00,
        seller_rating=4.9,
        historical_ctr=0.055
    ),
    SellerCampaign(
        campaign_id="camp_delhi_jewel_04",
        seller_id="seller_chandni_chowk",
        product_id="prod_earring_404",
        product_title="Traditional Kundan Jhumka Earring Set (Gold Plated)",
        category="jewellery",
        max_cpc_bid=2.50,
        daily_budget=250.0,
        spent_today=40.00,
        seller_rating=4.1,
        historical_ctr=0.029
    ),
    SellerCampaign(
        campaign_id="camp_bengaluru_watch_05",
        seller_id="seller_tech_direct",
        product_id="prod_smartwatch_505",
        product_title="Bluetooth Calling Smartwatch with Heart Rate Monitor",
        category="electronics",
        max_cpc_bid=6.00,
        daily_budget=1000.0,
        spent_today=320.00,
        seller_rating=4.5,
        historical_ctr=0.041
    )
]

for c in DEFAULT_CAMPAIGNS:
    server.register_campaign(c)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

@app.post("/api/campaigns", response_model=SellerCampaign)
def create_campaign(campaign: SellerCampaign):
    server.register_campaign(campaign)
    return campaign

@app.get("/api/campaigns", response_model=List[SellerCampaign])
def list_campaigns():
    return list(server.campaigns.values())

@app.post("/api/auction/run", response_model=AuctionResponse)
def run_auction(request: AuctionRequest, hour: int = None):
    return server.run_auction(request, current_hour=hour)

@app.post("/api/clicks/record")
def record_click(click: ClickEvent, req: Request):
    ip = click.ip_address or req.client.host
    valid, reason = fraud_detector.is_valid_click(ip, click.user_id, click.campaign_id)
    if not valid:
        return {"status": "REJECTED_FRAUD", "reason": reason, "charged": 0.0}

    # Deduct spend from campaign
    if click.campaign_id in server.campaigns:
        camp = server.campaigns[click.campaign_id]
        camp.spent_today = round(camp.spent_today + click.charged_cpc, 2)

    return {
        "status": "CLICK_CHARGED",
        "charged_inr": click.charged_cpc,
        "campaign_id": click.campaign_id,
        "reason": reason
    }

@app.get("/", response_class=HTMLResponse)
def index_view():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Ad-Auction Engine Running</h1>"
