"""
Master Deployment Gateway for Meesho DICE 3.0 Commerce Suite.
Mounts all 4 engines under a unified FastAPI host, enabling 1-click cloud deployment.
"""
import os
import sys
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import sub-services
from services.realtime_ad_auction.app import app as ad_auction_app
from services.distributed_group_commerce.app import app as group_commerce_app
from services.dynamic_price_elasticity.app import app as pricing_app
from services.shoppable_video_catalog.app import app as video_app

app = FastAPI(
    title="Meesho DICE 3.0: Unified Commerce Engineering Suite",
    description="Flagship 4-Pillar Portfolio for Growth, Monetization, Content Commerce, and Pricing",
    version="1.0.0"
)

# Mount all 4 microservices as sub-applications
app.mount("/monetization", ad_auction_app)
app.mount("/growth", group_commerce_app)
app.mount("/pricing-engine", pricing_app)
app.mount("/content-commerce", video_app)

static_dir = os.path.join(root_dir, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "competition": "Meesho DICE Challenge 3.0",
        "tracks": ["Growth", "Monetization", "Content Commerce", "Pricing"],
        "services_online": 4
    }

@app.get("/", response_class=HTMLResponse)
def master_portal():
    portal_file = os.path.join(static_dir, "index.html")
    if os.path.exists(portal_file):
        with open(portal_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Meesho DICE 3.0 Suite Online</h1>"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
