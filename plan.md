# ADK + A2UI 핸즈온: 크립토 대시보드

> **모델**: Claude (AnthropicLlm) via Mindlogic AI Gateway
> **데이터**: CoinGecko API (키 불필요)
> **구조**: build-with-agent 스타일 level1/level2/level3/level4

---

## 폴더 구조

```
buildwithai_handson/
├── .devcontainer/devcontainer.json
├── .env.example
├── .gitignore
├── requirements.txt          # google-adk, a2ui-agent-sdk, anthropic
├── README.md
│
├── level1/                   # 🟢 기본 에이전트 (도구 없음)
│   ├── handson/
│   │   └── crypto_dashboard/
│   │       ├── __init__.py
│   │       └── agent.py          # TODO 스켈레톤
│   └── solution/
│       └── crypto_dashboard/
│           ├── __init__.py
│           └── agent.py          # 완성 코드
│
├── level2/                   # 🟡 Tool Calling + 실시간 데이터
│   ├── handson/
│   │   └── crypto_dashboard/
│   │       ├── __init__.py
│   │       ├── agent.py          # TODO
│   │       └── market_data.py    # TODO (API 호출 미구현)
│   └── solution/
│       └── crypto_dashboard/
│           ├── __init__.py
│           ├── agent.py
│           └── market_data.py    # CoinGecko API 완성
│
├── level3/                   # 🔴 A2UI 대시보드 렌더링
│   ├── handson/
│   │   └── crypto_dashboard/
│   │       ├── __init__.py
│   │       ├── agent.py          # TODO (A2UI + callback)
│   │       ├── market_data.py
│   │       └── a2ui_utils.py     # TODO (DataPart 래핑)
│   └── solution/
│       └── crypto_dashboard/
│           ├── __init__.py
│           ├── agent.py
│           ├── market_data.py
│           └── a2ui_utils.py
│
└── level4/                   # 🟣 멀티 에이전트 + 라우팅 + A2A
    ├── handson/
    │   └── crypto_dashboard/
    │       ├── __init__.py
    │       ├── agent.py          # TODO (Workflow + edges + 라우팅)
    │       ├── market_data.py
    │       ├── a2ui_utils.py
    │       └── a2a_server.py     # TODO (to_a2a)
    └── solution/
        └── crypto_dashboard/
            ├── __init__.py
            ├── agent.py          # Workflow + classify_intent + LlmAgent nodes
            ├── market_data.py
            ├── a2ui_utils.py
            └── a2a_server.py     # to_a2a() A2A 서버
```

### 실행 방법

```bash
# Level 1 정답 실행
adk web level1/solution/ --port 8080 --allow_origins "*"

# Level 2 실습 코드로 작업
adk web level2/handson/ --port 8080 --allow_origins "*" --reload_agents

# Level 4 A2A 서버 (별도 터미널)
uvicorn level4.solution.crypto_dashboard.a2a_server:app --port 9000
```

---

## Level 1: "Hello, Agent" — 에이전트 첫 만남 (15분)

### 핵심 질문

> "비트코인 지금 얼마야?" 라고 물으면 에이전트가 정확히 대답할 수 있을까?

### 배우는 것


| 개념           | 설명                                   |
| ------------ | ------------------------------------ |
| Agent        | ADK의 핵심 단위. model + instruction으로 구성 |
| AnthropicLlm | Claude 모델을 ADK에서 사용하는 래퍼             |
| instruction  | 에이전트의 역할과 행동 규칙을 정의하는 시스템 프롬프트       |
| `adk web`    | 에이전트를 브라우저에서 테스트하는 개발 서버             |


### agent.py (solution)

```python
from google.adk.agents import Agent
from google.adk.models.anthropic_llm import AnthropicLlm

root_agent = Agent(
    model=AnthropicLlm(model="claude-sonnet-4-5-20250929"),
    name="crypto_dashboard",
    description="A cryptocurrency market assistant.",
    instruction=(
        "You are a crypto market assistant. "
        "Users will ask about cryptocurrency prices and market trends. "
        "Answer based on your knowledge. "
        "Be honest when you don't have real-time data."
    ),
)
```

### 테스트 프롬프트

```
비트코인 지금 얼마야?
```

### 기대 결과

