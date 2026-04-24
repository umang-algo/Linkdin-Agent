# 🤖 LinkedIn AI Agent (Advanced)

An autonomous AI agent designed to draft, review, and publish high-quality LinkedIn posts with **image support**.

## 🚀 Advanced Workflow

### 1. Generate a Draft File
Instead of publishing immediately, the agent now creates a local file for you to review or edit.
```bash
curl -X POST http://localhost:8080/generate \
     -H "Content-Type: application/json" \
     -d '{"topic": "Why AI Agents are the new UI"}'
```
- **Output**: A unique `draft_id` and a file saved in the `drafts/` directory.
- **Action**: Open the file in `drafts/`, tweak the text if needed, and save it.

### 2. Add an Image (Optional)
If you want to include a visual with your post, place the image in your project folder (e.g., `banner.png`).

### 3. Approve and Publish
When you are ready to go live, call the `/publish` endpoint with your `draft_id`.
```bash
curl -X POST http://localhost:8080/publish \
     -H "Content-Type: application/json" \
     -d '{
       "draft_id": "draft_20260424_1156",
       "image_path": "banner.png"
     }'
```

## 🛠️ Features
- **File-Based Drafts**: Edit your posts in your favorite text editor before they go live.
- **Image Upload API**: Seamless binary upload to LinkedIn's media servers.
- **GitHub Attribution**: Automatically appends your repository link to every post.
- **Human-in-the-Loop**: Total control over the final output.

## 📦 Requirements Update
The agent now uses `requests` for complex binary uploads and `openai` for drafting. Ensure your `.env` has:
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_URN`
- `OPENAI_API_KEY`
