import json
import logging
import re
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.common_modifiers import remove_strict_validation
from a2ui.schema.manager import A2uiSchemaManager

logger = logging.getLogger(__name__)

A2UI_MIME_TYPE = "application/json+a2ui"
A2UI_KEYS = {"beginRendering", "surfaceUpdate", "dataModelUpdate", "deleteSurface"}
A2UI_ALLOWED_ICONS = {
    "accountCircle",
    "add",
    "arrowBack",
    "arrowForward",
    "attachFile",
    "calendarToday",
    "call",
    "camera",
    "check",
    "close",
    "delete",
    "download",
    "edit",
    "event",
    "error",
    "favorite",
    "favoriteOff",
    "folder",
    "help",
    "home",
    "info",
    "locationOn",
    "lock",
    "lockOpen",
    "mail",
    "menu",
    "moreVert",
    "moreHoriz",
    "notificationsOff",
    "notifications",
    "payment",
    "person",
    "phone",
    "photo",
    "print",
    "refresh",
    "search",
    "send",
    "settings",
    "share",
    "shoppingCart",
    "star",
    "starHalf",
    "starOff",
    "upload",
    "visibility",
    "visibilityOff",
    "warning",
}
ICON_ALIASES = {
    "restaurant": "shoppingCart",
    "dumbbell": "check",
    "book": "info",
    "flight": "arrowForward",
    "briefcase": "folder",
    "check_circle": "check",
    "check-circle": "check",
    "calendar": "calendarToday",
    "location": "locationOn",
    "user": "person",
    "cart": "shoppingCart",
}
A2A_DATAPART_RE = re.compile(
    r"<a2a_datapart_json>(.*?)</a2a_datapart_json>",
    flags=re.DOTALL,
)

_VALIDATOR = None


def _a2ui_envelope(a2ui_message: dict) -> dict:
    return {
        "kind": "data",
        "metadata": {"mimeType": A2UI_MIME_TYPE},
        "data": a2ui_message,
    }


def _wrap_a2ui_payload(payload: dict) -> types.Part:
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
            mime_type="text/plain",
        )
    )


def _wrap_a2ui_part(a2ui_message: dict) -> types.Part:
    return _wrap_a2ui_payload(_a2ui_envelope(a2ui_message))


