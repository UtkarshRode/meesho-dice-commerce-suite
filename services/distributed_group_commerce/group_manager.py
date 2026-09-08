"""
Distributed Group-Buying State & Lock Manager.
Manages atomic reservation slots, countdown timers, and group completion lifecycle.
"""
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Tuple, List
import uuid

try:
    from group_models import GroupOrder, GroupStatus, Participant
except ImportError:
    from .group_models import GroupOrder, GroupStatus, Participant

class GroupOrderManager:
    def __init__(self, default_window_minutes: int = 120):
        self.default_window_minutes = default_window_minutes
        self._lock = threading.Lock()
        self.groups: Dict[str, GroupOrder] = {}

    def create_group(
        self,
        product_id: str,
        product_title: str,
        retail_price: float,
        group_discount_price: float,
        initiator_id: str,
        initiator_name: str,
        required_members: int = 3,
        window_minutes: Optional[int] = None
    ) -> GroupOrder:
        window = window_minutes or self.default_window_minutes
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=window)
        group_id = f"grp_{uuid.uuid4().hex[:8]}"
        ref_code = f"ref_{initiator_id}_{uuid.uuid4().hex[:4]}"

        initiator = Participant(
            user_id=initiator_id,
            user_name=initiator_name,
            phone_masked=f"+91 98*** **{initiator_id[-3:] if len(initiator_id) >= 3 else '123'}",
            joined_at=now,
            is_initiator=True,
            payment_status="CONFIRMED"
        )

        group = GroupOrder(
            group_id=group_id,
            product_id=product_id,
            product_title=product_title,
            retail_price=retail_price,
            group_discount_price=group_discount_price,
            required_members=required_members,
            current_members=1,
            participants=[initiator],
            status=GroupStatus.FORMING,
            created_at=now,
            expires_at=expires_at,
            referral_code=ref_code,
            initiator_user_id=initiator_id
        )

        with self._lock:
            self.groups[group_id] = group

        return group

    def join_group(
        self,
        group_id: str,
        user_id: str,
        user_name: str,
        phone_masked: str
    ) -> Tuple[bool, str, Optional[GroupOrder]]:
        with self._lock:
            group = self.groups.get(group_id)
            if not group:
                return False, "GROUP_NOT_FOUND", None

            now = datetime.now(timezone.utc)

            # Check expiration
            if now > group.expires_at:
                group.status = GroupStatus.EXPIRED
                return False, "GROUP_EXPIRED", group

            if group.status != GroupStatus.FORMING:
                return False, f"GROUP_NOT_OPEN_{group.status.value.upper()}", group

            # Check duplicate user
            if any(p.user_id == user_id for p in group.participants):
                return False, "USER_ALREADY_IN_GROUP", group

            # Atomic slot allocation
            new_participant = Participant(
                user_id=user_id,
                user_name=user_name,
                phone_masked=phone_masked,
                joined_at=now,
                is_initiator=False,
                payment_status="CONFIRMED"
            )
            group.participants.append(new_participant)
            group.current_members = len(group.participants)

            # Check if group threshold met
            if group.current_members >= group.required_members:
                group.status = GroupStatus.COMPLETED

            return True, "SUCCESS_JOINED", group

    def get_group(self, group_id: str) -> Optional[GroupOrder]:
        with self._lock:
            group = self.groups.get(group_id)
            if group and group.status == GroupStatus.FORMING:
                # Lazy expiration check
                if datetime.now(timezone.utc) > group.expires_at:
                    group.status = GroupStatus.EXPIRED
            return group

    def list_groups(self) -> List[GroupOrder]:
        with self._lock:
            now = datetime.now(timezone.utc)
            for g in self.groups.values():
                if g.status == GroupStatus.FORMING and now > g.expires_at:
                    g.status = GroupStatus.EXPIRED
            return list(self.groups.values())
