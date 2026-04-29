/**
 * ============================================
 * 🎯 여기에 A2UI Composer에서 만든 JSON을 붙여넣으세요!
 *
 * 방법:
 * 1. https://a2ui-composer.ag-ui.com 에서 프롬프트 입력
 * 2. 생성된 JSON 전체 복사
 * 3. 아래 sampleSpec 객체 전체를 복사한 JSON으로 교체
 * 4. 저장하면 브라우저가 자동으로 새 UI를 표시합니다 (HMR)
 * ============================================
 */

import { A2UIPageSpec } from "./types";

export const sampleSpec: A2UIPageSpec = {
  surface: {
    surfaceId: "today-todo-agent",
    catalogId: "handson-basic-catalog",
    theme: { primaryColor: "#6c63ff" },
  },

  components: [
      {
        "id": "root",
        "component": "Column",
        "children": ["hero_section", "summary_card", "todo_section", "schedule_card", "action_row"],
        "gap": 16,
        "align": "stretch"
      },
  
      // Hero Section: 학습 테마 및 에이전트 상태
      {
        "id": "hero_section",
        "component": "Row",
        "children": ["hero_icon", "hero_text_group"],
        "align": "center",
        "gap": 12
      },
      { "id": "hero_icon", "component": "Icon", "name": "school", "size": 36 },
      {
        "id": "hero_text_group",
        "component": "Column",
        "children": ["hero_title", "hero_subtitle"],
        "gap": 4
      },
      { "id": "hero_title", "component": "Text", "text": { "path": "/pageTitle" }, "variant": "headline" },
      { "id": "hero_subtitle", "component": "Text", "text": { "path": "/pageSubtitle" }, "variant": "body", "color": "secondary" },
  
      // Summary Card: 오늘의 집중 포인트
      { "id": "summary_card", "component": "Card", "child": "summary_content" },
      { "id": "summary_content", "component": "Column", "children": ["summary_title", "summary_desc"], "gap": 8 },
      { "id": "summary_title", "component": "Text", "text": "💡 오늘의 학습 전략", "variant": "title" },
      { "id": "summary_desc", "component": "Text", "text": { "path": "/summary" }, "variant": "body" },
  
      // TODO Checklist: 학습 세부 항목
      { "id": "todo_section", "component": "Card", "child": "todo_inner" },
      { "id": "todo_inner", "component": "Column", "children": ["todo_header", "todo_list"], "gap": 12 },
      { "id": "todo_header", "component": "Text", "text": "📝 세부 체크리스트", "variant": "title" },
      {
        "id": "todo_list",
        "component": "Column",
        "children": { "path": "/todos", "componentId": "todo_item_template" },
        "gap": 8
      },
      {
        "id": "todo_item_template",
        "component": "Row",
        "children": ["todo_check", "todo_text", "todo_difficulty"],
        "align": "center",
        "gap": 12
      },
      { "id": "todo_check", "component": "CheckBox", "value": { "path": "checked" } },
      { "id": "todo_text", "component": "Text", "text": { "path": "text" }, "variant": "body" },
      { "id": "todo_difficulty", "component": "Text", "text": { "path": "difficultyLabel" }, "variant": "caption" },
  
      // Schedule: 타임라인 테이블
      { "id": "schedule_card", "component": "Card", "child": "schedule_inner" },
      { "id": "schedule_inner", "component": "Column", "children": ["schedule_header", "schedule_table"], "gap": 12 },
      { "id": "schedule_header", "component": "Text", "text": "⏰ 집중 시간 블록", "variant": "title" },
      {
        "id": "schedule_table",
        "component": "DataTable",
        "columns": { "path": "/schedule/columns" },
        "rows": { "path": "/schedule/rows" }
      },
  
      // Action Buttons
      { "id": "action_row", "component": "Row", "children": ["btn_ask_ai", "btn_finish"], "gap": 12 },
      {
        "id": "btn_ask_ai",
        "component": "Button",
        "label": "🤖 모르는 개념 AI에게 묻기",
        "variant": "secondary",
        "action": { "name": "ask_ai_help" }
      },
      {
        "id": "btn_finish",
        "component": "Button",
        "label": "🏁 오늘 학습 종료하기",
        "variant": "primary",
        "action": { "name": "complete_study" }
      }
    ],
  
    "dataModel": {
      "pageTitle": "알고리즘 마스터 에이전트",
      "pageSubtitle": "코딩 테스트 D-7, 효율적인 개념 정리를 도와드릴게요",
      "summary": "오늘은 '그래프 탐색(BFS/DFS)'의 핵심 원리를 파악하고 관련 실무 문제를 3개 이상 해결하는 것이 목표입니다. 오후 2시 세션이 가장 중요합니다.",
      "todos": [
        { "text": "DFS/BFS 기본 원리 시각화 학습", "checked": true, "difficulty": "low", "difficultyLabel": "🟢 쉬움" },
        { "text": "백준 1260번(DFS와 BFS) 풀이", "checked": false, "difficulty": "medium", "difficultyLabel": "🟡 보통" },
        { "text": "재귀 함수 스택 오버플로우 주의점 정리", "checked": false, "difficulty": "high", "difficultyLabel": "🔴 어려움" },
        { "text": "큐(Queue)를 이용한 BFS 최단경로 구현", "checked": false, "difficulty": "medium", "difficultyLabel": "🟡 보통" }
      ],
      "schedule": {
        "columns": ["시간대", "학습 내용", "강도"],
        "rows": [
          ["10:00 - 11:30", "그래프 이론 및 인접 행렬 복습", "낮음"],
          ["13:00 - 15:00", "DFS/BFS 실전 문제 풀이 (Deep Work)", "매우 높음"],
          ["15:30 - 16:30", "오답 노트 및 코드 리팩토링", "보통"]
        ]
      }
    }
  }