def _make_empty_partial() -> LlmResponse:
    return LlmResponse(
        content=types.Content(role="model", parts=[types.Part(text="")]),
        partial=True,
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

    tag_match = re.search(
        r"<a2ui-json>(.*?)</a2ui-json>",
        text,
        flags=re.DOTALL,
    )
    if tag_match:
        return tag_match.group(1).strip()

    for i, ch in enumerate(text):
        if ch in ("[", "{"):
            return text[i:].strip()

    return None


def _parse_json_or_consecutive_objects(json_text: str):
    decoder = json.JSONDecoder()

    try:
        parsed, _ = decoder.raw_decode(json_text)
        return parsed
    except json.JSONDecodeError as e:
        repaired = _repair_json_mismatched_closers(json_text)
        if repaired != json_text:
            try:
                parsed, _ = decoder.raw_decode(repaired)
                logger.info("Repaired mismatched A2UI JSON closers before parsing")
                return parsed
            except json.JSONDecodeError:
                pass

        repaired = _repair_json_extra_closing_braces(json_text, e)
        if repaired != json_text:
            try:
                parsed, _ = decoder.raw_decode(repaired)
                logger.info("Repaired malformed A2UI JSON before parsing")
                return parsed
            except json.JSONDecodeError:
                pass

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

    return objects if objects else None


def _repair_json_mismatched_closers(json_text: str) -> str:
    chars = list(json_text)
    stack: list[str] = []
    in_string = False
    escaped = False

    for i, ch in enumerate(chars):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch in ("[", "{"):
            stack.append(ch)
        elif ch in ("]", "}"):
            if not stack:
                continue

            expected = "]" if stack[-1] == "[" else "}"
            if ch == expected:
                stack.pop()
            else:
                chars[i] = expected
                stack.pop()

    chars.extend("]" if ch == "[" else "}" for ch in reversed(stack))
    return "".join(chars)


def _repair_json_extra_closing_braces(json_text: str, error: json.JSONDecodeError) -> str:
    """
    모델이 컴포넌트 배열 끝에 닫는 중괄호를 하나 더 붙이는 케이스를 복구.
    예: ... "usageHint": "body"}}}}] -> ... "usageHint": "body"}}}]
    """

    repaired = json_text

    for _ in range(5):
        pos = min(max(error.pos, 0), len(repaired) - 1)

        if error.msg != "Expecting ',' delimiter" or repaired[pos] != "}":
            return repaired

        repaired = repaired[:pos] + repaired[pos + 1:]

        try:
            json.JSONDecoder().raw_decode(repaired)
            return repaired
        except json.JSONDecodeError as next_error:
            error = next_error

    return repaired


def _append_a2ui_message(messages: list[dict], value) -> None:
    value = _unwrap_a2ui_envelope(value)

    if isinstance(value, list):
        for item in value:
            _append_a2ui_message(messages, item)
        return

    if isinstance(value, dict) and any(key in value for key in A2UI_KEYS):
        messages.append(value)


def _extract_a2a_datapart_messages(text: str) -> list[dict]:
    messages: list[dict] = []

    for match in A2A_DATAPART_RE.finditer(text):
        json_text = match.group(1).strip()

        try:
            parsed = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse A2A DataPart JSON: %s", e)
            continue

        _append_a2ui_message(messages, parsed)

    return messages


def _unwrap_a2ui_envelope(value):
    """
    A2A DataPart envelope 형태를 A2UI message로 벗겨냄.

    {
      "kind": "data",
      "metadata": {"mimeType": "application/json+a2ui"},
      "data": {"surfaceUpdate": {...}}
    }

    ->

    {"surfaceUpdate": {...}}
    """

    if isinstance(value, list):
        return [_unwrap_a2ui_envelope(item) for item in value]

    if not isinstance(value, dict):
        return value

    if (
        value.get("kind") == "data"
        and isinstance(value.get("metadata"), dict)
        and value["metadata"].get("mimeType") == A2UI_MIME_TYPE
        and "data" in value
    ):
        return _unwrap_a2ui_envelope(value["data"])

    if value.get("kind") == "data" and "data" in value:
        return _unwrap_a2ui_envelope(value["data"])

    if isinstance(value.get("data"), dict) and any(
        key in value["data"] for key in A2UI_KEYS
    ):
        return _unwrap_a2ui_envelope(value["data"])

    return value


def _extract_a2ui_messages(text: str) -> list[dict]:
    text = _strip_markdown_fence(text)

    if not text:
        return []

    datapart_messages = _extract_a2a_datapart_messages(text)
    if datapart_messages:
        return datapart_messages

    json_text = _extract_json_region(text)

    if not json_text:
        return []

    json_text = _strip_markdown_fence(json_text)

    parsed = _parse_json_or_consecutive_objects(json_text)

    if parsed is None:
        return []

    parsed = _unwrap_a2ui_envelope(parsed)

    if isinstance(parsed, dict):
        parsed = [parsed]

    if not isinstance(parsed, list):
        return []

    messages: list[dict] = []

    for msg in parsed:
        _append_a2ui_message(messages, msg)
    return messages


def _surface_update_defaults(messages: list[dict]) -> tuple[str | None, str]:
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

    return surface_id, root_id


def _ensure_begin_rendering(messages: list[dict]) -> list[dict]:
    surface_id, root_id = _surface_update_defaults(messages)
    has_begin = any("beginRendering" in msg for msg in messages)

    if has_begin:
        for msg in messages:
            begin_rendering = msg.get("beginRendering")
            if not isinstance(begin_rendering, dict):
                continue

            begin_rendering.setdefault("surfaceType", "materialDynamic")
            if root_id:
                begin_rendering.setdefault("root", root_id)

        return messages

    if not surface_id:
        return messages

    return [
        {
            "beginRendering": {
                "surfaceId": surface_id,
                "surfaceType": "materialDynamic",
                "root": root_id,
            }
        },
        *messages,
    ]


def _normalize_icon_name(name):
    if isinstance(name, str):
        literal = name
    elif isinstance(name, dict):
        literal = name.get("literalString")
    else:
        literal = None

    if not literal:
        return {"literalString": "info"}

    normalized = ICON_ALIASES.get(literal, literal)
    if normalized not in A2UI_ALLOWED_ICONS:
        logger.warning("Unsupported A2UI icon %r replaced with 'info'", literal)
        normalized = "info"

    return {"literalString": normalized}


def _normalize_component(component_entry: dict) -> None:
    component = component_entry.get("component")
    if not isinstance(component, dict) or len(component) != 1:
        return

    component_type = next(iter(component))
    props = component[component_type]
    if not isinstance(props, dict):
        return

    if component_type == "Icon":
        props["name"] = _normalize_icon_name(props.get("name"))
        return

    if component_type == "Button":
        props.setdefault(
            "action",
            {
                "name": "buttonClick",
                "context": [
                    {
                        "key": "componentId",
                        "value": {
                            "literalString": component_entry.get("id", "button")
                        },
                    }
                ],
            },
        )
        return

    if component_type == "DatePicker":
        component["DateTimeInput"] = {
            "value": props.get("value", {"literalString": ""}),
            "enableDate": True,
            "enableTime": False,
        }
        del component["DatePicker"]


def _escape_non_ascii_literal_strings(value) -> None:
    if isinstance(value, list):
        for item in value:
            _escape_non_ascii_literal_strings(item)
        return

    if not isinstance(value, dict):
        return

    literal = value.get("literalString")
    if isinstance(literal, str):
        value["literalString"] = literal.encode(
            "ascii",
            "xmlcharrefreplace",
        ).decode("ascii")

    for child in value.values():
        _escape_non_ascii_literal_strings(child)


def _normalize_a2ui_messages(messages: list[dict]) -> list[dict]:
    for msg in messages:
        _escape_non_ascii_literal_strings(msg)

        surface_update = msg.get("surfaceUpdate")
        if not isinstance(surface_update, dict):
            continue

        components = surface_update.get("components")
        if not isinstance(components, list):
            continue

        for component_entry in components:
            if isinstance(component_entry, dict):
                _normalize_component(component_entry)

    return messages


def _get_a2ui_validator():
    global _VALIDATOR

    if _VALIDATOR is None:
        schema_manager = A2uiSchemaManager(
            version="0.8",
            catalogs=[BasicCatalog.get_config("0.8")],
            schema_modifiers=[remove_strict_validation],
        )
        _VALIDATOR = schema_manager.get_selected_catalog().validator

    return _VALIDATOR


def _validate_a2ui_messages(messages: list[dict]) -> bool:
    try:
        _get_a2ui_validator().validate(messages)
    except Exception as e:
        logger.warning("A2UI schema validation failed: %s", e)
        return False

    return True


def _looks_like_a2ui(text: str) -> bool:
    return any(key in text for key in A2UI_KEYS)


def _fallback_parse_error_messages() -> list[dict]:
    surface_id = "a2ui_parse_error"

    return [
        {
            "beginRendering": {
                "surfaceId": surface_id,
                "surfaceType": "materialDynamic",
                "root": "root",
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": surface_id,
                "components": [
                    {
                        "id": "root",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["message"]
                                }
                            }
                        },
                    },
                    {
                        "id": "message",
                        "component": {
                            "Text": {
                                "text": {
                                    "literalString": "UI 응답을 파싱하지 못했습니다. 다시 요청해 주세요."
                                },
                                "usageHint": "body",
                            }
                        },
                    },
                ],
            }
        },
    ]


