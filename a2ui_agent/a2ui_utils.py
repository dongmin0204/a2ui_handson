import json
import logging
import re
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse

logger = logging.getLogger(__name__)

A2UI_MIME_TYPE = "application/json+a2ui"
A2UI_KEYS = {"beginRendering", "surfaceUpdate", "dataModelUpdate", "deleteSurface"}


def _wrap_a2ui_part(a2ui_message: dict) -> types.Part:
    datapart_json = json.dumps(
        {
            "kind": "data",
            "metadata": {"mimeType": A2UI_MIME_TYPE},
            "data": a2ui_message,
        },
        ensure_ascii=False,
    )

    blob_data = (
        b"<a2a_datapart_json>"
        + datapart_json.encode("utf-8")
        + b"</a2a_datapart_json>"
    )

    return types.Part(
        inline_data=types.Blob(
            data=blob_data,
            mime_type="text/plain",
        )
    )


def _extract_a2ui_messages(text: str) -> list[dict]:
    text = text.strip()

    if not text:
        return []

    # markdown fence 제거
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text[:-3].strip()

    # <a2ui-json> 태그가 있으면 내부만 사용
    tag_match = re.search(
        r"<a2ui-json>(.*?)</a2ui-json>",
        text,
        flags=re.DOTALL,
    )
    if tag_match:
        text = tag_match.group(1).strip()

    # JSON 시작 위치 찾기
    json_start = None
    for i, ch in enumerate(text):
        if ch in ("[", "{"):
            json_start = i
            break

    if json_start is None:
        return []

    json_text = text[json_start:].strip()

    # 1차: 정상 JSON 파싱
    try:
        parsed, _ = json.JSONDecoder().raw_decode(json_text)
    except json.JSONDecodeError:
        # 2차: 연속 JSON 객체 보정
        try:
            fixed = "[" + re.sub(r"}\s*{", "},{", json_text) + "]"
            parsed, _ = json.JSONDecoder().raw_decode(fixed)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse A2UI JSON: %s", e)
            return []

    if isinstance(parsed, dict):
        parsed = [parsed]

    if not isinstance(parsed, list):
        return []

    return [
        msg
        for msg in parsed
        if isinstance(msg, dict) and any(k in msg for k in A2UI_KEYS)
    ]


def a2ui_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    if not llm_response.content or not llm_response.content.parts:
        return None

    # 일단 partial은 건드리지 않는 쪽이 디버깅에 안전
    if llm_response.partial:
        return None

    full_text = "".join(
        part.text for part in llm_response.content.parts if part.text
    )

    messages = _extract_a2ui_messages(full_text)

    if not messages:
        return None

    logger.info("Extracted %d A2UI messages", len(messages))

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[_wrap_a2ui_part(msg) for msg in messages],
        ),
        partial=False,
        custom_metadata={"a2a:response": "true"},
    )