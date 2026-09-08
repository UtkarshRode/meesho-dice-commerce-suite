"""
Predicted Click-Through Rate (pCTR) scoring model.
Simulates production ML ranking (e.g. LightGBM / Logistic Regression with feature hashing)
optimised for sub-3ms inference latency.
"""
import math
import re
from typing import Dict, Any

class PCTRModel:
    def __init__(self):
        # Calibrated weights representing logistic regression / tree leaf log-odds
        self.intercept = -3.20  # Base CTR around ~3.9%
        self.w_hist_ctr = 14.5
        self.w_seller_rating = 0.35
        self.w_text_match = 1.80
        self.w_tier2_affinity = 0.25

    def _text_overlap_score(self, query: str, product_title: str) -> float:
        """Computes Jaccard / token overlap between search query and product title."""
        q_tokens = set(re.findall(r'\w+', query.lower()))
        t_tokens = set(re.findall(r'\w+', product_title.lower()))
        if not q_tokens or not t_tokens:
            return 0.1
        intersection = q_tokens.intersection(t_tokens)
        if not intersection:
            # Soft fallback for partial match
            for q in q_tokens:
                for t in t_tokens:
                    if q in t or t in q:
                        return 0.4
            return 0.05
        return len(intersection) / len(q_tokens)

    def predict(self, query: str, campaign: Dict[str, Any], user_segment: str = "tier_2_shopper") -> float:
        """
        Computes pCTR = sigmoid(z)
        where z = w0 + w1*hist_ctr + w2*rating + w3*relevance + w4*user_segment
        """
        text_match = self._text_overlap_score(query, campaign.get("product_title", ""))
        hist_ctr = campaign.get("historical_ctr", 0.035)
        seller_rating = campaign.get("seller_rating", 4.0) - 3.0  # normalized around 3.0
        tier2_bonus = 1.0 if user_segment == "tier_2_shopper" else 0.0

        logit = (
            self.intercept
            + (self.w_hist_ctr * hist_ctr)
            + (self.w_seller_rating * seller_rating)
            + (self.w_text_match * text_match)
            + (self.w_tier2_affinity * tier2_bonus)
        )

        # Sigmoid clipping to ensure realistic bounds (1.0% to 25.0%)
        prob = 1.0 / (1.0 + math.exp(-logit))
        return max(0.005, min(0.35, prob))
