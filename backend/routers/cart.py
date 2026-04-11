"""
routers/cart.py — Per-user shopping cart in Firebase Realtime Database.

GET    /api/cart              — view cart           (auth required)
POST   /api/cart/add          — add / increment     (auth required)
DELETE /api/cart/{pid}        — remove item         (auth required)
DELETE /api/cart              — clear cart          (auth required)
"""
from fastapi import APIRouter, Depends, HTTPException
from ..firebase import get_db
from ..models import CartItem, CartResponse, CartItemDetail, UserProfile
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/cart", tags=["Cart"])

NODE = "carts"


def _build_response(items_raw: dict, root) -> CartResponse:
    detail_items: list[CartItemDetail] = []
    total = 0.0

    for product_id, quantity in (items_raw or {}).items():
        data = root.child("products").child(product_id).get()
        if data:
            price = float(data.get("price", 0))
            total += price * int(quantity)
            detail_items.append(CartItemDetail(
                product_id=product_id,
                quantity=int(quantity),
                name=data.get("name", "Unknown"),
                price=price,
                emoji=data.get("emoji", "📱"),
            ))

    return CartResponse(items=detail_items, total=round(total, 2))


@router.get("", response_model=CartResponse, summary="View cart")
async def get_cart(user: UserProfile = Depends(get_current_user)):
    root      = get_db()
    items_raw = root.child(NODE).child(user.uid).child("items").get() or {}
    return _build_response(items_raw, root)


@router.post("/add", response_model=CartResponse, summary="Add item to cart")
async def add_to_cart(item: CartItem, user: UserProfile = Depends(get_current_user)):
    root      = get_db()
    cart_ref  = root.child(NODE).child(user.uid).child("items")
    items_raw = cart_ref.get() or {}

    current_qty            = int(items_raw.get(item.product_id, 0))
    items_raw[item.product_id] = current_qty + item.quantity
    cart_ref.set(items_raw)

    return _build_response(items_raw, root)


@router.delete("/{product_id}", response_model=CartResponse, summary="Remove item from cart")
async def remove_from_cart(product_id: str, user: UserProfile = Depends(get_current_user)):
    root      = get_db()
    cart_ref  = root.child(NODE).child(user.uid).child("items")
    items_raw = cart_ref.get() or {}

    items_raw.pop(product_id, None)
    cart_ref.set(items_raw)

    return _build_response(items_raw, root)


@router.delete("", response_model=CartResponse, summary="Clear cart")
async def clear_cart(user: UserProfile = Depends(get_current_user)):
    root = get_db()
    root.child(NODE).child(user.uid).child("items").set({})
    return CartResponse()