에이전트가 **"실시간 데이터에 접근할 수 없어서 정확한 가격을 알려드리기 어렵습니다"** 류의 응답을 함.

→ **핵심 깨달음**: 모델만으로는 실시간 정보를 줄 수 없다. **도구(Tool)가 필요하다!**

---

## Level 2: Tool Calling — 실시간 데이터 연동 (20분)

### 핵심 질문

> 에이전트에게 "도구"를 주면 실시간 데이터를 가져올 수 있을까?

### 배우는 것


| 개념               | 설명                                     |
| ---------------- | -------------------------------------- |
| Tool (도구)        | Python 함수를 에이전트에 등록 → LLM이 필요할 때 자동 호출 |
| Function Calling | LLM이 "이 함수를 이 인자로 호출해줘" 라고 요청하는 메커니즘   |
| docstring의 역할    | 함수의 docstring이 LLM에게 도구 설명으로 전달됨       |
| 외부 API 연동        | CoinGecko API로 실시간 시세 조회               |


### Level 1 → Level 2 변경점


| 파일               | 변경                                       |
| ---------------- | ---------------------------------------- |
| `market_data.py` | **신규** — CoinGecko API 호출 + mock 폴백      |
| `agent.py`       | `tools=[get_prices]` 추가 + instruction 강화 |


### market_data.py 핵심

```python
def get_prices() -> list[dict]:
    """Get current cryptocurrency market data for top 5 coins.
    Returns a list of coins, each with:
    - symbol, name, price_usd, change_24h_pct,
    - market_cap_usd, volume_24h_usd, high_24h, low_24h
    """
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=..."
        # CoinGecko API 호출
        ...
    except:
        return MOCK_MARKET  # API 실패 시 모의 데이터
```

**핵심 포인트**: docstring이 곧 LLM에게 전달되는 도구 설명. 잘 써야 모델이 도구를 올바르게 사용함.

### agent.py (solution)

```python
root_agent = Agent(
    model=AnthropicLlm(model="claude-sonnet-4-5-20250929"),
    name="crypto_dashboard",
    description="A cryptocurrency market assistant with real-time price data.",
    instruction=(
        "You are a crypto market assistant with access to real-time market data. "
        "When users ask about cryptocurrency prices, trends, or market conditions, "
        "ALWAYS use the get_prices tool first to fetch current data. "
        "Never guess prices — always call the tool. ..."
    ),
    tools=[get_prices],  # ← 이 한 줄이 핵심!
)
```

### 테스트 프롬프트

```
비트코인 지금 얼마야?
```

```
Which coins are up today?
```

```
이더리움이랑 솔라나 비교해줘
```

### 기대 결과

에이전트가 `get_prices` 도구를 호출하고, **실시간 가격 데이터**를 포함한 텍스트 응답을 반환.
adk web의 **Trace 탭**에서 도구 호출 과정을 확인할 수 있음:

```
1. 사용자: "비트코인 지금 얼마야?"
2. Claude: get_prices() 호출 결정
3. ADK: get_prices() 실행 → CoinGecko API 호출
4. Claude: 결과를 받아 자연어로 요약
```

→ **핵심 깨달음**: 함수 하나 등록으로 에이전트가 외부 세계와 상호작용할 수 있다!

### 참고: 멀티 에이전트 패턴 (심화)

Level 2에서 배운 도구 개념을 확장하면 여러 에이전트를 조합할 수 있음:


| 패턴        | 클래스               | 용도                    |
| --------- | ----------------- | --------------------- |
| 순차 실행     | `SequentialAgent` | A 에이전트 결과 → B 에이전트 입력 |
| 병렬 실행     | `ParallelAgent`   | 여러 에이전트를 동시에 실행       |
| 반복 실행     | `LoopAgent`       | 조건 충족까지 반복            |
| 에이전트를 도구로 | `AgentTool`       | 에이전트를 다른 에이전트의 도구로 래핑 |


→ Level 4에서 직접 체험

---

## Level 3: A2UI 대시보드 — 리치 UI 렌더링 (20분)

### 핵심 질문

> 텍스트 대신 카드, 아이콘, 대시보드 UI로 보여줄 수 있을까?

### 배우는 것


