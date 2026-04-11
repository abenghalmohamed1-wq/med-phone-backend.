from fastapi import APIRouter, Depends
from pydantic import BaseModel
import google.generativeai as genai
import os
import logging
from ..config import get_settings
from ..firebase import get_db

logger = logging.getLogger("med_phone.chatbot")

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


class ChatRequest(BaseModel):
    message: str


async def _handle_chat(req: ChatRequest, settings) -> dict:
    # ── 1. Read API key ────────────────────────────────────────────────────────
    # Try settings first, then fall back to direct OS env var
    api_key = settings.gemini_api_key or os.environ.get("GEMINI_API_KEY", "")

    logger.info(f"[Chatbot] Gemini key present: {bool(api_key)} | length: {len(api_key)}")

    if not api_key:
        msg = "GEMINI_API_KEY is not set. Please add it as an environment variable on Render."
        logger.error(f"[Chatbot] {msg}")
        return {"reply": msg}

    # ── 2. Configure Gemini ────────────────────────────────────────────────────
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # ── 3. Fetch products from Firebase ───────────────────────────────────────
    product_context = "لا تتوفر معلومات عن المنتجات حاليا."
    try:
        root_ref = get_db()
        products_data = root_ref.child("products").get()
        logger.info(f"[Chatbot] Firebase products fetched: {type(products_data)}")

        if products_data and isinstance(products_data, dict):
            items = []
            for pid, data in products_data.items():
                if isinstance(data, dict):
                    name  = data.get("name",  "Unknown")
                    price = data.get("price", "N/A")
                    stock = data.get("stock", 0)
                    items.append(f"- {name}: {price} Dh (Stock: {stock})")
            if items:
                product_context = "\n".join(items)
                logger.info(f"[Chatbot] Loaded {len(items)} products into context.")
            else:
                product_context = "حاليا ماكاين حتى منتوج فـ الستوك."
        else:
            product_context = "حاليا ماكاين حتى منتوج فـ الستوك."

    except Exception as fb_err:
        logger.error(f"[Chatbot] Firebase error: {fb_err}")
        # Continue without product context — chatbot still responds

    # ── 4. Build prompt ────────────────────────────────────────────────────────
    user_message = req.message
    prompt = f"""أنت مساعد ذكي اسمك 'Med Phone Bot' تعمل في متجر إلكتروني للهواتف في المغرب. تتحدث بالدارجة المغربية.

المنتجات المتوفرة في المخزن:
{product_context}

تعليمات:
1. أجب العميل بالدارجة المغربية بأسلوب لطيف ومحترم.
2. أعطه السعر والمعلومات الدقيقة إذا كان المنتج متوفرا في المخزن.
3. إذا سألك عن شيء غير موجود، اعتذر وقترح بديلا قريبا إذا وجد.
4. كن مختصرا ومفيدا ولا تخرج عن الموضوع.
5. أجب فقط على الأسئلة المتعلقة بالهواتف أو بمتجرنا.

سؤال العميل: "{user_message}"
"""

    # ── 5. Call Gemini ─────────────────────────────────────────────────────────
    try:
        response = await model.generate_content_async(prompt)
        reply = response.text
        logger.info(f"[Chatbot] Gemini replied successfully ({len(reply)} chars).")
        return {"reply": reply}
    except Exception as e:
        logger.error(f"[Chatbot] Gemini error: {e}")
        return {"reply": "سمح ليا أخويا، كاين شي مشكل تقني فهاد اللحظة، عاود سولني من بعد شوية! 🙏"}


# ── Routes — both /api/chatbot and /api/chatbot/chat point here ────────────────

@router.post("")
async def chat_root(req: ChatRequest, settings=Depends(get_settings)):
    return await _handle_chat(req, settings)


@router.post("/chat")
async def chat_with_bot(req: ChatRequest, settings=Depends(get_settings)):
    return await _handle_chat(req, settings)