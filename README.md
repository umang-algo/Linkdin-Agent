# 🤖 LinkedIn AI Agent

An autonomous AI agent designed to draft and publish high-quality LinkedIn posts. This tool leverages **GPT-4o** for content generation and the **LinkedIn API** for zero-touch publishing.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- A LinkedIn Developer App (with `w_member_social` and `openid` permissions)
- An OpenAI API Key

### 2. Installation
```bash
git clone https://github.com/umang-algo/Linkdin-Agent.git
cd Linkdin-Agent
pip install -r requirements.txt
```

### 3. Setup Environment
Create a `.env` file based on `.env.example`:
```env
LINKEDIN_CLIENT_ID=your_id
LINKEDIN_CLIENT_SECRET=your_secret
OPENAI_API_KEY=your_openai_key
```

---

## 🔐 Authentication (The Handshake)

Before you can post, you need a temporary Access Token and your unique LinkedIn URN (Member ID).

1.  Run the auth script:
    ```bash
    python auth.py
    ```
2.  Your browser will open. Authorize the app.
3.  The terminal will print your `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_URN`.
4.  **Copy these into your `.env` file.**

---

## 🛠️ Usage

The agent runs as a FastAPI server. This allows you to integrate it into other workflows (like Sovereign or a Slack bot).

### 1. Start the Agent
```bash
python main.py
```
The API will be available at `http://localhost:8000`. You can access the interactive Swagger UI at `http://localhost:8000/docs`.

### 2. Generate a Draft
Send a `POST` request to `/generate`:
```json
{
  "topic": "The future of AI agents in 2026"
}
```
The agent will return a professionally crafted post with hooks and hashtags.

### 3. Publish to LinkedIn
Once you are happy with the draft, simply call:
`GET /publish`

The agent will push the post live to your LinkedIn profile.

---

## 🧠 Features
- **GPT-4o Integration**: High-fidelity, authentic writing style.
- **State Management**: Stores drafts in-memory for review before publishing.
- **RESTful API**: Easily connectable to any frontend or automation tool.

## 🛡️ License
MIT License.
