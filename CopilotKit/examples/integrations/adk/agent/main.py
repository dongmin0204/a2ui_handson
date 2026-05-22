"""Shared State feature."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.tools import AgentTool
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import ToolContext
from google.adk.tools.google_search_agent_tool import GoogleSearchAgentTool
from google.adk.tools.google_search_agent_tool import create_google_search_agent
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()


class PlansState(BaseModel):
    """List of the plans being maintained."""

    plans: list[str] = Field(
        default_factory=list,
        description="The list of current plans",
    )
    themeColor: str = Field(
        default="#6366f1",
        description="Current theme color used by the frontend",
    )
    textColor: str = Field(
        default="#ffffff",
        description="Current text color used by the frontend",
    )


class StockChartPoint(BaseModel):
    label: str = Field(description="Short date label such as May 16")
    price: float = Field(description="Approximate closing price for the period")


class StockChartSource(BaseModel):
    title: str = Field(description="Human readable source title")
    url: str = Field(description="Public source URL")


class StockChartRequest(BaseModel):
    request: str = Field(
        description=(
            "The user's stock or market chart request. Include ticker, company, "
            "or index name when known."
        )
    )


class StockChartResult(BaseModel):
    symbol: str = Field(description="Ticker or market symbol, such as NVDA or SPY")
    company_name: str = Field(description="Company or index name")
    exchange: str = Field(description="Exchange or market identifier")
    currency: str = Field(description="Currency code, such as USD")
    timeframe: str = Field(description="Human readable window, such as 5D")
    market_summary: str = Field(
        description="Short summary grounded in Google Search findings"
    )
    points: List[StockChartPoint] = Field(
        description="Ordered points for rendering the chart, oldest to newest"
    )
    sources: List[StockChartSource] = Field(
        default_factory=list,
        description="Search sources used to ground the result",
    )


def set_plans(tool_context: ToolContext, new_plans: list[str]) -> Dict[str, str]:
    """
    Set the list of plans using the provided new list.

    Args:
        "new_plans": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The new list of plans to maintain",
        }

    Returns:
        Dict indicating success status and message
    """
    try:
        new_state = {"plans": new_plans}
        tool_context.state["plans"] = new_state["plans"]
        return {"status": "success", "message": "Plans updated successfully"}

    except Exception as e:
        return {"status": "error", "message": f"Error updating plans: {str(e)}"}


def get_weather(tool_context: ToolContext, location: str) -> Dict[str, str]:
    """Get the weather for a given location. Ensure location is fully spelled out."""
    return {"status": "success", "message": f"The weather in {location} is sunny."}


def set_theme_color(
    tool_context: ToolContext, themeColor: str, textColor: str = "#ffffff"
) -> Dict[str, str]:
    """Set the frontend theme and text colors using CSS color strings."""
    try:
        tool_context.state["themeColor"] = themeColor
        tool_context.state["textColor"] = textColor
        return {
            "status": "success",
            "message": f"Theme color set to {themeColor} with text color {textColor}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Error updating theme color: {str(e)}"}


stock_chart_analysis_agent = LlmAgent(
    name="research_stock_chart",
    model="gemini-2.5-flash",
    description=(
        "Research a stock or market symbol with Google Search and return compact "
        "chart data plus a short market summary."
    ),
    instruction="""
        You are a market research agent.

        Use Google Search grounding to answer the request.
        Return only JSON that matches the output schema.

        Requirements:
        - Focus on a single stock, ETF, or index that best matches the request.
        - Build a short recent chart window, usually 5 recent market data points.
        - Use approximate recent closing prices from grounded search results.
        - Sort points from oldest to newest.
        - Keep market_summary under 2 sentences.
        - Include 1 to 3 public sources when available.
        - If the user is vague, choose the clearest matching ticker.
        - Never invent impossible symbols. If uncertain, use the best grounded match.
    """,
    input_schema=StockChartRequest,
    output_schema=StockChartResult,
    tools=[
        GoogleSearchAgentTool(
            agent=create_google_search_agent("gemini-2.5-flash")
        )
    ],
)


def on_before_agent(callback_context: CallbackContext):
    """
    Initialize plans state if it doesn't exist.
    """

    if "plans" not in callback_context.state:
        callback_context.state["plans"] = []
    if "themeColor" not in callback_context.state:
        callback_context.state["themeColor"] = "#6366f1"
    if "textColor" not in callback_context.state:
        callback_context.state["textColor"] = "#ffffff"

    return None


# --- Define the Callback Function ---
#  modifying the agent's system prompt to include the current state of the plans list
def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    if agent_name == "PlansAgent":
        plans_json = "No plans yet"
        if "plans" in callback_context.state and callback_context.state["plans"] is not None:
            try:
                plans_json = json.dumps(callback_context.state["plans"], indent=2)
            except Exception as e:
                plans_json = f"Error serializing plans: {str(e)}"
        original_instruction = llm_request.config.system_instruction or types.Content(
            role="system", parts=[]
        )
        prefix = f"""You are a helpful assistant for maintaining a list of plans.
        This is the current state of the plan list: {plans_json}
        When you modify the plan list, whether adding, removing, or editing plans, use the set_plans tool to update the list."""
        if not isinstance(original_instruction, types.Content):
            original_instruction = types.Content(
                role="system", parts=[types.Part(text=str(original_instruction))]
            )
        if not original_instruction.parts:
            original_instruction.parts = [types.Part(text="")]

        if original_instruction.parts and len(original_instruction.parts) > 0:
            modified_text = prefix + (original_instruction.parts[0].text or "")
            original_instruction.parts[0].text = modified_text
        llm_request.config.system_instruction = original_instruction

    return None


# --- Define the Callback Function ---
def simple_after_model_modifier(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Stop the consecutive tool calling of the agent"""
    agent_name = callback_context.agent_name
    if agent_name == "PlansAgent":
        if llm_response.content and llm_response.content.parts:
            if (
                llm_response.content.role == "model"
                and llm_response.content.parts[0].text
            ):
                callback_context._invocation_context.end_invocation = True

        elif llm_response.error_message:
            return None
        else:
            return None  # Nothing to modify
    return None


