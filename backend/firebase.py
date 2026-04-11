"""
firebase.py — Firebase Admin SDK initialisation (singleton).

Uses Firebase Realtime Database (RTDB) — no billing required on Spark plan.
Import `get_db` in routers to get a database reference.
"""
import os
import firebase_admin
from firebase_admin import credentials, db
from .config import get_settings

settings = get_settings()

_app: firebase_admin.App | None = None


def get_firebase_app() -> firebase_admin.App:
    global _app
    if _app is not None:
        return _app

   import os

    if os.path.exists("/etc/secrets/firebase_credentials.json"):
        cred_path = "/etc/secrets/firebase_credentials.json"
    else:
        cred_path = settings.firebase_credentials_path
    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"Firebase credentials not found at '{cred_path}'.\n"
            "Download your service-account key from:\n"
            "Firebase Console → Project Settings → Service Accounts → "
            "Generate new private key"
        )

    db_url = settings.firebase_database_url
    if not db_url:
        raise ValueError(
            "FIREBASE_DATABASE_URL is not set in backend/.env\n"
            "It should look like: https://med-phone-e4814-default-rtdb.firebaseio.com"
        )

    cred  = credentials.Certificate(cred_path)
    _app  = firebase_admin.initialize_app(cred, {"databaseURL": db_url})
    return _app


def get_db() -> db.Reference:
    """Return the root Realtime Database reference."""
    get_firebase_app()
    return db.reference("/")
