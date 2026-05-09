from google.adk.agents import Agent
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.common_modifiers import remove_strict_validation
from .resources import get_resources
from .a2ui_utils import a2ui_callback

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
        "Column, Row, CheckBox, DataTable, Icon, Button, and Divider "
        "components to build a visual response.\n\n"
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
        "Use icons for visual emphasis (e.g., check_circle, warning, error, "
        "briefcase, dumbbell, book, flight, restaurant). "
        "Use CheckBox for todo items and checklists. "
        "Use DataTable for tabular data. "
        "Use buttons for user actions (primary for main action, "
        "secondary for alternative). "
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
    tools=[get_resources],
    after_model_callback=a2ui_callback,
)
