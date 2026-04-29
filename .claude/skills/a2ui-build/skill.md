---
name: a2ui-build
description: "A2UI 핸즈온 스타터 코드 전체를 빌드하는 오케스트레이터. 5개 빌더 에이전트를 병렬 실행하여 /Users/dongminbaek/Documents/buildwithai_handson/ 하위에 완성된 프로젝트를 생성한다."
---

# A2UI Build Orchestrator

A2UI 핸즈온 v3 스타터 코드를 빌드하는 오케스트레이터.

## 실행 모드: 서브 에이전트 (병렬)

## 에이전트 구성

| 에이전트 | 역할 | 담당 파일 |
|---------|------|---------|
| scaffold-server | 스캐폴드 + 서버 | package.json, tsconfig*, vite.config.ts, index.html, .env.example, server/ |
| frontend-core | 프론트 핵심 | src/types.ts, src/sampleSpec.ts, src/main.tsx, src/App.tsx, src/App.css |
| renderer | 렌더러 | src/renderer/A2UIRenderer.tsx, src/renderer/resolveTree.ts |
| components | 컴포넌트 11개 | src/components/*.tsx + *.css |
| hooks-examples | 훅 + 예제 | src/hooks/, src/styles/, examples/, README.md |

## 워크플로우

### Phase 1: 디렉토리 생성
모든 필요한 디렉토리를 Bash로 생성한다.

### Phase 2: 병렬 빌드
5개 Agent를 단일 메시지에서 동시 호출한다 (run_in_background: true).

### Phase 3: 검증
- npm install 실행하여 의존성 확인
- TypeScript 컴파일 오류 확인 (tsc --noEmit)

## 에러 핸들링

| 상황 | 전략 |
|------|------|
| 에이전트 실패 | 해당 에이전트만 재실행 |
| TypeScript 오류 | types.ts 타입 확인 후 수정 |
| 의존성 누락 | package.json에 추가 후 npm install |

## 테스트 시나리오

### 정상 흐름
1. 5개 에이전트 병렬 실행
2. npm install 성공
3. npm start → Vite :5173, Express :3001 동시 실행
4. 브라우저에서 TODO Agent 페이지 확인
5. 체크박스 토글, JSON 뷰 전환 동작

### 에러 흐름
1. TypeScript 컴파일 오류 발생
2. 오류 파일 특정 후 해당 에이전트만 재실행
3. 재컴파일 확인
