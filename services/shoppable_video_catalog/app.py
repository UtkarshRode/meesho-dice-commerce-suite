"""
FastAPI Microservice for Interactive Shoppable Video Feed & Catalog Recognition System.
Provides timeline tag sync, computer-vision bounding box inference, and 1-click video commerce.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os

try:
    from video_models import VideoReel, ProductTag, VideoCartItem, BoundingBox
except ImportError:
    from .video_models import VideoReel, ProductTag, VideoCartItem, BoundingBox
try:
    from feed_service import VideoFeedService
    from vision_tagger import VisionCatalogMatcher
except ImportError:
    from .feed_service import VideoFeedService
    from .vision_tagger import VisionCatalogMatcher

app = FastAPI(
    title="Meesho DICE 3.0: Shoppable Video Feed & Catalog Pipeline",
    description="Contextual Video Commerce with Timeline Sync and Automated Visual Product Tagging",
    version="1.0.0"
)

feed = VideoFeedService()
matcher = VisionCatalogMatcher()

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

class FrameInferenceRequest(BaseModel):
    scene_label: str

@app.get("/api/videos", response_model=List[VideoReel])
def list_videos():
    return list(feed.reels.values())

@app.get("/api/videos/{video_id}/active-tag", response_model=Optional[ProductTag])
def get_active_tag(video_id: str, time: float = 0.0):
    tag = feed.get_active_tag(video_id, time)
    if not tag:
        raise HTTPException(status_code=404, detail="No active tag found")
    return tag

@app.post("/api/vision/detect-frame", response_model=List[BoundingBox])
def detect_frame_objects(payload: FrameInferenceRequest):
    return matcher.detect_and_match_frame(payload.scene_label)

@app.post("/api/cart/add")
def add_to_cart(item: VideoCartItem):
    total = feed.add_to_cart(item)
    return {
        "status": "ADDED_TO_CART",
        "total_cart_items": total,
        "sku_id": item.sku_id,
        "added_at_timestamp": item.added_at_timestamp_sec
    }

@app.get("/", response_class=HTMLResponse)
def index_view():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Shoppable Video Engine Running</h1>"
