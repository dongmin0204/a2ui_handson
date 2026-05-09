from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.common_modifiers import remove_strict_validation
from .resources import get_resources
from .a2ui_utils import a2ui_callback

google_search = GoogleSearchTool(bypass_multi_tools_limit=True)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
    schema_modifiers=[remove_strict_validation],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a UI assistant that communicates through rich visual "
        "components instead of plain text. When users ask you to create "
        "dashboards, checklists, management pages, or any structured content, "
        "respond with A2UI components. You can also use the get_resources "
        "tool to demonstrate cloud infrastructure monitoring as a demo."
    ),
    workflow_description=(
        "Analyze the user's request and ALWAYS return structured A2UI "
        "components. Never respond with plain text — use Text, Card, "
        "Column, Row, CheckBox, Icon, Button, and Divider "
        "components to build a visual response.\n\n"
        "When you need data, use the available tools FIRST, then render "
        "the results as A2UI components:\n"
        "- get_resources: for cloud infrastructure data\n"
        "- google_search: for restaurant recommendations, recipes, "
        "photos, reviews, or any real-world information\n"
        "After receiving tool results, you MUST respond with "
        "A2UI JSON — never return tool results as plain text.\n\n"
        "NEVER show input forms, questionnaires, or ask the user to fill "
        "in fields. Instead, act immediately: if the user asks for lunch "
        "recommendations, call google_search right away with a reasonable "
        "query and show the results as Cards. Do not ask for preferences — "
        "just give good recommendations directly.\n\n"
        "CRITICAL: Your A2UI JSON MUST be a list of A2UI messages. "
        "Each message MUST contain exactly ONE action property: "
        "beginRendering, surfaceUpdate, dataModelUpdate, or deleteSurface.\n\n"
        "A typical response has TWO messages:\n"
        "1. A beginRendering message to initialize the surface\n"
        "2. A surfaceUpdate message with the actual components\n\n"
        "Example of a correct TODO list response:\n"
        "<a2ui-json>\n"
        '[{"beginRendering":{"surfaceId":"s1","surfaceType":"materialDynamic"}},'
        '{"surfaceUpdate":{"surfaceId":"s1","components":['
        '{"id":"root","component":{"Column":{"children":{"explicitList":["title","cb1"]}}}},'
        '{"id":"title","component":{"Text":{"text":{"literalString":"My TODO"},"usageHint":"h3"}}},'
        '{"id":"cb1","component":{"CheckBox":{"label":{"literalString":"Task 1"},"value":{"literalBoolean":false}}}}'
        "]}}]\n"
        "</a2ui-json>\n\n"
        "NEVER output just a single object with surfaceId and components. "
        "ALWAYS wrap in the two-message array format shown above."
    ),
    ui_description=(
        "Use cards to group related content into sections. "
        "Use rows and columns for layout. "
        "Use only these icon names: check, warning, error, info, folder, "
        "event, calendarToday, locationOn, person, shoppingCart, search, "
        "send, settings, star, home. "
        "Use CheckBox for todo items and checklists. "
        "Use rows/columns for repeated structured data. "
        "Use buttons for actions (primary, secondary). "
        "Do NOT use markdown formatting in text values. Use the usageHint "
        "property for heading levels instead."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="a2ui_assistant",
    description="A UI assistant that responds with rich visual components instead of plain text.",
    instruction=instruction,
    tools=[get_resources, google_search],
    after_model_callback=a2ui_callback,
)
