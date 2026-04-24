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
        # Some legacy endpoints use id instead of sub
        response = requests.get("https://api.linkedin.com/v2/me?projection=(id)", headers=headers)
        if response.status_code == 200:
            member_id = response.json().get('id')
            if member_id:
                print(f"urn:li:person:{member_id}")
                return
            
        print(f"Could not fetch URN cleanly. Status: {response.status_code}")
        print("Response:", response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_urn()
