# Level 1

`level1`은 Google ADK의 가장 단순한 형태를 익히는 단계
아직 tool 호출이나 UI 렌더링은 없고, `Agent` 한 개를 정의해서 기본 응답 흐름만 다룸

## 목표

- ADK의 `Agent` 기본 구조 이해
- `model`, `name`, `description`, `instruction` 역할 구분
- 시스템 프롬프트가 에이전트 응답 스타일을 어떻게 바꾸는지 체감

## 폴더 구조

- `handson/`
  - 실습용 시작 코드
  - TODO를 직접 채우면서 에이전트를 완성하는 단계
- `solution/`
  - 완성 예시
  - 최소 동작 가능한 기준점

## 주요 파일

- `handson/crypto_dashboard/agent.py`
- `solution/crypto_dashboard/agent.py`

## 실습에서 하는 일

`handson/crypto_dashboard/agent.py` 에서 아래 항목을 채운다.

- `model=AnthropicLlm(model="claude-sonnet-4-5-20250929")`
- `name`
- `description`
- `instruction`

이 단계에서는 아직 실시간 데이터 조회를 하지 않는다.  
즉, 에이전트는 자신의 일반 지식만으로 답하고, 최신 가격을 모를 때는 솔직하게 모른다고 말해야 한다.

## 배울 포인트

- description은 “이 에이전트가 무엇을 하는지”를 짧게 설명
- instruction은 “어떤 태도로, 어떤 원칙으로 대답할지”를 고정
- 단일 파일로도 ADK 에이전트의 핵심 구조를 충분히 경험 가능

## 추천 진행 순서

1. `handson/crypto_dashboard/agent.py` 의 TODO 채우기
2. `solution/crypto_dashboard/agent.py` 와 비교
3. description과 instruction 문구를 바꿔보며 응답 스타일 차이 확인

## 이 레벨을 끝내면

다음 단계인 `level2`에서 tool을 붙여

- 실시간 검색
- 폴백 데이터
- “반드시 tool 호출” 같은 instruction 설계

로 넘어갈 준비가 된다.
