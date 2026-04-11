from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from ..config import get_settings
from ..firebase import get_db

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str

@router.post("")
async def chat_root(req: ChatRequest, settings=Depends(get_settings)):
    return await chat_with_bot(req, settings)

@router.post("/chat")
async def chat_with_bot(req: ChatRequest, settings=Depends(get_settings)):
    api_key = settings.gemini_api_key
    
    # تأكد من أن الساروت كاين
    if not api_key or api_key == "your_gemini_api_key_here":
        error_msg = "API key is not configured. Please add GEMINI_API_KEY to your .env file."
        return {"reply": error_msg, "response": error_msg, "message": error_msg}

    # إعداد Gemini بموديل مضمون
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # جلب معلومات السلعة من Firebase
    try:
        root_ref = get_db()
        products_data = root_ref.child("products").get()
    except Exception as fb_err:
        print("Firebase Error:", fb_err)
        products_data = None

    product_context = ""
    if products_data and isinstance(products_data, dict):
        items = []
        for pid, data in products_data.items():
            if isinstance(data, dict):
                name = data.get("name", "Unknown")
                price = data.get("price", "N/A")
                stock = data.get("stock", 0)
                items.append(f"- {name}: {price} Dh (Stock: {stock})")
        product_context = "\n".join(items) if items else "حاليا ماكاين حتى منتوج فـ الستوك."
    else:
        product_context = "حاليا ماكاين حتى منتوج فـ الستوك."

    user_message = req.message
    
    # بناء التعليمات ديال البوت
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
        # استدعاء Gemini بطريقة Async باش ما يتبلوكاش السيرفر
        response = await model.generate_content_async(prompt)
        
        # غانصيفطو الجواب بـ 3 ديال السميات باش السيت يلقاه كيفما كان مبرمج!
        return {
            "reply": response.text,
            "response": response.text,
            "message": response.text
        }
    except Exception as e:
        print("Gemini Error:", e)
        err_msg = "سمح ليا أخويا، كاين شي مشكل تقني فهاد اللحظة، عاود سولني من بعد شوية! 🙏"
        return {"reply": err_msg, "response": err_msg, "message": err_msg}