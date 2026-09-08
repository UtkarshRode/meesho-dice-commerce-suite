"""
Generalized Second-Price (GSP) Auction Server for Sponsored Products.
Executes real-time ranking using eCPM = Bid * pCTR * 1000,
budget pacing throttling, and second-price clearing.
"""
import time
from typing import List, Dict, Any, Optional
try:
    from auction_models import (
        SellerCampaign, AuctionRequest, AuctionResponse,
        WinningAd, ScoredBid, AdPlacement
    )
    from pctr_model import PCTRModel
    from budget_pacer import BudgetPacer
except ImportError:
    from .auction_models import (
        SellerCampaign, AuctionRequest, AuctionResponse,
        WinningAd, ScoredBid, AdPlacement
    )
    from .pctr_model import PCTRModel
    from .budget_pacer import BudgetPacer

class GSPAuctionServer:
    RESERVE_PRICE_CPC = 0.50  # Minimum floor price in INR

    def __init__(self):
        self.pctr_model = PCTRModel()
        self.budget_pacer = BudgetPacer()
        self.campaigns: Dict[str, SellerCampaign] = {}

    def register_campaign(self, campaign: SellerCampaign):
        self.campaigns[campaign.campaign_id] = campaign

    def run_auction(self, request: AuctionRequest, current_hour: Optional[int] = None) -> AuctionResponse:
        start_time = time.perf_counter()

        scored_bids: List[ScoredBid] = []
        eligible_candidates = []

        # 1. Candidate Retrieval & Filtering
        for camp in self.campaigns.values():
            if not camp.active:
                continue

            # Category filter if specified
            if request.category and camp.category.lower() != request.category.lower():
                continue

            # Check budget pacing
            participate, rho, status = self.budget_pacer.get_pacing_decision(
                camp.daily_budget, camp.spent_today, current_hour=current_hour
            )

            # Predict pCTR
            camp_data = camp.model_dump() if hasattr(camp, "model_dump") else camp.dict()
            pctr = self.pctr_model.predict(
                request.query, camp_data, user_segment=request.user_segment
            )
            raw_cpc = camp.max_cpc_bid
            ecpm = raw_cpc * pctr * 1000.0

            scored = ScoredBid(
                campaign_id=camp.campaign_id,
                seller_id=camp.seller_id,
                product_id=camp.product_id,
                product_title=camp.product_title,
                raw_bid_cpc=round(raw_cpc, 2),
                predicted_ctr=round(pctr, 4),
                ecpm=round(ecpm, 2),
                pacing_prob=rho,
                participated=participate,
                rejection_reason=None if participate else f"THROTTLED_{status}"
            )
            scored_bids.append(scored)

            if participate and raw_cpc >= self.RESERVE_PRICE_CPC:
                eligible_candidates.append(scored)

        # 2. Sort candidates by eCPM descending (GSP Ranking)
        eligible_candidates.sort(key=lambda x: x.ecpm, reverse=True)

        # 3. Determine Winners & GSP Clearing Price
        winning_ads: List[WinningAd] = []
        slots_to_fill = min(request.slot_count, len(eligible_candidates))

        for rank in range(slots_to_fill):
            winner = eligible_candidates[rank]
            # Next runner-up defines second price
            if rank + 1 < len(eligible_candidates):
                runner_up = eligible_candidates[rank + 1]
                runner_up_ecpm = runner_up.ecpm
                # GSP Formula: minimum CPC winner needed to maintain higher eCPM than runner-up
                charged_cpc = (runner_up_ecpm / (winner.predicted_ctr * 1000.0)) + 0.01
            else:
                charged_cpc = self.RESERVE_PRICE_CPC

            # Guarantee charged CPC never exceeds the bidder's declared maximum bid
            charged_cpc = min(winner.raw_bid_cpc, max(self.RESERVE_PRICE_CPC, charged_cpc))

            winning_ads.append(WinningAd(
                rank=rank + 1,
                campaign_id=winner.campaign_id,
                seller_id=winner.seller_id,
                product_id=winner.product_id,
                product_title=winner.product_title,
                charged_cpc=round(charged_cpc, 2),
                raw_bid_cpc=winner.raw_bid_cpc,
                predicted_ctr=winner.predicted_ctr,
                ecpm=winner.ecpm,
                pricing_rule="Generalized Second-Price (GSP)"
            ))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return AuctionResponse(
            request_id=request.request_id,
            query=request.query,
            placement=request.placement,
            total_eligible_bids=len(eligible_candidates),
            winning_ads=winning_ads,
            all_scored_bids=scored_bids,
            latency_ms=round(elapsed_ms, 3)
        )
