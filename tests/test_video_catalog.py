"""
Automated unit tests for Shoppable Video Feed & Catalog Pipeline.
Tests timeline active tag resolution and visual embedding vector similarity.
"""
import pytest
import sys
import os

# Add service directory to sys.path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "shoppable_video_catalog"))
sys.path.insert(0, service_dir)

from vision_tagger import VisionCatalogMatcher
from feed_service import VideoFeedService
from video_models import VideoCartItem

def test_vision_matcher_similarity():
    matcher = VisionCatalogMatcher()
    boxes = matcher.detect_and_match_frame("intro_saree")
    assert len(boxes) == 1
    assert boxes[0].label == "saree"
    assert boxes[0].matched_sku_id == "sku_saree_bandhani_01"
    assert boxes[0].similarity_score > 0.85

def test_timeline_active_tag_sync():
    feed = VideoFeedService()
    reel_id = "reel_festival_ootd_01"

    # At t=2s -> Saree
    tag_saree = feed.get_active_tag(reel_id, timestamp_sec=2.0)
    assert tag_saree is not None
    assert tag_saree.sku_id == "sku_saree_bandhani_01"

    # At t=8s -> Jewellery
    tag_jewel = feed.get_active_tag(reel_id, timestamp_sec=8.0)
    assert tag_jewel is not None
    assert tag_jewel.sku_id == "sku_jhumka_gold_02"

    # At t=14s -> Footwear
    tag_foot = feed.get_active_tag(reel_id, timestamp_sec=14.0)
    assert tag_foot is not None
    assert tag_foot.sku_id == "sku_mojari_jutti_03"

def test_video_cart_conversion():
    feed = VideoFeedService()
    cart_item = VideoCartItem(
        video_id="reel_festival_ootd_01",
        sku_id="sku_saree_bandhani_01",
        title="Jaipuri Bandhani Silk Saree",
        price=349.0,
        user_id="usr_test_99",
        added_at_timestamp_sec=3.5
    )
    total = feed.add_to_cart(cart_item)
    assert total >= 1
