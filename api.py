"""
Social Post API - FastAPI server for social media automation.
Receives content from n8n and queues it for scheduled posting.
"""

import json
import re
import time
from typing import Optional, List
from pathlib import Path
from datetime import datetime
from threading import Lock

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from social_post import post_to_twitter, post_to_linkedin


# === APP SETUP ===
app = FastAPI(title="Social Post API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Queue file path (shared with timer_post.py)
QUEUE_FILE = Path("content_queue.json")
queue_lock = Lock()


# === REQUEST MODELS ===
class PostRequest(BaseModel):
    twitter: Optional[str] = None
    linkedin: Optional[str] = None


class QueueRequest(BaseModel):
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    twitter_text: Optional[str] = None  # n8n field name
    linkedin_text: Optional[str] = None  # n8n field name


# === QUEUE HELPERS ===
def load_queue() -> List[dict]:
    """Load content queue from JSON file."""
    if not QUEUE_FILE.exists():
        return []
    try:
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_queue(queue: List[dict]):
    """Save content queue to JSON file with retries."""
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


def clean_text(text: Optional[str]) -> Optional[str]:
    """Clean and parse text content from n8n."""
    if not text:
        return None
    
    # Parse JSON-wrapped content from n8n (e.g., {"post_text": "..."})
    try:
        if text.strip().startswith('{'):
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                text = parsed.get('post_text') or parsed.get('text') or parsed.get('content') or text
    except (json.JSONDecodeError, TypeError):
        pass
    
    # Fix escaped newlines and clean whitespace
    text = text.replace("\\n", "\n")
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# === API ENDPOINTS ===
@app.get("/")
def root():
    return {"status": "ok", "message": "Social Post API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/post")
def create_post(request: PostRequest):
    """Post content to Twitter and/or LinkedIn immediately."""
    results = {}
    
    if request.twitter:
        try:
            tweet_id = post_to_twitter(request.twitter)
            results["twitter"] = {"success": True, "id": tweet_id}
        except Exception as e:
            results["twitter"] = {"success": False, "error": str(e)}
    
    if request.linkedin:
        try:
            success = post_to_linkedin(request.linkedin)
            results["linkedin"] = {"success": success}
        except Exception as e:
            results["linkedin"] = {"success": False, "error": str(e)}
    
    return {"results": results}


@app.post("/queue")
def add_to_queue(request: QueueRequest):
    """Add content to the posting queue for scheduled posting."""
    twitter_content = clean_text(request.twitter or request.twitter_text)
    linkedin_content = clean_text(request.linkedin or request.linkedin_text)
    
    if not twitter_content and not linkedin_content:
        return {"success": False, "error": "No content provided"}
    
    with queue_lock:
        queue = load_queue()
        new_item = {
            "twitter": twitter_content,
            "linkedin": linkedin_content,
            "added_at": datetime.now().isoformat()
        }
        queue.append(new_item)
        save_queue(queue)
        
        return {
            "success": True,
            "message": "Added to queue",
            "queue_size": len(queue)
        }


@app.get("/queue/status")
def queue_status():
    """Get the current queue status."""
    queue = load_queue()
    return {"queue_size": len(queue), "items": queue}


@app.delete("/queue/clear")
def clear_queue():
    """Clear all items from the queue."""
    save_queue([])
    return {"success": True, "message": "Queue cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
