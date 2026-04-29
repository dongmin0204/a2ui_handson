import { useState, useEffect } from "react";
import { A2UIPageSpec, ServerAction } from "./types";
import { sampleSpec } from "./sampleSpec";
import { A2UIRenderer } from "./renderer/A2UIRenderer";
import { PromptInput } from "./components/PromptInput";
import { JsonViewer } from "./components/JsonViewer";
import "./App.css";

export default function App() {
  const [spec, setSpec] = useState<A2UIPageSpec | null>(sampleSpec);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showJson, setShowJson] = useState(false);

  // sampleSpec.ts 수정 → Vite HMR → 즉시 반영
  useEffect(() => {
    setSpec(sampleSpec);
  }, []);

  async function handleGenerate(prompt: string) {
    try {
      setIsLoading(true);
      setError(null);
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ error: "생성 실패" }));
        throw new Error(errData.error || `서버 오류 ${res.status}`);
      }
      const data = await res.json();
      setSpec(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAction(action: ServerAction) {
    if (!spec) return;
    try {
      setIsLoading(true);
      setError(null);
      const res = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: action.name,
          context: action.context,
          currentDataModel: spec.dataModel,
          surfaceId: spec.surface.surfaceId,
        }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ error: "Action 실패" }));
        throw new Error(errData.error || `서버 오류 ${res.status}`);
      }
      const data = await res.json();
      setSpec((prev) =>
        prev
          ? {
              ...prev,
              dataModel: data.dataModel,
              ...(data.components ? { components: data.components } : {}),
            }
          : null
      );
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-row">
          <div>
            <h1 className="app-logo">🤖 A2UI Agent Tool Page</h1>
            <p className="app-subtitle">AI가 설계하고, React가 렌더링합니다</p>
          </div>
          <button
            className="json-toggle-btn"
            onClick={() => setShowJson((v) => !v)}
          >
            {showJson ? "🎨 UI 보기" : "{ } JSON 보기"}
          </button>
        </div>
      </header>

      <PromptInput onSubmit={handleGenerate} isLoading={isLoading} />

      {error && <div className="error-banner">❌ {error}</div>}

      {spec ? (
        showJson ? (
          <JsonViewer spec={spec} />
        ) : (
          <A2UIRenderer spec={spec} onAction={handleAction} isLoading={isLoading} />
        )
      ) : (
        <div className="empty-state">
          <p>프롬프트를 입력하면 AI가 Tool Page를 생성합니다</p>
        </div>
      )}
    </div>
  );
}
