import json
import os
import re
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel

from .prompts import SYSTEM_PROMPT, action_prompt

# .env 로드 (프로젝트 루트)
load_dotenv(Path(__file__).parent.parent / ".env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
PORT = int(os.environ.get("PORT", 3001))

client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="A2UI Agent Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def call_gemini(user_message: str, system_instruction: str = SYSTEM_PROMPT) -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_message,
        config={
            "system_instruction": system_instruction,
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        },
    )

    text = response.text or ""
    # 혹시 코드블록이 붙어있으면 제거
    cleaned = re.sub(r"```json\n?|```\n?", "", text).strip()
    return json.loads(cleaned)


class GenerateRequest(BaseModel):
    prompt: str


class ActionRequest(BaseModel):
    action: str
    context: dict = {}
    currentDataModel: dict = {}
    surfaceId: str = ""


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    if not req.prompt:
        raise HTTPException(status_code=400, detail="프롬프트를 입력하세요.")
    try:
        result = call_gemini(req.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/action")
async def action(req: ActionRequest):
    try:
        prompt = action_prompt(req.action, req.context, req.currentDataModel, req.surfaceId)
        result = call_gemini(prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "model": GEMINI_MODEL}


if __name__ == "__main__":
    print(f"\n A2UI Agent Server: http://localhost:{PORT}")
    print(f" API Key: {'설정됨' if GEMINI_API_KEY else '미설정 — .env에 GEMINI_API_KEY 입력 필요'}")
    print(f" Model: {GEMINI_MODEL}\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
