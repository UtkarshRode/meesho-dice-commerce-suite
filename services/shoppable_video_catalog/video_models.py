"""
Data models for Interactive Shoppable Video Feed & Catalog Recognition System.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone

class BoundingBox(BaseModel):
    label: str
    confidence: float
    ymin: float
    xmin: float
    ymax: float
    xmax: float
    matched_sku_id: str
    similarity_score: float

class ProductTag(BaseModel):
    tag_id: str
    sku_id: str
    title: str
    price: float
    discount_pct: int
    image_url: str
    start_time_sec: float
    end_time_sec: float
    bounding_box: Optional[BoundingBox] = None

class VideoReel(BaseModel):
    video_id: str
    creator_name: str
    creator_handle: str
    title: str
    video_url: str
    duration_sec: float
    views_count: int = 14200
    likes_count: int = 2480
    tags: List[ProductTag] = []

class VideoCartItem(BaseModel):
    video_id: str
    sku_id: str
    title: str
    price: float
    user_id: str
    added_at_timestamp_sec: float
