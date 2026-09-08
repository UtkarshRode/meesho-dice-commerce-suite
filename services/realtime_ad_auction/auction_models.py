"""
Data models for the Real-Time Sponsored Product Bidding & Ad-Pacing Engine.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
from enum import Enum

class AdPlacement(str, Enum):
    SEARCH_TOP = "search_top"
    FEED_RECOMMENDATION = "feed_recommendation"
    PRODUCT_DETAIL_CAROUSEL = "product_detail_carousel"

class SellerCampaign(BaseModel):
    campaign_id: str
    seller_id: str
    product_id: str
    product_title: str
    category: str
    max_cpc_bid: float = Field(..., description="Maximum Cost Per Click in INR (e.g. ₹5.00)")
    daily_budget: float = Field(..., description="Daily budget in INR (e.g. ₹500.00)")
    spent_today: float = 0.0
    seller_rating: float = Field(default=4.2, ge=1.0, le=5.0)
    historical_ctr: float = Field(default=0.035, ge=0.001, le=0.5)
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AuctionRequest(BaseModel):
    request_id: str
    query: str
    category: Optional[str] = None
    placement: AdPlacement = AdPlacement.SEARCH_TOP
    user_id: str
    user_segment: str = "tier_2_shopper"
    slot_count: int = 1

class ScoredBid(BaseModel):
    campaign_id: str
    seller_id: str
    product_id: str
    product_title: str
    raw_bid_cpc: float
    predicted_ctr: float
    ecpm: float
    pacing_prob: float
    participated: bool
    rejection_reason: Optional[str] = None

class WinningAd(BaseModel):
    rank: int
    campaign_id: str
    seller_id: str
    product_id: str
    product_title: str
    charged_cpc: float
    raw_bid_cpc: float
    predicted_ctr: float
    ecpm: float
    pricing_rule: str = "Generalized Second-Price (GSP)"

class AuctionResponse(BaseModel):
    request_id: str
    query: str
    placement: AdPlacement
    total_eligible_bids: int
    winning_ads: List[WinningAd]
    all_scored_bids: List[ScoredBid]
    latency_ms: float

class ClickEvent(BaseModel):
    campaign_id: str
    product_id: str
    user_id: str
    charged_cpc: float
    ip_address: str
    user_agent: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
