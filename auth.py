import os
import urllib.parse
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback")

# Scopes needed for posting and getting profile id
SCOPES = "w_member_social profile openid email"

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/callback':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            if 'code' in query_params:
                auth_code = query_params['code'][0]
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication successful!</h1><p>You can close this window now and return to the terminal.</p></body></html>")
                
                # Exchange code for access token
                self.server.auth_code = auth_code
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Authentication failed: No code provided.")
        else:
            self.send_response(404)
            self.end_headers()

def get_linkedin_urn(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Try /v2/userinfo
    try:
        res = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
        if res.status_code == 200:
            data = res.json()
            # Usually 'sub' is the unique member id, let's try to format it as a URN
            return f"urn:li:person:{data.get('sub')}"
    except Exception as e:
        pass
        
    # Try /v2/me
    try:
        res = requests.get('https://api.linkedin.com/v2/me', headers=headers)
        if res.status_code == 200:
            return f"urn:li:person:{res.json().get('id')}"
    except Exception as e:
        pass
        
    return None

def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET is missing in the .env file.")
        print("Please fill them in and try again.")
        return

    # 1. Generate Auth URL
    auth_url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "random_string_xyz123", # Required for CSRF protection
        "scope": SCOPES
    })

    print("\n--- LinkedIn Authentication ---")
    print(f"Opening browser to authorize with LinkedIn...\nIf it doesn't open automatically, click here:\n{auth_url}\n")
    
    webbrowser.open(auth_url)

    # 2. Start local server to wait for callback
    server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
    server.auth_code = None
    
    print("Waiting for callback on http://localhost:8000/callback (Press Ctrl+C to abort)...")
    while not server.auth_code:
        server.handle_request()
        
    print("\n✅ Authorization code received! Exchanging for access token...")
    
    # 3. Exchange code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": server.auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        print("\n🎉 SUCCESS! Access Token retrieved.")
        
        print("Fetching your LinkedIn URN (Person ID)...")
        urn = get_linkedin_urn(access_token)
        
        if not urn:
            print("⚠️ Could not fetch URN automatically. This usually means your app is missing 'profile' or 'openid' permissions.")
            print("You will need to run the profile fetch manually, or just use the token later if URN is pre-known.")
        
        print("\n" + "="*60)
        print("Please paste the following into your `.env` file:")
        print("="*60)
        print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
        if urn:
            print(f"LINKEDIN_PERSON_URN={urn}")
        print("="*60 + "\n")
    else:
        print(f"\n❌ Error exchanging token: {response.text}")

if __name__ == "__main__":
    main()
