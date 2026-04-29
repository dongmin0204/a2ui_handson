import { useDataModel } from "../hooks/useDataModel";
import { ServerAction } from "../types";
import "./ButtonBlock.css";

interface ButtonBlockProps {
  label?: any;
  variant?: string;
  action?: ServerAction;
  onAction: (action: ServerAction) => void;
  isLoading: boolean;
}

export function ButtonBlock({
  label,
  variant = "primary",
  action,
  onAction,
  isLoading,
}: ButtonBlockProps) {
  const { resolve } = useDataModel();
  const resolvedLabel = resolve(label);

  function handleClick() {
    if (action) onAction(action);
  }

  return (
    <button
      className={`button-block button-${variant}`}
      onClick={handleClick}
      disabled={isLoading}
    >
      {isLoading && action ? "처리 중..." : resolvedLabel ?? "버튼"}
    </button>
  );
}
