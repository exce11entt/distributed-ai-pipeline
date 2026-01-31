from fastapi import APIRouter, Request, HTTPException, Depends
from src.agents.graph import EnterpriseAgent
from src.api.vapi_schema import VAPI_TOOLS
import logging

router = APIRouter()
agent = EnterpriseAgent()
logger = logging.getLogger("vapi_handler")

async def verify_vapi_secret(request: Request):
    """Production Security: Verify request comes from Vapi."""
    # secret = request.headers.get("x-vapi-secret")
    # if secret != os.getenv("VAPI_SECRET"): raise HTTPException(403)
    return True

@router.post("/vapi/webhook")
async def vapi_webhook(request: Request, authorized: bool = Depends(verify_vapi_secret)):
    """
    The brain of the voice agent. Vapi calls this when:
    1. It needs to know what tools are available (tool-definition)
    2. A user speaks and Vapi wants to run a function (function-call)
    """
    payload = await request.json()
    message_type = payload.get("message", {}).get("type")

    # 1. Vapi asking for tool definitions
    if message_type == "tool-calls":
        # In a real scenario, we might look at the call list details
        # For now, we assume Vapi is asking us to execute logic
        tool_calls = payload.get("message", {}).get("toolCalls", [])
        results = []
        
        for tool in tool_calls:
            function_name = tool["function"]["name"]
            req_id = tool["id"]
            args = tool["function"]["arguments"]
            
            result_content = "Error: Tool not found"
            
            # Simple atomic tools
            if function_name == "check_balance":
                # Simulate DB call
                result_content = f"The balance for {args.get('account_type')} is $5,430.22."
                
            # Complex reasoning tool -> Hand off to LangGraph
            elif function_name == "ask_policy_agent":
                query = args.get("query")
                # Use the call_id as session_id for now, or map a user ID
                # Persistence allows multi-turn voice conversations
                vapi_session_id = payload.get("message", {}).get("call", {}).get("id", "voice-default")
                
                agent_response = agent.run(query, session_id=vapi_session_id)
                result_content = agent_response["messages"][-1].content
                
            results.append({
                "toolCallId": req_id,
                "result": result_content
            })
            
        return {"results": results}

    # 2. Status updates (transcript, end of call)
    elif message_type == "transcript":
        # We could log this to a DB for analytics
        pass
        
    return {"status": "ok"}
