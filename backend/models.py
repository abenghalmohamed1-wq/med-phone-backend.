"""
models.py — Pydantic request / response schemas for the Med Phone API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class Category(str, Enum):
    phones    = "phones"
    airpods   = "airpods"
    watches   = "watches"

class OrderStatus(str, Enum):
    pending    = "pending"
    confirmed  = "confirmed"
    shipped    = "shipped"
    delivered  = "delivered"
    cancelled  = "cancelled"


# ─── Auth ─────────────────────────────────────────────────────────────────────

class TokenVerifyRequest(BaseModel):
    id_token: str = Field(..., description="Firebase ID token from the client")

class UserProfile(BaseModel):
    uid:          str
    email:        Optional[str]  = None
    display_name: Optional[str]  = None
    photo_url:    Optional[str]  = None
    email_verified: bool         = False


# ─── Products ─────────────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    name:        str
    brand:       str
    category:    Category
    price:       float = Field(..., gt=0)
    description: Optional[str]  = None
    emoji:       Optional[str]  = "📱"
    badge:       Optional[str]  = None
    stock:       int            = Field(default=0, ge=0)
    rating:      float          = Field(default=5.0, ge=0, le=5)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id:         str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Cart ─────────────────────────────────────────────────────────────────────

class CartItem(BaseModel):
    product_id: str
    quantity:   int = Field(..., ge=1)

class CartItemDetail(CartItem):
    name:      str
    price:     float
    emoji:     Optional[str] = "📱"

class CartResponse(BaseModel):
    items: List[CartItemDetail] = []
    total: float                = 0.0


# ─── Orders ───────────────────────────────────────────────────────────────────

class ShippingAddress(BaseModel):
    full_name: str
    phone:     str
    city:      str
    address:   str

class OrderCreate(BaseModel):
    items:    List[CartItem]
    shipping: ShippingAddress
    notes:    Optional[str] = None

class Order(BaseModel):
    id:          str
    user_uid:    str
    items:       List[CartItem]
    shipping:    ShippingAddress
    status:      OrderStatus = OrderStatus.pending
    total:       float
    notes:       Optional[str]     = None
    created_at:  Optional[datetime] = None


# ─── Contact ──────────────────────────────────────────────────────────────────

class ContactMessage(BaseModel):
    name:    str = Field(..., min_length=2)
    email:   EmailStr
    subject: str
    message: str = Field(..., min_length=10)

class ContactResponse(BaseModel):
    success: bool
    message: str


# ─── Commandes (Paiement à la livraison / COD) ────────────────────────────────

class CommandeStatus(str, Enum):
    en_attente = "en_attente"   # Commande reçue, pas encore traitée
    confirmee  = "confirmee"    # Confirmée par téléphone
    expediee   = "expediee"     # Envoyée au livreur
    livree     = "livree"       # Livrée au client
    annulee    = "annulee"      # Annulée

class Commande(BaseModel):
    id_produit:     str  = Field(..., description="ID du produit commandé")
    smiya_kliyane:  str  = Field(..., min_length=2, description="Nom complet du client")
    telephone:      str  = Field(..., description="Numéro de téléphone")
    adresse:        str  = Field(..., description="Adresse de livraison")
    ville:          str  = Field(..., description="Ville de livraison")
    notes:          Optional[str] = None

class CommandeResponse(BaseModel):
    message:     str
    id_commande: str
    status:      CommandeStatus = CommandeStatus.en_attente


# ─── Generic ──────────────────────────────────────────────────────────────────

class StatusResponse(BaseModel):
    status:  str
    message: str
