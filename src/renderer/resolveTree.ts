import { A2UIComponent, ResolvedNode } from "../types";

/**
 * A2UI Flat Adjacency List → 렌더링 가능한 트리 구조 변환
 *
 * 컴포넌트는 flat list로 전달되고, 부모가 자식 ID를 참조합니다.
 * 이 함수가 root부터 시작하는 트리로 변환합니다.
 *
 * 자식 케이스:
 *   1. 정적 배열: children: ["id1", "id2"]
 *   2. 단일 자식: child: "some_id"
 *   3. 템플릿 반복: children: { path: "/todos", componentId: "todo_template" }
 *      → dataModel의 /todos 배열 길이만큼 template 복제
 *      → 각 복제본에 scopePath 부여 (/todos/0, /todos/1, ...)
 */
export function resolveTree(
  components: A2UIComponent[],
  dataModel: Record<string, any>
): ResolvedNode | null {
  const map = new Map<string, A2UIComponent>();
  for (const comp of components) {
    map.set(comp.id, comp);
  }

  const root = map.get("root");
  if (!root) return null;

  function getByPath(obj: any, pointer: string): any {
    if (!pointer || pointer === "/") return obj;
    const parts = pointer.replace(/^\//, "").split("/");
    let current = obj;
    for (const part of parts) {
      if (current == null) return undefined;
      current = current[part];
    }
    return current;
  }

  function buildNode(comp: A2UIComponent, scopePath?: string): ResolvedNode {
    const resolvedChildren: ResolvedNode[] = [];

    // Case 1: 정적 자식 배열 — children: ["id1", "id2"]
    if (Array.isArray(comp.children)) {
      for (const childId of comp.children) {
        const childComp = map.get(childId);
        if (childComp) {
          resolvedChildren.push(buildNode(childComp, scopePath));
        }
      }
    }
    // Case 2: 템플릿 반복 — children: { path: "/todos", componentId: "template_id" }
    else if (
      comp.children &&
      typeof comp.children === "object" &&
      "path" in comp.children
    ) {
      const templateDef = comp.children as { path: string; componentId: string };
      const listPath = templateDef.path.startsWith("/")
        ? templateDef.path
        : `${scopePath || ""}/${templateDef.path}`;
      const list = getByPath(dataModel, listPath);

      if (Array.isArray(list)) {
        const templateComp = map.get(templateDef.componentId);
        if (templateComp) {
          for (let i = 0; i < list.length; i++) {
            const itemScopePath = `${listPath}/${i}`;
            // 템플릿 컴포넌트를 복제하여 고유 ID 부여
            const clonedComp = { ...templateComp, id: `${templateComp.id}__${i}` };
            const node = buildNode(clonedComp, itemScopePath);
            node.scopePath = itemScopePath;
            resolvedChildren.push(node);
          }
        }
      }
    }

    // Case 3: 단일 자식 — child: "some_id"
    if (typeof comp.child === "string") {
      const childComp = map.get(comp.child);
      if (childComp) {
        resolvedChildren.push(buildNode(childComp, scopePath));
      }
    }

    return {
      component: comp,
      children: resolvedChildren,
      scopePath,
    };
  }

  return buildNode(root);
}
