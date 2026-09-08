"""
Master CLI Launcher for Meesho DICE 3.0 Engineering Suite.
Usage:
    python run_suite.py --service ad_auction       (Port 8001)
    python run_suite.py --service group_commerce   (Port 8002)
    python run_suite.py --service pricing          (Port 8003)
    python run_suite.py --service video            (Port 8004)
    python run_suite.py --test                     (Runs all pytest suites)
"""
import sys
import os
import argparse
import subprocess
import uvicorn

SERVICE_CONFIGS = {
    "ad_auction": {
        "name": "Monetization: Real-Time Ad-Auction Engine (GSP)",
        "app_module": "services.realtime_ad_auction.app:app",
        "default_port": 8001,
        "path": "services/realtime_ad_auction"
    },
    "group_commerce": {
        "name": "Growth: Distributed Social Group-Buying & Referral Engine",
        "app_module": "services.distributed_group_commerce.app:app",
        "default_port": 8002,
        "path": "services/distributed_group_commerce"
    },
    "pricing": {
        "name": "Pricing: Dynamic Price Elasticity Optimizer",
        "app_module": "services.dynamic_price_elasticity.app:app",
        "default_port": 8003,
        "path": "services/dynamic_price_elasticity"
    },
    "video": {
        "name": "Content Commerce: Shoppable Video Feed & Catalog Pipeline",
        "app_module": "services.shoppable_video_catalog.app:app",
        "default_port": 8004,
        "path": "services/shoppable_video_catalog"
    }
}

def main():
    parser = argparse.ArgumentParser(description="Meesho DICE 3.0 Engineering Suite")
    parser.add_argument(
        "--service",
        choices=["ad_auction", "group_commerce", "pricing", "video"],
        help="Specific microservice engine to launch"
    )
    parser.add_argument("--port", type=int, default=None, help="Port to bind the server")
    parser.add_argument("--test", action="store_true", help="Run automated unit test suite")

    args = parser.parse_args()

    # Ensure root directory is on python path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    if args.test:
        print("\n==========================================")
        print(" Running Full Automated Test Suite...    ")
        print("==========================================\n")
        res = subprocess.run([sys.executable, "-m", "pytest", "tests/"])
        sys.exit(res.returncode)

    if not args.service:
        print("\n" + "="*60)
        print("  MEESHO DICE 3.0: COMMERCE ENGINEERING SUITE LAUNCHER  ")
        print("="*60)
        print("\nSelect a project engine to run:\n")
        print("  1. [Monetization] Real-Time Ad-Auction Engine (Port 8001)")
        print("  2. [Growth]       Distributed Group-Buying Engine (Port 8002)")
        print("  3. [Pricing]      Dynamic Price Elasticity Optimizer (Port 8003)")
        print("  4. [Content]      Shoppable Video & Catalog Pipeline (Port 8004)")
        print("  5. Run All Unit Tests")
        print("  0. Exit\n")

        choice = input("Enter choice (1-5): ").strip()
        choice_map = {
            "1": "ad_auction",
            "2": "group_commerce",
            "3": "pricing",
            "4": "video"
        }
        if choice == "5":
            subprocess.run([sys.executable, "-m", "pytest", "tests/"])
            sys.exit(0)
        elif choice in choice_map:
            args.service = choice_map[choice]
        else:
            print("Exiting.")
            sys.exit(0)

    cfg = SERVICE_CONFIGS[args.service]
    port = args.port or cfg["default_port"]

    print("\n" + "#"*60)
    print(f" Starting: {cfg['name']}")
    print(f" Local Web Interface: http://localhost:{port}")
    print(f" Interactive Swagger API Docs: http://localhost:{port}/docs")
    print("#"*60 + "\n")

    # Add service folder to sys.path so internal imports resolve
    service_path = os.path.join(root_dir, cfg["path"])
    if service_path not in sys.path:
        sys.path.insert(0, service_path)

    uvicorn.run(cfg["app_module"], host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    main()
