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
from fastapi.responses import HTMLResponse, Response
from google import genai
from pydantic import BaseModel, Field

from .prompts import SYSTEM_PROMPT, action_prompt

logger = logging.getLogger(__name__)

# .env 로드
load_dotenv(Path(__file__).parent.parent / ".env")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
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

INTERACTIVE_HTML = r"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>A2UI Interactive</title>
  <style>
    :root { color-scheme: light; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; background: #f7f7f8; color: #1f2937; }
    .shell { display: grid; grid-template-columns: 360px 1fr; min-height: 100vh; }
    .panel { border-right: 1px solid #e5e7eb; background: #fff; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
    .panel h1 { font-size: 18px; margin: 0; }
    textarea { min-height: 130px; resize: vertical; border: 1px solid #d1d5db; border-radius: 8px; padding: 10px; font: inherit; }
    button { border: 0; border-radius: 8px; padding: 10px 12px; font: inherit; cursor: pointer; background: #2563eb; color: white; }
    button.secondary { background: #e5e7eb; color: #111827; }
    button:disabled { opacity: .6; cursor: wait; }
    pre { margin: 0; white-space: pre-wrap; word-break: break-word; font-size: 12px; background: #111827; color: #d1d5db; border-radius: 8px; padding: 12px; max-height: 260px; overflow: auto; }
    .canvas { padding: 28px; }
    .surface { max-width: 920px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }
    .col { display: flex; flex-direction: column; gap: 12px; }
    .row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .card { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 18px; box-shadow: 0 1px 2px rgb(0 0 0 / .04); }
    .headline { font-size: 28px; font-weight: 750; margin: 0; }
    .title { font-size: 20px; font-weight: 700; margin: 0; }
    .body { font-size: 15px; margin: 0; }
    .caption { font-size: 12px; color: #6b7280; margin: 0; }
    label.field { display: grid; gap: 6px; font-size: 13px; color: #374151; }
    input, select { border: 1px solid #d1d5db; border-radius: 8px; padding: 9px 10px; font: inherit; background: #fff; }
    input[type="checkbox"] { width: 18px; height: 18px; }
    table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
    th, td { text-align: left; padding: 10px; border-bottom: 1px solid #e5e7eb; }
    th { background: #f3f4f6; font-weight: 700; }
    .empty { color: #6b7280; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 24px; text-align: center; }
  </style>
</head>
<body>
  <main class="shell">
    <aside class="panel">
      <h1>A2UI Interactive</h1>
      <textarea id="prompt">호텔 예약 UI를 만들어줘. 목적지, 체크인 날짜, 체크아웃 날짜, 인원, 객실 타입 입력과 검색 버튼을 포함해줘.</textarea>
      <button id="generate">Generate</button>
      <button id="reset" class="secondary">Reset State</button>
      <pre id="log">ready</pre>
    </aside>
    <section class="canvas">
      <div id="surface" class="surface"><div class="empty">Generate a UI to start.</div></div>
    </section>
  </main>
  <script>
    const app = {
      surfaceId: "",
      rootId: "root",
      components: new Map(),
      dataModel: {},
      loading: false,
    };

    const surfaceEl = document.getElementById("surface");
    const logEl = document.getElementById("log");
    const generateBtn = document.getElementById("generate");
    const promptEl = document.getElementById("prompt");

    function log(value) {
      logEl.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
    }

    function setLoading(value) {
      app.loading = value;
      generateBtn.disabled = value;
    }

    function getPath(path, base) {
      if (!path) return undefined;
      const source = path.startsWith("/") ? app.dataModel : base;
      const parts = path.replace(/^\//, "").split("/").filter(Boolean);
      return parts.reduce((acc, part) => acc == null ? undefined : acc[part], source);
    }

    function setPath(path, value) {
      if (!path || !path.startsWith("/")) return;
      const parts = path.replace(/^\//, "").split("/").filter(Boolean);
      let target = app.dataModel;
      for (let i = 0; i < parts.length - 1; i++) {
        target[parts[i]] ??= {};
        target = target[parts[i]];
      }
      target[parts.at(-1)] = value;
    }

    function setRelativePath(base, path, value) {
      if (!path || path.startsWith("/") || base == null || typeof base !== "object") return;
      const parts = path.split("/").filter(Boolean);
      let target = base;
      for (let i = 0; i < parts.length - 1; i++) {
        target[parts[i]] ??= {};
        target = target[parts[i]];
      }
      target[parts.at(-1)] = value;
    }

    function valueOf(value, base) {
      if (value == null) return "";
      if (typeof value !== "object") return value;
      if ("path" in value) return getPath(value.path, base);
      if ("literalString" in value) return value.literalString;
      if ("literalBoolean" in value) return value.literalBoolean;
      if ("literalNumber" in value) return value.literalNumber;
      return "";
    }

    function childrenOf(component) {
      const children = component.children;
      if (Array.isArray(children)) return children;
      if (children?.explicitList) return children.explicitList;
      return [];
    }

    function componentDef(id) {
      return app.components.get(id);
    }

    function normalizeComponent(def) {
      const raw = def.component;
      if (typeof raw === "string") return { type: raw, props: def };
      const [[type, props]] = Object.entries(raw || {});
      return { type, props: { ...props, id: def.id } };
    }

    function labelText(props, fallback = "") {
      return valueOf(props.label, {}) || props.label || props.placeholder || fallback;
    }

    async function sendAction(action, context = {}, event = {}, stateChange = {}) {
      setLoading(true);
      try {
        const res = await fetch("/api/action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action,
            context,
            event,
            stateChange,
            surfaceId: app.surfaceId,
            currentDataModel: app.dataModel,
          }),
        });
        if (!res.ok) throw new Error(await res.text());
        const messages = await res.json();
        log({ action, context, stateChange, response: messages });
        applyMessages(messages);
      } catch (err) {
        log(String(err));
      } finally {
        setLoading(false);
      }
    }

    function actionInfo(action) {
      if (!action) return null;
      if (action.event) return { name: action.event.name, context: action.event.context || {} };
      return { name: action.name, context: action.context || {} };
    }

    function renderNode(id, base = app.dataModel) {
      const def = componentDef(id);
      if (!def) return document.createComment(`missing ${id}`);
      const { type, props } = normalizeComponent(def);

      if (type === "Column" || type === "Row") {
        const el = document.createElement("div");
        el.className = type === "Column" ? "col" : "row";
        if (props.children?.path && props.children?.componentId) {
          const items = getPath(props.children.path, base) || [];
          items.forEach(item => el.append(renderNode(props.children.componentId, item)));
        } else {
          for (const childId of childrenOf(props)) el.append(renderNode(childId, base));
        }
        return el;
      }

      if (type === "Card") {
        const el = document.createElement("div");
        el.className = "card";
        el.append(renderNode(props.child, base));
        return el;
      }

      if (type === "Text") {
        const el = document.createElement("p");
        const variant = props.variant || props.usageHint || "body";
        el.className = variant === "headline" || variant === "h1" ? "headline" : variant === "title" || variant === "h3" ? "title" : variant === "caption" ? "caption" : "body";
        el.textContent = valueOf(props.text, base);
        return el;
      }

      if (type === "Icon") {
        const el = document.createElement("span");
        el.textContent = props.name || "";
        return el;
      }

      if (type === "Divider") return document.createElement("hr");

      if (type === "Button") {
        const el = document.createElement("button");
        if (props.child && componentDef(props.child)) {
          el.append(renderNode(props.child, base));
        } else {
          el.textContent = props.label || props.text || "Run";
        }
        const action = actionInfo(props.action);
        el.addEventListener("click", () => {
          if (!action) return;
          sendAction(action.name, action.context, { type: "click", componentId: id }, {});
        });
        return el;
      }

      if (type === "CheckBox") {
        const path = props.value?.path;
        const wrapper = document.createElement("label");
        wrapper.className = "row";
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = Boolean(valueOf(props.value, base));
        const text = document.createElement("span");
        text.textContent = labelText(props, id);
        input.addEventListener("change", () => {
          if (path?.startsWith("/")) setPath(path, input.checked);
          else setRelativePath(base, path, input.checked);
          sendAction("checkbox_changed", { componentId: id, path }, { type: "change", componentId: id }, { path, value: input.checked });
        });
        wrapper.append(input, text);
        return wrapper;
      }

      if (type === "TextField" || type === "DatePicker" || type === "Slider") {
        const path = props.value?.path || props.text?.path;
        const wrapper = document.createElement("label");
        wrapper.className = "field";
        wrapper.append(labelText(props, id));
        const input = document.createElement("input");
        input.type = type === "DatePicker" ? "date" : type === "Slider" ? "range" : "text";
        if (props.min != null) input.min = props.min;
        if (props.max != null) input.max = props.max;
        if (props.step != null) input.step = props.step;
        input.value = valueOf(props.value || props.text, base) ?? "";
        input.addEventListener("change", () => {
          const value = input.type === "range" ? Number(input.value) : input.value;
          if (path?.startsWith("/")) setPath(path, value);
          else setRelativePath(base, path, value);
          sendAction("state_changed", { componentId: id, path }, { type: "change", componentId: id }, { path, value });
        });
        wrapper.append(input);
        return wrapper;
      }

      if (type === "DataTable") {
        const table = document.createElement("table");
        const columns = valueOf(props.columns, base) || [];
        const rows = valueOf(props.rows, base) || [];
        const thead = document.createElement("thead");
        const tr = document.createElement("tr");
        columns.forEach(col => {
          const th = document.createElement("th");
          th.textContent = col;
          tr.append(th);
        });
        thead.append(tr);
        const tbody = document.createElement("tbody");
        rows.forEach(row => {
          const tr = document.createElement("tr");
          row.forEach(cell => {
            const td = document.createElement("td");
            td.textContent = cell;
            tr.append(td);
          });
          tbody.append(tr);
        });
        table.append(thead, tbody);
        return table;
      }

      const fallback = document.createElement("pre");
      fallback.textContent = JSON.stringify(def, null, 2);
      return fallback;
    }

    function applyMessages(messages) {
      for (const msg of messages) {
        if (msg.beginRendering) {
          app.surfaceId = msg.beginRendering.surfaceId || app.surfaceId;
          app.rootId = msg.beginRendering.root || "root";
        }
        if (msg.surfaceUpdate) {
          app.surfaceId = msg.surfaceUpdate.surfaceId || app.surfaceId;
          app.components = new Map((msg.surfaceUpdate.components || []).map(c => [c.id, c]));
        }
        if (msg.dataModelUpdate) {
          app.surfaceId = msg.dataModelUpdate.surfaceId || app.surfaceId;
          app.dataModel = msg.dataModelUpdate.dataModel || app.dataModel;
        }
      }
      surfaceEl.replaceChildren(renderNode(app.rootId));
    }

    document.getElementById("reset").addEventListener("click", () => {
      app.surfaceId = "";
      app.rootId = "root";
      app.components = new Map();
      app.dataModel = {};
      surfaceEl.innerHTML = '<div class="empty">Generate a UI to start.</div>';
      log("ready");
    });

    generateBtn.addEventListener("click", async () => {
      setLoading(true);
      try {
        const res = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: promptEl.value }),
        });
        if (!res.ok) throw new Error(await res.text());
        const messages = await res.json();
        log(messages);
        applyMessages(messages);
      } catch (err) {
        log(String(err));
      } finally {
        setLoading(false);
      }
    });
  </script>
</body>
</html>
"""

A2UI_KEYS = {
    "beginRendering",
    "surfaceUpdate",
    "dataModelUpdate",
    "deleteSurface",
}
A2UI_MIME_TYPE = "application/json+a2ui"


class GenerateRequest(BaseModel):
    prompt: str


class ActionRequest(BaseModel):
    action: str
    context: dict = Field(default_factory=dict)
    currentDataModel: dict = Field(default_factory=dict)
    event: dict = Field(default_factory=dict)
    stateChange: dict = Field(default_factory=dict)
    surfaceId: str = ""


@app.get("/", response_class=HTMLResponse)
def interactive_page():
    return HTMLResponse(INTERACTIVE_HTML)


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


def _unwrap_a2ui_envelope(value: Any) -> Any:
    """
    A2A DataPart envelope나 data wrapper를 A2UI message로 정규화한다.
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

    if isinstance(value.get("data"), dict) and _is_a2ui_message(value["data"]):
        return _unwrap_a2ui_envelope(value["data"])

    return value


def _data_model_update_message(parsed: dict, surface_id: str = "") -> dict | None:
    if not isinstance(parsed.get("dataModel"), dict):
        return None

    data_model_update: dict[str, Any] = {
        "dataModel": parsed["dataModel"],
    }

    if surface_id:
        data_model_update["surfaceId"] = surface_id
    elif isinstance(parsed.get("surface"), dict) and parsed["surface"].get("surfaceId"):
        data_model_update["surfaceId"] = parsed["surface"]["surfaceId"]

    return {"dataModelUpdate": data_model_update}


def _document_to_messages(parsed: dict) -> list[dict]:
    surface = parsed.get("surface")
    components = parsed.get("components")

    if not isinstance(surface, dict) or not isinstance(components, list):
        return []

    surface_id = surface.get("surfaceId")
    if not surface_id:
        return []

    messages: list[dict] = [
        {
            "beginRendering": {
                "surfaceId": surface_id,
                "surfaceType": surface.get("surfaceType", "materialDynamic"),
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": surface_id,
                "components": components,
            }
        },
    ]

    if isinstance(parsed.get("dataModel"), dict):
        messages.append(
            {
                "dataModelUpdate": {
                    "surfaceId": surface_id,
                    "dataModel": parsed["dataModel"],
                }
            }
        )

    return messages


def normalize_a2ui_messages(parsed: Any, surface_id: str = "") -> list[dict]:
    """
    Gemini 출력 형태가 조금 달라도 최종적으로 A2UI message array로 통일.
    """
    parsed = _unwrap_a2ui_envelope(parsed)

    # 이미 A2UI message 하나인 경우
    if _is_a2ui_message(parsed):
        return [parsed]

    # 배열인 경우
    if isinstance(parsed, list):
        messages: list[dict] = []

        for item in parsed:
            item = _unwrap_a2ui_envelope(item)

            if _is_a2ui_message(item):
                messages.append(item)
                continue

            if isinstance(item, dict):
                data_model_update = _data_model_update_message(item, surface_id)
                if data_model_update:
                    messages.append(data_model_update)

        return messages

    # object wrapper인 경우
    if isinstance(parsed, dict):
        document_messages = _document_to_messages(parsed)
        if document_messages:
            return document_messages

        # {"messages": [...]}
        if isinstance(parsed.get("messages"), list):
            return normalize_a2ui_messages(parsed["messages"], surface_id)

        # {"a2ui": [...]}
        if isinstance(parsed.get("a2ui"), list):
            return normalize_a2ui_messages(parsed["a2ui"], surface_id)

        # {"data": {"surfaceUpdate": ...}}
        if _is_a2ui_message(parsed.get("data")):
            return [_unwrap_a2ui_envelope(parsed["data"])]

        # {"kind": "data", "data": {"surfaceUpdate": ...}}
        if parsed.get("kind") == "data" and _is_a2ui_message(parsed.get("data")):
            return [_unwrap_a2ui_envelope(parsed["data"])]

        # action 응답 호환: {"dataModel": {...}}
        data_model_update = _data_model_update_message(parsed, surface_id)
        if data_model_update:
            return [data_model_update]

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


def call_gemini(
    user_message: str,
    system_instruction: str = SYSTEM_PROMPT,
    surface_id: str = "",
) -> list[dict]:
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

    messages = normalize_a2ui_messages(parsed, surface_id)

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
            req.event,
            req.stateChange,
        )

        result = call_gemini(prompt, surface_id=req.surfaceId)
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