| 개념                   | 설명                               |
| -------------------- | -------------------------------- |
| A2UI 프로토콜            | LLM이 JSON으로 UI를 기술 → 프론트엔드가 렌더링  |
| A2uiSchemaManager    | 시스템 프롬프트에 A2UI 컴포넌트 스키마를 자동 주입   |
| after_model_callback | 모델 응답을 가로채서 변환하는 콜백              |
| A2A DataPart         | ADK Web에서 A2UI를 렌더링하는 래핑 형식      |
| 데이터 바인딩              | `dataModelUpdate`로 UI에 동적 데이터 연결 |


### Level 2 → Level 3 변경점


| 파일               | 변경                                          |
| ---------------- | ------------------------------------------- |
| `market_data.py` | 변경 없음 (Level 2 그대로)                         |
| `a2ui_utils.py`  | **신규** — JSON→DataPart 변환 콜백                |
| `agent.py`       | A2uiSchemaManager + after_model_callback 추가 |


### A2UI 3단계 메시지 흐름 (데이터 바인딩)

```
① beginRendering    → Surface(대시보드 영역) 초기화
② surfaceUpdate     → 컴포넌트 트리 전달 (Card, Text, Icon, Row, Column)
③ dataModelUpdate   → 동적 데이터 바인딩 (가격, 변동률 등)
```

예시 JSON:

```json
[
  {
    "beginRendering": {
      "surfaceId": "crypto-dashboard",
      "surfaceType": "card"
    }
  },
  {
    "surfaceUpdate": {
      "surfaceId": "crypto-dashboard",
      "components": [
        {"type": "Text", "text": "Crypto Market Dashboard", "usageHint": "heading1"},
        {"type": "Row", "children": [
          {"type": "Card", "children": [
            {"type": "Text", "text": "Bitcoin (BTC)", "usageHint": "heading2"},
            {"type": "Text", "text": "$107,250.42"},
            {"type": "Icon", "icon": "trending_up", "color": "green"},
            {"type": "Text", "text": "+2.35%"}
          ]},
          {"type": "Card", "children": [
            {"type": "Text", "text": "Ethereum (ETH)", "usageHint": "heading2"},
            {"type": "Text", "text": "$2,534.18"},
            {"type": "Icon", "icon": "trending_down", "color": "red"},
            {"type": "Text", "text": "-1.28%"}
          ]}
        ]}
      ]
    }
  },
  {
    "dataModelUpdate": {
      "surfaceId": "crypto-dashboard",
      "data": {
        "last_updated": "2026-05-20T16:30:00Z",
        "market_sentiment": "bullish"
      }
    }
  }
]
```

### a2ui_utils.py 핵심 — DataPart 래핑

```python
def _wrap_a2ui_part(a2ui_message: dict) -> types.Part:
    datapart_json = json.dumps({
        "kind": "data",
        "metadata": {"mimeType": "application/json+a2ui"},  # ← ADK Web이 인식하는 키
        "data": a2ui_message,
    })
    blob_data = (
        b"<a2a_datapart_json>"        # ← A2A 프로토콜 태그
        + datapart_json.encode("utf-8")
        + b"</a2a_datapart_json>"
    )
    return types.Part(inline_data=types.Blob(data=blob_data, mime_type="text/plain"))
```

### agent.py (solution) — Level 3

```python
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description="...",
    workflow_description="...",
    ui_description=(
        "Build a dashboard layout: "
        "- Card for each coin with price, change %, trend icon "
        "- Icon: trending_up (green) for gains, trending_down (red) for losses "
        "- Row/Column for grid layout ..."
    ),
    include_schema=True,     # A2UI JSON 스키마 포함
    include_examples=True,   # 예제 JSON 포함
)

root_agent = Agent(
    ...
    instruction=instruction,
    tools=[get_prices],
    after_model_callback=a2ui_callback,  # ← JSON→리치UI 변환
)
```

### 테스트 프롬프트

```
Show me crypto prices
```

```
비트코인이랑 이더리움 비교해줘
```

### 기대 결과

텍스트 대신 **카드, 아이콘(▲▼), 가격 정보**가 포함된 리치 UI 대시보드가 렌더링됨.

→ **핵심 깨달음**: 같은 도구, 같은 데이터인데 출력 형태만 바꿔서 대시보드가 됨!

### 데이터 바인딩 체험

