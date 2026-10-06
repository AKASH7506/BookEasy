import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import os


# Render Secret File location
RENDER_SECRET_FILE = "/etc/secrets/serviceAccountKey.json"

# Local development location
LOCAL_SECRET_FILE = (
    Path(__file__).resolve().parent.parent
    / "firebase"
    / "serviceAccountKey.json"
)


if os.path.exists(RENDER_SECRET_FILE):
    SERVICE_ACCOUNT_FILE = RENDER_SECRET_FILE
else:
    SERVICE_ACCOUNT_FILE = str(LOCAL_SECRET_FILE)


if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)


db = firestore.client()