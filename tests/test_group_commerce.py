"""
Automated unit tests for Distributed Group-Buying & Viral Referral Engine.
Tests atomic slot allocation, group completion transition, and K-factor virality calculation.
"""
import pytest
import sys
import os
from datetime import datetime, timezone, timedelta

# Add service directory to sys.path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "distributed_group_commerce"))
sys.path.insert(0, service_dir)

from group_manager import GroupOrderManager
from referral_graph import ReferralGraph
from group_models import GroupStatus

def test_group_order_lifecycle():
    mgr = GroupOrderManager(default_window_minutes=60)
    grp = mgr.create_group(
        product_id="prod_saree",
        product_title="Silk Saree",
        retail_price=500.0,
        group_discount_price=250.0,
        initiator_id="usr_init",
        initiator_name="Initiator",
        required_members=3
    )

    assert grp.status == GroupStatus.FORMING
    assert grp.current_members == 1

    # Join 2nd participant
    success, msg, grp_updated = mgr.join_group(grp.group_id, "usr_friend_1", "Friend 1", "+91 99999 11111")
    assert success is True
    assert grp_updated.current_members == 2
    assert grp_updated.status == GroupStatus.FORMING

    # Join 3rd participant -> Should complete group!
    success, msg, grp_updated = mgr.join_group(grp.group_id, "usr_friend_2", "Friend 2", "+91 99999 22222")
    assert success is True
    assert grp_updated.current_members == 3
    assert grp_updated.status == GroupStatus.COMPLETED

    # Try to join full group -> Should reject
    success, msg, _ = mgr.join_group(grp.group_id, "usr_friend_3", "Friend 3", "+91 99999 33333")
    assert success is False
    assert "GROUP_NOT_OPEN" in msg

def test_k_factor_calculation():
    graph = ReferralGraph()
    # 2 seed initiators
    graph.register_user("usr_seed_1", "Seed 1")
    graph.register_user("usr_seed_2", "Seed 2")

    # Seed 1 sends 4 invites, Seed 2 sends 6 invites -> total 10 invites
    graph.record_invites_sent("usr_seed_1", count=4)
    graph.record_invites_sent("usr_seed_2", count=6)

    # 3 friends convert from Seed 1, 2 friends convert from Seed 2 -> total 5 conversions
    graph.register_user("usr_c1", "C 1", parent_id="usr_seed_1")
    graph.register_user("usr_c2", "C 2", parent_id="usr_seed_1")
    graph.register_user("usr_c3", "C 3", parent_id="usr_seed_1")
    graph.register_user("usr_c4", "C 4", parent_id="usr_seed_2")
    graph.register_user("usr_c5", "C 5", parent_id="usr_seed_2")

    metrics = graph.get_metrics()
    # Initiators = 2
    # Invites = 10 -> invites_per_initiator = 5.0
    # Conversions = 5 -> conversion_rate = 5/10 = 0.5
    # K = 5.0 * 0.5 = 2.5
    assert metrics.total_initiators == 2
    assert metrics.total_invites_sent == 10
    assert metrics.total_converted_joins == 5
    assert metrics.viral_coefficient_k == 2.5
    assert metrics.is_viral_loop_sustainable is True
