"""
routers/commandes.py — Paiement à la livraison (Cash on Delivery).

POST  /api/commandes              — passer une commande COD (public, sans auth)
GET   /api/commandes              — lister toutes les commandes (auth required)
GET   /api/commandes/{id}         — détails d'une commande (auth required)
PATCH /api/commandes/{id}/status  — changer le statut (auth required)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import List

from ..firebase import get_db
from ..models import Commande, CommandeResponse, CommandeStatus
from ..dependencies import get_current_user, UserProfile

router = APIRouter(prefix="/api/commandes", tags=["Commandes (COD)"])

NODE = "commandes"


# ── Passer une commande ───────────────────────────────────────────────────────

@router.post(
    "",
    response_model=CommandeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Passer une commande (COD) — Paiement à la livraison",
)
def dir_commande(commande: Commande):
    """
    Le client envoie sa commande sans paiement en ligne.
    On la sauvegarde dans Firebase avec le statut 'en_attente'.
    """
    root = get_db()
    ref  = root.child(NODE)

    commande_data                = commande.model_dump()
    commande_data["date"]        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commande_data["status"]      = CommandeStatus.en_attente.value

    nouvelle_commande = ref.push(commande_data)

    return CommandeResponse(
        message="Dazt l'commande mzyan! Ghanhedro m3ak f a9rab wa9t. 📦",
        id_commande=nouvelle_commande.key,
        status=CommandeStatus.en_attente,
    )


# ── Lister toutes les commandes (admin) ───────────────────────────────────────

@router.get(
    "",
    summary="Lister toutes les commandes (admin)",
)
def list_commandes(_user: UserProfile = Depends(get_current_user)):
    """Retourne toutes les commandes COD triées par date décroissante."""
    root = get_db()
    raw  = root.child(NODE).get() or {}

    commandes = []
    for cid, data in raw.items():
        if isinstance(data, dict):
            data["id"] = cid
            commandes.append(data)

    commandes.sort(key=lambda c: c.get("date", ""), reverse=True)
    return commandes


# ── Détails d'une commande ────────────────────────────────────────────────────

@router.get("/{commande_id}", summary="Voir une commande")
def get_commande(commande_id: str, _user: UserProfile = Depends(get_current_user)):
    root = get_db()
    data = root.child(NODE).child(commande_id).get()

    if not data:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    data["id"] = commande_id
    return data


# ── Changer le statut ─────────────────────────────────────────────────────────

@router.patch("/{commande_id}/status", summary="Changer le statut d'une commande")
def update_commande_status(
    commande_id: str,
    new_status:  CommandeStatus,
    _user:       UserProfile = Depends(get_current_user),
):
    root = get_db()
    ref  = root.child(NODE).child(commande_id)

    if not ref.get():
        raise HTTPException(status_code=404, detail="Commande introuvable")

    ref.update({"status": new_status.value})
    data       = ref.get()
    data["id"] = commande_id
    return data
