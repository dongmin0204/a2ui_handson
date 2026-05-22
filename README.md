# Build With AI Hands-on

이 저장소는 Google ADK와 CopilotKit를 이용해  
점진적으로 에이전트를 만들어보는 핸즈온 워크샵용 작업 공간이다.

현재 기준으로 실습 트랙은 3개다.

- `level1`: 가장 단순한 텍스트 ADK 에이전트
- `level2`: tool 호출과 fallback이 있는 텍스트 에이전트
- `CopilotKit/examples/integrations/adk`: CopilotKit + ADK + Next.js 기반 UI 에이전트 앱

## 빠른 실행

루트에 준비된 실행 스크립트 3개를 사용하면 된다.

### 1. Level 1 실행

```bash
./run_level1.sh
```

옵션:

```bash
./run_level1.sh handson 8080
./run_level1.sh solution 8082
```

- 첫 번째 인자: `handson` 또는 `solution`
- 두 번째 인자: 포트 번호
- 포트가 이미 사용 중이면 해당 프로세스를 먼저 종료한 뒤 실행한다.

### 2. Level 2 실행

```bash
./run_level2.sh
```

옵션:

```bash
./run_level2.sh handson 8081
./run_level2.sh solution 8083
```

- 첫 번째 인자: `handson` 또는 `solution`
- 두 번째 인자: 포트 번호
- 포트가 이미 사용 중이면 해당 프로세스를 먼저 종료한 뒤 실행한다.

### 3. CopilotKit 예제 실행

```bash
./run_copilotkit.sh
```

- `3000` 포트: Next.js UI
- `8000` 포트: Python ADK agent
- 두 포트가 이미 사용 중이면 기존 프로세스를 종료한 뒤 다시 실행한다.

## 사전 준비

루트 `.env` 파일에 유효한 `GOOGLE_API_KEY`가 필요하다.

```bash
cp .env.example .env
```

`.env` 예시:

```bash
GOOGLE_GENAI_USE_VERTEXAI=False
GOOGLE_API_KEY=your-real-api-key
```

의존성 준비:

```bash
python3 -m pip install -r requirements.txt
```

CopilotKit 예제는 추가로 Node.js 환경이 필요하다.

```bash
cd CopilotKit/examples/integrations/adk
npm install
```

## 실습 구조

### `level1`

ADK의 가장 기본적인 형태를 익히는 단계다.

- 단일 `Agent`
- `model`, `name`, `description`, `instruction`
- tool 없음
- 텍스트 응답만 다룸

자세한 설명:
- [level1/README.md](./level1/README.md)

### `level2`

텍스트 에이전트에 tool을 붙여서  
실시간 검색과 폴백 데이터 흐름을 다루는 단계다.

- `search_web`
- `get_prices`
- tool 우선순위 instruction
- fallback 전략

자세한 설명:
- [level2/README.md](./level2/README.md)

### `CopilotKit`

CopilotKit 원본 저장소에서 `examples/integrations/adk`만 가져와  
로컬 핸즈온용으로 수정한 UI 예제다.

현재 반영된 커스터마이징:

- 한국어 UI
- `오늘의 계획` 보드
- 배경색 + 글자색 테마 변경
- Google Search 기반 주식 차트
- 아리따 폰트 적용
- Inspector 숨김 설정

자세한 설명:
- [CopilotKit/guide.md](./CopilotKit/guide.md)

## 현재 폴더 구조

```text
buildwithai_handson/
├── CopilotKit/
│   ├── README.md
│   ├── guide.md
│   └── examples/
│       └── integrations/
│           └── adk/
├── level1/
│   ├── README.md
│   ├── handson/
│   └── solution/
├── level2/
│   ├── README.md
│   ├── handson/
│   └── solution/
├── .env.example
├── requirements.txt
├── run.sh
├── run_level1.sh
├── run_level2.sh
└── run_copilotkit.sh
```

## 참고 사항

- 기존 `run.sh`는 루트의 다른 ADK/A2UI 실험용 스크립트다.
- 현재 핸즈온 3종 실행은 `run_level1.sh`, `run_level2.sh`, `run_copilotkit.sh` 기준으로 보는 것이 맞다.
- CopilotKit 예제에서 보이는 `GET /api/copilotkit/threads?agentId=my_agent 404` 로그는 현재 구조에서 치명적 오류가 아니다.
  - 스레드 히스토리 기능 없이 프런트가 조회를 시도하는 로그에 가깝다.
