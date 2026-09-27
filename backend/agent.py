import config  # loads dotenv and sets environment variables
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

# Model reads GROQ_API_KEY from .env
import os
import config
model = ChatGroq(model="qwen/qwen3.8-27b", api_key=config.GROQ_API_KEY)

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