plans_agent = LlmAgent(
    name="PlansAgent",
    model="gemini-2.5-flash",
    instruction="""
        When a user asks you to do anything regarding plans, tasks, schedules, or today's to-do items, you MUST use the set_plans tool.

        IMPORTANT RULES ABOUT PLANS AND THE SET_PLANS TOOL:
        1. Always use the set_plans tool for any plan-related request.
        2. Always pass the COMPLETE LIST of plans to the set_plans tool.
        3. Plans should be short, actionable, and concrete.
        4. If the user asks to revise priorities, reorder the full list accordingly.
        5. After using the tool, provide a brief summary of what you added, removed, or changed.

        Examples of when to use the set_plans tool:
        - "오늘 할 일 추가해줘" → Add a concrete plan item and send the full updated list.
        - "첫 번째 계획 지워줘" → Remove it and send the full remaining list.
        - "회의 준비를 제일 위로 올려줘" → Reorder the list and send the full updated list.


        IMPORTANT RULES ABOUT WEATHER AND THE GET_WEATHER TOOL:
        1. Only call the get_weather tool if the user asks you for the weather in a given location.
        2. If the user does not specify a location, you can use the location "Everywhere ever in the whole wide world"

        Examples of when to use the get_weather tool:
        - "What's the weather today in Tokyo?" → Use the tool with the location "Tokyo"
        - "Whats the weather right now" → Use the location "Everywhere ever in the whole wide world"
        - Is it raining in London? → Use the tool with the location "London"

        IMPORTANT RULES ABOUT STOCKS AND MARKET CHARTS:
        1. If the user asks for a stock, ETF, or index price trend, market chart, or asks you to use Google Search for market information, call the research_stock_chart tool.
        2. After calling the tool, briefly summarize the trend using the grounded result.
        3. Do not manually fabricate a chart or price series when the tool can be used.

        IMPORTANT RULES ABOUT FRONTEND THEME CHANGES:
        1. If the user asks to change the theme, color, accent color, or background color, call the set_theme_color tool.
        2. Always set both themeColor and textColor.
        3. textColor should usually be either "#ffffff" or "#000000" unless the user asks for another readable color.
        4. Pass CSS color strings such as "green", "#22c55e", "black", or "white".
        5. After calling the tool, briefly confirm the theme change.
        """,
    tools=[
        set_plans,
        get_weather,
        set_theme_color,
        AgentTool(agent=stock_chart_analysis_agent, skip_summarization=True),
    ],
    before_agent_callback=on_before_agent,
    before_model_callback=before_model_modifier,
    after_model_callback=simple_after_model_modifier,
)

adk_plans_agent = ADKAgent(
    adk_agent=plans_agent,
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

app = FastAPI(title="ADK Middleware Plans Agent")

add_adk_fastapi_endpoint(app, adk_plans_agent, path="/")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import os

    import uvicorn

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set!")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        print("   Get a key from: https://makersuite.google.com/app/apikey")
        print()

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
