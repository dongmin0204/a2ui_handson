import json
import logging
import re
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from a2ui.parser.parser import parse_response, has_a2ui_parts

logger = logging.getLogger(__name__)

A2UI_MIME_TYPE = "application/json+a2ui"

_A2UI_TAG_RE = re.compile(
    r"(<a2ui-json>)(.*?)(</a2ui-json>)", re.DOTALL
)


def _fix_consecutive_json(text: str) -> str:
    """Wrap consecutive JSON objects inside <a2ui-json> tags into an array."""

    def _fix_match(m: re.Match) -> str:
        open_tag, body, close_tag = m.group(1), m.group(2), m.group(3)
        stripped = body.strip()

        if stripped.startswith("["):
            return m.group(0)

        objects: list[str] = []
        decoder = json.JSONDecoder()
        pos = 0
        while pos < len(stripped):
            if stripped[pos] in " \t\r\n":
                pos += 1
                continue
            try:
                _obj, end = decoder.raw_decode(stripped, pos)
                objects.append(stripped[pos : pos + end])
                pos += end
            except json.JSONDecodeError:
                return m.group(0)

        if len(objects) <= 1:
            return m.group(0)

        logger.info("Fixed %d consecutive JSON objects into array", len(objects))
        return f"{open_tag}[{','.join(objects)}]{close_tag}"

    return _A2UI_TAG_RE.sub(_fix_match, text)


def _wrap_a2ui_part(a2ui_message: dict) -> types.Part:
    blob_data = (
        b"<a2a_datapart_json>"
        + json.dumps({
            "data": a2ui_message,
            "metadata": {"mimeType": A2UI_MIME_TYPE},
        }).encode("utf-8")
        + b"</a2a_datapart_json>"
    )
    return types.Part(
        inline_data=types.Blob(
            data=blob_data,
            mime_type="text/plain",
        )
    )


def _make_empty_partial() -> LlmResponse:
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text="")]),
        partial=True,
    )


def a2ui_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    if not llm_response.content or not llm_response.content.parts:
        return None

    if llm_response.partial:
        return _make_empty_partial()

    full_text = ""
    for part in llm_response.content.parts:
        if part.text:
            full_text += part.text

    if not full_text.strip() or not has_a2ui_parts(full_text):
        return None

    full_text = _fix_consecutive_json(full_text)

    try:
        response_parts = parse_response(full_text)
    except ValueError:
        logger.warning("Failed to parse A2UI from LLM output")
        return None

    new_parts: list[types.Part] = []
    for rp in response_parts:
        if rp.text:
            new_parts.append(types.Part(text=rp.text))
        if rp.a2ui_json:
            data = rp.a2ui_json
            if isinstance(data, list):
                for msg in data:
                    new_parts.append(_wrap_a2ui_part(msg))
            else:
                new_parts.append(_wrap_a2ui_part(data))

    if not new_parts:
        return None

    return LlmResponse(
        content=types.Content(role="model", parts=new_parts),
        partial=False,
        custom_metadata={"a2a:response": "true"},
    )
