import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("LINKEDIN_ACCESS_TOKEN")

# Try with person URN using the `sub` ID
author = "urn:li:person:uEcPa0lV3r"

url = "https://api.linkedin.com/v2/ugcPosts"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

payload = {
    "author": author,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Testing the LinkedIn API..."
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

response = requests.post(url, headers=headers, json=payload)
print(response.status_code)
print(response.text)
