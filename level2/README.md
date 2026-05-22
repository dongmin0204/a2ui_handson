# Level 2

`level2`는 텍스트 에이전트에 tool을 붙여서  
“모델 단독 응답”에서 “도구를 활용하는 에이전트”로 넘어가는 단계

## 목표

- ADK tool 함수 등록 방식 이해
- `search_web` 우선, `get_prices` 실패시 임시 데이터 전략 구현
- instruction으로 tool 사용 규칙을 명시하는 방법 익히기

## 폴더 구조

- `handson/`
  - 실습용 시작 코드
  - `search_web`, `get_prices`, `tools=[...]`, instruction TODO 포함
- `solution/`
  - 완성 예시
  - 실시간 검색 + 폴백 데이터 흐름 반영

## 주요 파일

- `handson/crypto_dashboard/agent.py`
- `handson/crypto_dashboard/market_data.py`
- `solution/crypto_dashboard/agent.py`
- `solution/crypto_dashboard/market_data.py`

## 이 단계에서 추가되는 것

### 1. `search_web`

Gemini의 Google Search grounding을 이용해  
실시간에 가까운 시장 정보를 검색하는 함수다.

예시 질문:

- `Bitcoin price today USD`
- `crypto market overview today`

### 2. `get_prices`

실시간 검색이 실패했을 때 사용하는 정적 폴백 데이터다.

- `GOOGLE_API_KEY`가 없을 때
- 검색 호출이 실패했을 때
- 구조화된 요약이 필요할 때

최소한의 시장 데이터 응답을 유지하기 위한 안전장치 역할이다.

## 구현 포인트

`handson/crypto_dashboard/agent.py` 에서 핵심은 두 가지다.

1. `tools=[search_web, get_prices]` 등록
2. instruction에 아래 원칙을 명시

- 먼저 `search_web` 사용
- 실패하면 `get_prices` 사용
- 현재 가격, 변동, 시장 분위기를 요약
- 어떤 소스를 썼는지 밝히기

즉, 이 단계의 핵심은 단순히 tool을 “붙이는 것”이 아니라  
모델이 언제 어떤 tool을 써야 하는지 행동 규칙을 설계하는 데 있다.

## 추천 진행 순서

1. `market_data.py` 의 `search_web` TODO 구현
2. `agent.py` 에 tool 등록
3. instruction에 우선순위와 fallback 규칙 명시
4. `solution/` 과 비교

## 이 레벨을 끝내면

다음 단계에서는 단순 텍스트 응답을 넘어서

- UI와 상태를 공유하는 에이전트
- 렌더링 가능한 tool 결과
- 사용자 인터랙션이 있는 에이전트 앱

으로 확장할 준비가 된다.
