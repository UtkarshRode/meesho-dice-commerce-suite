"""
Click Fraud & Anomaly Detection Filter for E-Commerce PPC.
Detects malicious competitor budget-draining clicks, IP bursts, and bot patterns.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple

class ClickFraudDetector:
    def __init__(self, window_seconds: int = 60, max_clicks_per_window: int = 3):
        self.window_seconds = window_seconds
        self.max_clicks_per_window = max_clicks_per_window
        # ip -> list of timestamps
        self.ip_click_history = defaultdict(list)
        # (user_id, campaign_id) -> list of timestamps
        self.user_campaign_clicks = defaultdict(list)

    def is_valid_click(self, ip_address: str, user_id: str, campaign_id: str) -> Tuple[bool, str]:
        now = time.time()

        # Clean old records
        cutoff = now - self.window_seconds
        self.ip_click_history[ip_address] = [t for t in self.ip_click_history[ip_address] if t > cutoff]
        self.user_campaign_clicks[(user_id, campaign_id)] = [
            t for t in self.user_campaign_clicks[(user_id, campaign_id)] if t > cutoff
        ]

        # Check IP burst frequency
        if len(self.ip_click_history[ip_address]) >= self.max_clicks_per_window:
            return False, "FRAUD_IP_BURST_DETECTED"

        # Check repeat click spam on the same campaign
        if len(self.user_campaign_clicks[(user_id, campaign_id)]) >= 2:
            return False, "FRAUD_REPEAT_CAMPAIGN_SPAM"

        # Record valid click timestamp
        self.ip_click_history[ip_address].append(now)
        self.user_campaign_clicks[(user_id, campaign_id)].append(now)
        return True, "CLICK_VERIFIED_VALID"
