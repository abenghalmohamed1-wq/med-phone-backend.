"""
routers/products.py — Product catalogue backed by Firebase Realtime Database.

GET    /api/products              — list / filter products
POST   /api/products              — create a product   (auth required)
GET    /api/products/{id}         — get a single product
PUT    /api/products/{id}         — update a product   (auth required)
DELETE /api/products/{id}         — delete a product   (auth required)
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import Optional, List
from datetime import datetime, timezone
from ..firebase import get_db
from ..models import Product, ProductCreate, Category
from ..dependencies import get_current_user, UserProfile

router = APIRouter(prefix="/api/products", tags=["Products"])

NODE = "products"


def _to_product(pid: str, data: dict) -> Product:
    data["id"] = pid
    return Product(**data)


# ── List / filter ─────────────────────────────────────────────────────────────

@router.get("", response_model=List[Product], summary="List products")
async def list_products(
    category: Optional[Category] = Query(None, description="Filter by category"),
    brand:    Optional[str]      = Query(None, description="Filter by brand name"),
    limit:    int                = Query(50, ge=1, le=200),
):
    root = get_db()
    raw  = root.child(NODE).get() or {}

    products: List[Product] = []
    for pid, data in raw.items():
        if not isinstance(data, dict):
            continue
        if category and data.get("category") != category.value:
            continue
        if brand and data.get("brand", "").lower() != brand.lower():
            continue
        products.append(_to_product(pid, data))
        if len(products) >= limit:
            break

    return products


# ── Single product ────────────────────────────────────────────────────────────

@router.get("/{product_id}", response_model=Product, summary="Get product by ID")
async def get_product(product_id: str):
    root = get_db()
    data = root.child(NODE).child(product_id).get()
    if not data:
        raise HTTPException(status_code=404, detail="Product not found")
    return _to_product(product_id, data)


# ── Create ────────────────────────────────────────────────────────────────────

@router.post("", response_model=Product, status_code=status.HTTP_201_CREATED, summary="Create product")
async def create_product(
    product: ProductCreate,
    _user:   UserProfile = Depends(get_current_user),
):
    root = get_db()
    data = product.model_dump()
    data["category"]   = data["category"].value
    data["created_at"] = datetime.now(timezone.utc).isoformat()

    ref = root.child(NODE).push(data)   # push() returns a Reference with a new key
    return _to_product(ref.key, data)


# ── Update ────────────────────────────────────────────────────────────────────

@router.put("/{product_id}", response_model=Product, summary="Update product")
async def update_product(
    product_id: str,
    product:    ProductCreate,
    _user:      UserProfile = Depends(get_current_user),
):
    root = get_db()
    ref  = root.child(NODE).child(product_id)
    if not ref.get():
        raise HTTPException(status_code=404, detail="Product not found")

    data             = product.model_dump()
    data["category"] = data["category"].value
    ref.update(data)
    return _to_product(product_id, ref.get())


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete product")
async def delete_product(
    product_id: str,
    _user:      UserProfile = Depends(get_current_user),
):
    root = get_db()
    ref  = root.child(NODE).child(product_id)
    if not ref.get():
        raise HTTPException(status_code=404, detail="Product not found")
    ref.delete()
