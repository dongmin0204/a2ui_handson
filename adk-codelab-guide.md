# ADK + A2UI Codelab 실습 가이드

> GitHub Codespace에서 진행 · Gemini API Key 인증 방식
> 레포: `dongmin0204/a2ui_handson`

---

## 0단계: Codespace 열기

GitHub 레포에서 **Code → Codespaces → Create codespace on main** 클릭


---

## 1단계: 기존 파일 정리

기존 React/Express 코드를 삭제하고 ADK 구조로 전환합니다.

```bash
# 프론트엔드/서버 관련 파일 전부 삭제
rm -rf server/ src/ node_modules/
rm -f index.html package.json package-lock.json
rm -f tsconfig.json tsconfig.node.json vite.config.ts
```

---

## 2단계: 설정 파일 수정

### .gitignore 교체

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
.venv/
*.egg-info/

# env
.env

# IDE
.vscode/
.idea/
EOF
```

### .env.example 교체

```bash
cat > .env.example << 'EOF'
# ADK 환경변수
GOOGLE_GENAI_USE_VERTEXAI=False
GOOGLE_API_KEY=your-gemini-api-key-here
EOF
```

### .env 생성 및 API Key 입력

```bash
cp .env.example .env
```

`.env` 파일을 열어서 `your-gemini-api-key-here` 부분을 실제 API Key로 교체하세요.
API Key 발급: https://aistudio.google.com/app/apikey

### requirements.txt 생성

```bash
cat > requirements.txt << 'EOF'
google-adk
a2ui-agent-sdk
EOF
```

---

## 3단계: 의존성 설치

```bash
pip install -r requirements.txt
```

설치 완료 후 확인:

```bash
adk --version
```

---

## 4단계: 에이전트 패키지 생성 (텍스트 에이전트)

Codelab Step 3-4에 해당합니다.
일반 텍스트를 반환하는 기본 ADK 에이전트를 만듭니다.

### 폴더 및 __init__.py 생성

```bash
mkdir -p a2ui_agent
touch a2ui_agent/__init__.py
```

### a2ui_agent/resources.py 작성

도구(Tool) 함수와 모의 클라우드 리소스 데이터입니다.

```bash
cat > a2ui_agent/resources.py << 'PYEOF'
RESOURCES = [
    {
        "name": "auth-service",
        "type": "Cloud Run",
        "region": "us-west1",
        "status": "healthy",
        "cpu": "2 vCPU",
        "memory": "1 GiB",
        "instances": 3,
        "url": "https://auth-service-abc123.run.app",
        "last_deployed": "2026-04-18T14:22:00Z",
    },
    {
        "name": "events-db",
        "type": "Cloud SQL",
        "region": "us-east1",
        "status": "warning",
        "tier": "db-custom-8-32768",
        "storage": "500 GB SSD",
        "connections": 195,
        "version": "PostgreSQL 16",
        "issue": "Storage usage at 92%",
    },
    {
        "name": "analytics-pipeline",
        "type": "Cloud Run",
        "region": "us-west1",
        "status": "error",
        "cpu": "2 vCPU",
        "memory": "4 GiB",
        "instances": 0,
        "url": "https://analytics-pipeline-ghi789.run.app",
        "last_deployed": "2026-04-10T16:45:00Z",
        "issue": "CrashLoopBackOff: OOM killed",
    },
]


def get_resources() -> list[dict]:
    """Get all cloud resources in the current project.
    Returns a list of cloud infrastructure resources including their
    name, type, region, status, and type-specific details.
    Status is one of: healthy, warning, error. Resources with
    warning or error status include an 'issue' field describing
    the problem.
    """
    return RESOURCES
PYEOF
```

### a2ui_agent/agent.py 작성 (v1: 텍스트 에이전트)

```bash
cat > a2ui_agent/agent.py << 'PYEOF'
from google.adk.agents import Agent
from .resources import get_resources

