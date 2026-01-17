"""
Timer-Based Social Media Scheduler
Fetches content from queue and posts one item every N minutes.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()

# === CONFIGURATION ===
POST_API_URL = os.getenv("POST_API_URL", "http://localhost:8000/post")
INTERVAL_MINUTES = int(os.getenv("POSTING_INTERVAL_MINUTES", "5"))
QUEUE_FILE = Path("content_queue.json")


def log(message: str):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def load_queue() -> list:
    """Load content queue from JSON file."""
    if not QUEUE_FILE.exists():
        return []
    try:
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_queue(queue: list):
    """Save content queue to JSON file."""
    max_retries = 3
    for i in range(max_retries):
        try:
            with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
            return
        except PermissionError:
            if i == max_retries - 1:
                raise
            time.sleep(0.1)


def post_single(twitter_text: str = None, linkedin_text: str = None) -> dict:
    """Post content to the API."""
    try:
        payload = {}
        if twitter_text:
            payload["twitter"] = twitter_text
        if linkedin_text:
            payload["linkedin"] = linkedin_text
        
        response = requests.post(POST_API_URL, json=payload, timeout=30)
        result = response.json()
        log(f"Posted: {result}")
        return result
    except Exception as e:
        log(f"Error posting: {e}")
        return {"error": str(e)}


def post_next_from_queue() -> dict:
    """Get next item from queue and post it."""
    queue = load_queue()
    
    if not queue:
        return {"status": "empty"}
    
    item = queue.pop(0)
    save_queue(queue)
    
    log(f"Posting from queue. Remaining: {len(queue)}")
    return post_single(item.get("twitter"), item.get("linkedin"))


def run_timer_loop():
    """Main timer loop - posts one item every INTERVAL_MINUTES."""
    log("=" * 50)
    log(f"🚀 TIMER STARTED - Posting every {INTERVAL_MINUTES} minutes")
    log(f"📍 API URL: {POST_API_URL}")
    log(f"📊 Queue size: {len(load_queue())}")
    log("=" * 50)
    
    while True:
        queue = load_queue()
        
        if queue:
            log(f"⏰ Time to post! Queue has {len(queue)} items")
            result = post_next_from_queue()
            
            if "error" in result:
                log(f"❌ Post failed: {result['error']}")
            else:
                log("✅ Post successful!")
        else:
            log("📭 Queue empty, waiting for new content...")
        
        log(f"💤 Sleeping for {INTERVAL_MINUTES} minutes...")
        time.sleep(INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        run_timer_loop()
    else:
        print("Usage: python timer_post.py start")
