from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

@tool
def search_inventory(query: str) -> str:
    """Search mock inventory."""
    return f"Found items matching: {query}"

memory = MemorySaver()
agent = create_react_agent(
    model=model,
    tools=[search_inventory],
    checkpointer=memory,
)
