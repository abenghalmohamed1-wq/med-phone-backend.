from fastapi import APIRouter, Query
from typing import List
from ..firebase import get_db

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get("", summary="Search products for the chatbot")
async def search_products(q: str = Query(..., min_length=1, description="Search query for product name, brand, or description")):
    """
    Dedicated search endpoint for the chatbot to retrieve real-time prices and stock availability.
    """
    db = get_db()
    products_data = db.child("products").get()
    
    if not products_data:
        return []
    
    results = []
    query = q.lower()
    
    # In a larger app, we would use a proper search engine or database indexing.
    # For this scale, a simple iteration over the products node is efficient.
    for pid, data in products_data.items():
        if not isinstance(data, dict):
            continue
            
        name = data.get("name", "").lower()
        brand = data.get("brand", "").lower()
        description = data.get("description", "").lower()
        
        if query in name or query in brand or query in description:
            results.append({
                "id": pid,
                "name": data.get("name"),
                "brand": data.get("brand"),
                "price": data.get("price"),
                "stock": data.get("stock", 0),
                "emoji": data.get("emoji", "📱"),
                "category": data.get("category"),
                "available": data.get("stock", 0) > 0
            })
            
    return results
