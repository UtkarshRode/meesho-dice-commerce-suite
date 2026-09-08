"""
FastAPI Microservice for Distributed Social Group-Buying Engine.
Handles group deals, atomic countdown slots, WhatsApp referral deep-links,
and real-time Viral K-factor graph attribution.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os

try:
    from group_models import GroupOrder, JoinGroupRequest, ViralMetrics
except ImportError:
    from .group_models import GroupOrder, JoinGroupRequest, ViralMetrics
try:
    from group_manager import GroupOrderManager
    from referral_graph import ReferralGraph
except ImportError:
    from .group_manager import GroupOrderManager
    from .referral_graph import ReferralGraph

app = FastAPI(
    title="Meesho DICE 3.0: Distributed Group-Buying Engine",
    description="High-Concurrency Social Group-Commerce Protocol with Viral Graph Attribution and K-Factor Analytics",
    version="1.0.0"
)

manager = GroupOrderManager(default_window_minutes=120)
graph = ReferralGraph()

# Seed initial seed community initiators and a demo group deal
seed_initiator = graph.register_user("usr_anita_sharma", "Anita Sharma (Jaipur Reseller)")
graph.record_invites_sent("usr_anita_sharma", count=4)

# Seed 2 friends who joined
friend_1 = graph.register_user("usr_sunita_verma", "Sunita Verma", parent_id="usr_anita_sharma")
friend_2 = graph.register_user("usr_pooja_singh", "Pooja Singh", parent_id="usr_anita_sharma")
graph.record_invites_sent("usr_sunita_verma", count=3)
friend_3 = graph.register_user("usr_rekha_patel", "Rekha Patel", parent_id="usr_sunita_verma")

# Seed initial open group deal
demo_group = manager.create_group(
    product_id="prod_saree_bandhani_01",
    product_title="Jaipuri Silk Bandhani Saree with Zari Border",
    retail_price=599.0,
    group_discount_price=299.0,
    initiator_id="usr_anita_sharma",
    initiator_name="Anita Sharma",
    required_members=3,
    window_minutes=120
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

class CreateGroupPayload(BaseModel):
    product_id: str
    product_title: str
    retail_price: float
    group_discount_price: float
    initiator_id: str
    initiator_name: str
    required_members: int = 3
    window_minutes: int = 120

class InvitePayload(BaseModel):
    sender_id: str
    count: int = 1

@app.post("/api/groups/create", response_model=GroupOrder)
def create_group(payload: CreateGroupPayload):
    graph.register_user(payload.initiator_id, payload.initiator_name)
    grp = manager.create_group(
        product_id=payload.product_id,
        product_title=payload.product_title,
        retail_price=payload.retail_price,
        group_discount_price=payload.group_discount_price,
        initiator_id=payload.initiator_id,
        initiator_name=payload.initiator_name,
        required_members=payload.required_members,
        window_minutes=payload.window_minutes
    )
    return grp

@app.post("/api/groups/{group_id}/join")
def join_group(group_id: str, payload: JoinGroupRequest, referrer_id: Optional[str] = None):
    success, reason, group = manager.join_group(
        group_id=group_id,
        user_id=payload.user_id,
        user_name=payload.user_name,
        phone_masked=payload.phone_masked
    )
    if not success:
        raise HTTPException(status_code=400, detail=reason)

    # Register in viral graph with parent attribution
    parent = referrer_id or group.initiator_user_id
    graph.register_user(payload.user_id, payload.user_name, parent_id=parent)

    return {"status": "SUCCESS", "message": "Joined group successfully", "group": group}

@app.get("/api/groups/{group_id}", response_model=GroupOrder)
def get_group_details(group_id: str):
    grp = manager.get_group(group_id)
    if not grp:
        raise HTTPException(status_code=404, detail="Group not found")
    return grp

@app.get("/api/groups", response_model=List[GroupOrder])
def list_groups():
    return manager.list_groups()

@app.post("/api/referrals/invite")
def record_invite(payload: InvitePayload):
    graph.record_invites_sent(payload.sender_id, count=payload.count)
    return {"status": "RECORDED", "total_invites": graph.total_invites}

@app.get("/api/virality/metrics", response_model=ViralMetrics)
def get_virality_metrics():
    return graph.get_metrics()

@app.get("/api/virality/graph")
def get_graph():
    return graph.export_graph_data()

@app.get("/", response_class=HTMLResponse)
def index_view():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Group-Commerce Engine Running</h1>"
