import "./RowBlock.css";

interface RowBlockProps {
  children: React.ReactNode;
  gap?: number;
  align?: string;
}

export function RowBlock({ children, gap = 8, align = "center" }: RowBlockProps) {
  const alignItems =
    align === "start" ? "flex-start" :
    align === "end" ? "flex-end" :
    "center";

  return (
    <div
      className="row-block"
      style={{ gap: `${gap}px`, alignItems }}
    >
      {children}
    </div>
  );
}
