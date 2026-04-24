import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("LINKEDIN_ACCESS_TOKEN")

if not token:
    print("Token missing")
    exit(1)

# Try userinfo endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
print("UserInfo response:", response.status_code, response.text)

# Try me endpoint just in case
response2 = requests.get("https://api.linkedin.com/v2/me", headers=headers)
print("Me response:", response2.status_code, response2.text)
