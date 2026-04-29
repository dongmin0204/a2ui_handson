# A2UI 프롬프트 가이드

> **사용 방법**
> 1. https://a2ui-composer.ag-ui.com 접속
> 2. 아래 프롬프트를 복사해서 입력
> 3. 생성된 JSON의 `components`와 `dataModel`을 살펴보기
> 4. 마음에 들면 `src/sampleSpec.ts`에 붙여넣기

---

## JSON 구조 읽는 법

Composer가 생성하는 JSON은 항상 이 3가지로 구성됩니다:

```
surface   → 페이지 기본 정보 (이름, 테마 색상)
components → UI 부품 목록 (레이아웃 + 콘텐츠 + 버튼)
dataModel  → 화면에 표시될 실제 데이터
```

**체크포인트 3가지:**
- `components` 안에 `"id": "root"` 가 있는가?
- `{ "path": "/키" }` 가 `dataModel`의 키와 일치하는가?
- 배열 반복은 `{ "path": "/배열", "componentId": "템플릿id" }` 형태인가?

---

## 난이도별 프롬프트

---

### ⭐ Level 1 — 텍스트 + 버튼만

**목표**: 가장 단순한 구조 이해. `Text`, `Button`, `Column` 컴포넌트만 나와야 합니다.

```
간단한 명언 카드 페이지를 만들어줘.
- 오늘의 명언과 출처를 크게 표시해줘
- 명언 배경은 카드 형태로
- "새 명언 받기" 버튼 1개
```

**JSON에서 확인할 것:**
- `components`에 `"component": "Text"` 의 `variant`가 뭔지 (`headline`, `title`, `body`)
- `"component": "Button"`의 `action.name`이 뭔지
- `dataModel`에 명언 텍스트가 어떤 키로 들어가는지

---

### ⭐ Level 2 — 체크리스트 (배열 반복)

**목표**: 배열 데이터가 체크리스트로 반복 렌더링되는 구조를 이해합니다.

```
오늘의 할 일 체크리스트 페이지를 만들어줘.
- 페이지 상단에 아이콘과 제목 "오늘의 TODO"
- 할 일 목록: 아침 운동, 점심 약속, 코드 리뷰, 저녁 독서
- 각 항목에 체크박스와 할 일 텍스트
- "완료 처리" 버튼 (primary), "목록 초기화" 버튼 (secondary)
```

**JSON에서 확인할 것:**
- `"component": "Column"`의 `children`이 배열(`[]`)인지 객체(`{ path, componentId }`)인지
- `"component": "CheckBox"`의 `value`가 어떻게 생겼는지
- `dataModel`의 배열 항목 구조 (예: `{ "text": "...", "checked": false }`)
- 템플릿 컴포넌트의 `children`에 있는 상대경로 (`{ "path": "checked" }` — `/` 없음)

---

### ⭐ Level 3 — 카드 + 체크리스트 조합

**목표**: `Card`로 섹션을 나누고, 여러 종류의 컴포넌트가 함께 쓰이는 구조를 이해합니다.

```
취업 준비 대시보드를 만들어줘.

구성:
1. 헤더: 아이콘(briefcase)과 제목 "취업 준비 현황", 부제목 "AI가 분석한 오늘의 우선순위"
2. 요약 카드: 오늘의 핵심 목표를 한 문장으로 표시
3. 할 일 카드: 체크리스트
   - 자기소개서 3문항 수정
   - 포트폴리오 README 업데이트
   - 기업 분석 자료 정리 (네이버, 카카오)
   - 코딩테스트 문제 2문제 풀기
4. 버튼 2개: "완료한 항목 처리" (primary), "오늘 일정 다시 짜기" (secondary)

테마 색상: 남색 계열
```

**JSON에서 확인할 것:**
- `"component": "Card"`는 `child`(단수)를 쓰는지 `children`(복수)를 쓰는지
- 헤더의 `Row` 안에 `Icon`과 `Column`이 중첩되는 구조
- `Card` > `Column` > `Text` + `Column(체크리스트)` 의 계층 구조

---

### ⭐⭐ Level 4 — 테이블 포함

**목표**: `DataTable`이 `dataModel`의 2차원 배열을 어떻게 참조하는지 이해합니다.

```
주간 운동 루틴 관리 페이지를 만들어줘.

구성:
1. 헤더: 아이콘(dumbbell)과 제목 "이번 주 운동 루틴"
2. 운동 체크리스트 카드:
   - 월: 스쿼트 3세트, 런지 3세트
   - 수: 벤치프레스 3세트, 덤벨로우 3세트
   - 금: 달리기 30분, 플랭크 3세트
   - 각 항목에 체크박스, 운동 이름, 목표 세트 수
3. 이번 주 시간표 카드:
   - 테이블: 요일 / 운동 / 강도 / 예상 시간
   - 월요일부터 금요일까지 데이터 포함
4. 버튼: "완료 처리", "루틴 재구성"

테마: 초록색 계열
```

