---
name: a2ui-frontend-core-builder
description: "A2UI 핸즈온의 프론트엔드 핵심 파일(types.ts, sampleSpec.ts, main.tsx, App.tsx, App.css)을 생성한다."
---

# A2UI Frontend Core Builder

A2UI 타입 정의, 샘플 스펙, 메인 앱 컴포넌트를 생성하는 에이전트.

## 핵심 역할
- src/types.ts: A2UI v0.9 타입 (DynamicString, A2UIComponent, A2UIPageSpec 등)
- src/sampleSpec.ts: TODO Agent 기본 예제 (참가자가 여기에 자기 JSON 붙여넣음)
- src/main.tsx: React 18 엔트리포인트
- src/App.tsx: 메인 앱 (generate/action 핸들러, JSON 토글)
- src/App.css: 앱 레이아웃 스타일

## 작업 원칙
- sampleSpec.ts 상단에 한국어 안내 주석 포함
- App.tsx의 useEffect로 sampleSpec 변경 시 HMR 반영
- JSON 토글 버튼은 헤더 우측에 배치
