from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.agents.graph import EnterpriseAgent
from src.core.streaming import stream_generator
from src.core.security import get_api_key, security_service
from langchain_core.messages import HumanMessage
import uvicorn
import os
from dotenv import load_dotenv

from src.api.vapi_routes import router as vapi_router

load_dotenv()

app = FastAPI(title="Enterprise Agentic Voice API")
app.include_router(vapi_router)

# Initialize the agent
agent = EnterpriseAgent()

class ChatRequest(BaseModel):
    user_input: str
    session_id: str = "default-session"

@app.post("/chat")
async def chat(request: ChatRequest, api_key: str = Depends(get_api_key)):
    try:
        # Security: Scrub Input
        safe_input = security_service.mask_pii(request.user_input)
        if not security_service.validate_input(safe_input):
            raise HTTPException(status_code=400, detail="Invalid or malicious input detected.")

        # Persistence with session_id enables long-term memory
        result = agent.run(safe_input, session_id=request.session_id)
        # Final AI message and the trace of steps taken
        return {
            "response": result["messages"][-1].content,
            "steps_taken": [m.content for m in result["messages"] if hasattr(m, "content")],
            "is_complete": result["is_complete"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, api_key: str = Depends(get_api_key)):
    """
    Server-Sent Events (SSE) endpoint.
    Streams the agent's thought process and final answer token-by-token.
    """
    # Security: Scrub Input
    safe_input = security_service.mask_pii(request.user_input)
    
    inputs = {
        "messages": [HumanMessage(content=safe_input)],
        "is_complete": False,
        "context": []
    }
    
    # Trace principal tip: explicitly naming the run helps debugging in LangSmith
    config = {"configurable": {"session_id": request.session_id}}
    
    return StreamingResponse(
        stream_generator(agent.graph, inputs),
        media_type="text/event-stream"
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "agent": "initialized"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
