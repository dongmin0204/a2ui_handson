import json
import re
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse


def _wrap_a2ui_part(a2ui_message: dict) -> types.Part:
    datapart_json = json.dumps({
        "kind": "data",
        "metadata": {"mimeType": "application/json+a2ui"},
        "data": a2ui_message,
    })
    blob_data = (
        b"<a2a_datapart_json>"
        + datapart_json.encode("utf-8")
        + b"</a2a_datapart_json>"
    )
    return types.Part(
        inline_data=types.Blob(data=blob_data, mime_type="text/plain")
    )


def a2ui_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    if not llm_response.content or not llm_response.content.parts:
        return None
    for part in llm_response.content.parts:
        if not part.text:
            continue
        text = part.text.strip()
        if not text or not any(
            k in text for k in ("beginRendering", "surfaceUpdate", "dataModelUpdate")
        ):
            continue
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            if text.endswith("```"):
                text = text[:-3].strip()
        json_start = next(
            (i for i, ch in enumerate(text) if ch in ("[", "{")), None
        )
        if json_start is None:
            continue
        json_text = text[json_start:]
        try:
            parsed, _ = json.JSONDecoder().raw_decode(json_text)
        except json.JSONDecodeError:
            try:
                fixed = "[" + re.sub(r'\}\s*\{', '},{', json_text) + "]"
                parsed, _ = json.JSONDecoder().raw_decode(fixed)
            except json.JSONDecodeError:
                continue
        if not isinstance(parsed, list):
            parsed = [parsed]
        a2ui_keys = {"beginRendering", "surfaceUpdate", "dataModelUpdate", "deleteSurface"}
        a2ui_messages = [
            msg for msg in parsed
            if isinstance(msg, dict) and any(k in msg for k in a2ui_keys)
        ]
        if not a2ui_messages:
            continue
        new_parts = [_wrap_a2ui_part(msg) for msg in a2ui_messages]
        return LlmResponse(
            content=types.Content(role="model", parts=new_parts),
            custom_metadata={"a2a:response": "true"},
        )
    return None
