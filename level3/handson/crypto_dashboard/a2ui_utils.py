import json
import re
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse


def _wrap_a2ui_part(a2ui_message: dict) -> types.Part:
    """A2UI 메시지 하나를 ADK Web이 인식하는 A2A DataPart로 래핑합니다."""
    # TODO: datapart_json을 구성하세요.
    # 힌트: {"kind": "data", "metadata": {"mimeType": "application/json+a2ui"}, "data": a2ui_message}
    # 그런 다음 <a2a_datapart_json>...</a2a_datapart_json> 태그로 감싸서
    # types.Part(inline_data=types.Blob(data=..., mime_type="text/plain")) 반환

    datapart_json = json.dumps({
        # TODO: 여기를 채우세요
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
    """LLM 응답에서 A2UI JSON을 찾아 DataPart로 변환하는 콜백."""
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

        # TODO: text에서 JSON을 파싱하세요.
        # 힌트:
        #   1. markdown fence (```) 제거
        #   2. JSON 시작 위치 찾기 ([ 또는 {)
        #   3. json.JSONDecoder().raw_decode() 로 파싱
        #   4. A2UI 키가 있는 메시지만 필터링
        #   5. _wrap_a2ui_part()로 래핑하여 LlmResponse 반환

        pass  # TODO: 구현

    return None
