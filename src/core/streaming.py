import asyncio
from typing import AsyncIterable, Any
from langchain_core.callbacks import AsyncIteratorCallbackHandler
from langchain_core.messages import BaseMessage

async def stream_generator(agent_runnable, inputs) -> AsyncIterable[str]:
    """
    Wraps the LangGraph agent execution to stream tokens.
    Note: LangGraph streaming is complex because it steps through nodes.
    For this demo, we will stream the final LLM calls.
    """
    # Create a queue to hold tokens
    callback = AsyncIteratorCallbackHandler()
    
    # We need to pass this callback to the LLM inside the agent.
    # This requires a small refactor of the Agent class to accept runtime config,
    # or we can use the .astream method of the graph itself if supported.
    
    # Simpler Approach for Demo: 
    # We will use the graph's .astream_events or .astream_log API which is 
    # the standard way to stream from LangGraph.
    
    async for event in agent_runnable.astream_events(inputs, version="v1"):
        kind = event["event"]
        
        # Filter for LLM generation events
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield f"data: {content}\n\n"
                
        # Optional: Stream tool usage events
        elif kind == "on_tool_start":
            tool_name = event["data"].get("name", "tool")
            yield f"event: tool_start\ndata: {tool_name}\n\n"

    yield "event: end\ndata: [DONE]\n\n"