1. "Show me crypto prices" → 대시보드 렌더링
2. (잠시 후) "Refresh prices" → **새 세션에서** 다시 요청
3. CoinGecko 실시간 데이터가 달라진 것을 확인
4. `dataModelUpdate`의 데이터가 UI에 반영되는 과정 이해

---

## Level 4: Workflow 그래프 + 라우팅 + A2A (20분)

### 핵심 질문

> LLM에게 라우팅을 맡기지 않고, 코드로 실행 흐름을 제어하면 어떻게 될까?

### 배우는 것


| 개념                 | 설명                                                          |
| ------------------ | ----------------------------------------------------------- |
| Workflow           | ADK 2.0의 그래프 오케스트레이터. `edges`로 노드 간 연결 정의                   |
| Function Node      | Python 함수를 워크플로우 노드로 사용. 라우팅, 전처리 등                         |
| Dict Routing       | `(node, {"route_a": target_a, "route_b": target_b})` 조건부 분기 |
| LlmAgent Node      | LLM 에이전트를 워크플로우 노드로 사용                                      |
| output_key + {var} | 에이전트 결과를 `state`에 저장 → 다음 노드가 템플릿으로 읽음                      |
| A2A                | `to_a2a()`로 Workflow 전체를 독립 HTTP 서비스로 노출                    |


### Level 3 → Level 4 변경점


| 파일               | 변경                                                               |
| ---------------- | ---------------------------------------------------------------- |
| `agent.py`       | `Agent` → `Workflow` + `LlmAgent` + function node + edges 기반 그래프 |
| `a2a_server.py`  | **신규** — `to_a2a()`로 Workflow를 A2A 서버로 노출                        |
| `market_data.py` | 변경 없음                                                            |
| `a2ui_utils.py`  | 변경 없음                                                            |


### 아키텍처: Workflow 그래프

```
                    ┌──────────────────┐
                    │      START       │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  classify_intent │  ← Python 함수 (Function Node)
                    │  (의도 분류)      │
                    └────────┬─────────┘
                             │ Event(route=...)
               ┌─────────────┴─────────────┐
               │ "text"                     │ "dashboard"
               ▼                            ▼
   ┌───────────────────┐       ┌───────────────────┐
   │   quick_analyst   │       │  pipeline_analyst  │ ← LlmAgent Node
   │   (LlmAgent)      │       │  tools=[get_prices] │
   │                   │       │  output_key=        │
   │ tools=[get_prices]│       │   "market_analysis" │
   │ → 텍스트 응답     │       └────────┬────────────┘
   │   (terminal)      │                │ state 전달
   └───────────────────┘       ┌────────▼────────────┐
                               │ pipeline_renderer   │ ← LlmAgent Node
                               │ {market_analysis?}  │
                               │ after_model_callback │
                               │ → A2UI 대시보드      │
                               │   (terminal)        │
                               └─────────────────────┘
```

### Level 3과 Level 4의 핵심 차이


|         | Level 3           | Level 4                                |
| ------- | ----------------- | -------------------------------------- |
| 오케스트레이션 | `Agent` (LLM이 판단) | `Workflow` (코드가 제어)                    |
| 라우팅     | 없음 (단일 에이전트)      | `classify_intent` 함수가 결정론적으로 분기        |
| 데이터 전달  | 한 에이전트가 전부 처리     | `output_key` → `{var}` 템플릿으로 에이전트 간 전달 |
| 노드 유형   | LLM만              | **함수 노드 + LLM 노드** 혼합                  |


### 핵심 패턴 3가지

**1. Function Node — 결정론적 라우팅**

```python
from google.adk import Workflow, Event

def classify_intent(node_input: str):
    """Python 함수가 워크플로우 노드가 됨. LLM 호출 없이 즉시 분기."""
    dashboard_keywords = ["dashboard", "show", "대시보드", "보여"]
    if any(k in node_input.lower() for k in dashboard_keywords):
        return Event(output=node_input, route="dashboard")
    return Event(output=node_input, route="text")
```

LLM에게 라우팅을 맡기면 비결정적 — 같은 입력에 다른 결과가 나올 수 있음.
Function Node는 Python 코드가 분기하므로 **100% 결정론적**.

**2. edges — 그래프 정의**

