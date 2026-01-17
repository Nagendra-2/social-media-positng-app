"""
Social Media Posting Clients
Handles posting to Twitter (X) and LinkedIn.
"""

import os
import requests
import tweepy
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str, required: bool = True) -> Optional[str]:
    """Read an environment variable."""
    value = os.getenv(name)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass
class TwitterCredentials:
    """Twitter API credentials."""
    api_key: str
    api_secret: str
    access_token: str
    access_secret: str

    @classmethod
    def from_env(cls) -> "TwitterCredentials":
        return cls(
            api_key=_get_env("TWITTER_API_KEY"),
            api_secret=_get_env("TWITTER_API_SECRET"),
            access_token=_get_env("TWITTER_ACCESS_TOKEN"),
            access_secret=_get_env("TWITTER_ACCESS_SECRET"),
        )


@dataclass
class LinkedInCredentials:
    """LinkedIn API credentials."""
    token: str
    person_urn: Optional[str] = None

    @classmethod
    def from_env(cls) -> "LinkedInCredentials":
        return cls(
            token=_get_env("LINKEDIN_TOKEN"),
            person_urn=_get_env("LINKEDIN_PERSON_URN", required=False),
        )


def post_to_twitter(message: str, creds: Optional[TwitterCredentials] = None) -> str:
    """Publish a tweet. Returns the tweet ID."""
    if creds is None:
        creds = TwitterCredentials.from_env()

    client = tweepy.Client(
        consumer_key=creds.api_key,
        consumer_secret=creds.api_secret,
        access_token=creds.access_token,
        access_token_secret=creds.access_secret,
    )

    response = client.create_tweet(text=message)
    tweet_id = response.data["id"]
    print(f"✅ Twitter post ID: {tweet_id}")
    return str(tweet_id)


def _fetch_linkedin_urn(token: str) -> str:
    """Fetch the authenticated member's URN."""
    headers = {"Authorization": f"Bearer {token}"}

    # Try OpenID endpoint first
    resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers, timeout=15)
    if resp.status_code == 200:
        return resp.json().get("sub")

    # Fallback to legacy /me
    resp = requests.get("https://api.linkedin.com/v2/me", headers=headers, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"Unable to fetch profile URN: {resp.status_code}")
    return resp.json().get("id")


def post_to_linkedin(message: str, creds: Optional[LinkedInCredentials] = None) -> bool:
    """Publish a text post to LinkedIn. Returns True on success."""
    if creds is None:
        creds = LinkedInCredentials.from_env()

    token = creds.token
    profile_urn = creds.person_urn or _fetch_linkedin_urn(token)

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    post_data = {
        "author": f"urn:li:person:{profile_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    resp = requests.post(url, headers=headers, json=post_data, timeout=15)
    if resp.status_code == 201:
        print("✅ LinkedIn post successful!")
        return True
    else:
        print(f"❌ LinkedIn error: {resp.status_code}, {resp.text}")
        return False
