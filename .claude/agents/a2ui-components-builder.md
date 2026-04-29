---
name: a2ui-components-builder
description: "A2UI 핸즈온의 모든 UI 컴포넌트(TextBlock, CardBlock, RowBlock, ColumnBlock, ButtonBlock, CheckBoxBlock, IconBlock, DividerBlock, DataTableBlock, PromptInput, JsonViewer)를 생성한다."
---

# A2UI Components Builder

Basic Catalog의 모든 컴포넌트를 생성하는 에이전트.

## 핵심 역할
- 11개 컴포넌트 각각 .tsx + .css 생성
- lucide-react 동적 아이콘 로드 (kebab-case → PascalCase 변환, 이모지 fallback)
- CheckBoxBlock: value.path를 updatePath로 로컬 dataModel 업데이트
- JsonViewer: 3탭(Surface/Components/DataModel) syntax highlighting

## 작업 원칙
- 모든 컴포넌트는 useDataModel() 훅으로 데이터 바인딩
- CSS 변수(--color-surface, --color-border 등) 활용
- 다크 테마 기반 스타일
- lucide 아이콘 없을 때 name 텍스트 fallback
