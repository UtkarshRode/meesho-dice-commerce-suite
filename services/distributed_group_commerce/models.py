"""
Data models for the Distributed Social Group-Buying & Viral Referral Attribution Engine.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
from enum import Enum

class GroupStatus(str, Enum):
    FORMING = "forming"         # Waiting for participants
    COMPLETED = "completed"     # All required slots filled within time window
    EXPIRED = "expired"         # Timer expired before threshold met

class Participant(BaseModel):
    user_id: str
    user_name: str
    phone_masked: str
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_initiator: bool = False
    payment_status: str = "CONFIRMED"

class GroupOrder(BaseModel):
    group_id: str
    product_id: str
    product_title: str
    retail_price: float
    group_discount_price: float
    required_members: int = 3
    current_members: int = 1
    participants: List[Participant] = []
    status: GroupStatus = GroupStatus.FORMING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    referral_code: str
    initiator_user_id: str

class JoinGroupRequest(BaseModel):
    user_id: str
    user_name: str
    phone_masked: str

class ViralMetrics(BaseModel):
    total_initiators: int
    total_invites_sent: int
    total_converted_joins: int
    invites_per_initiator: float
    conversion_rate: float
    viral_coefficient_k: float
    is_viral_loop_sustainable: bool
    avg_cycle_time_minutes: float
