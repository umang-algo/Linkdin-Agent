import os
import requests
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LinkedIn Agent", description="An AI Agent to draft and publish LinkedIn posts.")

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# In-memory storage for our draft
pending_draft = ""

class DraftRequest(BaseModel):
    topic: str

@app.get("/")
def home():
    return {"message": "LinkedIn Agent is running. Go to /docs to use the API."}

@app.post("/generate")
def generate_draft(request: DraftRequest):
    """Uses OpenAI to draft a LinkedIn post based on a topic."""
    global pending_draft
    
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set.")
        
    prompt = f"""
    Write a highly engaging, professional LinkedIn post about: {request.topic}.
    Include a catchy hook, 2-3 short paragraphs, and relevant hashtags.
    Do not use generic buzzwords. Make it sound authentic and insightful.
    The output should JUST be the text of the post itself.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        pending_draft = response.choices[0].message.content
        return {
            "status": "Draft generated successfully.",
            "draft": pending_draft,
            "next_step": "Review the draft. If it looks good, call GET /publish to post it."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

@app.get("/draft")
def get_draft():
    """Returns the currently stored draft."""
    if not pending_draft:
        return {"status": "No draft pending. Call POST /generate first."}
    return {"draft": pending_draft}

@app.get("/publish")
def publish_to_linkedin():
    """Publishes the approved draft to LinkedIn."""
    global pending_draft
    
    if not pending_draft:
        raise HTTPException(status_code=400, detail="No draft to publish. Call POST /generate first.")
        
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
        raise HTTPException(status_code=500, detail="LinkedIn Access Token or Person URN is missing from .env.")

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
                    "text": pending_draft
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC" # or "CONNECTIONS"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 201:
        published_urn = response.json().get('id', 'Unknown ID')
        print(f"✅ Successfully posted to LinkedIn! ID: {published_urn}")
        
        # Clear draft after successful publish
        published_text = pending_draft
        pending_draft = "" 
        
        return {
            "status": "Success",
            "message": "Post successfully published to LinkedIn!",
            "post_urn": published_urn,
            "content": published_text
        }
    else:
        print(f"❌ Failed to post. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=f"LinkedIn API Error: {response.text}")

if __name__ == "__main__":
    import uvicorn
    print("\n--- Starting LinkedIn Agent Server ---")
    print("API is available at: http://localhost:8000")
    print("Swagger docs available at: http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
