# CopilotKit Guide

이 디렉터리는 `CopilotKit` 원본 저장소를 sparse checkout으로 가져온 뒤,  
`examples/integrations/adk` 예제를 로컬 핸즈온용으로 수정한 작업 공간이다.

## 이 폴더를 왜 두었나

- CopilotKit의 ADK 연동 예제를 직접 실행해보기 위해
- `Google ADK + CopilotKit + Next.js` 조합을 빠르게 데모하기 위해
- 기본 예제를 한국어 UI, 계획 보드, 색상 테마 변경, 주식 차트 렌더링 흐름으로 커스터마이징하기 위해

## 현재 실습에서 중요한 경로

- `examples/integrations/adk/`
  - 실제로 수정하고 실행하는 메인 예제
- `examples/integrations/adk/agent/main.py`
  - ADK 에이전트 로직
- `examples/integrations/adk/src/app/page.tsx`
  - 메인 화면과 CopilotSidebar
- `examples/integrations/adk/src/components/`
  - 계획 카드, 날씨 카드, 주식 차트 UI

## 현재 예제에서 바뀐 내용

- UI 문구를 한국어로 변경
- 카드 제목을 `오늘의 계획` 기준으로 변경
- 상태 구조를 `plans` 기준으로 정리
- `set_theme_color`로 배경색과 글자색을 함께 변경 가능
- Google Search 기반 주식 차트 렌더링 추가
- 아리따 폰트 적용
- CopilotKit Inspector 숨김 설정 적용

## 실행 방법

```bash
cd examples/integrations/adk
npm install
npm run dev
```

추가로 `GOOGLE_API_KEY`가 필요하다.

```bash
cp .env.example .env
export GOOGLE_API_KEY="your-google-api-key"
```

## 확인 포인트

- `http://localhost:3000` 에서 UI 확인
- 사이드바에서 계획 추가/수정 요청
- `테마를 초록색으로 바꾸고 글자는 검은색으로 해줘`
- `구글 검색으로 엔비디아 5일 차트 보여줘`

## 주의할 점

- `GET /api/copilotkit/threads?agentId=my_agent 404` 는 현재 예제 구조에서 치명적 오류가 아니다.
  - 스레드 히스토리 기능이 없는 상태에서 프런트가 조회를 시도하는 로그에 가깝다.
- 이 폴더는 원본 CopilotKit 전체 개발용이 아니라, 현재 핸즈온에서 필요한 예제만 다루는 로컬 작업본이다.

## 원본 저장소

- Repository: https://github.com/CopilotKit/CopilotKit
- 사용한 예제: `examples/integrations/adk`
