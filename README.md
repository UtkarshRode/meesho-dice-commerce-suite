# Meesho DICE 3.0: Commerce Engineering Suite

Production-grade engineering and economic modeling suite designed specifically for the **Meesho DICE (Democratising Internet Commerce Ecosystem) Challenge 3.0**, directly addressing its four core pillars: **Growth**, **Monetization**, **Content Commerce**, and **Pricing**.

```
                           ┌──────────────────────────────────────────────┐
                           │         Meesho DICE 3.0 Engineering          │
                           └──────────────────────┬───────────────────────┘
                                                  │
         ┌────────────────────────┬───────────────┴────────────────┬────────────────────────┐
         │                        │                                │                        │
         ▼                        ▼                                ▼                        ▼
┌──────────────────┐    ┌──────────────────┐             ┌──────────────────┐     ┌──────────────────┐
│   MONETIZATION   │    │      GROWTH      │             │     PRICING      │     │ CONTENT COMMERCE │
│  Ad-Auction RTB  │    │  Group-Commerce  │             │ Price Elasticity │     │  Shoppable Video │
│   (GSP Engine)   │    │  (Viral Loops)   │             │   (Optimizer)    │     │ (Catalog Pipeline│
└──────────────────┘    └──────────────────┘             └──────────────────┘     └──────────────────┘
```

---

## 1. Projects Overview & Formal Titles

| DICE 3.0 Pillar | Formal System Title | Codename | Core Math / Algorithms | Port |
| :--- | :--- | :--- | :--- | :--- |
| **Monetization** | **Real-Time Sponsored Product Bidding & Ad-Pacing Engine** | `realtime-ad-auction-engine` | Generalized Second-Price (GSP), LightGBM $p\text{CTR}$, Diurnal Budget Pacing ($\rho$) | `8001` |
| **Growth** | **Distributed Social Group-Buying & Viral Referral Attribution Engine** | `distributed-group-commerce-engine` | Atomic reservation locking, Referral DAG traversal, Viral Coefficient ($K = i \times c$) | `8002` |
| **Pricing** | **Econometric Price Elasticity Modeling & Dynamic Revenue Optimizer** | `dynamic-price-elasticity-optimizer` | Log-Log OLS Demand Curve ($\ln Q = \alpha + \varepsilon \ln P$), Lerner Index markup ($P^*$), Buy-Box index | `8003` |
| **Content Commerce** | **Interactive Shoppable Video Feed & Catalog Recognition System** | `shoppable-video-catalog-pipeline` | YOLOv8 Bounding Box detection, 512-dim CLIP Cosine Similarity, Timeline sync | `8004` |

---

## 2. Architecture & Key Features

### Module 1: Real-Time Ad-Auction Engine (`services/realtime_ad_auction/`)
* **Generalized Second-Price (GSP):** Ranks candidate seller bids by $\text{eCPM} = \text{Bid}_{\text{CPC}} \times p\text{CTR} \times 1000$. The winning advertiser is charged the minimum bid required to maintain rank over the runner-up + ₹0.01.
* **Probabilistic Diurnal Budget Pacing:** Prevents seller budgets (e.g. ₹500/day) from exhausting during early morning off-peak hours by throttling participation probability ($\rho$) to track Indian diurnal shopping curves.
* **Click-Fraud Protection:** Dual-window velocity checks on IP bursts and user-campaign repetition to protect sellers from malicious competitor budget draining.

### Module 2: Distributed Group-Commerce Engine (`services/distributed_group_commerce/`)
* **Atomic Group Lifecycle:** Manages 2-hour deal countdown windows where users unlock steep 50% discounts upon forming 3-buyer teams.
* **Viral Referral Attribution Graph:** Tracks multi-generational referral paths ($\text{Gen } 0 \to \text{Gen } 1 \to \text{Gen } 2$), calculating:
  $$K = \text{Invites per Initiator } (i) \times \text{Conversion Rate } (c)$$
  Guarantees super-critical self-sustaining organic acquisition when $K > 1.0$.

### Module 3: Dynamic Price Elasticity Optimizer (`services/dynamic_price_elasticity/`)
* **Econometric Log-Log OLS Regression:** Estimates price elasticity ($\varepsilon$) across historical sales data:
  $$\ln(Q) = \alpha + \varepsilon \cdot \ln(P)$$
* **Lerner Analytical Optimal Pricing:** Computes $P^* = \text{Cost} \cdot \frac{\varepsilon}{1 + \varepsilon}$ to identify maximum profit margin sweet spots.
* **Competitor Benchmarking:** Real-time Buy-Box price index against Flipkart, Amazon, and Shopsy to provide actionable margin-preserving undercutting nudges.

### Module 4: Shoppable Video & Catalog Pipeline (`services/shoppable_video_catalog/`)
* **Timeline-Synchronized Overlays:** Auto-transitions bottom purchase drawers as the creator switches products across a 16-second reel (Saree $\to$ Jhumka $\to$ Jutti).
* **Automated Visual Matching:** Extracts simulated YOLOv8 apparel bounding boxes and matches 512-dim CLIP vector embeddings against catalog SKUs with cosine similarity $> 0.85$.

---

## 3. Quickstart & How to Run

### Requirements
- Python 3.10+
- Dependencies: `fastapi`, `uvicorn`, `pydantic`, `numpy`, `pytest`

### Launching Services
You can run any individual service or use the interactive master runner:

```bash
# Launch master interactive menu:
python run_suite.py

# Or launch specific services directly:
python run_suite.py --service ad_auction       # http://localhost:8001
python run_suite.py --service group_commerce   # http://localhost:8002
python run_suite.py --service pricing          # http://localhost:8003
python run_suite.py --service video            # http://localhost:8004
```

### Running Automated Test Suite
To verify all algorithmic math, concurrency state transitions, and models:
```bash
python run_suite.py --test
# Or
python -m pytest tests/
```
All 11 unit tests across the 4 services execute in $<0.5\text{s}$.

---

## 4. Competitive Advantage for Meesho DICE 3.0

1. **Strategic Relevance:** Evaluators reviewing resumes and case submissions will see direct alignment with Meesho’s unique business model (0% commission marketplace, WhatsApp social virality, Bharat consumer preferences, supplier price enablement).
2. **Senior Associate / PPI Role Alignment:** Demonstrates end-to-end thinking: connecting complex algorithmic code (GSP auction math, OLS econometrics, DAG trees) directly to top-line commercial metrics (GMV, CAC, eCPM, take rate).
3. **Execution Ready:** Complete with runnable web visualizers and automated unit tests.
