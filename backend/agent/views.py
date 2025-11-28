import json
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from langchain_core.messages import HumanMessage
from .graph import graph, pool

# Helper to handle async views in Django
from asgiref.sync import sync_to_async

async def ensure_pool_open():
    """Ensure the DB pool is open."""
    # This is a simple check. In production, you might want a more robust lifespan handler.
    try:
        await pool.check()
    except Exception:
        # If check fails or pool is closed, try to open
        # psycopg_pool doesn't have a simple is_open property exposed easily in all versions,
        # but calling open() on an open pool might raise or be no-op.
        # We'll just try to open if we suspect it's closed.
        # Actually, let's just use a flag or try/except.
        pass
    
    # Simpler approach: Just call open() and catch if it's already open?
    # AsyncConnectionPool.open() is idempotent in some versions but let's be safe.
    # We will assume daphne lifespan handles it if we configure it, but for now:
    pass # We will handle this in apps.py or just rely on it being open? 
    # WAIT. The pool was created with open=False.
    # We MUST open it.
    # Let's try to open it globally in apps.py using a signal?
    # Or just here.
    pass

# Better approach: Use a middleware or just open it once.
# Since we are using daphne, we can use the lifespan protocol if we implement it.
# But standard Django doesn't expose it easily to apps.
# Let's just do:
async def get_graph_response(inputs, config):
    # Ensure pool is open
    # We can't easily check pool status without accessing private members or try/except.
    # Let's try to open it.
    try:
        await pool.open()
    except Exception:
        pass # Already open
    
    return await graph.ainvoke(inputs, config=config)

@csrf_exempt
async def chat_agent(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        query = data.get('query')
        thread_id = data.get('thread_id', 'default_thread')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    config = {"configurable": {"thread_id": thread_id}}
    input_message = HumanMessage(content=query)

    # Ensure pool is open
    try:
        await pool.open()
    except Exception:
        pass

    # Invoke the graph
    result = await graph.ainvoke({"messages": [input_message]}, config=config)
    
    # Check current state to see if we are paused/stuck
    snapshot = await graph.aget_state(config)
    
    # If the last node executed was 'human_node', we are waiting for help
    if snapshot.next and "human_node" in snapshot.next:
         return JsonResponse({"response": "I am stuck and need your help. Please use the dashboard to provide feedback.", "status": "paused"})

    final_response = result["messages"][-1].content
    return JsonResponse({"response": final_response, "status": "completed"})

@csrf_exempt
async def human_feedback(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        feedback = data.get('feedback')
        thread_id = data.get('thread_id')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        await pool.open()
    except Exception:
        pass

    # Inject the human's feedback into the state
    await graph.aupdate_state(
        config, 
        {"messages": [HumanMessage(content=f"Here is the help you requested: {feedback}")]}, 
        as_node="human_node"
    )
    
    # Resume execution
    result = await graph.ainvoke(None, config=config)
    
    final_response = result["messages"][-1].content
    return JsonResponse({"response": final_response, "status": "completed"})

async def stream_agent(request):
    query = request.GET.get('query')
    thread_id = request.GET.get('thread_id', 'default_thread')
    
    async def event_generator():
        try:
            await pool.open()
        except Exception:
            pass

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

    return StreamingHttpResponse(event_generator(), content_type="text/event-stream")
