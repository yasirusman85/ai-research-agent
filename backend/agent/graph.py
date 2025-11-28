import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

load_dotenv()

# --- DATABASE SETUP ---
DB_URI = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/agent_db")

# Global connection pool
pool = AsyncConnectionPool(conninfo=DB_URI, open=False)

# --- GRAPH SETUP ---

# 1. Setup Tools
search_tool = DuckDuckGoSearchRun()
tools = [search_tool]

# 2. Setup LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant" 
)
llm_with_tools = llm.bind_tools(tools)

# 3. Define State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 4. Define Nodes
def agent_node(state: AgentState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content="You are a helpful assistant. Search for the answer, then summarize it.")] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def human_node(state: AgentState):
    print("--- Entered Human Node ---")
    return {"messages": [SystemMessage(content="I am stuck. Please help me.")]}

# Router Logic
def custom_router(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    if any(isinstance(m, ToolMessage) for m in messages):
        return END
    
    if last_message.tool_calls:
        return "tools"
    
    # Trigger human help if specific keyword found or confidence is low
    if "help" in last_message.content.lower():
        return "human_node"
        
    return END

# 5. Build Graph
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_node("human_node", human_node)

# 6. Define Edges
builder.set_entry_point("agent")
builder.add_conditional_edges("agent", custom_router)
builder.add_edge("tools", "agent")
builder.add_edge("human_node", "agent") # Return to agent after human help

# 7. Compile Graph with Checkpointer
checkpointer = AsyncPostgresSaver(pool)
graph = builder.compile(checkpointer=checkpointer, interrupt_before=["human_node"])

async def initialize_graph():
    """Initialize the DB pool and checkpointer."""
    print("Opening DB connection for LangGraph...")
    await pool.open()
    # await checkpointer.setup() # Run manually via init_db script

async def close_graph():
    """Close the DB pool."""
    print("Closing DB connection for LangGraph...")
    await pool.close()
