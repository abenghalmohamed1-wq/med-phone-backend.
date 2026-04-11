"""
routers/orders.py — Order management in Firebase Realtime Database.

POST  /api/orders               — place a new order        (auth required)
GET   /api/orders               — list orders for the user (auth required)
GET   /api/orders/{id}          — get a single order       (auth required)
PATCH /api/orders/{id}/status   — update status            (auth required)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime, timezone
from ..firebase import get_db
from ..models import Order, OrderCreate, OrderStatus, CartItem
from ..dependencies import get_current_user, UserProfile

router = APIRouter(prefix="/api/orders", tags=["Orders"])

NODE = "orders"


def _to_order(oid: str, data: dict) -> Order:
    data["id"] = oid
    return Order(**data)


def _calculate_total(items: List[CartItem], root) -> float:
    total = 0.0
    for item in items:
        data = root.child("products").child(item.product_id).get()
        if data:
            total += float(data.get("price", 0)) * item.quantity
    return round(total, 2)


# ── Place order ───────────────────────────────────────────────────────────────

@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED, summary="Place order")
async def place_order(
    order:        OrderCreate,
    current_user: UserProfile = Depends(get_current_user),
):
    root  = get_db()
    total = _calculate_total(order.items, root)

    data = {
        "user_uid":   current_user.uid,
        "items":      [i.model_dump() for i in order.items],
        "shipping":   order.shipping.model_dump(),
        "notes":      order.notes,
        "status":     OrderStatus.pending.value,
        "total":      total,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    ref = root.child(NODE).push(data)
    return _to_order(ref.key, data)


# ── List user orders ──────────────────────────────────────────────────────────

@router.get("", response_model=List[Order], summary="List my orders")
async def list_orders(current_user: UserProfile = Depends(get_current_user)):
    root = get_db()
    raw  = root.child(NODE).get() or {}

    orders = []
    for oid, data in raw.items():
        if isinstance(data, dict) and data.get("user_uid") == current_user.uid:
            orders.append(_to_order(oid, data))

    # Newest first
    orders.sort(key=lambda o: o.created_at or "", reverse=True)
    return orders


# ── Single order ──────────────────────────────────────────────────────────────

@router.get("/{order_id}", response_model=Order, summary="Get order")
async def get_order(order_id: str, current_user: UserProfile = Depends(get_current_user)):
    root = get_db()
    data = root.child(NODE).child(order_id).get()

    if not data:
        raise HTTPException(status_code=404, detail="Order not found")

    order = _to_order(order_id, data)
    if order.user_uid != current_user.uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    return order


# ── Update status ─────────────────────────────────────────────────────────────

@router.patch("/{order_id}/status", response_model=Order, summary="Update order status")
async def update_status(
    order_id:     str,
    new_status:   OrderStatus,
    current_user: UserProfile = Depends(get_current_user),
):
    root = get_db()
    ref  = root.child(NODE).child(order_id)
    data = ref.get()

    if not data:
        raise HTTPException(status_code=404, detail="Order not found")

    order = _to_order(order_id, data)
    if order.user_uid != current_user.uid:
        raise HTTPException(status_code=403, detail="Forbidden")

    ref.update({"status": new_status.value})
    return _to_order(order_id, ref.get())
