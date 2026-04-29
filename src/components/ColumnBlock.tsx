import "./ColumnBlock.css";

interface ColumnBlockProps {
  children: React.ReactNode;
  gap?: number;
  align?: string;
}

export function ColumnBlock({ children, gap = 8, align = "stretch" }: ColumnBlockProps) {
  const alignItems =
    align === "center" ? "center" :
    align === "start" ? "flex-start" :
    align === "end" ? "flex-end" :
    "stretch";

  return (
    <div
      className="column-block"
      style={{ gap: `${gap}px`, alignItems }}
    >
      {children}
    </div>
  );
}