root_agent = Agent(
    model="gemini-2.5-flash",
    name="cloud_dashboard",
    description="A cloud infrastructure assistant that reports on project resources.",
    instruction=(
        "You are a cloud infrastructure assistant. When users ask about their "
        "cloud resources, use the get_resources tool to fetch the current state. "
        "Summarize the results clearly in plain text."
    ),
    tools=[get_resources],
)
PYEOF
```

---

## 5단계: 텍스트 에이전트 테스트

### 환경변수 로드

```bash
export GOOGLE_GENAI_USE_VERTEXAI=False
export GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
```

### ADK 개발 UI 실행

```bash
adk web --port 8080 --allow_origins "*" --reload_agents
```

### 테스트 방법

1. Codespace **PORTS** 탭에서 8080 포트의 URL 클릭 (visibility가 Private면 Public으로 변경)
2. 드롭다운에서 `a2ui_agent` 선택
3. 아래 프롬프트를 입력:

```
What's running in my project?
```

```
Does anything need my attention?
```

✅ 텍스트로 리소스 정보가 잘 출력되면 성공!
→ Ctrl+C로 서버 종료 후 다음 단계로.

---

## 6단계: A2UI JSON 생성 에이전트로 업그레이드

Codelab Step 5-6에 해당합니다.
에이전트가 일반 텍스트 대신 A2UI JSON을 출력하도록 변경합니다.

### a2ui_agent/agent.py 덮어쓰기 (v2: A2UI JSON 출력)

```bash
cat > a2ui_agent/agent.py << 'PYEOF'
from google.adk.agents import Agent
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .resources import get_resources

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a cloud infrastructure assistant. When users ask about "
        "their cloud resources, use the get_resources tool to fetch the "
        "current state."
    ),
    workflow_description=(
        "Analyze the user's request and return structured UI when appropriate."
    ),
    ui_description=(
        "Use cards for resource summaries, rows and columns for comparisons, "
        "icons for status indicators, and buttons for drill-down actions. "
        "Do NOT use markdown formatting in text values. Use the usageHint "
        "property for heading levels instead. "
        "Respond ONLY with the A2UI JSON array. Do NOT include any text "
        "outside the JSON. Put all explanations into Text components."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="cloud_dashboard",
    description="A cloud infrastructure assistant that renders rich A2UI interfaces.",
    instruction=instruction,
    tools=[get_resources],
)
PYEOF
```

### JSON 출력 테스트

```bash
adk web --port 8080 --allow_origins "*" --reload_agents
```

브라우저에서 **+새 세션** 클릭 후:

```
What's running in my project?
```

✅ `beginRendering`, `surfaceUpdate`, `dataModelUpdate`가 포함된 JSON이 출력되면 성공!
→ Ctrl+C로 서버 종료 후 다음 단계로.

---

## 7단계: A2UI 렌더링 적용

Codelab Step 8-9에 해당합니다.
JSON을 실제 UI 컴포넌트로 렌더링하는 콜백을 추가합니다.

### a2ui_agent/a2ui_utils.py 작성

```bash
cat > a2ui_agent/a2ui_utils.py << 'PYEOF'
import json
import re
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse


def _wrap_a2ui_part(a2ui_message: dict) -> types.Part:
    """Wrap a single A2UI message for rendering in adk web."""
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
        inline_data=types.Blob(
            data=blob_data,
            mime_type="text/plain",
        )
    )


