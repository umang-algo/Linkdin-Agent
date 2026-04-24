import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

def get_urn():
    if not LINKEDIN_ACCESS_TOKEN:
        print("No access token found.")
        return

    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    try:
        response = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
        if response.status_code == 200:
            print(f"URN found via userinfo: urn:li:person:{response.json().get('sub')}")
            return
        
        response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
        if response.status_code == 200:
            print(f"URN found via me: urn:li:person:{response.json().get('id')}")
            return
            
        print(f"Could not fetch URN. Userinfo status: {response.status_code}. Me status: {response.status_code}")
        print("Response:", response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_urn()
