"""
Automated Deployment Verification (Smoke Test) Script.
Tests all 4 project endpoints and web interfaces against any target URL (Localhost or Cloud).

Usage:
    python verify_deployment.py                                      # Default: http://localhost:8000
    python verify_deployment.py --url https://<your-app>.onrender.com  # Against live cloud deployment
"""
import sys
import argparse
import time
import urllib.request
import json
import urllib.error

def check_endpoint(name, url, method="GET", data=None):
    print(f"\n[Testing {name}]")
    print(f"  --> {method} {url}")
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header("Content-Type", "application/json")
            json_bytes = json.dumps(data).encode("utf-8")
        else:
            json_bytes = None

        with urllib.request.urlopen(req, data=json_bytes, timeout=15) as resp:
            elapsed = (time.perf_counter() - start) * 1000.0
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            body = resp.read().decode("utf-8")

            if "application/json" in content_type:
                payload = json.loads(body)
                print(f"  [PASS] Status: {status} OK | Latency: {elapsed:.2f}ms")
                return True, payload
            else:
                print(f"  [PASS] HTML Web UI Delivered | Status: {status} OK | Size: {len(body)} bytes")
                return True, body
    except urllib.error.HTTPError as e:
        print(f"  [FAIL] HTTP Error: {e.code} - {e.reason}")
        return False, None
    except Exception as e:
        print(f"  [FAIL] Connection Failed: {str(e)}")
        return False, None

def main():
    parser = argparse.ArgumentParser(description="Meesho DICE 3.0 Smoke Test")
    parser.add_argument("--url", default="http://localhost:8000", help="Base deployment URL")
    args = parser.parse_args()

    base = args.url.rstrip("/")
    print("="*65)
    print("  MEESHO DICE 3.0: PRACTICAL DEPLOYMENT VERIFICATION  ")
    print(f"  Target Deployment: {base}")
    print("="*65)

    success_count = 0
    total_tests = 9

    # 1. Master Health Check
    ok, res = check_endpoint("Master Gateway Health", f"{base}/health")
    if ok and res.get("status") == "HEALTHY":
        success_count += 1

    # 2. Master Portal UI
    ok, _ = check_endpoint("Master Landing Portal HTML", f"{base}/")
    if ok:
        success_count += 1

    # 3. Project 1 (Monetization) - Web UI
    ok, _ = check_endpoint("Project 1 [Monetization] Web UI", f"{base}/monetization/")
    if ok:
        success_count += 1

    # 4. Project 1 (Monetization) - Live GSP Auction API
    auction_payload = {
        "request_id": "verify_req_01",
        "query": "yellow saree",
        "placement": "search_top",
        "user_id": "usr_verify",
        "slot_count": 1
    }
    ok, res = check_endpoint("Project 1 [Monetization] GSP Auction API", f"{base}/monetization/api/auction/run", method="POST", data=auction_payload)
    if ok and len(res.get("winning_ads", [])) > 0:
        winner = res["winning_ads"][0]
        print(f"       Winner: {winner['product_title'][:30]}... | Charged CPC: Rs.{winner['charged_cpc']}")
        success_count += 1

    # 5. Project 2 (Growth) - Web UI
    ok, _ = check_endpoint("Project 2 [Growth] Web UI", f"{base}/growth/")
    if ok:
        success_count += 1

    # 6. Project 2 (Growth) - Virality Metrics API
    ok, res = check_endpoint("Project 2 [Growth] Virality K-Factor API", f"{base}/growth/api/virality/metrics")
    if ok and "viral_coefficient_k" in res:
        print(f"       Viral Coefficient K-factor: {res['viral_coefficient_k']} | Total Joins: {res['total_converted_joins']}")
        success_count += 1

    # 7. Project 3 (Pricing) - Web UI
    ok, _ = check_endpoint("Project 3 [Pricing] Web UI", f"{base}/pricing-engine/")
    if ok:
        success_count += 1

    # 8. Project 3 (Pricing) - Elasticity Regression API
    ok, res = check_endpoint("Project 3 [Pricing] Econometric Elasticity API", f"{base}/pricing-engine/api/products/prod_bandhani_saree_01/elasticity")
    if ok and "elasticity_coefficient" in res:
        print(f"       Elasticity (epsilon): {res['elasticity_coefficient']} | Optimal P*: Rs.{res['optimal_profit_price']}")
        success_count += 1

    # 9. Project 4 (Content Commerce) - Shoppable Video Feed API
    ok, res = check_endpoint("Project 4 [Content Commerce] Video Tag Sync API", f"{base}/content-commerce/api/videos/reel_festival_ootd_01/active-tag?time=2.0")
    if ok and "sku_id" in res:
        print(f"       Active Video Tag: {res['title']} (Rs.{res['price']})")
        success_count += 1

    print("\n" + "="*65)
    print(f"  VERIFICATION RESULTS: {success_count}/{total_tests} CHECKS PASSED")
    if success_count == total_tests:
        print("  >>> SUCCESS: ALL 4 PROJECTS ARE HEALTHY AND FULLY OPERATIONAL! <<<")
    else:
        print("  >>> WARNING: Some checks failed. Check deployment logs. <<<")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