```python
root_agent = Workflow(
    name="crypto_dashboard",
    edges=[
        ("START", classify_intent),              # 시작 → 분류
        (classify_intent, {                      # 조건부 분기
            "text": quick_analyst,               #   "text" → 텍스트 응답
            "dashboard": pipeline_analyst,       #   "dashboard" → 대시보드
        }),
        (pipeline_analyst, pipeline_renderer),   # 분석 → 렌더링 (순차)
    ],
)
```

`edges` 한 곳에서 전체 실행 흐름을 한눈에 볼 수 있음. 프롬프트에 흩어져 있던 흐름 제어가 코드로 집중됨.

**3. State-based Data Flow (output_key + {var})**

```python
# analyst가 결과를 state에 저장
pipeline_analyst = LlmAgent(
    ...,
    output_key="market_analysis",  # ← state["market_analysis"]에 저장
)

# renderer가 instruction에서 state를 읽음
dashboard_instruction = schema_manager.generate_system_prompt(
    workflow_description=(
        "=== Market Analysis ===\n"
        "{market_analysis?}\n"     # ← state에서 자동 주입!
        "=== End ==="
    ),
)
```

### agent.py (solution) — Level 4

```python
from google.adk import Workflow, Event
from google.adk.agents.llm_agent import LlmAgent

model = AnthropicLlm(model="claude-sonnet-4-5-20250929")

# ── Function Node: 의도 분류 ──
def classify_intent(node_input: str):
    dashboard_keywords = ["dashboard", "show", "대시보드", "보여"]
    if any(k in node_input.lower() for k in dashboard_keywords):
        return Event(output=node_input, route="dashboard")
    return Event(output=node_input, route="text")

# ── LLM Node: 빠른 텍스트 응답 ──
quick_analyst = LlmAgent(
    name="quick_analyst", model=model,
    instruction="...ALWAYS call get_prices first...",
    tools=[get_prices],
)

# ── LLM Node: 파이프라인 분석가 ──
pipeline_analyst = LlmAgent(
    name="pipeline_analyst", model=model,
    instruction="...structured analysis...",
    tools=[get_prices],
    output_key="market_analysis",          # state에 저장
)

# ── LLM Node: 대시보드 렌더러 ──
pipeline_renderer = LlmAgent(
    name="pipeline_renderer", model=model,
    instruction=dashboard_instruction,     # {market_analysis?} 포함
    after_model_callback=a2ui_callback,
)

# ── Workflow Graph ──
root_agent = Workflow(
    name="crypto_dashboard",
    edges=[
        ("START", classify_intent),
        (classify_intent, {
            "text": quick_analyst,
            "dashboard": pipeline_analyst,
        }),
        (pipeline_analyst, pipeline_renderer),
    ],
)
```

### a2a_server.py — Workflow를 HTTP 서비스로

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from .agent import root_agent    # Workflow 전체를 노출

app = to_a2a(
    root_agent,                  # Workflow도 to_a2a 가능
    host="localhost",
    port=9000,
    protocol="http",
)
```

```bash
uvicorn level4.solution.crypto_dashboard.a2a_server:app --port 9000
```

### 테스트 프롬프트

```
비트코인 지금 얼마야?
```

→ classify_intent → route="text" → **quick_analyst** → 텍스트 응답

```
Show me a crypto dashboard
```

→ classify_intent → route="dashboard" → **pipeline_analyst** → **pipeline_renderer** → A2UI 대시보드

```
이더리움이랑 솔라나 비교해줘, 대시보드로
```

→ classify_intent → route="dashboard" → 분석 → A2UI 카드 렌더링

```
Which coins are up today?
```

→ classify_intent → route="text" → **quick_analyst** → 텍스트 상승 코인 목록

### 기대 결과

- **Trace 탭**에서 Workflow 실행 경로 확인: `classify_intent → quick_analyst` 또는 `classify_intent → pipeline_analyst → pipeline_renderer`
- 같은 질문이라도 **"dashboard"/"보여"** 키워드 유무로 결정론적 분기
- `output_key`로 state에 저장된 `market_analysis`가 renderer의 instruction에 주입되는 과정 확인
- A2A 서버로 Workflow 전체를 외부 서비스로 노출

→ **핵심 깨달음**: `Workflow` + `edges`로 실행 흐름을 코드로 제어하면, LLM의 불확실성 없이 결정론적 파이프라인을 만들 수 있다!

---

## 데이터 흐름 (전체)

```
Level 1:  사용자 → Agent(Claude) → 텍스트 (훈련 데이터만)
                ❌ 실시간 데이터 없음

