import { useState } from "react";
import "./PromptInput.css";

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  isLoading: boolean;
}

export function PromptInput({ onSubmit, isLoading }: PromptInputProps) {
  const [value, setValue] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim() || isLoading) return;
    onSubmit(value.trim());
    setValue("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!value.trim() || isLoading) return;
      onSubmit(value.trim());
      setValue("");
    }
  }

  return (
    <form className="prompt-input-form" onSubmit={handleSubmit}>
      <div className="prompt-input-wrapper">
        <textarea
          className="prompt-input"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="어떤 Agent Tool Page를 만들까요? (예: 오늘의 운동 루틴 관리 페이지) — Enter로 전송, Shift+Enter로 줄바꿈"
          disabled={isLoading}
          rows={2}
        />
        <button
          type="submit"
          className="prompt-submit-btn"
          disabled={isLoading || !value.trim()}
        >
          {isLoading ? "생성 중..." : "생성 →"}
        </button>
      </div>
    </form>
  );
}
