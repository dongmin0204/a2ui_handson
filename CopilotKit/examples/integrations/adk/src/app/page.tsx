"use client";

import { PlansCard } from "@/components/plans";
import { StockChart } from "@/components/stock-chart";
import { WeatherCard } from "@/components/weather";
import { AgentState } from "@/lib/types";
import {
  useCoAgent,
  useRenderToolCall,
} from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotSidebar } from "@copilotkit/react-ui";

export default function CopilotKitPage() {
  return (
    <YourMainContent />
  );
}

function YourMainContent() {
  // Shared State: https://docs.copilotkit.ai/adk/shared-state
  const { state, setState } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: {
      plans: [
        "오늘 데모 화면 문구를 한국어로 다듬기",
      ],
      themeColor: "#6366f1",
      textColor: "#ffffff",
    },
  });
  const themeColor = state.themeColor || "#6366f1";
  const textColor = state.textColor || "#ffffff";

  //Generative UI: https://docs.copilotkit.ai/adk/generative-ui
  useRenderToolCall(
    {
      name: "get_weather",
      description: "Get the weather for a given location.",
      parameters: [{ name: "location", type: "string", required: true }],
      render: ({ args, result }) => {
        return (
          <WeatherCard
            location={args.location}
            themeColor={themeColor}
            textColor={textColor}
          />
        );
      },
    },
    [themeColor, textColor],
  );

  useRenderToolCall(
    {
      name: "research_stock_chart",
      description:
        "Research a stock or market symbol and render a compact chart.",
      parameters: [{ name: "request", type: "string", required: true }],
      render: ({ result }) => {
        if (!result || !Array.isArray(result.points) || result.points.length === 0) {
          return <></>;
        }

        return (
          <StockChart
            result={result}
            themeColor={themeColor}
            textColor={textColor}
          />
        );
      },
    },
    [themeColor, textColor],
  );

  return (
    <main
      style={
        { "--copilot-kit-primary-color": themeColor } as CopilotKitCSSProperties
      }
    >
      <CopilotSidebar
        disableSystemMessage={true}
        clickOutsideToClose={false}
        defaultOpen={true}
        labels={{
          title: "AI 도우미",
          initial: "안녕하세요. 오늘의 계획, 날씨, 주식 차트를 도와드릴게요.",
        }}
        suggestions={[
          {
            title: "날씨 카드",
            message: "서울 날씨 보여줘.",
          },
          {
            title: "주식 차트",
            message: "구글 검색으로 엔비디아 5일 차트 보여줘.",
          },
          {
            title: "테마 변경",
            message: "테마를 초록색으로 바꿔줘.",
          },
          {
            title: "계획 추가",
            message: "오늘 할 계획 하나 추가해줘.",
          },
          {
            title: "계획 수정",
            message: "계획이 있으면 하나만 지워줘.",
          },
          {
            title: "계획 읽기",
            message: "지금 계획 목록 알려줘.",
          },
        ]}
      >
        <div
          style={{ backgroundColor: themeColor, color: textColor }}
          className="hero-shell h-screen flex justify-center items-center flex-col transition-colors duration-500"
        >
          <PlansCard state={state} setState={setState} />
        </div>
      </CopilotSidebar>
    </main>
  );
}
