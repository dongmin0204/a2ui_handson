// A2UI v0.9 프로토콜 기반 타입 정의 (세션용 서브셋)

// --- Dynamic 타입: 리터럴 값 또는 데이터 바인딩 path ---
export type DynamicString = string | { path: string };
export type DynamicNumber = number | { path: string };
export type DynamicBoolean = boolean | { path: string };

// --- 자식 참조 (Adjacency List) ---
export type ComponentId = string;
export type ChildList =
  | ComponentId[]
  | { path: string; componentId: ComponentId };

// --- 액션 ---
export interface ServerAction {
  name: string;
  context?: Record<string, any>;
}

// --- 컴포넌트 정의 ---
export interface A2UIComponent {
  id: string;
  component: string;
  // Layout
  children?: ChildList;
  child?: ComponentId;
  gap?: number;
  align?: string;
  // Text
  text?: DynamicString;
  variant?: string;
  color?: string;
  // Button
  label?: DynamicString;
  action?: ServerAction;
  // CheckBox
  value?: DynamicBoolean;
  // Icon
  name?: string;
  size?: number;
  // DataTable
  columns?: any;
  rows?: any;
  // 확장 가능
  [key: string]: any;
}

// --- Surface ---
export interface A2UISurface {
  surfaceId: string;
  catalogId: string;
  theme?: { primaryColor?: string; [key: string]: any };
}

// --- 통합 응답 ---
export interface A2UIPageSpec {
  surface: A2UISurface;
  components: A2UIComponent[];
  dataModel: Record<string, any>;
}

// --- Action 응답 ---
export interface A2UIActionResponse {
  dataModel: Record<string, any>;
  components?: A2UIComponent[];
}

// --- 렌더러 내부용 ---
export interface ResolvedNode {
  component: A2UIComponent;
  children: ResolvedNode[];
  scopePath?: string;
}
