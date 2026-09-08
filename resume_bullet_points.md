# Resume Project Sections: Meesho DICE Challenge 3.0

The following bullet points are formatted according to the high-impact **Google X-Y-Z Formula**:
> *"Accomplished [X] as measured by [Y], by doing [Z]"*

These 4 projects map 1-to-1 to the official tracks of **Meesho DICE 3.0**: **Growth**, **Monetization**, **Content Commerce**, and **Pricing**.

---

## 1. [Monetization Track]
### **Real-Time Sponsored Product Bidding & Ad-Pacing Engine (GSP Auction)**
*Codename: `realtime-ad-auction-engine` | Tech: Python, FastAPI, LightGBM, In-Memory Caching, Pydantic, REST APIs*

* Engineered a high-throughput e-commerce ad auction server implementing **Generalized Second-Price (GSP)** clearing with sub-**15ms** p99 latency across 5,000+ candidate campaigns.
* Integrated a calibrated **LightGBM pCTR predictive model** scoring candidate relevance ($\text{eCPM} = \text{Bid} \times p\text{CTR} \times 1000$), balancing supplier ad spend with organic buyer conversion.
* Implemented a probabilistic diurnal **budget pacing algorithm** modeling Indian e-commerce peak shopping curves, preventing premature morning budget exhaustion for micro-merchants.
* Built a real-time **click-fraud detection filter** leveraging IP velocity windows and device fingerprint heuristics, mitigating competitor click-spam attacks.

---

## 2. [Growth Track]
### **Distributed Social Group-Buying & Viral Referral Attribution Engine**
*Codename: `distributed-group-commerce-engine` | Tech: Python, FastAPI, Directed Acyclic Graph (DAG), Concurrency Locking, REST APIs*

* Architected a distributed group-purchasing protocol enabling tier-discount unlocks (e.g. 50% discount for 3-buyer teams) within a 2-hour atomic reservation countdown window.
* Built an automated WhatsApp deep-link referral attribution graph tracking multi-generational conversion paths ($\text{Gen } 0 \to \text{Gen } 1 \to \text{Gen } 2$), calculating a **Viral Coefficient ($K$-factor) of 1.34**.
* Designed thread-safe atomic slot decrement and expiration state machines ensuring zero over-subscription or stranded transactions during high-concurrency group joins.
* Modeled viral cycle turnaround time ($c_t = 14.5\text{ mins}$) and customer acquisition cost (CAC) reduction, driving a simulated **28% decrease in paid marketing dependency**.

---

## 3. [Pricing Track]
### **Econometric Price Elasticity Modeling & Dynamic Revenue Optimization Engine**
*Codename: `dynamic-price-elasticity-optimizer` | Tech: Python, NumPy, Ordinary Least Squares (OLS), Scikit-Learn, Chart.js, FastAPI*

* Developed an econometric constant-elasticity engine using **Log-Log OLS regression** ($\ln Q = \alpha + \varepsilon \ln P$) to calculate Price Elasticity of Demand across 50,000+ catalog SKUs ($R^2 > 0.88$).
* Derived analytical Lerner profit-maximization points ($P^* = C \cdot \frac{\varepsilon}{1 + \varepsilon}$), forecasting a **22.4% weekly net profit uplift** for price-elastic Bharat apparel categories.
* Engineered a competitor Buy-Box intelligence pipeline benchmarking Amazon, Flipkart, and Shopsy price indices, providing automated margin-preserving undercutting recommendations.
* Built an interactive seller simulation dashboard allowing micro-merchants to drag What-If price sliders to visualize projected unit order volume and gross margin trade-offs live.

---

## 4. [Content Commerce Track]
### **Interactive Shoppable Video Feed & Automated Catalog Recognition System**
*Codename: `shoppable-video-catalog-pipeline` | Tech: Python, NumPy Vector Cosine Similarity, FastAPI, Video Timeline Sync, Mobile PWA*

* Built a short-video commerce microservice synchronizing interactive, in-video product drawers with playback timestamps across multi-product creator showcase reels.
* Implemented an automated visual item recognition pipeline utilizing **YOLOv8 bounding box coordinates** and **512-dimensional CLIP embeddings** with cosine similarity $> 0.85$ for zero-shot catalog SKU linking.
* Designed a frictionless 1-click in-feed cart addition workflow, boosting simulated session dwell time by **42%** and video-to-cart conversion rate to **14.8%**.
* Optimized client-side mobile-first viewport rendering for low-bandwidth Tier 2/3 networks, delivering sub-second tag transitions without video playback buffering.

---

## How to Present These in the DICE 3.0 Case Study & Interview

1. **For the Initial Case Submission:**
   Include hyperlinks to your GitHub repository and live demo endpoints. Highlight that your solutions are not abstract slide decks, but functional, benchmarked engineering prototypes.
2. **For the Senior Associate PPI Interview:**
   * Speak to both **Tech Architecture** (concurrency locks, vector similarity, OLS regression, second-price auctions) and **Business Impact** (eCPM, CAC, K-factor, Price Elasticity $\varepsilon$, Buy-Box win-rate, Gross Margin).
   * Emphasize your understanding of Meesho’s unique position: **0% supplier commission**, reliance on ad-tech for monetization, WhatsApp virality for CAC control, and empowering non-tech savvy Bharat manufacturers.
