# A2UI로 만드는 AI Agent Tool Page

프롬프트로 UI를 설계하고, React가 렌더링하는 Agent Tool Page를 만들어봅시다.

## 이 프로젝트는?

- **A2UI**: AI가 UI 구조(JSON)를 생성하면, React가 그걸 실제 화면으로 렌더링하는 프로토콜
- **이 핸즈온**: Gemini가 A2UI JSON을 생성 → React 렌더러가 화면을 만듦 → 버튼 클릭 시 AI가 데이터를 갱신

---

## 시작하기

### 1. API Key 발급

https://aistudio.google.com/app/apikey 접속 → "Create API key" → 복사

### 2. 코드 받기

```bash
git clone https://github.com/[YOUR_ORG]/a2ui-handson.git
cd a2ui-handson
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열고 GEMINI_API_KEY에 발급받은 키 입력
```

### 4. 의존성 설치

```bash
# 프론트엔드
npm install

# Python 에이전트 서버
pip install -e agent/
```

### 5. 실행

```bash
npm start
```

브라우저에서 http://localhost:5173 접속

> **GitHub Codespace**: 포트 5173이 자동으로 포워딩됩니다.
> PORTS 탭에서 5173 포트의 링크를 클릭하세요.

---

## 첫 화면 확인

- TODO Agent 페이지가 렌더링되어 있습니다
- 체크박스를 클릭하면 토글됩니다 (로컬 상태)
- **"{ } JSON 보기"** 버튼 → JSON과 UI를 비교해보세요

---

## #1: A2UI Composer로 UI 구조 이해하기

A2UI Composer: https://a2ui-composer.ag-ui.com

참고용 프롬프트는 `examples/prompt-guide.md`를 보세요.

생성된 JSON의 구조를 살펴보세요:
- `surface`: 페이지 기본 정보
- `components`: UI 부품 목록 (flat list, ID로 연결)
- `dataModel`: 화면에 표시될 데이터

---

## #2: 내 페이지 만들기

### 방법 A: 실시간 생성 (권장)

1. 화면 상단 프롬프트 입력창에 원하는 내용 입력
2. 전송 → Gemini가 A2UI JSON 생성 → 즉시 렌더링
3. 버튼 클릭 → AI가 데이터를 갱신 → UI 업데이트

### 방법 B: sampleSpec.ts 교체 (HMR)

1. `src/sampleSpec.ts` 파일 열기
2. 원하는 JSON을 `sampleSpec` 객체 자리에 붙여넣기
3. 저장 → 브라우저 자동 갱신

---

## 보너스 챌린지

### ⭐⭐ 시스템 프롬프트 수정

`agent/prompts.py`를 열어 Gemini에게 다른 스타일을 지시해보세요

### ⭐⭐ 다른 모델 사용

`.env`에서 `GEMINI_MODEL=gemini-2.5-pro`로 변경 후 서버 재시작

### ⭐⭐⭐ 새 컴포넌트 추가

`src/components/`에 새 컴포넌트 추가 → `src/renderer/A2UIRenderer.tsx`에 등록 → `agent/prompts.py`에 설명 추가

---

## 참고 자료

- A2UI 공식 문서: https://a2ui.org
- A2UI Composer: https://a2ui-composer.ag-ui.com
- Gemini API: https://aistudio.google.com
