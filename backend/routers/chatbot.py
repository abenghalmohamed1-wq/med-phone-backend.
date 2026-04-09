from fastapi import APIRouter

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])

@router.get("", summary="Chatbot endpoint")
async def chatbot_root():
    return {"message": "Chatbot router is active"}