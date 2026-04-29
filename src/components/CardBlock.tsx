import "./CardBlock.css";

interface CardBlockProps {
  children: React.ReactNode;
}

export function CardBlock({ children }: CardBlockProps) {
  return <div className="card-block">{children}</div>;
}
