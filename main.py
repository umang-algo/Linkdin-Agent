import os
import requests
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LinkedIn Advanced Agent", description="AI Agent with human-in-the-loop approval and image support.")

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")
GITHUB_REPO_URL = "https://github.com/umang-algo/Linkdin-Agent"

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

DRAFTS_DIR = "drafts"
if not os.path.exists(DRAFTS_DIR):
    os.makedirs(DRAFTS_DIR)

class DraftRequest(BaseModel):
    topic: str
    include_github: bool = True

class PublishRequest(BaseModel):
    draft_id: str
    image_path: str = None # Path to an image on the server or URN

@app.get("/")
def home():
    return {"message": "LinkedIn Advanced Agent is active.", "drafts_folder": DRAFTS_DIR}

@app.post("/generate")
def generate_draft(request: DraftRequest):
    """Generates an AI post and saves it to a local file for review."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set.")
        
    prompt = f"""
    Write a highly engaging, professional LinkedIn post about: {request.topic}.
    Include a catchy hook, 2-3 short paragraphs, and relevant hashtags.
    Make it sound authentic and insightful.
    The output should JUST be the text of the post itself.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        
        if request.include_github:
            content += f"\n\n🚀 Check out the project on GitHub: {GITHUB_REPO_URL}"
            
        draft_id = f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"
        file_path = os.path.join(DRAFTS_DIR, f"{draft_id}.txt")
        
        with open(file_path, "w") as f:
            f.write(content)
            
        return {
            "status": "Draft created and saved locally.",
            "draft_id": draft_id,
            "file_path": file_path,
            "content": content,
            "next_step": f"Review {file_path}. To publish, call POST /publish with this draft_id."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

def register_image_upload():
    """Step 1: Register image upload with LinkedIn."""
    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": LINKEDIN_PERSON_URN,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Register upload failed: {response.text}")
    return response.json()

def upload_image_binary(upload_url, image_path):
    """Step 2: Upload the actual image binary."""
    with open(image_path, "rb") as f:
        headers = {"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"}
        response = requests.put(upload_url, headers=headers, data=f)
        if response.status_code != 201:
            raise Exception(f"Image upload failed: {response.text}")

@app.post("/publish")
def publish_to_linkedin(request: PublishRequest):
    """Publishes a pre-approved draft file to LinkedIn with optional image."""
    file_path = os.path.join(DRAFTS_DIR, f"{request.draft_id}.txt")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Draft file not found.")
        
    with open(file_path, "r") as f:
        content = f.read()
        
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_PERSON_URN:
        raise HTTPException(status_code=500, detail="LinkedIn credentials missing.")

    image_urn = None
    if request.image_path:
        try:
            print(f"Uploading image: {request.image_path}...")
            reg_data = register_image_upload()
            upload_url = reg_data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            image_urn = reg_data['value']['asset']
            upload_image_binary(upload_url, request.image_path)
            print(f"Image uploaded successfully. URN: {image_urn}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    # Constructing payload
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    share_content = {
        "shareCommentary": {"text": content},
        "shareMediaCategory": "NONE"
    }

    if image_urn:
        share_content["shareMediaCategory"] = "IMAGE"
        share_content["media"] = [
            {
                "status": "READY",
                "description": {"text": "Image via LinkedIn Agent"},
                "media": image_urn,
                "title": {"text": "Attached Image"}
            }
        ]

    payload = {
        "author": LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": share_content
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        return {"status": "Success", "post_id": response.json().get('id')}
    else:
        raise HTTPException(status_code=response.status_code, detail=f"LinkedIn Error: {response.text}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