def _a2ui_message_summary(messages: list[dict]) -> list[dict]:
    summary = []

    for msg in messages:
        if isinstance(msg.get("beginRendering"), dict):
            begin_rendering = msg["beginRendering"]
            summary.append(
                {
                    "beginRendering": {
                        "surfaceId": begin_rendering.get("surfaceId"),
                        "surfaceType": begin_rendering.get("surfaceType"),
                        "root": begin_rendering.get("root"),
                    }
                }
            )
            continue

        if isinstance(msg.get("surfaceUpdate"), dict):
            surface_update = msg["surfaceUpdate"]
            summary.append(
                {
                    "surfaceUpdate": {
                        "surfaceId": surface_update.get("surfaceId"),
                        "components": len(surface_update.get("components", [])),
                    }
                }
            )
            continue

        summary.append({key: True for key in msg if key in A2UI_KEYS})

    return summary


def a2ui_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    if not llm_response.content or not llm_response.content.parts:
        return None

    if llm_response.partial:
        return _make_empty_partial()

    full_text = "".join(
        part.text or ""
        for part in llm_response.content.parts
    )

    logger.info("LLM full_text repr: %r", full_text[:500])

    messages = _extract_a2ui_messages(full_text)

    if not messages:
        if not _looks_like_a2ui(full_text):
            return None

        logger.warning("A2UI-looking response could not be parsed; returning fallback UI")
        messages = _fallback_parse_error_messages()

    messages = _normalize_a2ui_messages(_ensure_begin_rendering(messages))

    if not _validate_a2ui_messages(messages):
        messages = _fallback_parse_error_messages()

    logger.info("Extracted %d A2UI messages", len(messages))
    logger.info("A2UI outbound summary: %r", _a2ui_message_summary(messages))

    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[_wrap_a2ui_part(msg) for msg in messages],
        ),
        partial=False,
        custom_metadata={"a2a:response": "true"},
    )
