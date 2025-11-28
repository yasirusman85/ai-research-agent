import os
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
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
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

load_dotenv()

# --- DATABASE SETUP ---
DB_URI = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/agent_db")

# Global connection pool
pool = AsyncConnectionPool(conninfo=DB_URI, open=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Open pool
    print("Opening DB connection...")
    await pool.open()
    yield
    # SHUTDOWN: Close pool
    print("Closing DB connection...")
    await pool.close()

app = FastAPI(title="AI Research Agent", lifespan=lifespan)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
graph = builder.compile(checkpointer=checkpointer)

# --- API ENDPOINTS ---

class ChatRequest(BaseModel):
    query: str
    thread_id: str = "default_thread"

class FeedbackRequest(BaseModel):
    feedback: str
    thread_id: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    input_message = HumanMessage(content=request.query)

    # Invoke the graph
    result = await graph.ainvoke({"messages": [input_message]}, config=config)
    
    # Check current state to see if we are paused/stuck
    snapshot = await graph.aget_state(config)
    
    # If the last node executed was 'human_node', we are waiting for help
    if snapshot.next and "human_node" in snapshot.next:
         return {"response": "I am stuck and need your help.", "status": "paused"}

    final_response = result["messages"][-1].content
    return {"response": final_response, "status": "completed"}

@app.post("/human-feedback")
async def human_feedback(request: FeedbackRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Inject the human's feedback into the state
    await graph.aupdate_state(
        config, 
        {"messages": [HumanMessage(content=f"Here is the help you requested: {request.feedback}")]}, 
        as_node="human_node"
    )
    
    # Resume execution
    result = await graph.ainvoke(None, config=config)
    
    final_response = result["messages"][-1].content
    return {"response": final_response, "status": "completed"}

@app.get("/stream")
async def stream_agent(query: str, thread_id: str = "default_thread"):
    async def event_generator():
        inputs = {"messages": [HumanMessage(content=query)]}
        config = {"configurable": {"thread_id": thread_id}}
        
        async for event in graph.astream_events(inputs, config=config, version="v1"):
            kind = event["event"]
            
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
            elif kind == "on_tool_start":
                tool_name = event['name']
                msg = json.dumps({'type': 'log', 'content': f'Starting tool: {tool_name}'})
                yield f"data: {msg}\n\n"
            elif kind == "on_tool_end":
                tool_name = event['name']
                msg = json.dumps({'type': 'log', 'content': f'Tool finished: {tool_name}'})
                yield f"data: {msg}\n\n"
            elif kind == "on_chain_end" and event["name"] == "LangGraph":
                 yield f"data: {json.dumps({'type': 'done', 'content': 'Processing complete'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")