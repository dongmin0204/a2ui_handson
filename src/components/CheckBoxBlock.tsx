import { useDataModel } from "../hooks/useDataModel";
import "./CheckBoxBlock.css";

interface CheckBoxBlockProps {
  value?: any;
  scopePath?: string;
}

export function CheckBoxBlock({ value, scopePath }: CheckBoxBlockProps) {
  const { resolve, updatePath } = useDataModel();
  const resolved = resolve(value, scopePath);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (value && typeof value === "object" && "path" in value) {
      const p = value.path as string;
      const fullPath = p.startsWith("/") ? p : `${scopePath || ""}/${p}`;
      updatePath(fullPath, e.target.checked);
    }
  }

  return (
    <input
      type="checkbox"
      className="checkbox-block"
      checked={!!resolved}
      onChange={handleChange}
    />
  );
}
