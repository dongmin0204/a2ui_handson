import { useDataModel } from "../hooks/useDataModel";
import "./TextBlock.css";

interface TextBlockProps {
  text?: any;
  variant?: string;
  color?: string;
  scopePath?: string;
}

export function TextBlock({ text, variant = "body", color, scopePath }: TextBlockProps) {
  const { resolve } = useDataModel();
  const resolved = resolve(text, scopePath);

  const tag = variant === "headline" ? "h1" : variant === "title" ? "h2" : "span";

  return (
    <span
      className={`text-block text-${variant}${color ? ` text-color-${color}` : ""}`}
    >
      {resolved ?? ""}
    </span>
  );
}
