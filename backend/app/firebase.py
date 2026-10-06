import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path


# Initialize Firebase only once
if not firebase_admin._apps:

    # Vercel / production
    firebase_credentials = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    if firebase_credentials:
        service_account_info = json.loads(firebase_credentials)
        cred = credentials.Certificate(service_account_info)

    else:
        # Local development
        BASE_DIR = Path(__file__).resolve().parent.parent
        SERVICE_ACCOUNT_FILE = (
            BASE_DIR / "firebase" / "serviceAccountKey.json"
        )

        cred = credentials.Certificate(
            str(SERVICE_ACCOUNT_FILE)
        )

    firebase_admin.initialize_app(cred)


# Firestore database connection
db = firestore.client()