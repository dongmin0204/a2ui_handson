---
name: a2ui-hooks-examples-builder
description: "A2UI 핸즈온의 훅(useDataModel.ts), 글로벌 스타일(global.css), 예제 JSON(examples/), README.md를 생성한다."
---

# A2UI Hooks & Examples Builder

데이터 바인딩 훅, 글로벌 CSS 변수, 참가자용 예제 JSON, README를 생성하는 에이전트.

## 핵심 역할
- src/hooks/useDataModel.ts: DataModelContext + resolve() + updatePath() + replaceData()
- src/styles/global.css: CSS 커스텀 프로퍼티 (다크 테마 토큰)
- examples/study-planner.json: 학습 플래너 예제
- examples/expense-tracker.json: 경비 트래커 예제
- README.md: Cloud Shell 세팅 + 핸즈온 가이드

## 작업 원칙
- resolve()는 절대경로(/로 시작)와 상대경로(template 내) 모두 처리
- setByPath는 불변성 유지 (새 객체 반환)
- 예제 JSON은 spec의 study-planner.json 내용 그대로 + expense-tracker 새로 작성
- README는 Cloud Shell 기반 세팅 가이드 (gcloud, npm start, 웹 미리보기)
