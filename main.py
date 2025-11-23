import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain & LangGraph Imports
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

load_dotenv()

app = FastAPI(title="AI Research Agent")

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
    # Simpler system prompt for the 8B model
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content="You are a helpful assistant. Search for the answer, then summarize it.")] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# --- THE SAFETY BRAKE ---
def custom_router(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    # 1. Check if we have ALREADY searched.
    # If the history contains a ToolMessage, it means we have results.
    # So we force the agent to STOP and give the answer.
    if any(isinstance(m, ToolMessage) for m in messages):
        return END
    
    # 2. If we haven't searched yet, check if the AI wants to search.
    if last_message.tool_calls:
        return "tools"
    
    # 3. Otherwise, just end.
    return END

# 5. Build Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))

builder.set_entry_point("agent")

# Use our CUSTOM router instead of the default one
builder.add_conditional_edges("agent", custom_router)
builder.add_edge("tools", "agent")

graph = builder.compile()

class ChatRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"status": "active", "agent": "Safety Brake Enabled"}

@app.post("/chat")
def chat_agent(request: ChatRequest):
    inputs = {"messages": [HumanMessage(content=request.query)]}
    
    # Run the graph
    result = graph.invoke(inputs)
    
    final_response = result["messages"][-1].content
    return {"response": final_response}