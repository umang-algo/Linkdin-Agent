import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

post_text = """Which future do we choose? 🤔 

In today's digital age, our phones and browsers brim with countless apps—each designed to tackle a single issue, yet each vying for our attention and taxing our time. Over time, the pursuit of "productivity" has morphed into a sprawling web of fragmentation. 

That's why with ChatOS, we're venturing into a cleaner, more unified future. Imagine a workspace where you don't toggle between tools, or juggle a multitude of apps—where instead, you simply... talk. ChatOS is pioneering the seamless integration of multiple business AI agents in one place—enabling work, decisions, and actions to unfold through conversation, not chaos. One chat. One interface. Limitless potential.

We're in the throes of developing this revolutionary product, questioning norms, and gaining insights each step of the way. This post is our invitation to join us on this journey—here's what we're creating, why it matters, and how we envision the future of software interaction. The future doesn't need more apps; it needs less friction. #ChatOS #FutureOfWork #ProductivityReimagined"""

def publish_to_linkedin():
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
        print("Error: Required environment variables are missing.")
        return

    print(f"Publishing to LinkedIn as {LINKEDIN_PERSON_URN}...")
    
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    payload = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 201:
        print(f"✅ Successfully posted to LinkedIn! ID: {response.json().get('id')}")
    else:
        print(f"❌ Failed to post. Status Code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    publish_to_linkedin()
