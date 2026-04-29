import { useState, useCallback, useContext, createContext } from "react";

interface DataModelContextValue {
  data: Record<string, any>;
  resolve: (value: any, scopePath?: string) => any;
  updatePath: (path: string, value: any) => void;
}

export const DataModelContext = createContext<DataModelContextValue>({
  data: {},
  resolve: (v) => v,
  updatePath: () => {},
});

export function useDataModel() {
  return useContext(DataModelContext);
}

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

function setByPath(
  obj: Record<string, any>,
  pointer: string,
  value: any
): Record<string, any> {
  const parts = pointer.replace(/^\//, "").split("/");
  const result = { ...obj };
  let current: any = result;
  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i];
    if (Array.isArray(current[part])) {
      current[part] = [...current[part]];
    } else {
      current[part] = { ...current[part] };
    }
    current = current[part];
  }
  current[parts[parts.length - 1]] = value;
  return result;
}

export function useDataModelState(initialData: Record<string, any>) {
  const [data, setData] = useState<Record<string, any>>(initialData);

  const resolve = useCallback(
    (value: any, scopePath?: string): any => {
      if (value === null || value === undefined) return value;
      if (typeof value === "object" && "path" in value) {
        const path = value.path as string;
        if (path.startsWith("/")) {
          // 절대 경로
          return getByPath(data, path);
        } else {
          // 상대 경로 (template 내)
          const fullPath = `${scopePath || ""}/${path}`;
          return getByPath(data, fullPath);
        }
      }
      return value;
    },
    [data]
  );

  const updatePath = useCallback((path: string, value: any) => {
    setData((prev) => setByPath(prev, path, value));
  }, []);

  const replaceData = useCallback((newData: Record<string, any>) => {
    setData(newData);
  }, []);

  return { data, resolve, updatePath, replaceData };
}
