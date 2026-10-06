import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path


# Path to Firebase service account key
BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_ACCOUNT_FILE = BASE_DIR / "firebase" / "serviceAccountKey.json"


# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(str(SERVICE_ACCOUNT_FILE))
    firebase_admin.initialize_app(cred)


# Firestore database connection
db = firestore.client()