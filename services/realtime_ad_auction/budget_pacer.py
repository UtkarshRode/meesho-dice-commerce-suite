"""
Probabilistic Diurnal Budget Pacing Engine.
Prevents seller budget exhaustion during morning off-peak hours
by regulating auction participation probability based on the Indian e-commerce traffic curve.
"""
import random
from datetime import datetime
from typing import Dict, Tuple

class BudgetPacer:
    # Typical Indian e-commerce diurnal traffic distribution (hourly weights, 0 to 23)
    # Peak hours: 12 PM - 3 PM and 7 PM - 10 PM
    HOURLY_TRAFFIC_WEIGHTS = [
        0.015, 0.008, 0.005, 0.004, 0.005, 0.010, # 00:00 - 05:00 (Night)
        0.020, 0.035, 0.050, 0.060, 0.065, 0.070, # 06:00 - 11:00 (Morning)
        0.075, 0.070, 0.060, 0.055, 0.050, 0.055, # 12:00 - 17:00 (Afternoon)
        0.070, 0.085, 0.095, 0.080, 0.055, 0.032  # 18:00 - 23:00 (Evening Peak)
    ]

    def __init__(self):
        # Normalize weights so sum is 1.0
        total = sum(self.HOURLY_TRAFFIC_WEIGHTS)
        self.hourly_weights = [w / total for w in self.HOURLY_TRAFFIC_WEIGHTS]
        # Cumulative Distribution Function (CDF) of traffic
        self.traffic_cdf = []
        cum = 0.0
        for w in self.hourly_weights:
            cum += w
            self.traffic_cdf.append(cum)

    def get_pacing_decision(self, daily_budget: float, spent_today: float, current_hour: int = None) -> Tuple[bool, float, str]:
        """
        Calculates participation probability rho based on budget consumption vs expected traffic CDF.
        Returns: (participate: bool, rho: float, status_message: str)
        """
        if current_hour is None:
            current_hour = datetime.utcnow().hour

        if spent_today >= daily_budget:
            return False, 0.0, "DAILY_BUDGET_EXHAUSTED"

        expected_fraction = self.traffic_cdf[current_hour]
        actual_fraction = spent_today / daily_budget if daily_budget > 0 else 1.0

        # Burn ratio: > 1 means burning too fast; < 1 means burning slowly
        if expected_fraction <= 0.01:
            burn_ratio = actual_fraction / 0.01
        else:
            burn_ratio = actual_fraction / expected_fraction

        if burn_ratio <= 1.0:
            # Under budget, participate 100%
            rho = 1.0
            status = "OPTIMAL_PACING"
        elif burn_ratio > 1.8:
            # Burning critically fast, throttle severely
            rho = max(0.10, 1.0 / (burn_ratio ** 2))
            status = "SEVERE_THROTTLE"
        else:
            # Moderate throttle
            rho = max(0.25, 1.0 / burn_ratio)
            status = "MODERATE_THROTTLE"

        # Probabilistic coin flip
        participate = (random.random() < rho)
        return participate, round(rho, 4), status