Level 2:  사용자 → Agent(Claude) → get_prices() → CoinGecko API
                → Claude가 텍스트로 요약

Level 3:  사용자 → Agent(Claude) → get_prices() → CoinGecko API
                → Claude가 A2UI JSON 생성
                → a2ui_callback → DataPart 래핑
                → ADK Web → 리치 UI 렌더링

Level 4:  사용자 → Workflow(crypto_dashboard)
                  → classify_intent (Function Node)
                  ├─ route="text" → quick_analyst → get_prices() → 텍스트
                  └─ route="dashboard" → pipeline_analyst → get_prices()
                       → output_key="market_analysis" (state)
                       → pipeline_renderer → {market_analysis?}
                            → A2UI JSON → DataPart → 리치 UI
                  (A2A) Workflow → to_a2a() → HTTP:9000
```

---

## 시간 계획


| 단계      | 시간  | 누적  | 핵심                                     |
| ------- | --- | --- | -------------------------------------- |
| 환경 설정   | 10분 | 10분 | Codespace + .env + pip install         |
| Level 1 | 15분 | 25분 | Agent + instruction → "도구가 필요하다" 깨달음   |
| Level 2 | 20분 | 45분 | Tool + API → 실시간 데이터                   |
| Level 3 | 20분 | 65분 | A2UI + callback → 대시보드                 |
| Level 4 | 20분 | 85분 | Workflow 그래프 + Function Node 라우팅 + A2A |
| 보너스     | 10분 | 95분 | 자유 실험                                  |


---

## 환경변수

```bash
# .env
ANTHROPIC_BASE_URL=https://factchat-cloud.mindlogic.ai/v1/gateway/claude
ANTHROPIC_API_KEY=your-mindlogic-api-key
```

Mindlogic API 키 발급: 동국 AI CHAT → 좌측 하단 "API Gateway" → "API 키 생성"

---

## 보너스 챌린지


| 챌린지          | 내용                              | 난이도 |
| ------------ | ------------------------------- | --- |
| 한국어 대시보드     | instruction에 한국어 응답 지시 추가       | ★☆☆ |
| 코인 추가        | `COIN_IDS`에 doge, avax 추가       | ★☆☆ |
| 알림 도구 추가     | `get_alerts()` 함수 — 급등/급락 감지    | ★★☆ |
| 포트폴리오 계산     | `get_portfolio()` — 보유량 기반 손익   | ★★☆ |
| LoopAgent 추가 | 분석 결과를 검증하는 `LoopAgent` 패턴      | ★★★ |
| A2A 클라이언트    | 다른 에이전트에서 A2A 서버를 호출하는 클라이언트 구현 | ★★★ |


---

## 트러블슈팅


| 증상                               | 해결                                                    |
| -------------------------------- | ----------------------------------------------------- |
| `adk: command not found`         | `export PATH="$HOME/.local/bin:$PATH"`                |
| 403 permission_denied            | Mindlogic 모델명 확인 (`claude-sonnet-4-5-20250929`)       |
| A2UI JSON만 보이고 렌더링 안 됨           | 브라우저 Ctrl+Shift+R 강제 새로고침                             |
| CoinGecko 타임아웃                   | mock 데이터로 자동 폴백 (정상)                                  |
| `ModuleNotFoundError: anthropic` | `pip install anthropic`                               |
| 라우팅이 엉뚱한 경로로 감                   | `classify_intent`의 keyword 리스트 확인                     |
| A2A 서버 연결 거부                     | `uvicorn ... --port 9000` 실행 확인                       |
| `ImportError: Workflow`          | ADK 2.0+ 필요 (`pip install -U google-adk`)             |
| `ImportError: to_a2a`            | `google-adk` 최신 버전인지 확인 (`pip install -U google-adk`) |
| `Duplicate edge found`           | dict 라우팅에서 같은 노드를 두 경로에 사용 불가 — 별도 노드 인스턴스 필요         |


