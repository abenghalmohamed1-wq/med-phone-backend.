from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from ..config import get_settings
from ..firebase import get_db

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_with_bot(req: ChatRequest, settings=Depends(get_settings)):
    api_key = settings.gemini_api_key
    
    # Check if API key is set
    if not api_key or api_key == "your_gemini_api_key_here":
        return {"reply": "API key is not configured. Please add GEMINI_API_KEY to your .env file."}

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Fetch products from Firebase for context
    db = get_db()
    products_data = db.child("products").get()
    
    product_context = ""
    if products_data:
        items = []
        for pid, data in products_data.items():
            if isinstance(data, dict):
                name = data.get("name", "Unknown")
                price = data.get("price", "N/A")
                stock = data.get("stock", 0)
                items.append(f"- {name}: {price} Dh (Stock: {stock})")
        product_context = "\n".join(items)
    else:
        product_context = "No products currently in stock."

    user_message = req.message
    
    # Prompt construction
    prompt = f"""
أنت مساعد ذكي سميتك 'Med Phone Bot' خدام فمتجر إلكتروني ديال التليفونات فالمغرب. كتهضر بالدارجة المغربية.

المعلومات اللي عندنا فـ الستوك هي:
{product_context}

تعليمات:
1. جاوب الكليان بالدارجة المغربية بأسلوب زوين ومحترم.
2. عطيه الثمن والمعلومات الدقيقة يلا كان المنتوج متوفر فـ الستوك.
3. يلا سألك على شي حاجة ماكايناش، اعتذر منو وقوليه بلي ماعندناش حاليا ولكن اقترح عليه شي حاجة قريبة يلا كاينة.
4. حاول تكون مختصر ومفيد وما تخرجش على الموضوع.
5. جاوب غير على الأسئلة اللي عندها علاقة بالتليفونات أو المتجر ديالنا.

سؤال الكليان: "{user_message}"
"""

    try:
        response = model.generate_content(prompt)
        return {"reply": response.text}
    except Exception as e:
        print("Gemini Error:", e)
        return {"reply": "سمح ليا أخويا، كاين شي مشكل تقني فهاد اللحظة، عاود سولني من بعد شوية! 🙏"}