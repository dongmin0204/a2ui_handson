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


class ProverbsState(BaseModel):
    """List of the proverbs being written."""

    proverbs: list[str] = Field(
        default_factory=list,
        description="The list of already written proverbs",
    )
    themeColor: str = Field(
        default="#6366f1",
        description="Current theme color used by the frontend",
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


def set_proverbs(tool_context: ToolContext, new_proverbs: list[str]) -> Dict[str, str]:
    """
    Set the list of provers using the provided new list.

    Args:
        "new_proverbs": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The new list of proverbs to maintain",
        }

    Returns:
        Dict indicating success status and message
    """
    try:
        # Put this into a state object just to confirm the shape
        new_state = {"proverbs": new_proverbs}
        tool_context.state["proverbs"] = new_state["proverbs"]
        return {"status": "success", "message": "Proverbs updated successfully"}

    except Exception as e:
        return {"status": "error", "message": f"Error updating proverbs: {str(e)}"}


def get_weather(tool_context: ToolContext, location: str) -> Dict[str, str]:
    """Get the weather for a given location. Ensure location is fully spelled out."""
    return {"status": "success", "message": f"The weather in {location} is sunny."}


def set_theme_color(tool_context: ToolContext, themeColor: str) -> Dict[str, str]:
    """Set the frontend theme color using a CSS color string."""
    try:
        tool_context.state["themeColor"] = themeColor
        return {"status": "success", "message": f"Theme color set to {themeColor}"}
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
    Initialize proverbs state if it doesn't exist.
    """

    if "proverbs" not in callback_context.state:
        # Initialize with default recipe
        default_proverbs = []
        callback_context.state["proverbs"] = default_proverbs
    if "themeColor" not in callback_context.state:
        callback_context.state["themeColor"] = "#6366f1"

    return None


# --- Define the Callback Function ---
#  modifying the agent's system prompt to incude the current state of the proverbs list
def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    if agent_name == "ProverbsAgent":
        proverbs_json = "No proverbs yet"
        if (
            "proverbs" in callback_context.state
            and callback_context.state["proverbs"] is not None
        ):
            try:
                proverbs_json = json.dumps(callback_context.state["proverbs"], indent=2)
            except Exception as e:
                proverbs_json = f"Error serializing proverbs: {str(e)}"
        # --- Modification Example ---
        # Add a prefix to the system instruction
        original_instruction = llm_request.config.system_instruction or types.Content(
            role="system", parts=[]
        )
        prefix = f"""You are a helpful assistant for maintaining a list of proverbs.
        This is the current state of the list of proverbs: {proverbs_json}
        When you modify the list of proverbs (wether to add, remove, or modify one or more proverbs), use the set_proverbs tool to update the list."""
        # Ensure system_instruction is Content and parts list exists
        if not isinstance(original_instruction, types.Content):
            # Handle case where it might be a string (though config expects Content)
            original_instruction = types.Content(
                role="system", parts=[types.Part(text=str(original_instruction))]
            )
        if not original_instruction.parts:
            original_instruction.parts = [types.Part(text="")]

        # Modify the text of the first part
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
    # --- Inspection ---
    if agent_name == "ProverbsAgent":
        if llm_response.content and llm_response.content.parts:
            # Assuming simple text response for this example
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


proverbs_agent = LlmAgent(
    name="ProverbsAgent",
    model="gemini-2.5-flash",
    instruction="""
        When a user asks you to do anything regarding proverbs, you MUST use the set_proverbs tool.

        IMPORTANT RULES ABOUT PROVERBS AND THE SET_PROVERBS TOOL:
        1. Always use the set_proverbs tool for any proverbs-related requests
        2. Always pass the COMPLETE LIST of proverbs to the set_proverbs tool. If the list had 5 proverbs and you removed one, you must pass the complete list of 4 remaining proverbs.
        3. You can use existing proverbs if one is relevant to the user's request, but you can also create new proverbs as required.
        4. Be creative and helpful in generating complete, practical proverbs
        5. After using the tool, provide a brief summary of what you create, removed, or changed        7.

        Examples of when to use the set_proverbs tool:
        - "Add a proverb about soap" → Use tool with an array containing the existing list of proverbs with the new proverb about soap at the end.
        - "Remove the first proverb" → Use tool with an array containing the all of the existing proverbs except the first one"
        - "Change any proverbs about cats to mention that they have 18 lives" → If no proverbs mention cats, do not use the tool. If one or more proverbs do mention cats, change them to mention cats having 18 lives, and use the tool with an array of all of the proverbs, including ones that were changed and ones that did not require changes.

        Do your best to ensure proverbs plausibly make sense.


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
        2. Pass a CSS color string such as "green", "#22c55e", or "rgb(34,197,94)".
        3. After calling the tool, briefly confirm the theme change.
        """,
    tools=[
        set_proverbs,
        get_weather,
        set_theme_color,
        AgentTool(agent=stock_chart_analysis_agent, skip_summarization=True),
    ],
    before_agent_callback=on_before_agent,
    before_model_callback=before_model_modifier,
    after_model_callback=simple_after_model_modifier,
)

# Create ADK middleware agent instance
adk_proverbs_agent = ADKAgent(
    adk_agent=proverbs_agent,
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True,
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Proverbs Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_proverbs_agent, path="/")


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
