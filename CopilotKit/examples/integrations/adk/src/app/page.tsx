"use client";

import { ProverbsCard } from "@/components/proverbs";
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
  // 🪁 Shared State: https://docs.copilotkit.ai/adk/shared-state
  const { state, setState } = useCoAgent<AgentState>({
    name: "my_agent",
    initialState: {
      proverbs: [
        "CopilotKit may be new, but its the best thing since sliced bread.",
      ],
      themeColor: "#6366f1",
    },
  });
  const themeColor = state.themeColor || "#6366f1";

  //🪁 Generative UI: https://docs.copilotkit.ai/adk/generative-ui
  useRenderToolCall(
    {
      name: "get_weather",
      description: "Get the weather for a given location.",
      parameters: [{ name: "location", type: "string", required: true }],
      render: ({ args, result }) => {
        return <WeatherCard location={args.location} themeColor={themeColor} />;
      },
    },
    [themeColor],
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

        return <StockChart result={result} themeColor={themeColor} />;
      },
    },
    [themeColor],
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
          title: "Popup Assistant",
          initial: "👋 Hi, there! You're chatting with an agent.",
        }}
        suggestions={[
          {
            title: "Generative UI",
            message: "Get the weather in San Francisco.",
          },
          {
            title: "Market Chart",
            message: "Use Google Search to show me a 5 day chart for Nvidia stock.",
          },
          {
            title: "Theme Color",
            message: "Set the theme to green.",
          },
          {
            title: "Write Agent State",
            message: "Add a proverb about AI.",
          },
          {
            title: "Update Agent State",
            message:
              "Please remove 1 random proverb from the list if there are any.",
          },
          {
            title: "Read Agent State",
            message: "What are the proverbs?",
          },
        ]}
      >
        <div
          style={{ backgroundColor: themeColor }}
          className="h-screen flex justify-center items-center flex-col transition-colors duration-300"
        >
          <ProverbsCard state={state} setState={setState} />
        </div>
      </CopilotSidebar>
    </main>
  );
}
