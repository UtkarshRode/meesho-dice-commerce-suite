"""
Video Feed Service & Interactive Timeline Synchronizer.
Manages video reels and resolves active product tags at current playback timestamp.
"""
from typing import List, Dict, Optional
try:
    from video_models import VideoReel, ProductTag, VideoCartItem, BoundingBox
except ImportError:
    from .video_models import VideoReel, ProductTag, VideoCartItem, BoundingBox
try:
    from vision_tagger import VisionCatalogMatcher
except ImportError:
    from .vision_tagger import VisionCatalogMatcher

class VideoFeedService:
    def __init__(self):
        self.matcher = VisionCatalogMatcher()
        self.reels: Dict[str, VideoReel] = {}
        self.cart_items: List[VideoCartItem] = []
        self._init_demo_reel()

    def _init_demo_reel(self):
        # Auto-match tags using VisionCatalogMatcher
        box_saree = self.matcher.detect_and_match_frame("intro_saree")[0]
        item_saree = self.matcher.catalog_database["sku_saree_bandhani_01"]

        box_jhumka = self.matcher.detect_and_match_frame("close_up_jewellery")[0]
        item_jhumka = self.matcher.catalog_database["sku_jhumka_gold_02"]

        box_jutti = self.matcher.detect_and_match_frame("footwear_pan")[0]
        item_jutti = self.matcher.catalog_database["sku_mojari_jutti_03"]

        reel = VideoReel(
            video_id="reel_festival_ootd_01",
            creator_name="Komal Pandey (Creator Partner)",
            creator_handle="@komal_ethnic_meesho",
            title="✨ Complete Festive Saree Look Under ₹800! Affordable Bharat Chic",
            video_url="https://assets.mixkit.co/videos/preview/mixkit-woman-wearing-an-indian-sari-42566-large.mp4",
            duration_sec=16.0,
            views_count=48200,
            likes_count=6950,
            tags=[
                ProductTag(
                    tag_id="tag_01",
                    sku_id="sku_saree_bandhani_01",
                    title=item_saree["title"],
                    price=item_saree["price"],
                    discount_pct=item_saree["discount_pct"],
                    image_url=item_saree["image_url"],
                    start_time_sec=0.0,
                    end_time_sec=6.0,
                    bounding_box=box_saree
                ),
                ProductTag(
                    tag_id="tag_02",
                    sku_id="sku_jhumka_gold_02",
                    title=item_jhumka["title"],
                    price=item_jhumka["price"],
                    discount_pct=item_jhumka["discount_pct"],
                    image_url=item_jhumka["image_url"],
                    start_time_sec=6.0,
                    end_time_sec=11.0,
                    bounding_box=box_jhumka
                ),
                ProductTag(
                    tag_id="tag_03",
                    sku_id="sku_mojari_jutti_03",
                    title=item_jutti["title"],
                    price=item_jutti["price"],
                    discount_pct=item_jutti["discount_pct"],
                    image_url=item_jutti["image_url"],
                    start_time_sec=11.0,
                    end_time_sec=16.0,
                    bounding_box=box_jutti
                )
            ]
        )
        self.reels[reel.video_id] = reel

    def get_active_tag(self, video_id: str, timestamp_sec: float) -> Optional[ProductTag]:
        reel = self.reels.get(video_id)
        if not reel:
            return None
        for tag in reel.tags:
            if tag.start_time_sec <= timestamp_sec < tag.end_time_sec:
                return tag
        # Fallback to last tag if reached duration
        return reel.tags[-1] if reel.tags else None

    def add_to_cart(self, item: VideoCartItem) -> int:
        self.cart_items.append(item)
        return len(self.cart_items)
