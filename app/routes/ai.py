from fastapi import APIRouter, HTTPException
from app.schemas.ai import ChatRequest, ChatResponse
from app.services.ai import process_message

router = APIRouter(prefix="/ai")


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest):
    """Handle a simple chat request by delegating to the AI agent."""
    try:
        answer = await process_message(body.message)
        return ChatResponse(answer=answer)
    except Exception as exc:
        # Log the exception in a real application
        raise HTTPException(status_code=500, detail="Internal server error")
