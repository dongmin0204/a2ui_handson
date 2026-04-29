import { useState } from "react";
import { A2UIPageSpec } from "../types";
import "./JsonViewer.css";

interface JsonViewerProps {
  spec: A2UIPageSpec;
}

type Tab = "surface" | "components" | "dataModel";

export function JsonViewer({ spec }: JsonViewerProps) {
  const [activeTab, setActiveTab] = useState<Tab>("components");

  const content =
    activeTab === "surface"
      ? spec.surface
      : activeTab === "components"
      ? spec.components
      : spec.dataModel;

  const jsonString = JSON.stringify(content, null, 2);

  return (
    <div className="json-viewer">
      <div className="json-viewer-tabs">
        {(["surface", "components", "dataModel"] as Tab[]).map((tab) => (
          <button
            key={tab}
            className={`json-tab ${activeTab === tab ? "active" : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === "surface" && "🌐 Surface"}
            {tab === "components" && "🧩 Components"}
            {tab === "dataModel" && "📦 DataModel"}
          </button>
        ))}
      </div>
      <div className="json-viewer-body">
        <pre className="json-content">
          <code dangerouslySetInnerHTML={{ __html: highlight(jsonString) }} />
        </pre>
      </div>
    </div>
  );
}

// 간단한 JSON syntax highlighting
function highlight(json: string): string {
  return json
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      (match) => {
        let cls = "json-number";
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = "json-key";
          } else {
            cls = "json-string";
          }
        } else if (/true|false/.test(match)) {
          cls = "json-boolean";
        } else if (/null/.test(match)) {
          cls = "json-null";
        }
        return `<span class="${cls}">${match}</span>`;
      }
    );
}
