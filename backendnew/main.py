import os
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()
API_KEY     = os.getenv("TOGETHER_API_KEY")
MODEL_URL   = "https://api.together.ai/v1/chat/completions"
MODEL_ID    = "mistralai/Mistral-7B-Instruct-v0.2"
MAX_QUESTIONS = 10

app = FastAPI()

# In‐memory session store
sessions: dict[str, list[dict]] = {}

class ChatRequest(BaseModel):
    session_id: str
    user_input: str

class ChatResponse(BaseModel):
    session_id: str
    content: dict
    done: bool

@app.post("/chat/next", response_model=ChatResponse)
async def chat_next(req: ChatRequest):
    sid = req.session_id

    # 1) Initialize a new session with a strict system prompt
    if sid not in sessions:
        sessions[sid] = [{
            "role": "system",
            "content": (
                "You are a basketball-injury diagnostician. "
                "Ask exactly one question at a time, and output *only* a single JSON object.  \n"
                "- Every JSON must include a \"type\" field: "
                "\"subjective\" (open-ended) or \"objective\" (multiple-choice).  \n"
                "- If \"type\" is \"objective\", include an \"options\" array of strings.  \n"
                "Examples:\n"
                "  Subjective: {\"type\":\"subjective\",\"question\":\"Describe your pain location.\"}\n"
                "  Objective:  {\"type\":\"objective\",\"question\":\"Rate your pain\",\"options\":[\"1–3\",\"4–6\",\"7–10\"]}"
            )
        }]

    # 2) Record the user's answer
    sessions[sid].append({"role": "user", "content": req.user_input})

    # 3) Count how many questions we've already asked
    asked = sum(1 for msg in sessions[sid] if msg["role"] == "assistant")
    # Determine whether to switch to diagnosis mode
    if asked >= MAX_QUESTIONS:
        # Replace the system prompt to instruct final diagnosis
        diagnosis_prompt = {
            "role": "system",
            "content": (
                "You have gathered enough info. Now output *only* a JSON object with:\n"
                "- \"type\":\"diagnosis\"\n"
                "- \"injuries\":[list of possible injury names]\n"
                "- \"confidence\":[matching confidences between 0.0–1.0]\n"
                "Example:\n"
                "{\"type\":\"diagnosis\",\"injuries\":[\"Ankle sprain\",\"Achilles tendonitis\"],"
                "\"confidence\":[0.85,0.65]}"
            )
        }
        to_send = [diagnosis_prompt] + sessions[sid]
    else:
        # Normal Q/A loop
        to_send = sessions[sid]

    # 4) Call Together.ai
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ID,
        "messages": to_send,
        "temperature": 0.1,
        "max_tokens": 150
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(MODEL_URL, json=payload, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    raw = resp.json()["choices"][0]["message"]["content"].strip()

    # 5) Extract the first {...} JSON block
    m = re.search(r'(\{[\s\S]*?\})', raw)
    if m:
        js = m.group(1)
        try:
            data = json.loads(js)
        except json.JSONDecodeError: 
            data = {"error": "invalid_json", "raw": raw}
    else:
        data = {"error": "no_json_found", "raw": raw}

    # 6) Store the assistant's raw reply
    sessions[sid].append({"role": "assistant", "content": raw})

    # 7) Determine if we're done
    done = data.get("type") == "diagnosis"

    return ChatResponse(session_id=sid, content=data, done=done)

# To run locally:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