**JSON에서 확인할 것:**
- `"component": "DataTable"`의 `columns`와 `rows`가 어떤 형태인지
  - 리터럴 배열: `"columns": ["요일", "운동", ...]`
  - path 참조: `"columns": { "path": "/schedule/columns" }`
- `dataModel`에서 `rows`가 2차원 배열(`[["월", "스쿼트", ...], ...]`)인지 확인
- 체크리스트의 template과 테이블이 각각 다른 데이터를 참조하는 방식

---

### ⭐⭐ Level 5 — 나만의 페이지 만들기 (실전)

> **파이프라인 이해가 중요합니다**
>
> Composer는 JSONL(스트리밍 이벤트) 포맷을 출력합니다.
> 우리 앱은 **A2UI v0.9 단일 JSON** `{ surface, components, dataModel }` 포맷을 씁니다.
> **직접 붙여넣기는 안 됩니다.** 아래 2단계 파이프라인을 따르세요.

---

#### Step 1. Composer에서 구조 확인 (학습)

https://a2ui-composer.ag-ui.com 에서 원하는 프롬프트를 입력합니다.
목적은 붙여넣기가 아니라 **"어떤 컴포넌트들이 나오는지"** 눈으로 확인하는 것입니다.

- 어떤 컴포넌트 타입이 나왔나? (`Card`, `Column`, `CheckBox`, `DataTable` ...)
- 데이터 바인딩이 어떻게 걸려 있나? (`{ "path": "..." }`)
- 버튼의 `action.name`이 뭔가?

---

#### Step 2. 우리 앱에서 실제 생성

**동일한 프롬프트**를 앱 상단 입력창에 붙여넣고 전송합니다.
Gemini가 **A2UI v0.9 포맷 JSON**으로 직접 생성하고 화면에 바로 렌더링됩니다.

```
[내가 원하는 주제] 관리 페이지를 만들어줘.

구성:
1. 헤더: [아이콘 이름]과 제목 "[제목]", 부제목 "[설명]"
2. [섹션 이름] 카드:
   - [항목 설명]
   - 각 항목에 [필요한 정보들]
3. [다른 섹션] 카드 (선택):
   - [테이블 or 텍스트]
4. 버튼: "[동작1]", "[동작2]"

테마 색상: [색상] 계열
```

생성 후 **"{ } JSON 보기"** 버튼으로 구조를 확인하고,
마음에 들면 `src/sampleSpec.ts`에 복사해 저장하세요 (HMR로 즉시 반영).

---

#### 아이디어가 없으면

| 주제 | 포인트 |
|------|--------|
| 여행 준비물 체크리스트 | 카테고리별 체크리스트 + 날짜 테이블 |
| 월간 독서 목표 트래커 | 진행률 카드 + 책 목록 체크리스트 |
| 스터디 발표 순서 관리 | 발표자 체크리스트 + 일정 테이블 |
| 냉장고 재료 관리 | 재료 목록 + 유통기한 테이블 |
| 구독 서비스 정리 | 서비스 목록 + 월 비용 요약 카드 |

---

## 자주 나오는 JSON 패턴 읽기

### 패턴 1: 체크리스트 반복

```json
// components 안에:
{ "id": "list", "component": "Column",
  "children": { "path": "/items", "componentId": "item_template" } }

{ "id": "item_template", "component": "Row", "children": ["chk", "txt"] }
{ "id": "chk", "component": "CheckBox", "value": { "path": "done" } }
{ "id": "txt", "component": "Text", "text": { "path": "name" } }

// dataModel 안에:
{ "items": [{ "name": "항목1", "done": false }, { "name": "항목2", "done": false }] }
```

### 패턴 2: 카드 안에 콘텐츠

```json
// Card는 child (단수) 하나만 받음
{ "id": "my_card", "component": "Card", "child": "card_content" }

// 안에 Column으로 여러 항목 묶기
{ "id": "card_content", "component": "Column", "children": ["title", "body"], "gap": 8 }
```

### 패턴 3: 데이터 바인딩

```json
// dataModel 절대경로: / 로 시작
{ "text": { "path": "/pageTitle" } }   → dataModel.pageTitle

// template 내 상대경로: / 없음
{ "text": { "path": "name" } }          → 현재 아이템의 .name
```

---

## Composer에서 JSON이 이상하면?

| 증상 | 해결 |
|------|------|
| `root` 컴포넌트가 없음 | 프롬프트에 "root 컴포넌트부터 시작해서" 추가 |
| 체크박스가 안 생김 | "각 항목에 체크박스" 명시 |
| 테이블 데이터가 비어있음 | "테이블에 실제 데이터 3~5개 채워줘" 추가 |
| 버튼이 action 없이 생성됨 | "버튼 클릭 시 서버에 요청을 보내도록" 추가 |
| JSON이 너무 단순함 | 구성 항목을 더 구체적으로 적기 |