def a2ui_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse | None:
    """Convert A2UI JSON in text output to rendered components."""
    if not llm_response.content or not llm_response.content.parts:
        return None
    for part in llm_response.content.parts:
        if not part.text:
            continue
        text = part.text.strip()
        if not text:
            continue
        if not any(k in text for k in ("beginRendering", "surfaceUpdate", "dataModelUpdate")):
            continue
        # Strip markdown fences
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            if text.endswith("```"):
                text = text[:-3].strip()
        # Find where JSON starts (skip conversational prefix)
        json_start = None
        for i, ch in enumerate(text):
            if ch in ("[", "{"):
                json_start = i
                break
        if json_start is None:
            continue
        json_text = text[json_start:]
        # raw_decode parses JSON and ignores trailing text
        try:
            parsed, _ = json.JSONDecoder().raw_decode(json_text)
        except json.JSONDecodeError:
            # Handle concatenated JSON objects: {"a":1} {"b":2}
            try:
                fixed = "[" + re.sub(r'\}\s*\{', '},{', json_text) + "]"
                parsed, _ = json.JSONDecoder().raw_decode(fixed)
            except json.JSONDecodeError:
                continue
        if not isinstance(parsed, list):
            parsed = [parsed]
        a2ui_keys = {"beginRendering", "surfaceUpdate", "dataModelUpdate", "deleteSurface"}
        a2ui_messages = [msg for msg in parsed if isinstance(msg, dict) and any(k in msg for k in a2ui_keys)]
        if not a2ui_messages:
            continue
        new_parts = [_wrap_a2ui_part(msg) for msg in a2ui_messages]
        return LlmResponse(
            content=types.Content(role="model", parts=new_parts),
            custom_metadata={"a2a:response": "true"},
        )
    return None
PYEOF
```

### a2ui_agent/agent.py 덮어쓰기 (v3: 렌더링 콜백 연결)

```bash
cat > a2ui_agent/agent.py << 'PYEOF'
from google.adk.agents import Agent
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .resources import get_resources
from .a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a cloud infrastructure assistant. When users ask about "
        "their cloud resources, use the get_resources tool to fetch the "
        "current state."
    ),
    workflow_description=(
        "Analyze the user's request and return structured UI when appropriate."
    ),
    ui_description=(
        "Use cards for resource summaries, rows and columns for comparisons, "
        "icons for status indicators, and buttons for drill-down actions. "
        "Do NOT use markdown formatting in text values. Use the usageHint "
        "property for heading levels instead. "
        "Respond ONLY with the A2UI JSON array. Do NOT include any text "
        "outside the JSON. Put all explanations into Text components."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="cloud_dashboard",
    description="A cloud infrastructure assistant that renders rich A2UI interfaces.",
    instruction=instruction,
    tools=[get_resources],
    after_model_callback=a2ui_callback,
)
PYEOF
```

---

## 8단계: 최종 테스트

```bash
adk web --port 8080 --allow_origins "*" --reload_agents
```

브라우저 탭을 **새로고침**하고, `a2ui_agent` 선택 → **+새 세션** 후 테스트:

```
What's running in my project?
```

```
Does anything need my attention?
```

```
I need to deploy a new service
```

✅ 카드, 아이콘, 버튼이 포함된 **리치 UI**가 렌더링되면 완료!

> A2UI 컴포넌트가 렌더링되지 않고 JSON만 보이면 브라우저를 강제 새로고침(Ctrl+Shift+R)하세요.

---

## 9단계: Git 커밋

```bash
git add -A
git commit -m "refactor: convert to ADK + A2UI agent (Codelab structure)"
git push
```

---

## 최종 폴더 구조

```
a2ui_handson/
├── a2ui_agent/
│   ├── __init__.py        # 빈 파일 (패키지 인식용)
│   ├── resources.py       # 모의 데이터 + get_resources 도구
│   ├── agent.py           # ADK Agent + A2UI 렌더링
│   └── a2ui_utils.py      # A2UI JSON → adk web 렌더링 변환
├── examples/              # 기존 프롬프트 가이드 (선택 유지)
├── .env.example
├── .env                   # git에 안 올라감
├── .gitignore
├── requirements.txt
└── README.md              # 내용 업데이트 필요
```

---

## 트러블슈팅

| 증상 | 해결 |
|---|---|
| `adk: command not found` | `export PATH="$HOME/.local/bin:$PATH"` 실행 |
| `gemini-2.5-flash` 모델 에러 | `gemini-2.0-flash`로 변경 후 재시도 |
| A2UI가 렌더링 안 되고 JSON만 보임 | 브라우저 강제 새로고침 (Ctrl+Shift+R) |
| `ModuleNotFoundError: a2ui` | `pip install -r requirements.txt` 재실행 |
| 포트 8080 접속 불가 | PORTS 탭에서 visibility를 Public으로 변경 |
