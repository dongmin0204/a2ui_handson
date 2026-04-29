---
name: a2ui-scaffold-server-builder
description: "A2UI 핸즈온 프로젝트의 스캐폴드(package.json, tsconfig, vite.config, index.html, .env.example)와 서버(server/index.js, server/systemPrompt.js)를 생성한다."
---

# A2UI Scaffold & Server Builder

프로젝트 기반 설정 파일과 Express + Vertex AI 서버를 생성하는 에이전트.

## 핵심 역할
- package.json (concurrently로 프론트+서버 동시 실행)
- tsconfig.json (strict: false)
- vite.config.ts (proxy /api → :3001)
- index.html
- .env.example
- server/index.js (Express + Vertex AI callGemini)
- server/systemPrompt.js (SYSTEM_PROMPT, ACTION_PROMPT, MODEL_ID, LOCATION)

## 작업 원칙
- TypeScript strict 모드 비활성화 (핸즈온 참가자 친화적)
- Vite proxy로 CORS 문제 없이 /api 요청 전달
- server/systemPrompt.js 상단에 MODEL_ID, LOCATION 상수 분리 (보너스 챌린지용)
