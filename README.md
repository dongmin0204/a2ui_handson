# ADK + A2UI 핸즈온 워크샵

> AI 에이전트가 텍스트 대신 **리치 UI 컴포넌트**를 생성하는 과정을 단계별로 체험합니다.

```
"내 클라우드 리소스 상태 보여줘"  →  카드, 아이콘, 테이블이 포함된 대시보드 UI
```

---

## 이 워크샵에서 만드는 것

| 단계 | 에이전트 버전 | 출력 형태 |
|:---:|---|---|
| **Step 1** | 텍스트 에이전트 | 일반 텍스트 응답 |
| **Step 2** | A2UI JSON 에이전트 | A2UI JSON 출력 |
| **Step 3** | A2UI 렌더링 에이전트 | 리치 UI 컴포넌트 렌더링 |

최종 결과물: Gemini가 사용자 요청을 분석하고, A2UI 프로토콜에 맞는 JSON을 생성하면, ADK Web UI에서 카드/테이블/체크박스/버튼 등으로 렌더링되는 **AI 에이전트**

---

## 사전 준비

- **Gemini API Key** — [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급
- **GitHub 계정**

---

## 0단계: Codespace 열기 및 환경 설정

### Codespace 시작하기

1. 이 레포의 **Code** 버튼 클릭
2. **Codespaces** 탭 선택
3. **Create codespace on main** 클릭

> Codespace가 열리면 Python 환경과 의존성(`google-adk`, `a2ui-agent-sdk`)이 자동으로 설치됩니다.

설치 완료 확인:

```bash
adk --version
```

> `adk: command not found`가 나오면 `pip install -r requirements.txt`를 수동 실행하세요.

### API Key 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어서 발급받은 API Key를 입력합니다:

```
GOOGLE_GENAI_USE_VERTEXAI=False
GOOGLE_API_KEY=여기에-발급받은-키-입력
```

<details>
<summary><b>로컬 환경에서 실행하기 (Codespace 없이)</b></summary>

```bash
# 코드 받기
git clone https://github.com/dongmin0204/a2ui_handson.git
cd a2ui_handson

# 환경 변수 설정
cp .env.example .env
# .env 파일에 GOOGLE_API_KEY 입력

# 의존성 설치
pip install -r requirements.txt
```

이후 단계는 동일합니다. 브라우저에서 `http://localhost:8080`으로 접속하세요.
</details>

---

## 1단계: 텍스트 에이전트 만들기

> 가장 기본적인 ADK 에이전트를 만듭니다. 도구(Tool)를 호출해서 클라우드 리소스 정보를 가져오고, **일반 텍스트**로 응답합니다.

### 폴더 구조 생성

```bash
mkdir -p a2ui_agent
touch a2ui_agent/__init__.py
```

### 1-1. 모의 데이터 도구 작성 — `a2ui_agent/resources.py`

에이전트가 호출할 도구(Tool) 함수와 모의 클라우드 리소스 데이터입니다.

```python
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
    """Get all cloud resources in the current project."""
    return RESOURCES
```

3개의 리소스가 각각 `healthy`, `warning`, `error` 상태를 가지고 있어서 다양한 UI 표현을 테스트할 수 있습니다.

### 1-2. 에이전트 정의 — `a2ui_agent/agent.py` (v1)

```python
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
```

### 1-3. 실행 및 테스트

```bash
./run.sh
```

또는 직접 실행:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=False
export GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
adk web --port 8080 --allow_origins "*" --reload_agents
```

### Codespace에서 브라우저 접속하기

1. 하단 **PORTS** 탭 클릭
2. 포트 `8080`의 주소(🌐 아이콘) 클릭 → 브라우저가 열립니다
3. 만약 접속이 안 되면 visibility를 **Public**으로 변경

### 테스트

1. 드롭다운에서 `a2ui_agent` 선택
2. 프롬프트 입력:

```
What's running in my project?
```

```
Does anything need my attention?
```

**확인**: 텍스트로 리소스 정보가 출력되면 성공입니다.

`Ctrl+C`로 서버를 종료하고 다음 단계로 진행합니다.

---

## 2단계: A2UI JSON 생성 에이전트로 업그레이드

> 에이전트가 일반 텍스트 대신 **A2UI JSON**을 출력하도록 변경합니다. A2UI 스키마 매니저가 시스템 프롬프트에 컴포넌트 스키마와 예시를 자동으로 주입합니다.

### 2-1. `a2ui_agent/agent.py` 덮어쓰기 (v2)

```python
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
```

**핵심 변경점**:
- `A2uiSchemaManager`가 A2UI 컴포넌트 스키마를 시스템 프롬프트에 주입
- `generate_system_prompt()`로 역할, 워크플로우, UI 스타일을 정의
- Gemini가 이제 `beginRendering`, `surfaceUpdate`, `dataModelUpdate` 등의 A2UI 메시지를 JSON으로 출력

### 2-2. 테스트

```bash
adk web --port 8080 --allow_origins "*" --reload_agents
```

브라우저에서 **+새 세션** 클릭 후 동일한 프롬프트를 입력합니다.

**확인**: `beginRendering`, `surfaceUpdate`, `dataModelUpdate`가 포함된 JSON이 출력되면 성공입니다.

`Ctrl+C`로 서버를 종료하고 다음 단계로 진행합니다.

---

## 3단계: A2UI 렌더링 적용

> JSON 출력을 실제 UI 컴포넌트로 렌더링하는 **콜백(callback)**을 추가합니다. 이 콜백이 Gemini의 텍스트 출력에서 A2UI JSON을 파싱하고, ADK Web UI가 이해할 수 있는 형태로 변환합니다.

### 3-1. 렌더링 유틸리티 작성 — `a2ui_agent/a2ui_utils.py`

```python
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
    """Convert A2UI JSON in text output to rendered components."""
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
```

**콜백 동작 흐름**:

```
Gemini 응답 (텍스트)
  → a2ui_callback 호출
    → A2UI JSON 존재 여부 확인 (has_a2ui_parts)
    → 연속된 JSON 객체를 배열로 수정 (_fix_consecutive_json)
    → A2UI 파서로 파싱 (parse_response)
    → ADK Web이 렌더링할 수 있는 Part로 변환 (_wrap_a2ui_part)
  → 리치 UI 렌더링
```

### 3-2. `a2ui_agent/agent.py` 덮어쓰기 (v3: 최종)

```python
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
```

**v2 대비 변경점**: `after_model_callback=a2ui_callback` 한 줄 추가로 JSON이 리치 UI로 렌더링됩니다.

---

## 4단계: 최종 테스트

```bash
./run.sh
```

Codespace **PORTS** 탭에서 8080 포트 주소를 클릭해 브라우저를 엽니다.

`a2ui_agent` 선택 → **+새 세션** 후:

```
What's running in my project?
```

```
Does anything need my attention?
```

```
오늘의 할 일 체크리스트 만들어줘
```

```
I need to deploy a new service
```

**확인**: 카드, 아이콘, 버튼이 포함된 리치 UI가 렌더링되면 완료입니다.

> A2UI 컴포넌트가 렌더링되지 않고 JSON만 보이면 브라우저를 강제 새로고침(`Ctrl+Shift+R`)하세요.

---

## 프로젝트 구조

```
a2ui_handson/
├── a2ui_agent/                 # 메인 에이전트 패키지
│   ├── __init__.py             # 패키지 인식용
│   ├── agent.py                # ADK Agent 정의 + A2UI 시스템 프롬프트
│   ├── resources.py            # 모의 클라우드 리소스 데이터 + get_resources 도구
│   └── a2ui_utils.py           # A2UI JSON → ADK Web 렌더링 변환 콜백
├── agent/                      # 레거시 에이전트 (참고용)
│   ├── prompts.py              # A2UI v0.9 시스템 프롬프트
│   └── ...
├── examples/                   # A2UI 프롬프트 가이드 및 예제 JSON
│   ├── prompt-guide.md         # 난이도별 프롬프트 예시
│   ├── expense-tracker.json    # 지출 관리 예제
│   └── study-planner.json      # 학습 계획 예제
├── .env.example                # 환경 변수 템플릿
├── .gitignore
├── requirements.txt            # google-adk, a2ui-agent-sdk
├── run.sh                      # 원클릭 실행 스크립트
└── README.md
```

---

## 핵심 개념

### ADK (Agent Development Kit)

Google의 AI 에이전트 개발 프레임워크입니다. `Agent` 클래스에 모델, 지시문, 도구를 정의하면 대화형 에이전트가 만들어집니다.

```python
Agent(
    model="gemini-2.5-flash",       # 사용할 LLM
    name="cloud_dashboard",         # 에이전트 이름
    instruction="...",              # 시스템 프롬프트
    tools=[get_resources],          # 호출 가능한 도구 함수
    after_model_callback=callback,  # 응답 후처리 콜백
)
```

### A2UI (AI-to-UI)

AI가 UI 구조(JSON)를 생성하면 프론트엔드가 실제 화면으로 렌더링하는 프로토콜입니다.

| A2UI 메시지 | 역할 |
|---|---|
| `beginRendering` | 새로운 Surface(화면) 초기화 |
| `surfaceUpdate` | 컴포넌트 트리 전달 |
| `dataModelUpdate` | 화면에 표시할 데이터 전달 |
| `deleteSurface` | Surface 제거 |

### 데이터 흐름

```
사용자 입력
  → Gemini (gemini-2.5-flash)
    → get_resources() 도구 호출
    → A2UI JSON 생성
  → a2ui_callback (후처리)
    → A2UI 파서로 파싱
    → ADK Web 렌더링 포맷으로 변환
  → 브라우저에 리치 UI 렌더링
```

---

## 보너스 챌린지

### 시스템 프롬프트 커스터마이징

`a2ui_agent/agent.py`의 `ui_description`을 수정해서 다른 UI 스타일을 지시해보세요:

```python
ui_description=(
    "Use a dark theme with neon accent colors. "
    "Prefer DataTable for all list-type data. "
    "Add status icons: check_circle for healthy, warning for warning, error for error."
),
```

### 새로운 도구 추가

`a2ui_agent/resources.py`에 새 함수를 추가하고 `agent.py`의 `tools` 리스트에 등록하세요:

```python
def get_billing() -> dict:
    """Get current month billing summary."""
    return {"total": "$1,234.56", "forecast": "$1,890.00", "budget": "$2,000.00"}
```

### 다른 모델 사용

`agent.py`에서 모델을 변경할 수 있습니다:

```python
root_agent = Agent(
    model="gemini-2.5-pro",  # 더 강력한 모델
    ...
)
```

---

## 트러블슈팅

| 증상 | 해결 |
|---|---|
| `adk: command not found` | `export PATH="$HOME/.local/bin:$PATH"` 실행 |
| `gemini-2.5-flash` 모델 에러 | `gemini-2.0-flash`로 변경 후 재시도 |
| A2UI가 렌더링 안 되고 JSON만 보임 | 브라우저 강제 새로고침 (`Ctrl+Shift+R`) |
| `ModuleNotFoundError: a2ui` | `pip install -r requirements.txt` 재실행 |
| 포트 8080 접속 불가 (Codespace) | PORTS 탭에서 visibility를 Public으로 변경 |
| API Key 에러 | `.env` 파일에 유효한 `GOOGLE_API_KEY` 확인 |

---

## 참고 자료

- [A2UI 공식 문서](https://a2ui.org)
- [A2UI Composer](https://a2ui-composer.ag-ui.com) — 브라우저에서 A2UI 컴포넌트를 실시간으로 생성/미리보기
- [Google ADK 문서](https://google.github.io/adk-docs/)
- [Gemini API](https://aistudio.google.com)
- [A2UI 프롬프트 가이드](examples/prompt-guide.md) — 난이도별 프롬프트 예시

---

## License

MIT
