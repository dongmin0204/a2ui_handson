import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from google import genai
from pydantic import BaseModel

from .prompts import SYSTEM_PROMPT, action_prompt

logger = logging.getLogger(__name__)

# .env 로드
load_dotenv(Path(__file__).parent.parent / ".env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
PORT = int(os.environ.get("PORT", 3001))

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

app = FastAPI(title="A2UI Agent Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

A2UI_KEYS = {
    "beginRendering",
    "surfaceUpdate",
    "dataModelUpdate",
    "deleteSurface",
}


class GenerateRequest(BaseModel):
    prompt: str


class ActionRequest(BaseModel):
    action: str
    context: dict = {}
    currentDataModel: dict = {}
    surfaceId: str = ""


def json_response(data: Any, status_code: int = 200) -> Response:
    """
    한글 깨짐 방지를 위해 ensure_ascii=False + UTF-8 charset 명시.
    """
    return Response(
        content=json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8"),
        status_code=status_code,
        media_type="application/json; charset=utf-8",
    )


def _strip_markdown_fence(text: str) -> str:
    text = text.strip()

    if not text.startswith("```"):
        return text

    text = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return text.strip()


def _extract_json_region(text: str) -> str | None:
    text = text.strip()

    # <a2ui-json>...</a2ui-json> 지원
    tag_match = re.search(
        r"<a2ui-json>(.*?)</a2ui-json>",
        text,
        flags=re.DOTALL,
    )
    if tag_match:
        return tag_match.group(1).strip()

    # 태그가 없으면 첫 JSON 시작점부터 사용
    for i, ch in enumerate(text):
        if ch in ("[", "{"):
            return text[i:].strip()

    return None


def _parse_json_or_consecutive_objects(json_text: str) -> Any:
    """
    아래 세 케이스 모두 처리:
    1. [{...}, {...}]
    2. {...}
    3. {...}\n{...}\n{...}
    """
    decoder = json.JSONDecoder()
    json_text = json_text.strip()

    # 1차: 정상 JSON
    try:
        parsed, _ = decoder.raw_decode(json_text)
        return parsed
    except json.JSONDecodeError:
        pass

    # 2차: 연속 JSON 객체 처리
    objects = []
    pos = 0

    while pos < len(json_text):
        while pos < len(json_text) and json_text[pos].isspace():
            pos += 1

        if pos >= len(json_text):
            break

        try:
            obj, end = decoder.raw_decode(json_text, pos)
            objects.append(obj)
            pos = end
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse Gemini JSON: %s", e)
            raise ValueError(f"Gemini 응답 JSON 파싱 실패: {e}") from e

    if objects:
        return objects

    raise ValueError("Gemini 응답에서 JSON 객체를 찾지 못했습니다.")


def parse_gemini_json(text: str) -> Any:
    text = _strip_markdown_fence(text)

    json_text = _extract_json_region(text)

    if not json_text:
        raise ValueError("Gemini 응답에서 JSON 시작점을 찾지 못했습니다.")

    json_text = _strip_markdown_fence(json_text)

    return _parse_json_or_consecutive_objects(json_text)


def _is_a2ui_message(value: Any) -> bool:
    return isinstance(value, dict) and any(key in value for key in A2UI_KEYS)


def normalize_a2ui_messages(parsed: Any) -> list[dict]:
    """
    Gemini 출력 형태가 조금 달라도 최종적으로 A2UI message array로 통일.
    """

    # 이미 A2UI message 하나인 경우
    if _is_a2ui_message(parsed):
        return [parsed]

    # 배열인 경우
    if isinstance(parsed, list):
        return [
            item
            for item in parsed
            if _is_a2ui_message(item)
        ]

    # object wrapper인 경우
    if isinstance(parsed, dict):
        # {"messages": [...]}
        if isinstance(parsed.get("messages"), list):
            return [
                item
                for item in parsed["messages"]
                if _is_a2ui_message(item)
            ]

        # {"a2ui": [...]}
        if isinstance(parsed.get("a2ui"), list):
            return [
                item
                for item in parsed["a2ui"]
                if _is_a2ui_message(item)
            ]

        # {"data": {"surfaceUpdate": ...}}
        if _is_a2ui_message(parsed.get("data")):
            return [parsed["data"]]

        # {"kind": "data", "data": {"surfaceUpdate": ...}}
        if parsed.get("kind") == "data" and _is_a2ui_message(parsed.get("data")):
            return [parsed["data"]]

    return []


def ensure_begin_rendering(messages: list[dict]) -> list[dict]:
    """
    surfaceUpdate만 오면 canvas가 root를 모를 수 있어서 beginRendering 자동 추가.
    """
    has_begin = any("beginRendering" in msg for msg in messages)

    if has_begin:
        return messages

    surface_id = None
    root_id = "root"

    for msg in messages:
        if "surfaceUpdate" not in msg:
            continue

        surface_update = msg["surfaceUpdate"]
        surface_id = surface_update.get("surfaceId")

        components = surface_update.get("components", [])
        if components and isinstance(components[0], dict):
            root_id = components[0].get("id", "root")

        break

    if not surface_id:
        return messages

    return [
        {
            "beginRendering": {
                "surfaceId": surface_id,
                "root": root_id,
            }
        },
        *messages,
    ]


def call_gemini(user_message: str, system_instruction: str = SYSTEM_PROMPT) -> list[dict]:
    if not GEMINI_API_KEY or client is None:
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

    logger.info("Gemini raw response repr: %r", text[:1000])

    parsed = parse_gemini_json(text)

    messages = normalize_a2ui_messages(parsed)

    if not messages:
        raise ValueError(
            "Gemini 응답은 JSON이지만 A2UI message가 아닙니다. "
            "beginRendering, surfaceUpdate, dataModelUpdate 중 하나가 필요합니다."
        )

    messages = ensure_begin_rendering(messages)

    logger.info("Normalized A2UI messages: %d", len(messages))

    return messages


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="프롬프트를 입력하세요.")

    try:
        result = call_gemini(req.prompt)
        return json_response(result)
    except Exception as e:
        logger.exception("Generate failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/action")
async def action(req: ActionRequest):
    try:
        prompt = action_prompt(
            req.action,
            req.context,
            req.currentDataModel,
            req.surfaceId,
        )

        result = call_gemini(prompt)
        return json_response(result)
    except Exception as e:
        logger.exception("Action failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": GEMINI_MODEL,
        "apiKey": "set" if GEMINI_API_KEY else "missing",
    }


if __name__ == "__main__":
    print(f"\nA2UI Agent Server: http://localhost:{PORT}")
    print(f"API Key: {'설정됨' if GEMINI_API_KEY else '미설정 — .env에 GEMINI_API_KEY 입력 필요'}")
    print(f"Model: {GEMINI_MODEL}\n")

    uvicorn.run(app, host="0.0.0.0", port=PORT)