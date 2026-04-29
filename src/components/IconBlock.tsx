import * as Icons from "lucide-react";
import "./IconBlock.css";

interface IconBlockProps {
  name: string;
  size?: number;
}

// kebab-case → PascalCase
function toPascalCase(str: string): string {
  return str
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("");
}

// 이모지 감지 (문자가 이모지인지)
function isEmoji(str: string): boolean {
  return /\p{Emoji}/u.test(str) && str.length <= 4;
}

export function IconBlock({ name, size = 24 }: IconBlockProps) {
  if (!name) return null;

  // 이모지면 span으로 표시
  if (isEmoji(name)) {
    return (
      <span className="icon-block" style={{ fontSize: size * 0.85 }}>
        {name}
      </span>
    );
  }

  // lucide-react 아이콘 동적 로드
  const iconName = toPascalCase(name);
  const IconComponent = (Icons as any)[iconName];

  if (!IconComponent) {
    // 아이콘 없으면 텍스트 fallback
    return (
      <span className="icon-block icon-fallback" style={{ fontSize: size * 0.6 }}>
        {name}
      </span>
    );
  }

  return <IconComponent className="icon-block" size={size} />;
}
