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
    payload = {
        "kind": "data",
        "metadata": {"mimeType": A2UI_MIME_TYPE},
        "data": a2ui_message,
    }

    # 중요:
    # ensure_ascii=True로 두면 한글이 \uc6b4\ub3d9 형태로 들어가서
    # 프론트에서 atob()만 써도 mojibake가 덜 발생함.
    datapart_json = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
    )

    blob_data = (
        b"<a2a_datapart_json>"
        + datapart_json.encode("utf-8")
        + b"</a2a_datapart_json>"
    )

    return types.Part(
        inline_data=types.Blob(
            data=blob_data,
            mime_type="text/plain; charset=utf-8",
        )
    )


def _strip_markdown_fence(text: str) -> str:
    text = text.strip()

    if not text.startswith("```"):
        return text

    # ```json ... ``` / ``` ... ``` 모두 처리
    text = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return text.strip()


def _extract_json_region(text: str) -> str | None:
    text = text.strip()

    # <a2ui-json>...</a2ui-json> 우선 처리
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


def _parse_json_or_consecutive_objects(json_text: str):
    decoder = json.JSONDecoder()

    # 1차: 정상 JSON
    try:
        parsed, _ = decoder.raw_decode(json_text)
        return parsed
    except json.JSONDecodeError:
        pass

    # 2차: {"a":1} {"b":2} 같은 연속 JSON 객체 처리
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
            logger.warning("Failed to parse A2UI JSON: %s", e)
            return None

    if objects:
        return objects

    return None


def _extract_a2ui_messages(text: str) -> list[dict]:
    text = _strip_markdown_fence(text)

    if not text:
        return []

    json_text = _extract_json_region(text)

    if not json_text:
        return []

    json_text = _strip_markdown_fence(json_text)

    parsed = _parse_json_or_consecutive_objects(json_text)

    if parsed is None:
        return []

    if isinstance(parsed, dict):
        parsed = [parsed]

    if not isinstance(parsed, list):
        return []

    messages: list[dict] = []

    for msg in parsed:
        if not isinstance(msg, dict):
            continue

        if any(key in msg for key in A2UI_KEYS):
            messages.append(msg)

    return messages


def a2ui_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    if not llm_response.content or not llm_response.content.parts:
        return None

    # streaming 중간 조각은 건드리지 않음
    if llm_response.partial:
        return None

    full_text = "".join(
        part.text or ""
        for part in llm_response.content.parts
    )

    logger.info("LLM full_text repr: %r", full_text[:500])

    messages = _extract_a2ui_messages(full_text)

    if not messages:
        return None

    logger.info("Extracted %d A2UI messages", len(messages))

    new_parts = [_wrap_a2ui_part(msg) for msg in messages]

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=new_parts,
        ),
        partial=False,
        custom_metadata={"a2a:response": "true"},
    )